import re
import numpy as np
from build import build, load
from ng import run
_, pins = load('nets.txt')
aout = f"v({pins[('U1', '1')]})"
db = lambda h: 20 * np.log10(abs(h))


def merge_vref(net, pins):
    vin = pins[('R33', '2')]
    net = re.sub(r'^RR33 .*$', f'RR33 {vin} {pins[("R33", "1")]} 1e-3', net, flags=re.M)
    return re.sub(r'^CC34 .*$', '', net, flags=re.M)


def supply_ripple(net, pins):          # 100 mV ripple on the supply instead of B signal
    return net.replace('Vsup vin 0 dc 9.0', 'Vsup vin 0 dc 9.0 ac 0.1')


f = '.ac dec 20 10 20k'
print('B signal leaking into preamp A output (A source off), rel. to A own gain (+20.8 dB):')
for name, var in (('R33/C34 fitted', ()), ('merged', (merge_vref,))):
    for s1 in (0, 1):
        r = run(build('nets.txt', sw=(s1, 0, 0, 0), src={'A': 'dc 0', 'B': 'dc 0 ac 1'}, variants=var, analysis=f), [aout])
        x = r['x']
        print(f'  {name:15} SW2-1={s1}: ' + '  '.join(f'{k}Hz {db(r[aout][np.argmin(abs(x-k))]) - 20.8:7.1f} dB' for k in (20, 100, 1000)))
print('100 mV supply ripple at preamp A output:')
for name, var in (('R33/C34 fitted', (supply_ripple,)), ('merged', (merge_vref, supply_ripple))):
    r = run(build('nets.txt', src={'A': 'dc 0', 'B': 'dc 0'}, variants=var, analysis=f), [aout])
    x = r['x']
    print(f'  {name:15}: ' + '  '.join(f'{k}Hz {db(r[aout][np.argmin(abs(x-k))]):7.1f} dBV' for k in (50, 100, 1000)))
