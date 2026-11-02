"""Clicks on the simplified circuit (SW2-2 now: closed = flat)."""
import numpy as np
from build import build, load
from ng import run
from variants import toggle
_, pins = load('nets.txt')
out = f"v({pins[('J3', 'T')]})"
print('Switch clicks at output, mV typ / worst-bias:')
for name, k, sc in (('SW2-1 polarity', 1, False), ('SW2-2 low cut on', 2, True), ('SW2-3 LPF on', 3, False)):
    row = []
    for ib in (200e-9, 800e-9):
        r = run(build('nets.txt', ib=ib, sw=(0, 1, 0, 0), src={'A': 'dc 0', 'B': 'dc 0'},
                      variants=(toggle(k, 0.2, start_closed=sc),), analysis='.tran 20u 0.4 0 20u'), [out])
        t, v = r['x'], r[out]
        row.append(1000 * np.max(abs(v[t > 0.2] - np.median(v[(t > 0.15) & (t < 0.2)]))))
    print(f'  {name:18}: {row[0]:6.1f} / {row[1]:6.1f}')
