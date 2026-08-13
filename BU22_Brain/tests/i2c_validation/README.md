# BU-22 reusable I2C validation tests

These are raw hardware/feature tests, not the final BU-22 protocol. They archive
the experiments proven on the Feather RP2040 Brain and KB2040 Eyes breadboard.

## Eye Controller setup

Load the universal receiver from `BU22_Eyes/tests/i2c_basic/` onto the KB2040:

- `code.py`
- `config.py`
- `lib/adafruit_dotstar.mpy`
- `lib/adafruit_pixelbuf.mpy`

It listens at address `0x30` and supports every test below.

## Brain setup

Copy `common.py` to the Feather RP2040 as `common.py`. Copy one numbered test
to the Feather as `code.py`.

| Test | Purpose |
|---|---|
| `01_identify.py` | Discovery, CLEAR, and IDENTIFY |
| `02_interrupt.py` | Interrupt a locally timed Eye animation |
| `03_brightness.py` | Two-byte parameter and global brightness |
| `04_channels.py` | Independent six-channel output and crosstalk |
| `05_pixels.py` | Independent 24-pixel addressing and order |
| `06_frame_stream.py` | Sustained 25-byte frames at 10 FPS |
| `07_status_readback.py` | Bidirectional status reads under frame traffic |
| `08_expressions.py` | Locally stored 3x4 eyes and local blink timing |
| `09_recovery.py` | Manual Brain/Eyes disconnect and recovery |

## Wiring assumptions

- Brain and Eyes powered independently by USB during development.
- LED strands and 74AHCT125 level shifters powered from regulated 5 V.
- All grounds connected.
- SDA, SCL, and GND connect between Brain and Eyes.
- Qwiic red power conductor is disconnected.
- One pair of 4.7k pull-ups connects SDA/SCL to the Brain's 3.3 V rail.
- Current CircuitPython target testing requires about 20 ms between immediate
  consecutive controller transactions.
