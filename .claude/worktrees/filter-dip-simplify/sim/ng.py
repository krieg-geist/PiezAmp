"""Minimal ctypes driver for KiCad's libngspice: run(netlist_text, vectors) -> {name: np.array}."""
import ctypes as C
import os
import tempfile

import numpy as np

LIB = C.CDLL('/usr/lib/x86_64-linux-gnu/libngspice.so.0')
LOG = []
_out = C.CFUNCTYPE(C.c_int, C.c_char_p, C.c_int, C.c_void_p)(lambda s, i, p: LOG.append(s.decode(errors='replace')) or 0)
_stat = C.CFUNCTYPE(C.c_int, C.c_char_p, C.c_int, C.c_void_p)(lambda s, i, p: 0)
_exit = C.CFUNCTYPE(C.c_int, C.c_int, C.c_bool, C.c_bool, C.c_int, C.c_void_p)(lambda *a: 0)
LIB.ngSpice_Init(_out, _stat, _exit, None, None, None, None)
LIB.ngSpice_Command.argtypes = [C.c_char_p]
LIB.ngSpice_Circ.argtypes = [C.POINTER(C.c_char_p)]


def cmd(s):
    return LIB.ngSpice_Command(s.encode())


def run(net, vecs, analysis=None):
    """net: netlist text without .end. vecs: list of expressions to dump. Returns dict incl. 'x' (time/freq/sweep)."""
    LOG.clear()
    cmd('destroy all')
    cmd('remcirc')
    lines = [l for l in net.strip().split('\n')] + ['.end']
    arr = (C.c_char_p * (len(lines) + 1))(*[l.encode() for l in lines], None)
    if LIB.ngSpice_Circ(arr) != 0:
        raise RuntimeError('\n'.join(LOG[-20:]))
    if analysis:
        cmd(analysis)
    else:
        cmd('run')
    err = [l for l in LOG if 'rror' in l and 'warning' not in l.lower()]
    if err:
        raise RuntimeError('\n'.join(LOG[-25:]))
    fd, path = tempfile.mkstemp(suffix='.txt')
    os.close(fd)
    cmd('set wr_singlescale')
    cmd('set wr_vecnames')
    cmd(f'wrdata {path} ' + ' '.join(vecs))
    with open(path) as f:
        head = f.readline().split()
    d = np.atleast_2d(np.loadtxt(path, skiprows=1))
    os.unlink(path)
    out = {'x': d[:, 0]}
    # complex vectors come out as re/im pairs
    cols = d[:, 1:]
    if cols.shape[1] == 2 * len(vecs):
        for k, v in enumerate(vecs):
            out[v] = cols[:, 2 * k] + 1j * cols[:, 2 * k + 1]
    else:
        for k, v in enumerate(vecs):
            out[v] = cols[:, k]
    return out


if __name__ == '__main__':
    r = run('t\nV1 a 0 dc 1 ac 1\nR1 a b 1k\nC1 b 0 159n\n.ac dec 10 10 100k', ['v(b)'])
    i = np.argmin(abs(r['x'] - 1000))
    print('f', r['x'][i], 'gain dB', 20 * np.log10(abs(r['v(b)'][i])))
    r = run('t\nV1 a 0 dc 1\nR1 a b 1k\nR2 b 0 3k\n.op', ['v(b)'])
    print('op', r['v(b)'])
