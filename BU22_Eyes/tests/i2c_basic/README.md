# Basic Eyes I2C test

Copy `code.py` and `config.py` to the KB2040 `CIRCUITPY` drive. Its `lib`
directory must contain `adafruit_dotstar.mpy` and `adafruit_pixelbuf.mpy`.

The KB2040 listens at I2C address `0x30`. It starts with all LEDs black:

- `CLEAR` (`0x00`) immediately makes every channel black.
- `IDENTIFY` (`0x01`) makes all six four-pixel strands glow amber for one
  second and then return to black.
- `START LONG PATTERN` (`0x02`) starts a six-second moving pixel pattern.
- `SET BRIGHTNESS` (`0x03`) accepts one additional byte from 0–255, applies it
  to all channels, and displays solid amber.
- `SET CHANNEL COLOR` (`0x04`) accepts a zero-based channel index followed by
  red, green, and blue bytes. It changes only the selected channel.
- `SET PIXEL` (`0x05`) accepts zero-based channel and pixel indices followed by
  red, green, and blue bytes. It changes only the selected pixel.
- `SET FRAME` (`0x06`) accepts 24 intensity bytes. Eyes maps them across six
  channels × four pixels and renders the complete amber frame together.
- `GET STATUS` (`0x07`) prepares a five-byte response containing identity
  (`0x22`), test version, activity, last display command, and error flag.

The current Brain test interleaves status reads with complete frame writes at
10 FPS. This tests bidirectional I2C under display traffic and confirms that a
final `CLEAR` changes reported activity from frame-active to idle.

The identify timer does not block the main loop. This is deliberate: future
animations must never prevent the Eye Controller from servicing I2C.

This code requires a CircuitPython build that includes the built-in
`i2ctarget` module. At the REPL, run `import i2ctarget` before wiring the full
test if you want to confirm support first.
