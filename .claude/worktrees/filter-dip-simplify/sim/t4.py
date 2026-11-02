import re
import numpy as np
from build import build, load
from ng import run
_, pins = load('nets.txt')
out = f"v({pins[('J3', 'T')]})"
db = lambda h: 20 * np.log10(abs(h))
ac1k = '.ac lin 1 1k 1k'

# --- polarity: B only, blend at B end
for s1 in (0, 1):
    r = run(build('nets.txt', pos={'RV3': 1.0}, sw=(s1, 0, 0, 0), src={'A': 'dc 0', 'B': 'dc 0 ac 1'}, analysis=ac1k), [out])
    h = r[out][0]
    print(f'polarity SW2-1={s1}: {db(h):.3f} dB, phase {np.degrees(np.angle(h)):7.2f} deg')
# A+B equal at blend centre: in-phase vs inverted
for s1 in (0, 1):
    r = run(build('nets.txt', pos={'RV3': 0.5}, sw=(s1, 0, 0, 0), src={'A': 'dc 0 ac 1', 'B': 'dc 0 ac 1'}, analysis=ac1k), [out])
    print(f'A+B same source, blend ctr, SW2-1={s1}: {db(r[out][0]):7.2f} dB')

# --- gate mute depth (AC small-signal around the silent operating point)
for off in (True, False):
    r = run(build('nets.txt', pos={'RV3': 0.0}, gate_off=off, analysis=ac1k), [out, f"v({pins[('Q3', '1')]})"])
    print(f'gate_off={off}: out {db(r[out][0]):7.2f} dB   GATE dc n/a')
r = run(build('nets.txt', gate_off=False, analysis='.op'), [f"v({pins[('Q3', '1')]})"])
print('silent GATE voltage (should be high = muted):', round(r[f"v({pins[('Q3', '1')]})"][0], 2))


# --- VREF_IN: crosstalk B -> A path through VREF
def merge_vref(net, pins):
    vin = pins[('R33', '2')]
    net = re.sub(r'^RR33 .*$', f'RR33 {vin} {pins[("R33", "1")]} 1e-3', net, flags=re.M)
    return re.sub(r'^CC34 .*$', '', net, flags=re.M)


f = '.ac dec 20 10 20k'
for name, var in (('with R33/C34 (now)', ()), ('VREF_IN merged into VREF', (merge_vref,))):
    for s1 in (0, 1):
        r = run(build('nets.txt', pos={'RV3': 0.0}, sw=(s1, 0, 0, 0), src={'A': 'dc 0', 'B': 'dc 0 ac 1'},
                      variants=var, analysis=f), [out])
        x = r['x']
        pick = {k: db(r[out][np.argmin(abs(x - k))]) for k in (20, 100, 1000)}
        print(f'B->A crosstalk, {name:26} SW2-1={s1}: ' + '  '.join(f'{k}Hz {v:7.1f} dB' for k, v in pick.items()))
