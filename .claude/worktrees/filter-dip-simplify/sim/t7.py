import numpy as np
from build import build, load
from ng import run
from variants import hpf_bypass, toggle, no_r14, r24
_, pins = load('nets.txt')
out = f"v({pins[('J3', 'T')]})"
tr = '.tran 20u 0.4 0 20u'
cases = [('current  SW2-2 HPF on ', (toggle(2, 0.2),)),
         ('bypass   SW2-2 HPF on ', (hpf_bypass, toggle(2, 0.2, start_closed=True))),
         ('current  SW2-3 LPF on ', (toggle(3, 0.2),)),
         ('bypass   SW2-3 LPF on ', (hpf_bypass, toggle(3, 0.2))),
         ('current  SW2-4 LPF2 on', (toggle(4, 0.2),)),
         ('bypass   SW2-4 LPF2 on', (hpf_bypass, toggle(4, 0.2))),
         ('current  SW2-1 polarity', (toggle(1, 0.2),)),
         ('R24=10k  SW2-1 polarity', (r24(10e3), toggle(1, 0.2)))]
print('Switch clicks at the output (no audio), peak deviation after toggle (mV):')
for name, var in cases:
    row = []
    for ib in (200e-9, 800e-9):
        r = run(build('nets.txt', ib=ib, src={'A': 'dc 0', 'B': 'dc 0'}, variants=var, analysis=tr), [out])
        t, v = r['x'], r[out]
        base = np.median(v[(t > 0.15) & (t < 0.2)])
        row.append(1000 * np.max(abs(v[t > 0.2] - base)))
    print(f'  {name}: typ {row[0]:6.1f}   worst-bias {row[1]:6.1f}')
