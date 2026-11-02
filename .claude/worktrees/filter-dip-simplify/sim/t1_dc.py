from build import build, load
from ng import run
_, pins = load('nets.txt')
N = lambda r, p: pins[(r, p)]
probes = {'VCC': N('U1','8'), 'VREF': N('R31','2'), 'VREF_IN': N('R33','2'), 'U1A out': N('U1','1'),
          'U1B out': N('U1','7'), 'NODE_A': N('C13','1'), 'NODE_B': N('C23','1'), 'U2A out': N('U2','1'),
          'LPF (U2B+)': N('U2','5'), 'U2B out': N('U2','7'), 'GATE': N('Q3','1'), 'U1 +IN A': N('U1','3')}
vecs = [f'v({n})' for n in probes.values()]
print(f"{'node':12}" + ''.join(f'{h:>11}' for h in ('9V typ', '9V 800nA', '18V typ', '18V 800nA')))
res = []
for vcc, ib in ((9, 200e-9), (9, 800e-9), (18, 200e-9), (18, 800e-9)):
    r = run(build('nets.txt', vcc=vcc, ib=ib, analysis='.op'), vecs)
    res.append([r[v][0] for v in vecs])
for i, k in enumerate(probes):
    print(f'{k:12}' + ''.join(f'{res[j][i]:11.3f}' for j in range(4)))
