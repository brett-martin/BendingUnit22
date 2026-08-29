# BU-22 Brain board bring-up

Interactive CircuitPython test for the Feather RP2040 Brain perfboard V1.

The automatic startup sequence is intentionally non-destructive:

1. Scan and identify the I2C bus.
2. Read the DS3231 RTC when present.
3. Report all seven buttons, Audio FX ACT, and sensor/interrupt inputs.
4. Measure the RTC SQW heartbeat for 4.5 seconds.
5. Leave antenna outputs low and Audio FX reset released.

Use the USB serial console for output tests:

| Key | Test |
|---|---|
| `s` | Scan I2C |
| `r` | Read RTC |
| `h` | Measure SQW heartbeat |
| `i` | Print input states |
| `a` | Cycle the three antenna outputs |
| `l` | Request the Audio FX track list without playing audio |
| `x` | Pulse the Audio FX reset line |
| `?` | Print help |

Each button press/release is printed automatically. The onboard NeoPixel is
green when the RTC and heartbeat pass, red when either needs attention, and
amber during startup.

## Install

With the Feather mounted as `CIRCUITPY`, run from this directory:

```sh
python3 -m circup install -r requirements.txt
cp code.py config.py /Volumes/CIRCUITPY/
```
