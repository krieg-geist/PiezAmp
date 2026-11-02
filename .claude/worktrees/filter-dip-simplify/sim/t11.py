import numpy as np
from build import build, load
from ng import run
from variants import burst
from t10 import rv6_series
_, pins = load('nets.txt')
gate = f"v({pins[('Q3', '1')]})"
print('Steady 1 kHz tone from t=0.1 s, RV6 = 1k (min). GATE at 0.5 / 1.0 / 1.9 s:')
for a in (1e-3, 2e-3, 3e-3, 4.5e-3, 6e-3):
    r = run(build('nets.txt', pos={'RV3': 0.0}, src={'B': 'dc 0'}, gate_off=False,
                  variants=(burst('A', a, 0.1, 9), rv6_series(1e3)), analysis='.tran 50u 2 0 50u'), [gate])
    t, g = r['x'], r[gate]
    v = [g[np.argmin(abs(t - x))] for x in (0.5, 1.0, 1.9)]
    print(f'  piezo {a*1000:4.1f} mVpk (~{a*10.8*1000:5.1f} mV at BLEND): ' + ' / '.join(f'{x:5.2f}' for x in v))
