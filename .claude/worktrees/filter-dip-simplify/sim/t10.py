import re
import numpy as np
from build import build, load
from ng import run
_, pins = load('nets.txt')
gate, blend = f"v({pins[('Q3', '1')]})", f"v({pins[('C50', '1')]})"


def ramp(amax, T):
    def g(net, pins):
        return re.sub(r'^VA (\S+) (\S+) .*$',
                      lambda m: f'BA {m.group(1)} {m.group(2)} V={amax}*(time/{T})*sin(2*3.14159265*1000*time)', net, flags=re.M)
    return g


def rv6_series(R):
    """replace the RV6 pot by a fixed series resistance R (wiper tied to pin 3 => R = r12)"""
    def g(net, pins):
        net = re.sub(r'^RRV6a (\S+) (\S+) \S+$', lambda m: f'RRV6a {m.group(1)} {m.group(2)} {R}', net, flags=re.M)
        return re.sub(r'^RRV6b .*$', '', net, flags=re.M)
    return g


if __name__ == '__main__':
  T = 3.0
  print('Gate-open threshold vs RV6 series resistance (1 kHz, 9 V): blend-node level where GATE drops below 2 V')
  for R in (1e3, 10e3, 30e3, 100e3, 200e3, 300e3, 500e3, 1e6):
      r = run(build('nets.txt', pos={'RV3': 0.0}, src={'B': 'dc 0'}, gate_off=False,
                    variants=(ramp(0.27, T), rv6_series(R)), analysis=f'.tran 50u {T} 0 50u'), [gate, blend])
      t, g = r['x'], r[gate]
      k = np.argmax((g < 2) & (t > 0.05))
      if g[k] < 2:
          b = r[blend]
          w = (t > t[k] - 0.01) & (t < t[k])
          pk = (b[w].max() - b[w].min()) / 2
          print(f'  RV6 = {R/1e3:6.0f}k : opens at {1000*pk:7.1f} mV peak at BLEND  ({20*np.log10(pk/1.414/0.775):6.1f} dBu)')
      else:
          print(f'  RV6 = {R/1e3:6.0f}k : never opens up to 2.9 V peak at BLEND')
  