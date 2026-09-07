# Display Controller Rev D 9x16 eye-tile test

Temporary CircuitPython firmware for visually validating one BU-22 `9 x 16`
eye tile on any Rev D controller output. It sends identical 144-pixel frames
to all six channels, so move the same known-good tile between channels without
changing firmware.

The test assumes a column-serpentine chain beginning at the top-left: even
columns run downward and odd columns run upward. It repeatedly displays:

1. A sequential physical-chain chase
2. A nine-column logical sweep from left to right
3. A sixteen-row logical sweep from top to bottom
4. Conservative red, green, blue, and dim-white fills
5. A commanded blackout

The chase changes only the previous and current pixels between frames and
prints once per physical column, avoiding the extra frame transmissions and
serial output that would unnecessarily slow a 144-pixel test.

The controller keeps its AHCT outputs disabled for five seconds at startup,
prepares a black frame, and only then enables the buffers.

## Install

Copy `code.py` and `config.py` to the controller's `CIRCUITPY` drive. Confirm
that `adafruit_dotstar.mpy` and `adafruit_pixelbuf.mpy` are present under
`CIRCUITPY/lib/`.

Power the eye tile from a current-limited external 5 V supply and share ground
with the controller. Do not power the LED tile from computer USB.

Record only physically observed results in the applicable controller bring-up
file.
