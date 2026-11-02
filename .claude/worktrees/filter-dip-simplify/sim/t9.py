import numpy as np
from build import build, load
from ng import run
from variants import burst
_, pins = load('nets.txt')
out, gate = f"v({pins[('J3', 'T')]})", f"v({pins[('Q3', '1')]})"
tr = '.tran 20u 1.6 0 20u'


def env(t, v, win=2e-3):
    tu = np.arange(0, t[-1], 1e-4)
    y = np.interp(tu, t, v)
    y = y - np.median(y[:500])
    n = int(win / 1e-4)
    return tu, np.sqrt(np.convolve(y * y, np.ones(n) / n, 'same')) * 1.414


print('Gate dynamics, gain x11, piezo tone burst 0.1-0.6 s (1 kHz):')
print(' RV6 pos  burst mVpk | open level  attack(to -3dB)  release(to -40dB)  GATE V during/after')
for rv6 in (0.0, 0.5, 1.0):
    for a in (0.3e-3, 1e-3, 3e-3, 10e-3, 30e-3):
        r = run(build('nets.txt', pos={'RV3': 0.0, 'RV6': rv6}, src={'B': 'dc 0'}, gate_off=False,
                      variants=(burst('A', a, 0.1, 0.6),), analysis=tr), [out, gate])
        t, e = env(r['x'], r[out])
        ideal = a * 10 ** (20.7 / 20)
        s = e[(t > 0.4) & (t < 0.59)].mean()
        lvl = 20 * np.log10(s / ideal)
        att = t[(t > 0.1) & (e > 0.707 * s)]
        att = (att[0] - 0.1) * 1000 if len(att) and lvl > -20 else float('nan')
        rel = t[(t > 0.6) & (e < 0.01 * s)]
        rel = (rel[0] - 0.6) * 1000 if len(rel) and lvl > -20 else float('nan')
        g = r[gate]
        gd = g[(r['x'] > 0.4) & (r['x'] < 0.59)].mean()
        ga = g[r['x'] > 1.5].mean()
        print(f'  {rv6:4}   {a*1000:8.1f}    | {lvl:7.1f} dB   {att:7.1f} ms      {rel:8.1f} ms      {gd:5.2f} / {ga:5.2f}')
