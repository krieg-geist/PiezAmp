import numpy as np
from build import build, load
from ng import run
_, pins = load('nets.txt')
out = pins[('J3', 'T')]
hand = {0: 0.0, .1: 3.2, .25: 6.5, .5: 10.4, .75: 13.8, .9: 16.4, 1: 20.8}
print('rot   sim dB @1k   hand dB')
for x, h in hand.items():
    r = run(build('nets.txt', pos={'RV1': x, 'RV3': 0.0}, analysis='.ac lin 1 1k 1k'), [f'v({out})'])
    print(f'{x:4}  {20*np.log10(abs(r[f"v({out})"][0])):9.2f}   {h:7.1f}')
