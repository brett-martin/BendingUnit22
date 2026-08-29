# BU-22 Display Controller Rev D — release audit

> **Assembly erratum:** The `+` silkscreen marks for D1 and D2 are on the
> wrong side. The left square pad 1 is cathode/GND; the right round pad 2 is
> anode/positive. See [ERRATA.md](ERRATA.md) before assembly.

Audit date: 2026-08-18

## Result

**PASS for bare-PCB fabrication.**

- KiCad 10 native DRC: 0 violations
- KiCad connectivity: 0 unconnected items/pads
- Independent 0.20 mm copper geometry audit: 0 front-layer conflicts,
  0 back-layer conflicts
- Footprint errors: 0
- Board outline: closed, 125.0 × 55.0 mm
- Four 3.20 mm non-plated mounting holes present
- Four copper layers present and exported
- All three copper zones refilled before export

## Electrical checks

- J1–J6 use the requested input order: pin 1 GND, pin 2 CLOCK,
  pin 3 DATA, pin 4 SYSTEM_5V.
- U1–U3 are 74AHCT125 SOIC-14 footprints; pin 14 is LOGIC_5V and pin 7
  is GND.
- D3 isolation polarity is SYSTEM_5V (anode/pad 2) to LOGIC_5V
  (cathode/pad 1).
- D1 and D2 use the KiCad T-1 convention: pad 1 cathode/GND, pad 2 anode.
- Q1 footprint/net order is emitter/GND, base/ENABLE_BASE,
  collector/OE_N for the selected inline 2N3904.
- I2C headers intentionally omit 3.3 V on pin 2. GND, SDA and SCL remain.
- Internal layer 1 is GND. Internal layer 2 is protected LOGIC_5V.
- External SYSTEM_5V remains on routed outer-layer copper.

## BOM/footprint checks

- 74AHCT125S14-13: SOIC-14 footprint matches the ordered package.
- 2N3904: inline TO-92 footprint matches the ordered through-hole package
  and its E-B-C lead order.
- R1–R20: 0805 footprints match the ordered resistor series.
- C1–C3: 0805 footprints match the ordered 100 nF capacitors.
- C4/C5: polarized radial through-hole footprints; polarity is marked.
- J1–J6: JST-XH B4B vertical through-hole footprints.
- J8/J9: JST-SH/Qwiic 4-position SMD footprints.
- J10/J11: JST-PH vertical through-hole footprints.
- JP1: 2×2, 2.54 mm through-hole header.
- MCU sockets: two 1×13, 2.54 mm through-hole rows for the KB2040.

## Manufacturing package

The JLCPCB ZIP contains 12 files: four copper Gerbers, two solder masks,
two silkscreens, board outline, plated drill, non-plated drill, and Gerber
job file. This release is intentionally for bare-PCB/manual assembly.

Package SHA-256:

`c70fd736b77c3282ce98b01e3636109fb81fb3cbc430332e36badc5e3fcaaf1a`

## Important order setting

Select **4 layers**. A two-layer order is not electrically equivalent because
the internal GND and LOGIC_5V planes are part of Rev D.
