# BU-22 Display Controller Rev D — assembly errata

## E1: D1 and D2 positive silkscreen marks are reversed

Discovered during first-board assembly and bring-up on 2026-08-29.

The PCB copper and footprint pad assignments are correct, but the nearby `+`
silkscreen marks were placed on the cathode side of both 3 mm LEDs.

Correct installation, viewed from the top/component side with the board
silkscreen readable:

| Component | Function | Left square pad 1 | Right round pad 2 |
|---|---|---|---|
| D1 | Green power LED | Cathode / GND / short lead / flat side | Anode / positive / long lead |
| D2 | Red heartbeat LED | Cathode / GND / short lead / flat side | Anode / positive / long lead |

Ignore the printed `+` marks on fabricated Rev D boards. Install both LEDs
with their positive/long leads in the right round pads.

### Required next-revision correction

- Move each `+` mark to the right/round/pad-2 side of its LED.
- Retain the existing electrical pad assignments and routing.
- Add explicit `A` and `K` polarity labels if space permits.
- Include LED silkscreen polarity in the fabrication-release audit.

## E2: JP1 address-selection copper is rotated relative to role labels

Confirmed during first-board bring-up on 2026-08-30.

The Rev D silkscreen places `EYES` to the left of JP1 and `MOUTH` to the right,
which indicates that one vertical shunt should select either role. The copper
instead assigns the 2x2 pads as:

| Physical position | Top | Bottom |
|---|---|---|
| Left column | pad 1 `ADDRESS` | pad 3 `ADDRESS` |
| Right column | pad 2 `ADDR_A0` | pad 4 `ADDR_A1` |

Consequences on fabricated Rev D boards:

- A vertical left shunt only joins `ADDRESS` to `ADDRESS` and has no effect.
- A vertical right shunt joins `ADDR_A0` to `ADDR_A1` without connecting them
  to `ADDRESS` and does not select the intended role.
- Only horizontal row shunts connect `ADDRESS` to a pull-down. The top row
  selects the 10 kOhm path and the bottom row selects the 20 kOhm path.

### Rev D workaround

Use the horizontal rows for electrical testing despite the role labels:

| Shunts | Temporary Rev D test role/address |
|---|---|
| None | Eyes `0x30` |
| Top horizontal row | Mouth `0x31` |
| Bottom horizontal row | Spare `0x32` |
| Both horizontal rows | Development `0x33` |

### Required next-revision correction

Route JP1 so each labeled vertical column connects `ADDRESS` to one resistor
path:

- Left vertical column: Eyes `0x30`
- Right vertical column: Mouth `0x31`
- No shunt: reserved Spare `0x32`
- Both vertical shunts: reserved Development `0x33`

One implementation is to connect pads 1 and 2 to `ADDRESS`, pad 3 to one
address pull-down, and pad 4 to the other. Confirm the final footprint
orientation and pad numbering against the physical board before release.
