# Stable development display-controller runtime

One runtime serves both Rev D Eyes and Mouth controllers. The address jumper
selects the I2C address and display geometry. It uses the validated half-array
hardware-SPI1 path: CH5 clock (`A0`) plus CH6 data (`A1`) at 4 MHz.

Copy `code.py` and `config.py` to the controller's `CIRCUITPY` root and copy the
repository `common` directory to `CIRCUITPY/common`. Install
`adafruit_dotstar` and its dependencies in `CIRCUITPY/lib`.

The controller starts dark for three seconds, scrolls `TARGET MODE` for two
seconds, shows `E30` or `M31` for two seconds, then clears and listens for the
Brain. The physical TEST button cycles `TARGET`, `TEST`, and `BENDER`.

In `TARGET`, Brain display commands are accepted. In `TEST` and `BENDER`, the
controller continues answering status reads but rejects visual commands with
`ERROR_LOCAL_MODE_BUSY`; the Brain decodes the response as the named local
mode. TEST repeats horizontal and vertical sweeps, a wiring-order chase, then
solid red, green, blue, Bender yellow, and off frames at 10 fps.

`LOGGING` and `MIRROR_I2C` are both disabled by default. Enable logging only
while attached to a serial console. I2C mirroring logs semantic packets, not
pixels, but should still remain disabled during timing-sensitive tests.

## First hardware acceptance pass

1. Boot each controller separately and confirm the 3/2/2-second startup sequence.
2. Press TEST and confirm all TEST patterns repeat without stale pixels.
3. Press TEST again and confirm the static Bender image; press once more for a
   dark TARGET display.
4. Boot both controllers, then the Brain. Confirm its delayed scan sees `0x30`
   and `0x31` by temporarily enabling `LOGGING` on the Brain.
5. Leave both controllers in TARGET and use the Brain MODE button to verify the
   CLOCK, SET TIME, BENDER, PLAY, and TEST states.
6. Put either controller in TEST or BENDER and confirm the Brain receives a
   named busy state without disturbing the local display.
