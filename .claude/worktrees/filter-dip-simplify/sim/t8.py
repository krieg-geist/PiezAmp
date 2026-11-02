import numpy as np
from build import build, load
from ng import run
from variants import hpf_bypass, toggle, no_r14, r24, burst, single_fet_vref, single_fet_out
_, pins = load('nets.txt')
out = f"v({pins[('J3', 'T')]})"
lpf = f"v({pins[('U2', '5')]})"
db = lambda x: 20 * np.log10(max(abs(x), 1e-12))
tr = '.tran 20u 0.4 0 20u'

print('Clicks with all three changes (no R14, HPF bypass, R24 10k), mV typ / worst:')
for name, k, sc in (('SW2-1', 1, False), ('SW2-2', 2, True), ('SW2-3', 3, False)):
    row = []
    for ib in (200e-9, 800e-9):
        r = run(build('nets.txt', ib=ib, src={'A': 'dc 0', 'B': 'dc 0'},
                      variants=(no_r14, hpf_bypass, r24(10e3), toggle(k, 0.2, start_closed=sc)), analysis=tr), [out])
        t, v = r['x'], r[out]
        row.append(1000 * np.max(abs(v[t > 0.2] - np.median(v[(t > 0.15) & (t < 0.2)]))))
    print(f'  {name}: {row[0]:5.1f} / {row[1]:5.1f}')


def thd(t, v, f=1000, ncyc=10):
    T = ncyc / f
    tu = np.linspace(t[-1] - T, t[-1], 4096, endpoint=False)
    y = np.interp(tu, t, v)
    y = y - y.mean()
    Y = abs(np.fft.rfft(y))
    h = [Y[ncyc * k] for k in range(1, 10)]
    return 100 * np.sqrt(sum(a * a for a in h[1:])) / h[0], 2 * h[0] / len(y)


print('Gate held OPEN (J7 linked), THD at output vs piezo drive (1 kHz, gain x11, volume full):')
tr2 = '.tran 2u 30m 0 2u'
for name, var in (('back-to-back (now)', ()), ('single FET to VREF', (single_fet_vref,)),
                  ('single FET at vol-top', (single_fet_out,))):
    row = []
    for a in (0.03, 0.1, 0.2):
        r = run(build('nets.txt', pos={'RV3': 0.0}, src={'A': f'dc 0 sin(0 {a} 1k)', 'B': 'dc 0'},
                      variants=var, gate_off=True, analysis=tr2), [out])
        d, amp = thd(r['x'], r[out])
        row.append(f'{a*1000:4.0f}mVpk -> {amp:5.2f}Vpk THD {d:6.2f}%')
    print(f'  {name:22} ' + ' | '.join(row))

print('Mute depth (silent, gate active), 1 kHz small-signal:')
for name, var in (('back-to-back (now)', ()), ('single FET to VREF', (single_fet_vref,)),
                  ('single FET at vol-top', (single_fet_out,))):
    on = run(build('nets.txt', pos={'RV3': 0.0}, variants=var, gate_off=True, analysis='.ac lin 1 1k 1k'), [out])[out][0]
    off = run(build('nets.txt', pos={'RV3': 0.0}, variants=var, gate_off=False, analysis='.ac lin 1 1k 1k'), [out])[out][0]
    print(f'  {name:22} {db(off) - db(on):7.1f} dB')
