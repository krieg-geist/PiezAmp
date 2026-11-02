import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from sexpr import parse
t = parse(open(sys.argv[1]).read())
def kids(n, k): return [c for c in n if isinstance(c, list) and c and c[0] == k]
def val(n, k):
    c = kids(n, k); return c[0][1] if c else ''
comps = kids(t, 'components')[0]
for c in kids(comps, 'comp'):
    print('COMP', val(c, 'ref'), val(c, 'value'), val(c, 'footprint'))
for n in kids(kids(t, 'nets')[0], 'net'):
    print('NET', val(n, 'name'), ':', ' '.join(val(x, 'ref') + '.' + val(x, 'pin') for x in kids(n, 'node')))
