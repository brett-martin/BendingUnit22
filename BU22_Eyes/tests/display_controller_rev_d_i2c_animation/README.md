# Stored-frame I2C animation test

This integrated test receives tagged `SHOW_EXPRESSION` commands from the Brain
at 10 FPS and renders stored frames locally over the combined CH5-clock/CH6-data
hardware-SPI1 output at 4 MHz.

- Eyes supports content IDs 0 center, 2 left, and 3 right across two 9x16
  panels.
- Mouth supports content IDs 0 through 4 from closed to fully open across three
  5x11 tiles.

The Brain sends the same frame tag to both controllers. This is a temporary
hardware/protocol validation; it does not finalize the simulator export format.
