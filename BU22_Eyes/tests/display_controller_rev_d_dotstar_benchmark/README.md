# Rev D CircuitPython DotStar benchmark

This diagnostic measures the output cost of the standard CircuitPython
`adafruit_dotstar` library with the corrected six-channel Rev D pin mapping.
It uses the full eye-controller load of 144 pixels per channel.

For every channel it reports:

- Whether the library acquired `busio.SPI` or fell back to software GPIO
- Average milliseconds per `show()`
- Maximum theoretical FPS for that channel alone

It then measures the complete sequential six-channel `show()` operation and
reports whether it fits within the 100 ms budget required for 10 FPS. The test
repeats every five seconds. Connected tiles may briefly show a dim amber color
during each benchmark and are returned to black afterward.

The backend report reads the library's private `_spi` field and is intended
only for this controlled diagnostic. It should not become a production API
dependency.

Copy `code.py` and `config.py` to `CIRCUITPY`. Confirm that
`adafruit_dotstar.mpy` and `adafruit_pixelbuf.mpy` are installed under `lib/`.
