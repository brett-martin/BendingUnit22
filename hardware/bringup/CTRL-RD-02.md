# CTRL-RD-02 bring-up record

Last updated: 2026-09-06

## Identity

- Assembly: second hand-assembled universal display controller
- PCB: BU-22 Display Controller Rev D
- MCU: socketed Adafruit KB2040
- KB2040 UID observed over USB: `DF63CC284F214629`
- Intended initial role: standalone controller and single eye-tile validation

## Connected hardware

- One `9 x 16` eye tile is connected to one controller channel.
- The previous controller remains associated with one mouth tile; no result
  for that board is inferred by this test.

## Firmware deployed

The dedicated eye-tile visual test was deployed from:
`BU22_Eyes/tests/display_controller_rev_d_eye_tile/`

The deployed `code.py` and `config.py` were verified byte-for-byte against the
repository copies. The test addresses 144 pixels per channel and sends
identical frames to all six Rev D outputs. It assumes a top-left-origin,
column-serpentine tile, runs a sequential chain chase, logical column and row
sweeps, conservative solid-color fills, and blackout, and retains the
five-second fail-dark startup interval.

The tile's static Bender-eye pattern was physically reported to look good. A
dedicated 10 FPS repeating blink test was subsequently deployed from
`BU22_Eyes/tests/display_controller_rev_d_eye_blink/`; its physical animation
result remains pending.

## Tests passed

- The centered Bender-style eye pattern looks good on the temporary `9 x 16`
  strip-built eye tile.

## Open observations

- Record which controller channel is connected.
- Confirm whether all 144 pixels respond during the physical-chain chase.
- Confirm the apparent start corner and chain direction.
- Confirm that logical column and row sweeps match the physical tile.
- Confirm red, green, blue, dim white, and blackout behavior.
- Record any dead, stuck, miscolored, or incorrectly mapped pixels without
  inferring a cause.

## Next test

Observe one complete visual-test cycle and report the connected channel plus
the physical behavior of the chase, column sweep, row sweep, colors, and
blackout.
