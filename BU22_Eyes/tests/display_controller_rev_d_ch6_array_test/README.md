# CH6 full-array LED test

This test validates every LED in a daisy-chained half-scale BU-22 array using
the controller's conventional CH6 output (`A2` clock and `A1` data). It runs a
single-pixel chase followed by solid red, green, blue, dim white, and black.

- `eye_config.py`: two 9x16 panels, 288 LEDs total.
- `mouth_config.py`: three 5x11 tiles, 165 LEDs total.

Copy `code.py` and the appropriate configuration as `config.py` to the target
controller. Use an external 5 V LED supply with common ground; USB is for
programming and serial only.
