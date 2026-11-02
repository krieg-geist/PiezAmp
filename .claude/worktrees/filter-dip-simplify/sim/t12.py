import numpy as np
from build import build, load
from ng import run
from variants import burst
from t10 import rv6_series
_, pins = load('nets.txt')
gate = f"v({pins[('Q3', '1')]})"


def opens(a, R):
    r = run(build('nets.txt', pos={'RV3': 0.0}, src={'B': 'dc 0'}, gate_off=False,
                  variants=(burst('A', a, 0.05, 9), rv6_series(R)), analysis='.tran 50u 0.6 0 50u'), [gate])
    t, g = r['x'], r[gate]
    return g[t > 0.5].mean() < 2.0


print('Steady-tone gate-open threshold (1 kHz, 9 V), level at BLEND node:')
import sys
for R in [float(x) for x in sys.argv[1:]] or (1e3, 30e3, 100e3, 250e3, 500e3, 1e6):
    lo, hi = np.log10(0.05e-3), np.log10(0.27)
    if not opens(10 ** hi, R):
        print(f'  RV6 {R/1e3:5.0f}k: never opens'); continue
    for _ in range(7):
        m = (lo + hi) / 2
        lo, hi = (lo, m) if opens(10 ** m, R) else (m, hi)
    pk = 10 ** hi * 10.8
    print(f'  RV6 {R/1e3:5.0f}k ({R/1e5*100:5.1f}% of a 100k pot): {pk*1000:7.1f} mV pk  ({20*np.log10(pk/1.414/0.775):6.1f} dBu)')
