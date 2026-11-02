"""KiCad netlist (parsed nets.txt) -> SPICE netlist for PiezAmp, with knobs and variants.

Models are approximations (see MODELS): NE5532 is a behavioural macromodel (Aol 100 dB,
GBW 10 MHz, 9 V/us, 200 nA bias, output 1.5 V from rails); 2N7002 is a VDMOS with body diode;
MMBT3904 / 1N4148 / 1N5819 are the common published discrete models.
"""
import math
import re

MODELS = r"""
.options rshunt=1e12
.subckt NE5532 inp inn vcc vee out params: ib=200n
Ibp inp 0 {ib}
Ibn inn 0 {ib}
Bmid mid 0 V=(v(vcc)+v(vee))/2
Bgm mid n1 I=0.143*tanh((v(inp)-v(inn))/0.143)
R1 n1 mid 1e5
C1 n1 mid 15.9n
Vh vcc clh 1.5
Vl cll vee 1.5
Dh n1 clh DCLAMP
Dl cll n1 DCLAMP
Eo o2 0 n1 0 1
Ro o2 out 5
Rin inp inn 1Meg
.model DCLAMP D(IS=1e-14 N=0.05)
.ends
.model Q3904 NPN(Is=6.734f Xti=3 Eg=1.11 Vaf=74.03 Bf=416.4 Ne=1.259 Ise=6.734f Ikf=66.78m Xtb=1.5 Br=.7371 Nc=2 Isc=0 Ikr=0 Rc=1 Cjc=3.638p Mjc=.3085 Vjc=.75 Fc=.5 Cje=4.493p Mje=.2593 Vje=.75 Tr=239.5n Tf=301.2p Itf=.4 Vtf=4 Xtf=2 Rb=10)
.model M7002 VDMOS(Vto=1.6 Kp=0.17 Rs=0.75 Rd=0 Rg=3 Rb=0.14 Is=0.04p Cjo=50p Cgdmax=80p Cgdmin=12p Cgs=50p ksubthres=0.1 mtriode=1.25)
.model D4148 D(Is=2.52n Rs=.568 N=1.752 Cjo=4p M=.4 tt=20n)
.model D5819 D(Is=31.7u Rs=.051 N=1.373 Cjo=110p M=.35 Eg=.69 Xti=2)
"""

UNIT = {'f': 1e-15, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'µ': 1e-6, 'm': 1e-3, 'k': 1e3, 'M': 1e6, 'R': 1, '': 1}


def val(s):
    """'1.5k' '470R' '100nF C0G' '22uf' '10k log' '4.7k' '0R' -> float"""
    s = s.split()[0]
    m = re.match(r'^(\d+(?:\.\d+)?)([fpnuµmkMR]?)(\d*)', s)
    assert m, s
    num = float(m.group(1))
    if m.group(3):                       # 4k7 style
        num = float(m.group(1) + '.' + m.group(3))
    return num * UNIT[m.group(2)]


def load(path):
    comps, pins = {}, {}
    for line in open(path):
        p = line.split()
        if not p:
            continue
        if p[0] == 'COMP':
            comps[p[1]] = ' '.join(p[2:-1])
        elif p[0] == 'NET':
            name, _, nodes = line[4:].partition(' : ')
            name = name.strip()
            n = 'n_' + re.sub(r'[^A-Za-z0-9]', '_', name.replace('+', 'P').replace('-', 'M')).strip('_')
            if name == 'GND':
                n = '0'
            for nd in nodes.split():
                ref, pin = nd.split('.')
                pins[(ref, pin)] = n
    return comps, pins


