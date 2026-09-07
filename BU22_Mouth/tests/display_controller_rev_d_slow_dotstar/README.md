# Display Controller Rev D slow DotStar test

This diagnostic bypasses `adafruit_dotstar` and transmits deliberately slow,
valid APA102/SK9822 frames to all six Rev D controller channels. It is intended
to distinguish static electrical continuity from dynamic protocol behavior.

The test is configured for the 55-pixel `5 x 11` mouth tile and nominally
clocks data at 1 kHz. It repeatedly sends solid red, green, blue, dim white,
and black frames. All channels receive identical bits, allowing the same
known-good tile to be moved between CH1 through CH6.

The implementation sends the APA102/SK9822 32-bit start frame, four bytes per
pixel in global-brightness/B/G/R order, and sufficient end clocks for 55
pixels. The AHCT outputs remain disabled during the five-second safe-start
interval and are enabled only after a valid black frame is prepared.

Copy `code.py` and `config.py` to the controller's `CIRCUITPY` drive. Power the
mouth tile from an appropriate external 5 V supply with a shared controller
ground.
