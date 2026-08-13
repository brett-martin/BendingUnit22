# Bending Unit 22

BU-22 is a modular animatronic Bender-inspired clock and character display.
The Brain orchestrates operating modes, sensors, time, audio, and user input.
Independent Eyes and Mouth controllers own their LED hardware, rendering, and
precisely timed local animations.

This repository currently contains the proven Brain/Eyes breadboard tests,
draft display protocol, experimental content catalogs, and first clean v0
CircuitPython firmware slice.

## Repository map

```text
BU22_Brain/
  firmware/v0/          First Brain protocol exerciser
  tests/                Feather smoke test and reusable I2C validation suite

BU22_Eyes/
  catalogs/             Experimental expressions, animations, performances
  firmware/v0/          First clean Eyes firmware slice
  tests/                Universal I2C receiver and hardware-test backups

BU22_Mouth/
  README.md             Mouth subsystem placeholder

protocol/
  semantic_protocol_v0.md   Behavior, terminology, and ownership
  wire_protocol_v0.md       Concrete draft I2C encoding
  commands.md               Raw breadboard-only validation bytes
```

The original six-channel electrical bring-up programs are preserved under the
named Brain and Eyes test folders rather than serving as production firmware.

## Current breadboard hardware

- Adafruit Feather RP2040 acting as Brain
- Adafruit KB2040 acting as Eyes controller
- Six independent four-pixel SK9822 strands
- Three 74AHCT125 level-shifter ICs
- Independent USB power for both MCUs during development
- External regulated 5 V for level shifters and LEDs
- Shared ground, SDA, and SCL
- 4.7k I2C pull-ups to the Brain's 3.3 V rail
- Qwiic red power conductor disconnected during independent USB testing

### Eyes channel pin map

| Channel | Data | Clock |
|---:|---:|---:|
| 1 | D2 | D3 |
| 2 | D4 | D5 |
| 3 | D6 | D7 |
| 4 | D8 | D9 |
| 5 | D10 | A0 |
| 6 | A1 | A2 |

The current test assembly is physically rotated 180 degrees. Firmware keeps
content in logical orientation and applies the hardware transform at render
time.

## Proven functionality

- I2C discovery at Eyes address `0x30`
- One-byte and parameterized multi-byte commands
- Global brightness control
- Independent six-channel and 24-pixel control
- Complete 25-byte frame streaming at 10 FPS with no late frames
- Bidirectional status readback under display traffic
- Locally stored expressions and animations
- Immediate Brain interruption and STOP
- Dedicated Visor Down/Up row transitions
- Brain and Eyes disconnect/reconnect recovery
- Five-second standalone Normal fallback
- Visible missing-content development errors
- Concise action-level Eyes serial logging

See [the I2C validation index](BU22_Brain/tests/i2c_validation/README.md)
for the reusable development-board test sequence.

## Content catalogs

Expressions, animations, and performances use separate numeric ID spaces.
They remain experimental before v1. At v1, reviewed IDs become stable; later
content is appended while existing entries may improve without changing their
semantic meaning.

See [the Eyes catalog rules](BU22_Eyes/catalogs/README.md).

## Protocol documents

- [Semantic protocol v0](protocol/semantic_protocol_v0.md)
- [Wire protocol v0](protocol/wire_protocol_v0.md)
- [Raw hardware-validation commands](protocol/commands.md)

The semantic and wire documents are drafts. The raw validation bytes remain
separate so future hardware can rerun today's proven tests regardless of how
the production protocol evolves.

## Running the v0 Brain/Eyes slice

On the KB2040 Eyes `CIRCUITPY` drive, copy:

```text
BU22_Eyes/firmware/v0/code.py
BU22_Eyes/firmware/v0/config.py
BU22_Eyes/firmware/v0/content.py
```

Its `lib` directory also needs:

```text
adafruit_dotstar.mpy
adafruit_pixelbuf.mpy
```

On the Feather RP2040 Brain `CIRCUITPY` drive, copy:

```text
BU22_Brain/firmware/v0/code.py
```

The exerciser cycles expressions and animations, interrupts an animation,
tests Off and visor transitions, requests missing animation `999`, reads the
error status, and recovers with Normal.

## CircuitPython dependencies

Install the DotStar CircuitPython dependencies with:

```sh
python3 -m circup install -r requirements.txt
```
