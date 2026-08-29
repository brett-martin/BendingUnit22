# BU-22 Display Controller Rev D — fabrication package

Upload `BU-22-Display-Controller-Rev-D-JLCPCB-Gerbers.zip` directly to the
JLCPCB PCB quote page. This is a bare-PCB package for manual assembly; it does
not contain paste, BOM, or component-placement files.

## Verified board properties

- Board size: 125.0 × 55.0 mm
- Layers: 4
- Thickness: 1.6 mm
- L1: front signal/component copper
- L2: GND plane
- L3: protected LOGIC_5V plane
- L4: back signal copper with additional GND pour
- Minimum routed track width: 0.20 mm
- Minimum routed clearance: 0.2016 mm
- Minimum via drill: 0.30 mm
- Mounting holes: four 3.20 mm non-plated holes
- KiCad DRC: 0 violations and 0 unconnected pads
- Channel pin order: GND, CLOCK, DATA, +5 V (J1–J6 pins 1–4)

## Suggested JLCPCB selections

- Product: Standard PCB/PCBA
- Base material: FR-4
- Layers: **4**
- PCB quantity: 5
- Different design: 1
- Delivery format: Single PCB
- PCB thickness: 1.6 mm
- Outer copper weight: 1 oz
- Inner copper weight: JLCPCB standard/default
- Solder mask: Black
- Silkscreen: White
- Surface finish: Lead-free HASL
- Via covering: Tented
- Gold fingers: No
- Castellated holes: No
- Edge plating: No
- Impedance control: No
- Confirm production file: recommended for this first Rev D order
- PCB assembly: Off

Do not select a two-layer board. The two internal power planes are part of the
electrical design.

## ZIP contents

- Four copper Gerbers: `.gtl`, `.g1`, `.g2`, `.gbl`
- Front/back solder mask: `.gts`, `.gbs`
- Front/back silkscreen: `.gto`, `.gbo`
- Board profile: `.gm1`
- Separate plated and non-plated Excellon drill files

The SHA-256 recorded below applies only to the reviewed package generated on
2026-08-18. Regeneration requires another Gerber review.

`c70fd736b77c3282ce98b01e3636109fb81fb3cbc430332e36badc5e3fcaaf1a`
