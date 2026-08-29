# BU-22 Display Controller Rev B — fabrication package

Upload `BU-22-Display-Controller-Rev-B-JLCPCB-Gerbers.zip` directly to the
JLCPCB PCB quote page. This package is for bare PCBs intended for manual
assembly; it intentionally contains no paste, BOM, or component-placement
files.

## Verified board properties

- Board size: 125.0 × 55.0 mm
- Layers: 4
- Thickness: 1.6 mm
- L1: front signal/component copper
- L2: ground plane
- L3: +5 V plane
- L4: back signal copper
- Minimum routed track width: 0.20 mm
- Minimum routed clearance: 0.2016 mm
- Minimum via drill: 0.30 mm
- Mounting holes: four 3.20 mm non-plated holes
- DRC: 0 violations and 0 unconnected pads

## Suggested JLCPCB selections

- Product: Standard PCB/PCBA
- Base material: FR-4
- Layers: 4
- PCB quantity: 5
- Different design: 1
- Delivery format: Single PCB
- PCB thickness: 1.6 mm
- Outer copper weight: 1 oz
- Inner copper weight: JLCPCB standard/default
- Solder mask: Black
- Silkscreen: White
- Surface finish: Lead-free HASL is adequate for this hand-soldered prototype
- Via covering: Tented
- Gold fingers: No
- Castellated holes: No
- Edge plating: No
- Impedance control: No
- Confirm production file: optional; recommended for the first revision
- Remove order number: optional cosmetic choice
- PCB assembly: Off

Do not select a two-layer board. The internal ground and +5 V planes are part
of the electrical design.

## ZIP contents

- Four copper Gerbers: `.gtl`, `.g1`, `.g2`, `.gbl`
- Front/back solder mask: `.gts`, `.gbs`
- Front/back silkscreen: `.gto`, `.gbo`
- Board profile: `.gm1`
- Plated and non-plated Excellon drill files

SHA-256 for the current approved Rev B package:

`03f0b7d8b6b48819e937978178b9f7fb4ce590767c627bf05799592c96089baa`

Regenerating the package changes the checksum and requires another visual
Gerber review before ordering.
