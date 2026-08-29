# BU-22 current project status

Last updated: 2026-08-29

## Active hardware

- `CTRL-RD-01`: first hand-assembled Display Controller Rev D. Passive power
  distribution and the five-second output-enable transition have passed. Slow
  output exercising now passes CH3 through CH6 after reflow. U1 pin 14 now has
  supply voltage, but CH1/CH2 outputs swing only from about 0 to 1.5 V. Do not
  attach LED arrays until U1 is corrected and all outputs pass. See
  `hardware/bringup/CTRL-RD-01.md`.
- `CTRL-RD-02`: PCB and parts available; assembly has not been recorded yet.
- `BRAIN-PERF-01`: prototype Brain perfboard assembled. I2C discovery, RTC
  read/set, configured 1 Hz SQW heartbeat, and Audio FX UART/list/play-command
  tests have passed. Physical NeoPixel, button, and audible Audio FX tests also
  pass. Raw sensor response, close interrupt assertion, and the physical red
  antenna outputs and USB/external-5 V isolation also pass. Sensor interrupt
  integration is intentionally deferred. See
  `hardware/bringup/BRAIN-PERF-01.md`.

## Active firmware

- Universal Rev D standalone controller test:
  `BU22_Eyes/tests/display_controller_rev_d_bringup/`
- Rev D fail-dark, jumper-addressed I2C target scan test:
  `BU22_Eyes/tests/display_controller_rev_d_i2c_target/`
- Rev D all-channel clock/data output exerciser:
  `BU22_Eyes/tests/display_controller_rev_d_output_exerciser/`
- Rev D 5x11 tooth-module visual test:
  `BU22_Mouth/tests/display_controller_rev_d_tooth_module/`
- Brain perfboard bring-up test:
  `BU22_Brain/tests/brain_board_bringup/`

The controller test source no longer enables the KB2040 heartbeat input's
internal pull-up. A disconnected heartbeat LED should therefore remain off.
Confirm that this corrected source is deployed before interpreting the LED.

## Immediate next steps

1. Diagnose U1 power/CH1/CH2 and the second half of U2/CH4 on `CTRL-RD-01`.
2. Deploy the corrected controller test to its KB2040.
3. Test one known-good four-pixel strip sequentially on CH1 through CH6.
4. Record channel identity, RGB order, direction, brightness, and current.
5. Assemble and repeat the same bring-up on `CTRL-RD-02`.
6. Optionally measure Brain I2C pull-up strength. Sensor interrupt integration
   is intentionally deferred.
7. Connect Brain and both display controllers only after standalone tests pass.

## Two-Mac workflow

1. Pull with `git pull --ff-only` before beginning work.
2. Work from repository files and copy them to `CIRCUITPY` only for deployment.
3. Record physical results under `hardware/bringup/`.
4. Commit and push before moving to the other Mac.
5. Avoid editing the same file concurrently on both machines.
