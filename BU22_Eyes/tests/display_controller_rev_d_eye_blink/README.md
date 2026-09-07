# Display Controller Rev D 9x16 eye blink

This CircuitPython test displays a single Bender-style eye on a `9 x 16`
column-serpentine eye tile and repeats a realistic blink indefinitely.

The sequence is:

1. Display the normal open eye for three seconds.
2. Close one row from both the top and bottom at 10 FPS for eight frames.
3. Hold the fully closed eye for two additional frames.
4. Reverse the eight closure frames to reopen the eye.
5. Hold the normal eye for three seconds and repeat.

Frames are sent identically to all six Rev D controller channels. The serial
log reports the duration of each 18-frame blink and any missed 100 ms frame
deadlines.

Copy `code.py` and `config.py` to the controller's `CIRCUITPY` drive. Confirm
that `adafruit_dotstar.mpy` and `adafruit_pixelbuf.mpy` are present under
`CIRCUITPY/lib/`. Power the LED tile from an appropriate external 5 V supply
with a shared controller ground.
