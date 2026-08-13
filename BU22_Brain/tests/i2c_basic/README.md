# Basic Brain I2C test

This raw feature test verifies Eye-to-Brain status readback while complete
24-pixel frames continue streaming at 10 frames per second.

| Value | Command | Result |
|---:|---|---|
| `0x00` | `CLEAR` | All eye LEDs turn off |
| `0x01` | `IDENTIFY` | All eye LEDs briefly glow amber |
| `0x02` | `START LONG PATTERN` | Start a six-second moving pixel pattern |
| `0x03, value` | `SET BRIGHTNESS` | Set raw brightness from 0–255 and show amber |
| `0x04, channel, R, G, B` | `SET CHANNEL COLOR` | Fill one channel with an RGB color |
| `0x05, channel, pixel, R, G, B` | `SET PIXEL` | Set one pixel on one channel |
| `0x06, 24 intensity bytes` | `SET FRAME` | Render six channels × four pixels in amber |
| `0x07`, followed by a 5-byte read | `GET STATUS` | Read identity, version, activity, last command, and error |

Copy `code.py` to the Feather RP2040 `CIRCUITPY` drive.

The script reads status once while idle, then streams 100 frames over ten
seconds while reading status once per second. It clears the display, reads
status again, reports timing, waits two seconds, and repeats.
