# Dual Piezo Preamp (NE5532): Final Design Plan

**Status:** design frozen, ready for schematic capture in `piezamp.kicad_sch`.

Two high-impedance piezo contact-mic preamps based on Richard Mudhar's low-noise
piezo amplifier, using two **NE5532** duals. The design adds:

- a gain trim on each channel
- a polarity invert on channel B, set by a DIP switch
- a trimpot blend
- DIP-switched low-cut (~72 Hz) and a 4-step high-cut (off / 10.6 / 7.2 / 4.3 kHz)
- optional direct A/B outputs on headers, before the blend
- a 9 mm master volume pot

---

## 0. Design decisions

| # | Decision | Choice | Notes |
|---|---|---|---|
| D1 | Op-amp | **NE5532** (×2) | Lowest A-weighted noise into a disc-sized source. Trade-offs are in Appendix A |
| D2 | Filter | **Fixed, DIP-switched: low-cut ~72 Hz (SW2-2 OFF; ON = flat); high-cut 10.6 kHz (SW2-3), 7.2 kHz (SW2-4), 4.3 kHz (both), 6 dB/oct each** | Replaced the RV4 1 MΩ high-cut trimmer (27 kHz → 34 Hz), which crammed most of its useful range into the first few degrees of rotation. §3.4 gives the sensible range for each corner |
| D3 | Source | **20–35 mm piezo contact discs** (≈5–30 nF) | Not suitable for 1 nF under-saddle pickups (§1) |
| D4 | Input impedance | **1 MΩ** | The limit is set by NE5532 bias current (§1) |
| D5 | Polarity | Channel B only, **+1/−1 op-amp stage** switched by SW2-1 | Only the relative polarity matters for the blend |
| D11 | Outputs | **Mono on J3 tip; optional direct A and B on headers J8/J9**, taken before the blend | Replaced the SW2-2…4 stereo-on-TRS mode, which needed three switch positions and routed A through U2B (§3.6) |
| D6 | Controls | Gain A, gain B and blend are **trimmers**; filters are DIP switches. **Master volume is a 9 mm 10k log panel pot** | |
| D7 | Power | **9–18 V** via a 2-pin power header (DC jack / battery / switching wired off-board), with reverse-polarity protection. All caps rated ≥ 25 V | Use 18 V for more headroom (§6) |
| D8 | Connectors | **2.54 mm pin headers** for piezo inputs, power and power switch, on the left edge. **Output jack J3 (Neutrik NMJ6HCD2, through-hole) and master pot RV5 (right-angle 9 mm) on the right edge**, both mounting through the panel | The jack holds the board in the enclosure. RV5's holes also take a 1×3 header if you'd rather use an off-board pot |
| D9 | Construction | **SMD for JLC assembly**: 0603 resistors, 0603/1206 ceramics (no electrolytics), SOD diodes, NE5532DR (SOIC-8). Through-hole trimmers (T73YE), DIP switch and headers | Favours JLC basic parts |
| D10 | Enclosure / PCB | **Grounded metal** box. PCB is **64 × 41.3 mm, 2 layers, all parts on top** (§12) | Needed for hum rejection (§8) |

---

## 1. How the reference circuit works

