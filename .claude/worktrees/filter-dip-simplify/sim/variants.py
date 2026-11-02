import re


def no_r14(net, pins):
    return re.sub(r'^RR14 .*$', '', net, flags=re.M)


def hpf_bypass(net, pins):
    """R44 gone; R43 permanently to VREF; SW2-2 shorts C43 (closed = HPF OFF)."""
    vref, node, blend = pins[('R31', '2')], pins[('C43', '2')], pins[('C43', '1')]
    net = re.sub(r'^RR44 .*$', '', net, flags=re.M)
    net = re.sub(r'^RR43 .*$', f'RR43 {node} {vref} 22000.0', net, flags=re.M)
    return re.sub(r'^RSW2_2 \S+ \S+ (\S+)$', lambda m: f'RSW2_2 {blend} {node} {m.group(1)}', net, flags=re.M)


def toggle(k, t_on, start_closed=False):
    """replace RSW2_k by a switch that changes state at t_on"""
    def f(net, pins):
        m = re.search(r'^RSW2_%d (\S+) (\S+) \S+$' % k, net, flags=re.M)
        a, b = m.group(1), m.group(2)
        v0, v1 = (1, 0) if start_closed else (0, 1)
        sw = (f'S{k} {a} {b} ctl{k} 0 SWM\nVctl{k} ctl{k} 0 PWL(0 {v0} {t_on} {v0} {t_on + 1e-6} {v1})\n'
              f'.model SWM SW(Ron=0.05 Roff=1e9 Vt=0.5 Vh=0.1)')
        return net[:m.start()] + sw + net[m.end():]
    return f


def r24(v):
    def f(net, pins):
        return re.sub(r'^RR24 (\S+) (\S+) \S+$', lambda m: f'RR24 {m.group(1)} {m.group(2)} {v}', net, flags=re.M)
    return f


def burst(ch, amp, t0, t1, f=1000):
    def g(net, pins):
        return re.sub(r'^V%s (\S+) (\S+) .*$' % ch,
                      lambda m: f'B{ch} {m.group(1)} {m.group(2)} V={amp}*sin(2*3.14159265*{f}*time)*(time>{t0})*(time<{t1})',
                      net, flags=re.M)
    return g


def single_fet_vref(net, pins):
    """one 2N7002: drain LPF, source VREF (Q4 removed)"""
    vref, s = pins[('R31', '2')], pins[('Q3', '2')]
    net = re.sub(r'^MQ4 .*$', '', net, flags=re.M)
    return re.sub(r'^MQ3 (\S+) (\S+) \S+ (\S+)$', lambda m: f'MQ3 {m.group(1)} {m.group(2)} {vref} {m.group(3)}', net, flags=re.M)


def single_fet_out(net, pins):
    """reference-style: Q3/Q4 off the LPF node; one 2N7002 from C41/RV5-top (0 V node) to GND"""
    top, gate = pins[('C41', '2')], pins[('Q3', '1')]
    net = re.sub(r'^MQ[34] .*$', '', net, flags=re.M)
    return net + f'\nMQX {top} {gate} 0 M7002'
