import numpy as np
from build import build, load
from ng import run
_, pins = load('nets.txt')
out = f"v({pins[('J3', 'T')]})"


def corners(f, h):
    db = 20 * np.log10(abs(h))
    ref = db[np.argmin(abs(f - 1000))]
    k = np.argmin(abs(f - 1000))
    lo = np.interp(-3, (db[:k] - ref), f[:k]) if (db[:k] - ref).min() < -3 else None
    hi_seg = db[k:] - ref
    hi = None
    if hi_seg.min() < -3:
        i = np.argmax(hi_seg < -3)
        hi = np.interp(-3, [hi_seg[i], hi_seg[i - 1]], [f[k + i], f[k + i - 1]])
    return ref, lo, hi, db[np.argmin(abs(f - 20))] - ref


print('(SW2-2 now: 1 = flat, 0 = low cut)')
print('blend  SW2-2 SW2-3 SW2-4 | 1k level   low -3dB   high -3dB   @20Hz rel')
for blend in (0.0, 0.5):
    for sw in ((0, 1, 0, 0), (0, 0, 0, 0), (0, 1, 1, 0), (0, 1, 0, 1), (0, 1, 1, 1), (0, 0, 1, 1)):
        r = run(build('nets.txt', pos={'RV1': 1, 'RV2': 1, 'RV3': blend}, sw=sw,
                      src={'A': 'dc 0 ac 1', 'B': 'dc 0 ac 1'} if blend else None,
                      analysis='.ac dec 60 5 100k'), [out])
        ref, lo, hi, d20 = corners(r['x'], r[out])
        fmt = lambda v: f'{v:9.0f}' if v else '        -'
        print(f'{"end" if blend == 0 else "ctr":5}  {sw[1]:5} {sw[2]:5} {sw[3]:5} | {ref:8.2f}  {fmt(lo)}  {fmt(hi)}  {d20:9.2f}')
