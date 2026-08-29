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
