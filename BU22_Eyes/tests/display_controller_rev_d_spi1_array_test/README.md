# Combined CH5/CH6 SPI1 full-array test

This test validates a complete daisy-chained array using hardware SPI1. Take
clock from CH5 `CLOCK` (`A0`) and data from CH6 `DATA` (`A1`), with common
ground and external 5 V power. Leave CH5 data and CH6 clock disconnected.

- `eye_config.py`: two 9x16 panels, 288 LEDs total.
- `mouth_config.py`: three 5x11 tiles, 165 LEDs total.

The repeating sequence is a complete single-pixel chase, solid red, solid
green, solid blue, dim white, and black.
