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
| None | Development `0x33` |
| Top horizontal row | Mouth `0x31` |
| Bottom horizontal row | Eyes `0x30` |
| Both horizontal rows | Spare `0x32` |

### Required next-revision correction

Route JP1 so each labeled vertical column connects `ADDRESS` to one resistor
path:

- Left vertical column: Eyes `0x30`
- Right vertical column: Mouth `0x31`
- No shunt: Development `0x33`
- Both vertical shunts: Spare `0x32`

One implementation is to connect pads 1 and 2 to `ADDRESS`, pad 3 to one
address pull-down, and pad 4 to the other. Confirm the final footprint
orientation and pad numbering against the physical board before release.

## E3: Original firmware reversed CH1–CH4 clock and data assignments

Confirmed on `CTRL-RD-01` during bring-up on 2026-09-06.

The original Rev D CircuitPython configurations treated D3/D5/D7/D9 as clock
and D2/D4/D6/D8 as data. With that mapping, a known-good 55-pixel mouth tile
worked only on U3/CH5 and CH6. All six channels nevertheless passed a slow
static 0 V/4.7 V output exerciser.

A deliberately slow valid-DotStar test at approximately 1 kHz still operated
only CH5/CH6. Reversing clock and data in firmware only for CH1–CH4 made the
same mouth tile work on all six channels. The observed functional mapping is:

| Channel | Clock | Data |
|---|---|---|
| CH1 | D2 | D3 |
| CH2 | D4 | D5 |
| CH3 | D6 | D7 |
| CH4 | D8 | D9 |
| CH5 | A0 | SCK |
| CH6 | A2 | A1 |

This result identifies a firmware-to-physical-pin mapping error; it does not
show defective U1/U2 buffers or failed PCB traces. All repository Rev D
firmware configurations have been updated to the observed functional mapping.
Repeat the dynamic test on `CTRL-RD-02` before marking the correction validated
on both assemblies.

### Required next-revision correction

- Preserve the validated functional mapping in controller firmware.
- Annotate the KB2040 socket symbols with their actual board pin names.
- Audit MCU1B socket pad numbering/orientation against the installed KB2040.
- Ensure the schematic, PCB net names, firmware mapping, and connector labels
  all describe the same clock/data signals before the next fabrication release.
