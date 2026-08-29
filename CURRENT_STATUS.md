# BU-22 current project status

Last updated: 2026-08-29

## Active hardware

- `CTRL-RD-01`: first hand-assembled Display Controller Rev D. Passive power
  distribution and the five-second output-enable transition have passed.
  U1's local supply measurement remains unresolved; do not attach LED arrays
  until it is corrected. See `hardware/bringup/CTRL-RD-01.md`.
- `CTRL-RD-02`: PCB and parts available; assembly has not been recorded yet.
- `BRAIN-PERF-01`: prototype Brain perfboard assembled. I2C discovery, RTC
  read/set, configured 1 Hz SQW heartbeat, and Audio FX UART/list/play-command
  tests have passed. Physical NeoPixel/audio confirmation, power isolation,
  buttons, antenna outputs, and sensor transition remain. See
  `hardware/bringup/BRAIN-PERF-01.md`.

## Active firmware

- Universal Rev D standalone controller test:
  `BU22_Eyes/tests/display_controller_rev_d_bringup/`
- Brain perfboard bring-up test:
  `BU22_Brain/tests/brain_board_bringup/`

The controller test source no longer enables the KB2040 heartbeat input's
internal pull-up. A disconnected heartbeat LED should therefore remain off.
Confirm that this corrected source is deployed before interpreting the LED.

## Immediate next steps

1. Resolve the missing U1 pin-14 `LOGIC_5V` measurement on `CTRL-RD-01`.
2. Deploy the corrected controller test to its KB2040.
3. Test one known-good four-pixel strip sequentially on CH1 through CH6.
4. Record channel identity, RGB order, direction, brightness, and current.
5. Assemble and repeat the same bring-up on `CTRL-RD-02`.
6. Complete the remaining Brain perfboard physical I/O tests: power isolation,
   visible heartbeat, audible audio, buttons, antenna, and sensor transition.
7. Connect Brain and both display controllers only after standalone tests pass.

## Two-Mac workflow

1. Pull with `git pull --ff-only` before beginning work.
2. Work from repository files and copy them to `CIRCUITPY` only for deployment.
3. Record physical results under `hardware/bringup/`.
4. Commit and push before moving to the other Mac.
5. Avoid editing the same file concurrently on both machines.
