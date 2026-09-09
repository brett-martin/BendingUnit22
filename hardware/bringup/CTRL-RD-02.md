# CTRL-RD-02 bring-up record

Last updated: 2026-09-09

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

## Assembly notes

- Assembly used a hot-air rework station, liquid flux, and microscope
  inspection.
- No obvious board, trace, or soldering flaw was visible under the microscope.

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

The slow all-channel electrical output exerciser was deployed afterward from
`BU22_Eyes/tests/display_controller_rev_d_output_exerciser/` to KB2040 UID
`DF63CC284F214629`. The deployed files were verified byte-for-byte against the
repository copies. New electrical measurements remain pending.

After the CH1–CH4 clock/data mapping correction was validated on CTRL-RD-01,
the corrected `9 x 16` eye-tile visual test was deployed to this controller.
The deployed `code.py` and corrected `config.py` were verified byte-for-byte;
dynamic CH1–CH6 results remain pending.

## Tests passed

- The centered Bender-style eye pattern looks good on the temporary `9 x 16`
  strip-built eye tile.
- LED-array operation passes on U3/CH5 and CH6.
- With the slow four-phase output exerciser, all six channels cycle between
  approximately 0 V and 4.7 V as commanded for both clock and data.
- With the corrected Rev D clock/data mapping, the known-good `9 x 16` eye tile
  visually operates across CH1 through CH6. This confirms dynamic LED-array
  operation through U1, U2, and U3 on the second assembly.
- With CTRL-RD-02 selected as Eyes and running the scan-only I2C target
  firmware, the Brain discovered it at `0x30` in a complete four-device scan
  alongside Mouth `0x31`, VCNL4200 `0x51`, and DS3231 `0x68`.
- The half-scale static Eyes I2C test passed visually with the physical left eye
  on CH6 and right eye on CH5. Brain commands selected Normal and static Angry
  images successfully. Keeping the first and last logical rows dark produced
  the desired less-open eye shape.
- The final half-scale eye geometry was visually confirmed: both tiles use the
  same symmetric eight-column image starting at the local left edge, leave the
  ninth/rightmost column unused, and use a centered two-column-by-four-row dark
  pupil. Normal and Angry appearance were accepted at the bench.
- The full-capacity mixed automatic-SPI benchmark transmitted 144 pixels on
  CH3–CH6 (576 total). Adafruit DotStar selected hardware SPI for CH3 and
  software SPI for CH4–CH6. The completed runs measured approximately 315–318
  ms per controller frame (about 3.1 FPS maximum; about 2.5 FPS at the 80%
  budget), missed every scheduled deadline from 10 through 60 FPS, and measured
  a 2.0× clear-then-show penalty. The attached CH5/CH6 panels visibly showed
  moving colored pixels; no visual frame-rate measurement is inferred.

## Open issues

- CircuitPython's six-channel software DotStar output does not sustain the
  intended 10 FPS animation rate. This is a firmware-performance issue and is
  separate from the now-passed channel hardware and corrected pin mapping.

## Open observations

- Record which controller channel is connected.
- Confirm whether all 144 pixels respond during the physical-chain chase.
- Confirm the apparent start corner and chain direction.
- Confirm that logical column and row sweeps match the physical tile.
- Confirm red, green, blue, dim white, and blackout behavior.
- Record any dead, stuck, miscolored, or incorrectly mapped pixels without
  inferring a cause.

## Next test

Address the six-channel animation-rate requirement separately with compiled or
hardware-assisted LED output firmware.