def build(nets_txt, vcc=9.0, pos=None, sw=(0, 0, 0, 0), gate_off=True, ib=200e-9,
          piezo_c=15e-9, rload=47e3, src=None, variants=(), analysis='', extra=''):
    """pos: dict of pot positions 0..1 measured from pin 1 (RV1/RV2 0=min gain? see note).
    sw: SW2 positions 1..4 (1=closed). src: dict {'A': 'spec', 'B': 'spec'} SPICE source specs."""
    comps, pins = load(nets_txt)
    pos = dict({'RV1': 1.0, 'RV2': 1.0, 'RV3': 0.5, 'RV5': 1.0, 'RV6': 0.5}, **(pos or {}))
    src = dict({'A': 'dc 0 ac 1', 'B': 'dc 0'}, **(src or {}))
    P = lambda r, n: pins.get((r, n), f'nc_{r}_{n}')
    out = [f'* PiezAmp generated', MODELS]
    out.append(f'Vsup vin 0 dc {vcc}')
    for ref, v in sorted(comps.items()):
        k = re.match(r'[A-Z#]+', ref).group(0)
        if k == 'R':
            out.append(f'R{ref} {P(ref, "1")} {P(ref, "2")} {max(val(v), 1e-3)}')
        elif k == 'C':
            out.append(f'C{ref} {P(ref, "1")} {P(ref, "2")} {val(v)}')
        elif k == 'RV':
            R = val(v)
            x = min(max(pos[ref], 1e-4), 1 - 1e-4)
            if 'log' in v:                        # A-taper approx: 10 % at mid (pin1 = GND end)
                r12 = R * (10 ** (2 * x) - 1) / 99
            else:
                r12 = R * x
            out.append(f'R{ref}a {P(ref, "1")} {P(ref, "2")} {r12}')
            out.append(f'R{ref}b {P(ref, "2")} {P(ref, "3")} {R - r12}')
        elif k == 'U':
            out.append(f'X{ref}A {P(ref, "3")} {P(ref, "2")} {P(ref, "8")} {P(ref, "4")} {P(ref, "1")} NE5532 ib={ib}')
            out.append(f'X{ref}B {P(ref, "5")} {P(ref, "6")} {P(ref, "8")} {P(ref, "4")} {P(ref, "7")} NE5532 ib={ib}')
        elif k == 'D':
            if 'BAV99' in v:
                out.append(f'D{ref}a {P(ref, "1")} {P(ref, "3")} D4148')
                out.append(f'D{ref}b {P(ref, "3")} {P(ref, "2")} D4148')
            elif '581' in v:
                out.append(f'D{ref} {P(ref, "2")} {P(ref, "1")} D5819')
            else:
                out.append(f'D{ref} {P(ref, "2")} {P(ref, "1")} D4148')
        elif k == 'Q':
            if '3904' in v:
                out.append(f'Q{ref} {P(ref, "3")} {P(ref, "1")} {P(ref, "2")} Q3904')
            else:
                out.append(f'M{ref} {P(ref, "3")} {P(ref, "1")} {P(ref, "2")} M7002')
        elif ref == 'SW2':
            for i, s in enumerate(sw):
                out.append(f'RSW2_{i + 1} {P(ref, str(i + 1))} {P(ref, str(8 - i))} {0.05 if s else 1e9}')
        elif ref == 'SW1':
            out.append(f'RSW1 {P(ref, "1")} {P(ref, "2")} 0.01')
        elif ref == 'J4':
            out.append(f'Rj4 vin {P(ref, "1")} 0.01')
            if (ref, '3') in pins:                       # 1x03: switch / jumper across 1-2 off-board
                out.append(f'Rj4sw {P(ref, "1")} {P(ref, "2")} 0.01')
        elif ref in ('J5', 'J6'):
            ch = 'A' if ref == 'J5' else 'B'
            out.append(f'Cpz{ch} {P(ref, "1")} pz{ch} {piezo_c}')
            out.append(f'V{ch} pz{ch} {P(ref, "2")} {src[ch]}')
        elif ref == 'J3':
            out.append(f'Rload {P(ref, "T")} {P(ref, "S")} {rload}')
        elif ref in ('J8', 'J9'):
            out.append(f'Rl{ref} {P(ref, "1")} {P(ref, "2")} {rload}')
        elif ref == 'J7':
            out.append(f'Rj7 {P(ref, "1")} {P(ref, "2")} {0.01 if gate_off else 1e12}')
        else:
            raise ValueError(ref)
    net = '\n'.join(out)
    for f in variants:
        net = f(net, pins)
    return net + '\n' + extra + '\n' + analysis


def node(pins, ref, pin):
    return pins[(ref, pin)]
