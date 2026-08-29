# Display Controller Rev D 5x11 tooth-module test

Visual test for one 5-column by 11-row tooth LED module wired as a vertical
serpentine path. Pixel 0 is at the top-left. Column 1 runs top to bottom,
column 2 bottom to top, and the pattern alternates through the bottom-right.

All six Rev D channels receive identical 55-pixel frames. Begin with only the
tooth module on the already validated CH6 output. This confirms that module and
channel only; move the same module to another channel with power removed before
claiming that channel passed.

## Patterns

1. Single-pixel chase through physical indices 1–55
2. Five whole columns, left to right
3. Eleven whole rows, top to bottom
4. Conservative all-on red, green, blue, and dim white
5. Blackout, then repeat

## Safety

- Use a current-limited external 5 V supply; do not power the module from USB.
- Verify module input order is `GND, CLOCK, DATA, +5V`.
- Connect or move the module only with power removed.
- Start on CH6. CH1 and CH2 remain blocked by the unresolved U1 fault.
- Brightness is intentionally limited to 0.03 and full-intensity white is not
  used.

The test holds the AHCT buffers disabled for five seconds, establishes a black
frame, and only then enables the outputs.
