ngspice checks for PiezAmp, driven through KiCad's libngspice (no ngspice CLI needed).

    kicad-cli sch export netlist --format kicadsexpr ../piezamp.kicad_sch -o /tmp/p.net
    python3 nets.py /tmp/p.net . > nets.txt
    python3 t2_gain.py        # any t*.py

Models are approximations: behavioural NE5532 (Aol 100 dB, GBW 10 MHz, 200 nA bias, 1.5 V
from rails), VDMOS 2N7002 with body diode, standard 2N3904/1N4148/1N5819 models.
`variants.py` holds the circuit-change experiments (no R14, HPF bypass, R24 value, single-FET gates).
