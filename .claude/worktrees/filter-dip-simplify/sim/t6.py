import numpy as np
from build import build, load
from ng import run
from variants import no_r14, hpf_bypass, toggle
_, pins = load('nets.txt')
out = f"v({pins[('J3', 'T')]})"
lpf = f"v({pins[('U2', '5')]})"
nodea = f"v({pins[('C13', '1')]})"
db = lambda h: 20 * np.log10(abs(h))


def resp(var, sw, blend=0.0):
    r = run(build('nets.txt', pos={'RV3': blend}, sw=sw, variants=var, analysis='.ac dec 60 5 50k'), [out])
    x, d = r['x'], db(r[out])
    ref = d[np.argmin(abs(x - 1000))]
    lo = np.interp(-3, d[:np.argmin(abs(x - 1000))] - ref, x[:np.argmin(abs(x - 1000))])
    return ref, lo


print('AC: 1k level / low -3dB corner')
for name, var, off, on in (('current', (), (0, 0, 0, 0), (0, 1, 0, 0)),
                           ('no R14', (no_r14,), (0, 0, 0, 0), (0, 1, 0, 0)),
                           ('HPF bypass (no R44)', (hpf_bypass,), (0, 1, 0, 0), (0, 0, 0, 0)),
                           ('both', (no_r14, hpf_bypass), (0, 1, 0, 0), (0, 0, 0, 0))):
    for blend in (0.0, 0.5):
        a, b = resp(var, off, blend), resp(var, on, blend)
        print(f'  {name:20} blend {blend}: HPF off {a[0]:6.2f} dB, {a[1]:5.1f} Hz | HPF on {b[0]:6.2f} dB, {b[1]:5.1f} Hz')

print('DC (9 V) LPF node / NODE_A, typ and worst-case bias:')
for name, var in (('current', ()), ('no R14', (no_r14,)), ('both', (no_r14, hpf_bypass))):
    row = []
    for ib in (200e-9, 800e-9):
        r = run(build('nets.txt', ib=ib, variants=var, analysis='.op'), [lpf, nodea, f"v({pins[('R31', '2')]})"])
        row.append(f'LPF-VREF {1000*(r[lpf][0]-r[f"v({pins[(chr(82)+"31", "2")]})"][0]):7.1f} mV  NODE_A-VREF {1000*(r[nodea][0]-r[f"v({pins[(chr(82)+"31", "2")]})"][0]):7.1f} mV')
    print(f'  {name:10} typ: {row[0]} | 800nA: {row[1]}')

print('Switch clicks at the output (no audio), peak deviation after toggle, mV:')
tr = '.tran 20u 0.4 0 20u'
cases = [('current  SW2-2 HPF on ', (toggle(2, 0.2),)),
         ('bypass   SW2-2 HPF on ', (hpf_bypass, toggle(2, 0.2, start_closed=True))),
         ('current  SW2-3 LPF on ', (toggle(3, 0.2),)),
         ('bypass   SW2-3 LPF on ', (hpf_bypass, toggle(3, 0.2))),
         ('current  SW2-1 polarity', (toggle(1, 0.2),))]
for name, var in cases:
    row = []
    for ib in (200e-9, 800e-9):
        r = run(build('nets.txt', ib=ib, src={'A': 'dc 0', 'B': 'dc 0'}, variants=var, analysis=tr), [out])
        t, v = r['x'], r[out]
        base = np.median(v[(t > 0.15) & (t < 0.2)])
        row.append(1000 * np.max(abs(v[t > 0.2] - base)))
    print(f'  {name}: typ {row[0]:6.1f}   worst-bias {row[1]:6.1f}')