Reference: [RM_piezo_amp schematic](https://i0.wp.com/www.richardmudhar.com/blog/wp-content/uploads/2018/12/RM_piezo_amp-1.png),
from ["Piezo contact microphone hi-Z amplifier – low noise version"](http://www.richardmudhar.com/blog/piezo-contact-microphone-hi-z-amplifier-low-noise-version/).

It is a single-supply (9 V) **non-inverting op-amp stage with a 1 MΩ input
resistance**, built around an NE5534.

| Part | Value | Role |
|---|---|---|
| R2, R3 | 56k / 56k | Divider that makes a mid-supply bias point (~4.5 V) |
| C2 | 10 µF | Decouples the bias point to AC ground, so the input sees exactly R1 at audio frequencies and supply ripple is filtered |
| R1 | 1 MΩ | Input resistance. It also carries the DC bias to the + input. **This is the key part** |
| Y1 | piezo | Hot side to the + input, brass side to ground |
| D1, D2 | 1N4148 | Clamp the input to the rails (here one BAV99 per channel). A knocked disc can produce 60 V or more |
| R5, R4 | 10k, 1k | Set the gain: 1 + R5/R4 = **11 (20.8 dB)** |
| C1 | 47 µF | In series with R4, so the **DC gain is 1** and the output sits at mid-supply. Corner ≈ 3.4 Hz |
| C3 | 47 µF | Supply decoupling |
| R6 | 470 Ω | Isolates the op-amp from cable capacitance |
| C4, R7 | 10 µF, 100k | Output DC block, plus a bleed resistor to stop plug-in thumps |

### Why high impedance matters

A piezo disc behaves like a voltage source in series with its capacitance
(Mudhar measured 15 nF and 28.5 nF discs). That capacitance and the load
resistance form a high-pass filter, fc = 1 / (2π·R·Cp):

| Piezo Cp | 1 MΩ load | 50 kΩ load (typical line input) |
|---|---|---|
| 28 nF | 5.7 Hz | 114 Hz |
| 15 nF | 10.6 Hz | 212 Hz |
| 5 nF | 32 Hz | 640 Hz |
| 1 nF (under-saddle) | 160 Hz ✗ | 3.2 kHz ✗ |

That's the "tinny piezo" effect: into a normal input, the bass is filtered away.

### Impedances of this design

| Point | Impedance | Notes |
|---|---|---|
| Input (J1/J2 tip) | **≈ 1 MΩ** (R11/R21), in series with 470 Ω + 1 µF | The op-amp input itself is far higher with feedback, so R11 sets it |
| Output (J3), volume full | ≈ 100 Ω | Set by R41 |
| Output (J3), volume mid | up to ≈ 2.5 kΩ | Worst case for a 10k pot. Drives any ≥ 10 kΩ input: mixers, audio interfaces, DI boxes, guitar amps |

**Best suited to:**
- 20–50 mm piezo discs (≈ 10–50 nF): contact mics, disc hydrophones, plate/spring reverb pickups, K&K-style disc transducers. Full bass (≤ 16 Hz corner) and the lowest noise.

**Usable:**
- small 10–15 mm discs (≈ 3–8 nF). The corner is 20–50 Hz, and noise is a few dB higher.

**Not suitable:**
- under-saddle guitar pickups, piezo film (PVDF) and other sources ≤ 2 nF. The corner is 80–300 Hz, so they sound thin. They want 10 MΩ, which needs a FET-input op-amp (Appendix A).

### Why the NE5532 works here, and its one catch

At audio frequencies the source impedance is the disc's *capacitive
reactance*. For 15 nF that is ~10 kΩ at 1 kHz, which is fairly low, so
**voltage noise** dominates. The NE5532 (5 nV/√Hz) is 8–10 dB quieter
A-weighted than a TL072 in this circuit (Appendix A).

The catch is **input bias current**: 200 nA typ, 800 nA max. It flows through
the 1 MΩ and shifts DC by **0.2–0.8 V**. The design handles this by
AC-coupling each preamp output (§3.1), and it is why R11 stays at 1 MΩ.

### NE5532 datasheet points (TI SLOS075K)

| Parameter | Value | Consequence here |
|---|---|---|
| Recommended supply | ±5 to ±15 V (10–30 V total); abs max ±18 V | 9 V is slightly below the recommended minimum. It works (Mudhar uses a PP3), but 18 V gives ~9 dB more headroom |
| Input bias current | 200 nA typ, 800 nA max | DC offset through 1 MΩ, handled by AC re-bias |
| Input CM range, output swing | ~2 V from each rail | ±2.3 V usable at 9 V |
| Noise | 5 nV/√Hz, 0.7 pA/√Hz @ 1 kHz | |
| Unity-gain stable | Yes | Unity-gain buffers and the ×1 minimum gain are OK (the 5534 needs ≥×3) |
| Supply current | 6 mA typ, 16 mA max per package | |

---

## 2. Block diagram

```
                 ┌────────────────┐
 PIEZO A ──J1──► │ Preamp A  U1A  │─┬C13──► NODE_A ───────────────┐
                 │                │ └R45/C45──► J8 direct A       │
                 │ gain ×1…×11    │         (biased via RV3)      │
                 │ (RV1 trim)     │                           ┌───┴───┐
                 └────────────────┘                           │ RV3   │ BLEND
                                                              │ 10k   │ (trim)
                 ┌────────────────┐        ┌──────────────┐   │ lin   │
 PIEZO B ──J2──► │ Preamp B  U1B  │──C23──►│ Polarity U2A │──►│       │
                 │ gain ×1…×11    │ NODE_B │ +1 / −1      │   └───┬───┘
                 │ (RV2 trim)     │        │ (SW2 DIP)    │       │ BLEND
                 └────────────────┘        └──────────────┘       ▼
                                                           ┌──────────────┐
                                                           │ Low-cut  72Hz│ SW2-2
                                                           │ High-cut     │ SW2-3/4
                                                           └──────┬───────┘
                                                                  ▼
                                                           ┌──────────────┐
                                                           │ Buffer U2B   │
                                                           └──────┬───────┘
                                                                  ▼
                                                  R41 100R ─ C41 ─ RV5 A10k
                                                                  │ (9 mm master)
                                                                  ▼
                                                               OUT J3
```

| Package | Half A (pins 1–3) | Half B (pins 5–7) |
|---|---|---|
| U1 | Preamp A | Preamp B |
| U2 | Polarity stage (ch B); also drives J9 direct B via R42/C42 | Filter buffer / output driver |

---

## 3. Stage-by-stage design

### 3.1 Preamp (×2, identical). Channel A shown; channel B uses R2x/C2x/D2x/RV2

```
                                   V+
                                   │
                                 D10 BAV99 (K to V+)
                                   │
 J5 pin 1 ──C10 1µ X7R──R10 470R────┼─────────────────► U1A +IN (3)
 (switched jack:                   │          │
  tip→GND when                   D10 (A to GND) R11 1M
  unplugged)                     (K to node)  │
                                   │        VREF_IN
                                  GND

 U1A −IN (2) ──┬──────────── C12 100p ─────────────┬──► U1A OUT (1)
               │                                   │
               ├──────────────── RV1 wiper (2)     RV1 pin 1
               │                   RV1 10k lin divider
               └── R13 1.5k ──┬─── RV1 pin 3 (CW end)
                              │
                              └── R12 1k ── C11 22µ 25V X5R 1206 ── GND

 U1A OUT (1) ── C13 10µ 25V X5R 1206 ──┬──► NODE_A
                                                │
                                               VREF
```

- **Gain trim (divider):** RV1 is wired as a divider, not a rheostat: pin 1 to the
  output, wiper to −IN, pin 3 to the R12/C11 gain leg. R13 (1.5k) runs from the wiper
  to pin 3. With x = rotation from pin 1, R_top = 10k·x and R_bot = 10k·(1−x):
  Gain = 1 + R_top / ((R_bot ∥ R13) + R12) = **×1 to ×11 (0 to +20.8 dB)**.

  | Rotation | 0 | 10% | 25% | 50% | 75% | 90% | 100% |
  |---|---|---|---|---|---|---|---|
  | Gain (dB) | 0 | 3.2 | 6.5 | 10.4 | 13.8 | 16.4 | 20.8 |

  A plain divider would crowd the top end (the last 10% covers 6 dB), and the old
  rheostat crowded the bottom (the first 10% covered 6 dB). R13 pulls the divider's
  mid-range up, giving roughly 2 dB per tenth of a turn. History: rev 1.0 was a
  rheostat with R13 = 1k (×2 to ×12); on the first build the trims did too little.
- **Dirty or open wiper:** −IN still sees pin 3 through R13, so the loop stays
  closed and the stage falls to maximum gain (×11) rather than open-loop.
- On 9 V, ×11 is about as much gain as the headroom allows with typical discs (§6).
  For more gain, drop R12/R22 to 560 Ω (×1 to ×18.9). **Clockwise = more gain**
  assumes the RM-065 wiper moves toward pin 3 when turned CW; check on the part.
- **C12 100 pF:** RF-breakthrough suppression, which one of Mudhar's builders
  needed. It rolls off at 145 kHz at max gain.
- **C10 1 µF X7R input block (1206, 50 V):** keeps the bias voltage off the jack tip, so the
  switched jack can short an unused input to ground. An open 1 MΩ input is
  ~30 dB noisier (Mudhar). It also makes plugging in pop-free. Its effect with a
  15 nF disc is −0.13 dB.
- **R10 470 Ω:** limits the clamp-diode current when a knocked disc throws
  60 V+ (≈130 mA for a few µs, well within the BAV99's surge rating). It costs
  ~0.8 dB of A-weighted noise; 1 kΩ would cost 1.6 dB.
- **C13, the AC re-bias:** the preamp output sits 0.2–0.8 V below VREF. NODE_A
  gets its DC from B_OUT through RV3's track (5k), so no separate re-bias resistor
  is needed (R14 was removed; simulation: response within 0.1 dB, DC within 2 mV).
  If RV3 is ever left out and its pads linked, refit a 100k from NODE_A to VREF.
  Without this coupling, flipping the polarity DIP would step the output by up
  to 1.6 V (a thump), and DC through the blend trimmer would make it scratchy.
  C13 is a ceramic, so it has no polarity. It has almost no DC across it,
  so it keeps nearly its full value.
- **C11/C21 are 22 µF 25 V X5R ceramics (1206).** With ~4 V across them they
  derate to ~12 µF on 9 V (~7 µF on 18 V). That moves the gain-leg corner
  from 3.4 Hz to ~13 Hz (~24 Hz on 18 V): about −1.6 dB at 20 Hz at full gain
  on 9 V, and about −4 dB on 18 V. For full bass on 18 V, use a 1210 47 µF or
  two 22 µF in parallel.

### 3.2 Polarity invert, channel B (U2A)

```
 NODE_B ──┬── R25 10k ──┬───────────► U2A −IN (2)
          │             └── R26 10k ──┬── U2A OUT (1) ──► B_OUT
          │                           │
          └── R27 10k ──┬──────────────► U2A +IN (3)
                        │
                     SW2-1 (DIP)
                        │
                      VREF
```

With R25 = R26, Vout = 2·V₊ − Vin:

- **DIP OFF (normal):** V₊ = Vin, so Vout = **+Vin**. This is exactly unity,
  independent of resistor matching.
- **DIP ON (Ø):** V₊ = VREF, so Vout = **−Vin**. Use 1 % resistors so both
  modes match in level.

NODE_B is re-biased to VREF, so both modes sit at the same DC level and
switching is quiet (a few mV of residual step). NODE_B's load is 100k in OFF
mode and 5k in ON mode; the C23 corner is ≤ 3.2 Hz. The switch is position 1 of the 4-way DIP SW2
(positions 2 and 3 are the filters, §3.4).

**Using it:** with both discs on the same instrument or surface, set the blend
near centre and toggle SW2-1. Keep whichever setting sounds fuller; the other one
is the partial cancellation.

### 3.3 Blend (RV3)

```
 NODE_A ──── RV3 5k lin ──── B_OUT
                  │
                wiper = BLEND ──► filters
```

The ends give 100 % A or 100 % B. The centre gives (A + B)/2, so two equal
in-phase signals keep the same level as either alone. The wiper's source
impedance is ≤ 1.25 kΩ. Keeping RV3 at 5k keeps that source impedance small next to the
filter resistors (§3.4).

### 3.4 Low-cut and high-cut (SW2-2…4) and buffer (U2B)

```
          ┌──── SW2-2 (ON = bypass) ──┐
 BLEND ───┴── C43 100n C0G ──────────┴──┬── R40 10k ──┬──► U2B +IN (5)   U2B −IN (6) ── OUT (7)
                                        │             │
                                     R43 22k     C40 1.5n C0G ─┬─ C44 2.2n C0G
                                        │             │            │
                                      VREF       SW2-3 ── VREF  SW2-4 ── VREF
```

| Switch | Off | On |
|---|---|---|
| SW2-2 low-cut (HPF), **inverted sense** | **72 Hz**, 6 dB/oct (C43 with R43); sim 76 Hz blend at an end, 71 Hz centred | C43 shorted: flat |
| SW2-3 high-cut (LPF) | flat (R40 into U2B's input only) | **10.6 kHz** at the blend ends, 9.4 kHz at blend centre, 6 dB/oct |
| SW2-4 high-cut (LPF) | flat | **7.2 kHz** (C44 2.2n); with SW2-3 too, **4.3 kHz** (3.7 nF) |

- **Why these corners.** 75–80 Hz is the usual mixer/desk low-cut. It removes
  handling thumps, table and stand rumble and the low "boom" of a disc on a
  resonant surface, without thinning a contact mic much. Sensible range
  **60–120 Hz** (R43 33k ≈ 51 Hz, 15k ≈ 110 Hz). 10 kHz takes the fizz and
  pick-click off the top without dulling. The two caps give three roughly
  half-octave steps: 10.6 kHz (gentle), 7.2 kHz (tames scrape and fizz), 4.3 kHz
  (dark, lo-fi). For a brighter set, C40 1n / C44 1.5n gives 16 / 10.6 / 6.4 kHz.
- **Low-cut first.** R43's 22k shunt would load R40 if the order were swapped
  (−4.5 dB). Driven from the blend wiper (≤ 1.25 kΩ), it costs at most 0.5 dB
  at blend centre and nothing at the ends. It also bends the blend law slightly.
- **Both switched legs return to VREF.** With a switch open, its floating side
  is within the bias offset of VREF (~0.1 V typ), so closing it gives only a
  small tick. SW2-2…4 can be flipped with the power on. SW2-2 shorts C43, which has
  only the blend node's few-mV offset across it.
- **Why SW2-2 bypasses C43 instead of switching R43:** R43 to VREF then also biases
  U2B, so the old 470k bias resistor (R44) is gone, the filter-node DC offset drops
  15× (96 → 6 mV typ, 384 → 26 mV worst) and the low-cut click drops from 80 to
  30 mV typ (sim, `sim/t6.py`). Cost: R43 always loads the blend wiper, so blend
  centre is 0.45 dB quieter with the low-cut off, and the switch sense is inverted.
- **C40, C43 and C44 must be C0G:** signal sits across both. C43 (100 nF C0G) is a
  1206 part and not a JLC basic part, so check stock.
- **R40 10k** keeps the blend's source impedance (0–1.25 kΩ) to an ~11% corner
  shift. Its noise (~1.8 µV over 20 kHz) only shows at minimum gain: about
  +3 dB there, under 0.5 dB from ×6 up. 4.7k with 3.3n halves that but lets the
  corner wander 8–10 kHz with the blend.
- **DC:** U2B's input is biased through R40 and R43 (32 kΩ total). NE5532
  bias current gives 6 mV typical, 26 mV worst-case offset. C41 blocks it.
- **Noise gate:** Q50 clamps the LPF node (U2B input) to VREF. R40 is now the
  source resistance it works against, giving about −60 dB of mute.
- **Rumble below 72 Hz with the low-cut off** is set by the piezo/1 MΩ corner
  (~10 Hz) and the gain-leg ceramics.

### 3.5 Output and master volume (RV5)

```
 U2B OUT (7) ── R41 100R ── C41 10µ 25V X5R ──┬── RV5 A10k top (lug 3)
                                                  RV5 bottom (lug 1) → GND
                                                  RV5 wiper (lug 2)  → J3 tip
```

- **R41 100 Ω** isolates cable capacitance and protects against output shorts.
- **C41 is ahead of the pot**, so the track carries no DC and turning it is
  quiet. The track also bleeds C41. The corner is 1.6 Hz.
- **RV5** is a 10 kΩ log (A) 9 mm PCB pot. Its worst-case output impedance is
  ~2.5 kΩ, which drives ≥10 kΩ inputs and several metres of cable.
- The maximum overall gain is ×11 (+20.8 dB); everything after the preamps is
  unity or attenuation.

### 3.6 Direct outs (J8, J9)

```
 A_OUT (U1-1) ── R45 100R ── C45 10µ ──┬──► J8 pin 1   (J8 pin 2 = GND)
                                       └── R46 100k ── GND
 B_OUT (U2-1) ── R42 100R ── C42 10µ ──┬──► J9 pin 1   (J9 pin 2 = GND)
                                       └── R47 100k ── GND
```

- Optional 2-pin headers for separate A/B outputs, taken before the blend,
  filters, gate and volume. Wire them to off-board jacks or leave them empty.
- Both are unity after the preamps, so each level is set by its gain trimmer.
  B comes after the polarity stage, so SW2-1 applies to J9 too.
- **R42/R45 (100 Ω)** keep a shorted or capacitive lead off the op-amp output.
  **C42/C45** block the 4.25 V DC. **R46/R47 (100 kΩ)** hold the jack side at
  0 V so plugging in doesn't thump (the old stereo mode had no bleed).
- J3's ring is now unconnected. Mono works on a TS or a TRS lead.
- This replaced the SW2-2…4 stereo mode (A → U2B → tip, B → ring, volume
  bypassed). That used three DIP positions, put A's DC offset into U2B, and
  needed the R40 isolation and the J7 gate link in stereo.

---

## 4. Power supply and reference

```
 J4 pin 1 (V in) ── switch / jumper cap ── J4 pin 2 ── D1 1N5819W ── R30 10Ω ──┬── V+
 J4 pin 3 (GND)                                           ├── C30 22µ 25V X5R
 (DC jack, battery and switch                             ├── C31 100n @ U1 pin 8
  wired off-board)                                        └── C32 100n @ U2 pin 8

 V+ ── R31 10k ──┬── R32 10k ── GND          VREF ── R33 47k ──┬── VREF_IN
                 │                                             │
               VREF ── C33 100µ/25V ── GND                   C34 47µ/25V ── GND
```

- **D1 1N5819W** (SOD-123) is Schottky reverse-polarity protection with a
  ~0.3–0.4 V drop.
- **R30/C30** is supply filtering, with a ~0.13 V drop.
- **VREF** (≈ V+/2) serves as the signal reference for the polarity stage,
  re-bias resistors and DIP switch. Its time constant is 0.5 s.
- **VREF_IN** (R33/C34) is a separately filtered copy for the two 1 MΩ bias
  resistors only. It keeps signal current that flows into VREF (via R27 and
  the re-bias resistors) out of the high-Z inputs, which would otherwise cause
  low-frequency crosstalk or motor-boating. The added offset is
  ~20 mV. **Don't merge VREF_IN into VREF.**
- **Ceramic C30/C33/C34.** C33 (22 µF, derated to ~12 µF) leaves VREF a
  little noisier at low frequencies than 100 µF would. After the VREF_IN
  filter, the feedback into the inputs is still about −45 dB at 20 Hz. R30
  (10 Ω) damps the voltage spike a ceramic C30 can see when an adapter is
  hot-plugged.
- **Battery vs DC.** If you want the battery to drop out when a DC plug is
  inserted, wire that at the jack, off-board.
- **Power-on:** C41 charges through RV5, so expect a thump at switch-on. Turn
  on with the volume down, or before connecting the output.

---

## 5. DC operating points (9 V battery, typical)

Use these for bring-up.

| Node | Expected |
|---|---|
| V+ | ~8.5 V |
| VREF | ~4.25 V |
| VREF_IN | ~4.23 V |
| U1 pins 1, 2, 3 and 5, 6, 7 | ~4.0 V typ (≥ ~3.4 V worst case) |
| NODE_A, NODE_B, U2 pin 1 | ≈ VREF (±10 mV) |
| U2 pins 5, 7 | VREF minus 0.1 V typ (up to 0.4 V), from bias current through R40 + R43 (6 mV typ, 26 mV worst) |
| J1, J2, J3 tips | 0 V |

At 18 V everything scales proportionally (VREF ≈ 8.75 V).

---

## 6. Headroom

Usable swing is roughly 1.8–2 V short of each rail. These are estimates, so
measure on the prototype.

| Supply | Clean peak (back end) | ≈ Vrms out |
|---|---|---|
| 9 V (fresh PP3) | ±2.3 V | ~1.6 V (+6 dBu) |
| 9 V (sagging, 7.5 V) | ±1.5 V | ~1 V |
| 12 V adapter | ±4 V | ~2.8 V |
| 18 V adapter | ±7 V | ~5 V (+16 dBu) |

The preamp outputs start 0.2–0.8 V low, so on 9 V their worst-case swing is
~±1.5 V. At ×11 that means the preamp clips at about 95 mV rms input
(≈150 mV typical); at ×1, about 1 V rms.

**Gain staging:** strike the discs at their hardest and set RV1/RV2 just below
clipping. Then balance with RV3 and set the level with RV5.

---

## 7. Current draw

| Item | Typ |
|---|---|
| 2 × NE5532 | 12 mA (32 mA max) |
| VREF divider | 0.4 mA |
| **Total** | **~12.5 mA**, so a PP3 lasts ~40 h |

---

## 8. Noise (input-referred, 20 Hz–20 kHz)

Model: NE5532 en = 5 nV/√Hz (8 @ 30 Hz), in = 0.7 pA/√Hz (2.7 @ 30 Hz), plus
thermal noise from R10 (470 Ω) and R11.

| Disc | A-weighted | Unweighted |
|---|---|---|
| 15 nF | **−119 dBu** | −103 dBu |
| 28 nF | −121 dBu | −108 dBu |
| 5 nF | −113 dBu | −96 dBu |

The unweighted figure is dominated by the NE5532's current noise flowing into
the disc's reactance at low frequencies. That is sub-100 Hz rumble, which
A-weighting removes.

In practice **hum dominates**, because 15 nF is ~200 kΩ at 50 Hz. Use:
- a grounded metal enclosure
- screened input cables (up to ~50 cm is fine)
- the **brass side of each disc to the sleeve**

---

## 9. Schematic capture reference

### IC pin map

| Pin | U1 (preamps) | U2 (polarity / output) |
|---|---|---|
| 1 | A_OUT → RV1, C12, C13, R45 | B_OUT → R26, R42, RV3 lug 3 |
| 2 | −IN_A → RV1 wiper, R13, C12 | → R25, R26 |
| 3 | +IN_A → R10, R11, D10 pin 3 | POL_P → R27, SW2 pin 1 |
| 4 | GND | GND |
| 5 | +IN_B → R20, R21, D20 pin 3 | LPF → R40, C40, C44, Q50 |
| 6 | −IN_B → R22, R23, C22 | → pin 7 |
| 7 | OUT_B → RV2 end, C22, C23(−) | OUT → pin 6, R41 |
| 8 | V+ → C31 | V+ → C32 |

### Named nets

| Net | Connects |
|---|---|
| V+ | R30, C30, C31, C32, R31, D10(K), D20(K), U1-8, U2-8 |
| VREF | R31/R32 junction, C33, R33, R24, R43, Q4, SW2 pins 5, 6, 8 |
| VREF_IN | R33, C34, R11, R21 |
| A_OUT | U1-1, RV1, C12, C13, R45 |
| NODE_A | C13, RV3 lug 1 (DC via the RV3 track) |
| NODE_B | C23, R24, R25, R27 |
| B_OUT | U2-1, R26, R42, RV3 lug 3 |
| LPF | R40, C40, C44, U2-5, Q50 |
| HPF | C43, R43, R40, SW2 pin 7 |
| BLEND | RV3 wiper, C43, C50, SW2 pin 2 |
| LPF_SW | C40, SW2 pin 3 |
| LPF2_SW | C44, SW2 pin 4 |
| B_AC | C42, R47, J9 pin 1 |
| BLEND | RV3 wiper, C43, C50 |
| (out) | RV5 wiper, J3 tip. J3 ring unconnected |
| GND | Star point at C30. Returns: C11, C21, C33, C34, R32, D10/D20 pin 1, RV5 lug 1, J3 sleeve, J4 pin 3, J5/J6/J7/J8/J9 pin 2, R46, R47, enclosure |

Trimmer rheostats (RV6): tie the wiper to one end so a dirty wiper
fails as maximum resistance, not open circuit.

### Layout rules

- Keep the high-Z nodes (U1 pins 3/5, R10/R11, R20/R21, D10/D20, C10/C20)
  short and on the jack side. Surround them with ground pour and keep them
  away from the output, U2 and the supply traces.
- Put the trimmers along one edge, reachable with the lid off (or through
  holes). Label them with arrows showing the CW direction.
- Use a single star ground at C30, and wire every jack sleeve back to it.
  Metal jacks will also bond their sleeves to the enclosure, which is normal
  for a pedal-style box. Just don't add further board-to-case ground
  connections.
- Place C31/C32 directly at pin 8 of each IC.

---

## 10. Bill of materials

| Ref | Value | Package / notes | Qty |
|---|---|---|---|
| U1, U2 | NE5532DR | SOIC-8 | 2 |
| R10, R20 | 470 Ω | 0603, input series | 2 |
| R11, R21 | 1 MΩ | 0603, input bias. Have the boards washed: flux on high-Z nodes adds noise | 2 |
| R12, R22 | 1 kΩ | 0603, gain leg | 2 |
| R13, R23 | 1.5 kΩ | 0603, gain-trim law resistor (wiper to RV pin 3) | 2 |
| R24 | 100 kΩ | 0603, NODE_B re-bias | 1 |
| R25, R26, R27 | 10 kΩ **1 %** | 0603, polarity stage | 3 |
| R30 | 10 Ω | 0603, supply filter | 1 |
| R31, R32 | 10 kΩ | 0603, VREF divider | 2 |
| R33 | 47 kΩ | 0603, VREF_IN filter | 1 |
| R40 | 10 kΩ | 0603, high-cut | 1 |
| R43 | 22 kΩ | 0603, low-cut shunt + U2B bias | 1 |
| R41, R42, R45 | 100 Ω | 0603, output isolation (J3, J9, J8) | 3 |
| R46, R47 | 100 kΩ | 0603, direct-out bleed | 2 |
| C10, C20 | 1 µF 50 V X7R | 1206, input DC block | 2 |
| C11, C21 | 22 µF 25 V X5R | 1206, gain leg (see §3.1 on derating) | 2 |
| C12, C22 | 100 pF C0G | 0603, feedback RF | 2 |
| C13, C23 | 10 µF 25 V X5R | 1206, preamp output coupling | 2 |
| C30 | 22 µF 25 V X5R | 1206, supply bulk | 1 |
| C31, C32 | 100 nF | 0603, at each pin 8 | 2 |
| C33 | 22 µF 25 V X5R | 1206, VREF | 1 |
| C34 | 10 µF 25 V X5R | 1206, VREF_IN | 1 |
| C40 | 1.5 nF 50 V **C0G** | 0603, high-cut 10.6 kHz (SW2-3) | 1 |
| C44 | 2.2 nF 50 V **C0G** | 0603, high-cut 7.2 kHz (SW2-4) | 1 |
| C43 | 100 nF 50 V **C0G** | 1206, low-cut series cap (not a JLC basic part, check stock) | 1 |
| C41, C42, C45 | 10 µF 25 V X5R | output DC blocks | 3 |
| D10, D20 | BAV99 | SOT-23, input clamps (pin 3 to input, 1 GND, 2 V+) | 2 |
| D1 | 1N5819W | SOD-123, reverse polarity | 1 |
| RV1, RV2 | 10 kΩ lin | Runtron RM-065 trimmer, gain | 2 |
| RV3 | 5 kΩ lin | Runtron RM-065 trimmer, blend | 1 |
| RV5 | 10 kΩ log (A) | Right-angle 9 mm pot with M7 bushing, Alps RK09K footprint (Alpha RV09 right-angle equivalents; check pin layout). Or a 1×3 header in the same holes | 1 |
| SW2 | 4-position DIP (SPST ×4) | Through-hole slide DIP. Pos 1 polarity, 2 low-cut (OFF = cut), 3 and 4 high-cut | 1 |
| J8, J9 | 1×2 header | Direct out A/B (signal, GND), optional | 2 |
| J4 | 1×3 header | 1 +V in, 2 +V to board, 3 GND. Off-board switch (or a jumper cap) across 1–2 | 1 |
| J5, J6 | 1×2 header | Piezo A/B (signal, GND). For silent unplugged inputs, wire the jack's switch lug to its sleeve | 2 |
| J3 | Neutrik NMJ6HCD2 TRS jack | Through-hole, right edge. Ring unconnected. Secures the board to the panel | 1 |

Notes:
- (Superseded: RV1–RV3 now use the standard Runtron RM-065 footprint with 1.0 mm holes.) The earlier 4ms T73YE footprint came from the 4ms third-party library. Copy it into
  a project library so the project opens on other machines. Check the real
  part's pinout (wiper on pad 2) and pin diameter against the 0.51 mm holes.

## 11. Build and verification

1. **Capture** in `piezamp.kicad_sch` with sections: Power/VREF, Preamp A,
   Preamp B, Polarity, Blend/High-cut/Output. Run ERC.
2. **Simulate** (ngspice with the TI NE5532 model). Check:
   - gain ×1–×11 on each channel
   - polarity ±1, with the level matched within 0.1 dB
   - low-cut 72 Hz (SW2-2 OFF) and high-cut 10.6 / 7.2 / 4.3 kHz (SW2-3, SW2-4, both), flat with all off
   - the DC points in §5, at both 9 V and 18 V
3. **Layout** per §9, then DRC.
4. **Bring-up:**
   1. Check the DC points (§5) with no inputs plugged in.
   2. Inject 1 kHz through a 15 nF series cap (a fake disc) into each input and
      verify the gain range.
   3. Scope B_OUT against NODE_B with SW2-1 off and on: it should be in
      phase, then inverted, at the same amplitude. Flipping SW2-1 should make
      no audible click.
   4. Sweep 20 Hz–20 kHz flat (SW2-2 ON, 3/4 OFF), then low-cut, 3, 4 and 3+4; compare with
      §3.4. Flipping them live should give at most a small tick.
   5. With the inputs unplugged, the output should be silent. Then check it on
      both 9 V and 18 V.
   6. Check J8/J9 carry A and B at unity after the preamps, unaffected by
      RV3/RV5 and SW2-2/3, and sit at 0 V DC.
5. **In use:** mount two discs, centre the blend, choose the SW2-1 setting that
   sounds fuller, then set the gains, blend and filter switches to taste.

---

## 12. PCB

> **Out of date (2026-10-08):** the schematic has since changed (discrete Q1–Q4 gate, divider gain trims, R14/R44/D11/D21/SW1 removed, D10/D20 now BAV99, J4 now 1×3, SW2-2 across C43). Update the PCB from the schematic and re-route.

`piezamp.kicad_pcb`: placed and **routed** (2026-10-07). DRC clean with schematic parity; the
only warnings are the jack/pot silkscreen hanging past the right edge.

- **Size:** 64 × 41.3 mm, 2 layers, every component on top. GND pour on both layers
  (0.3 mm clearance, thermal reliefs 0.3 gap / 0.4 spoke); B.Cu is the main ground.
- **Rules / net classes** (in `piezamp.kicad_pro`): Default 0.25 mm track, 0.2 mm clearance,
  0.6/0.3 mm via. Power (VCC, GND, the D1/J4 supply-entry nets) 0.5 mm, 0.8/0.4 mm via.
  Min track 0.15 mm: the autorouter necks to 0.187 mm into SOIC/SOT-363 pads. Copper-to-edge 0.3 mm.
- **Top edge:** trimmers RV1 gain A, RV2 gain B, RV3 blend (8.89 mm pitch, label band under them).
  The old RV4 slot holds the direct-out headers **J8 (A) / J9 (B)**, with C45/C42 under them and
  R42/R46/R47 in a column beside RV5. B_OUT comes straight off RV3 pin 3 into R42.
- **Right edge (panel side):** TRS jack J3 (bottom), 9 mm master pot RV5 (top), as before.
- **Left edge:** J5 piezo A, J6 piezo B, J4 power, SW1 power switch, as before.
- **Filters:** C43 (1206) and R40 sit right of U2, next to pin 5. The switched legs R43, R44, C40,
  C44 sit in a row above SW2, so the HPF_SW/LPF_SW/LPF2_SW runs to the DIP are short.
- **R45** (direct-out A isolation) sits under the RV1/RV2 gap, beside A_OUT.
- **Noise gate:** spread along the bottom: RV6, the C50/R50/R51/C51 column, Q51, D50, then C52, R52,
  Q50 under SW2.
- **Routing:** Freerouting 2.4.1 (via cost 1000) with GND removed from the DSN, then hand fixes
  (BLEND→C50, J4→SW1, Q50/Q51 under-body 0.2 mm links) and GND pours. 33 vias in total, 6 of them
  GND stitching that tie pour islands and boxed-in GND pads to the B.Cu plane. A few B.Cu signal
  runs slot the bottom plane; worth tidying by hand if hum shows up.
- **Silkscreen:** designators are on the fab layer only. Front labels: header functions, GAIN A,
  GAIN B, BLEND, VOLUME, GATE THRESH, GATE OFF, A/B under J8/J9, DIP numbers. The back legend has
  the power range, J8/J9 outputs and SW2 functions.
- **Routing notes:** keep the input nodes (J5/J6 → C10/C20 → R10/R20 → D/R11 clusters → U1 pins 3/5)
  short and away from output and supply traces when editing by hand.

---

## Appendix A: Op-amp choice (decision record)

Input noise is modelled for a 15 nF disc. Headroom is the clean peak swing on
9 V.

| Op-amp | A-wtd noise | Unwtd | 9 V headroom | I/pkg | Verdict |
|---|---|---|---|---|---|
| **NE5532** | **−119 dBu** | −103 dBu | ±2.25 V | 6 mA | **Chosen**: quietest common through-hole part in this circuit |
| TL072 (legacy die) | −111 dBu | −109 dBu | ~±1.3 V | 2.8 mA | Noisier. Input range stops ~3–4 V above V−, where the output phase-reverses |
| TL072H (TI current) | −109 dBu | −106 dBu | ±2.75 V | 2 mA | 37 nV/√Hz; only a marginal headroom gain |
| OPA2134 | −118 dBu | −116 dBu | ±2.25 V | 8 mA | Equal noise, costs more |
| OPA1642 | −120.5 dBu | −118 dBu | ±2.4 V as drawn | 3.6 mA | Best overall, but SMD only and needs a lower VREF |

A FET-input op-amp only earns its place if you need a **10 MΩ input** for
low-capacitance sources such as under-saddle pickups.

## Appendix B: Future options (not in this build)

1. **Low-cut (rumble) filter as well as the high-cut:** needs a third op-amp half, so add U3. Put a trimmable RC high-pass (100 nF, 15k + 100k trim to VREF, ≈14–106 Hz) in front of a U3A buffer.
2. **12 dB/oct high-cut:** make U2B a unity-gain Sallen-Key low-pass tuned with a dual-gang pot. A single trimmer can't tune a 2nd-order section without upsetting its Q.
3. **Balanced output:** U3B as a unity inverter after RV5, driving XLR pin 3.
4. **Low-capacitance piezos:** bootstrap R11 (2 × 470k, with the midpoint
   AC-coupled to −IN) to get a very high effective input impedance. Simulate
   it for an LF peak. A FET-input front end is the more conventional route.
5. **R11 = 2.2 MΩ** halves the LF corner. It is only sensible on 12–18 V
   because of the extra bias-current offset.

---

### Sources
- [Richard Mudhar – Piezo contact microphone hi-Z amplifier, low noise version](http://www.richardmudhar.com/blog/piezo-contact-microphone-hi-z-amplifier-low-noise-version/)
- [Richard Mudhar – Piezo contact mic amplifier measurements](https://www.richardmudhar.com/blog/piezo-contact-mic-amplifier-measurements/)
- [Richard Mudhar – Using piezo contact mics right](https://www.richardmudhar.com/blog/using-piezo-contact-mics-right/)
- [TI NE5532 datasheet (SLOS075K)](https://www.ti.com/lit/ds/symlink/ne5532.pdf)
- [TI TL072 datasheet (SLOS080W)](https://www.ti.com/lit/ds/symlink/tl072.pdf)
- [TI OPA1642 datasheet](https://www.ti.com/lit/ds/symlink/opa1642.pdf), [TI OPA2134 datasheet](https://www.ti.com/lit/ds/symlink/opa2134.pdf)
