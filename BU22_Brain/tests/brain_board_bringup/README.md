# BU-22 Brain board bring-up

Interactive CircuitPython test for the Feather RP2040 Brain perfboard V1.

The automatic startup sequence is intentionally non-destructive:

1. Scan and identify the I2C bus.
2. Read the DS3231 RTC when present.
3. Report all seven buttons, Audio FX ACT, and sensor/interrupt inputs.
4. Configure the RTC SQW output for 1 Hz and measure it for 4.5 seconds.
5. Leave antenna outputs low and Audio FX reset released.

After the RTC is found, the Feather NeoPixel mirrors the SQW level in red so
it blinks in sync with the RTC heartbeat.

Use the USB serial console for output tests:

| Key | Test |
|---|---|
| `s` | Scan I2C |
| `r` | Read RTC |
| `t YYYY-MM-DD HH:MM:SS` | Set RTC from a local wall-clock value |
| `h` | Measure SQW heartbeat |
| `i` | Print input states |
| `a` | Cycle the three antenna outputs |
| `l` | Request the Audio FX track list without playing audio |
| `p NUMBER` | Play `Txx.WAV`; for example, `p 3` plays `T03.WAV` |
| `x` | Pulse the Audio FX reset line |
| `?` | Print help |

The `t` command stores the supplied fields exactly as entered. It performs no
timezone or daylight-saving conversion. Audio playback is explicit because it
drives the attached speakers. Track numbers from 0 through 99 map directly to
the corresponding two-digit filename, `T00.WAV` through `T99.WAV`.

Each button press/release is printed automatically. The onboard NeoPixel is
amber during startup and then blinks red in sync with the RTC SQW heartbeat.
It remains solid red when the RTC is unavailable.

## Install

With the Feather mounted as `CIRCUITPY`, run from this directory:

```sh
python3 -m circup install -r requirements.txt
cp code.py config.py /Volumes/CIRCUITPY/
```
