# Tiled horizontal and vertical line scan

This 10 FPS diagnostic verifies logical coordinate mapping across daisy-chained
column-serpentine modules. Each module restarts at its own top-left pixel, so a
logical line remains continuous when the physical chain jumps from the end of
one module to the beginning of the next.

- Eyes: two 9x16 modules form an 18x16 display.
- Mouth: three 5x11 modules form a 15x11 display.
- Cyan horizontal line scans top-to-bottom.
- Purple vertical line scans left-to-right.

Output uses hardware SPI1: CH5 `CLOCK` (`A0`) and CH6 `DATA` (`A1`) at 4 MHz.
