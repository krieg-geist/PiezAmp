# PiezAmp

Piezos straight into pedals sound like deep fried ass, so I built this preamp. 
There's like 1000 of these circuits, but I wanted an all in one solution that you could just throw in
a noisebox and have it sound halfway decent, with some tweaks to really dial in a nice sound.

Based on Richard Mudhar's
[low-noise piezo preamp](http://www.richardmudhar.com/blog/piezo-contact-microphone-hi-z-amplifier-low-noise-version/),
doubled up and extended. 

## Features

- **1 MΩ inputs.** Piezo discs have waaaay too high impedance for line inputs.
  At 1 MΩ they keep their full thiccness (results may vary with piezo guitar pickups, 
  this is mainly designed for cheap discs).
- **Gain:** ×1 to ×11 (0 to +20.8 dB) per channel.
- **Low noise:** about −119 dBu with a 15 nF disc, inshallah.
- **Blend** between channel A and channel B.
- **Phase invert.** This might help when you have two piezos in the same box so 
  they don't phase cancel eachother out
- **Low-cut and high-cut filters** on DIP switches: ~72 Hz low-cut for rumble/boom, and a
  three-step high-cut (10.6 / 7.2 / 4.3 kHz) if it's still too harsh/tinny. All off = flat.
- **Master volume** with a 9 mm panel pot. It shoooould (?) mount in line with the output
  jack.
- **Mono output** on a TRS jack (TS or TRS lead both fine), plus optional **direct A/B
  outs** on headers J8/J9, taken before the blend. I mainly did these to use with digital
  drum triggers, so for a basic noisebox setup you can ignore them.
- **Power:** 9–18 V DC, should work with a 9v battery, or with pretty much any barreljack
  adapter you have lying around.

## How it works

- Read [Richard Mudhar's blog](http://www.richardmudhar.com/blog/piezo-contact-microphone-hi-z-amplifier-low-noise-version/) lol

## Connections

| Ref | Header / part | Pin 1 | Pin 2 | Pin 3 |
|---|---|---|---|---|
| J5 | Piezo A in | signal | GND | |
| J6 | Piezo B in | signal | GND | |
| J4 | Power in + switch | +9–18 V in | +V to board (switch across 1–2) | GND |
| RV5 | Master volume (9 mm right-angle pot) | GND | wiper (out) | top |
| J3 | Output, 6.35 mm TRS | tip = out | ring = not connected | sleeve = GND |
| J8 | Direct out A (optional) | signal | GND | |
| J9 | Direct out B (optional) | signal | GND | |

The inputs are 2-pin headers. You can put jacks on em or just wire the piezos directly
to the inputs. Polarity shouldn't matter.

If you don't want an on/off switch, put a jumper cap across J4 pins 1–2.

## Controls

| Control | Function |
|---|---|
| Gain A / gain B | ×1 - ×11 gain, CW = more gain |
| Blend | A <-> B |
| Master volume | CW = louder |

**DIP switch SW2** (fine to flip with the power on):

| Pos | Function |
|---|---|
| 1 | Channel B polarity invert |
| 2 | Low-cut (high-pass) ~72 Hz when **OFF**; ON = flat |
| 3 | High-cut (low-pass), 10.6 kHz |
| 4 | High-cut (low-pass), 7.2 kHz |

3 and 4 together give 4.3 kHz, so the high-cut has four settings: off, 10.6, 7.2, 4.3 kHz.

Signal path: blend -> low-cut -> high-cut -> gate -> volume -> tip.

**Direct outs (J8/J9):** A and B straight off the preamps, after the gain trims
(and B's polarity switch) but before blend, filters, gate and volume. Wire them to
jacks if you want separate channels.

**Setting up:** Make a loud noise, and raise each
gain until the output is just below clipping. Try flip DIP 1: whichever setting sounds nicer is
right. Then set the blend, the filters and the master to taste.

## Customisation

- **Trimmers to panel pots.** Any trimmer (RV1–RV3) can be replaced by a panel
  pot wired to its three pads:
  - Pot lug 1 -> pad 1, wiper -> pad 2, lug 3 -> pad 3. The board already ties
    pads 2 and 3 where the circuit needs a variable resistor.
  - Use the same resistance value as the trimmer. The exception is RV3, where
    anything from 5k to 10k works.
- **Jumpering trimmers to fixed settings.** Leave the trimmer out and link or
  fit parts instead:
  - **Gain, fixed:** link pads 1–2 for minimum gain (×1). For any other fixed
    gain, fit a resistor R across pads 1–2: gain = 1 + R / 2.5 kΩ (10k ≈ ×5).
    Never link only pads 2–3: that leaves the stage with no DC feedback.
  - **Blend, fixed:** link pads 2–1 for A only, or pads 2–3 for B only. For an
    equal mix, fit two equal resistors (about 2.2k), one from pad 1 to pad 2
    and one from pad 3 to pad 2.
  - **Master volume:** RV5's holes also take a 1×3 pin header for an off-board
    pot. For fixed full volume, link pads 2–3.
- **Different filter corners:** low-cut fc = 1 / (2π · R43 · C43), so 22k/100n = 72 Hz
  (15k ≈ 110 Hz, 33k ≈ 50 Hz). High-cut fc = 1 / (2π · R40 · C40), so 10k/1.5n = 10.6 kHz.
  C44 sits in parallel with C40 (2.2n = 7.2 kHz, both = 4.3 kHz). For a brighter set use
  C40 1n / C44 1.5n (16 / 10.6 / 6.4 kHz). Keep C40, C43 and C44 C0G.
- **More headroom:** run it on 18 V. Shouldn't catch fire.
