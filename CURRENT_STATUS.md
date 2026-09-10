# BU-22 current project status

Last updated: 2026-09-09

## Active hardware

- `CTRL-RD-01`: first hand-assembled Display Controller Rev D. Passive power
  distribution, five-second output-enable transition, static output levels,
  and dynamic mouth-tile operation pass across CH1–CH6 after correcting the
  reversed CH1–CH4 firmware clock/data mapping. Its KB2040 UID is
  `DF63CC284F66402B` and its current development role is Mouth. See
  `hardware/bringup/CTRL-RD-01.md`.
- `CTRL-RD-02`: second Display Controller Rev D assembled and connected to one
  `9 x 16` eye tile. Static levels and dynamic eye-tile operation pass across
  CH1–CH6 with the corrected mapping. No obvious board or solder flaw was
  visible under microscope inspection. Its KB2040 UID is
  `DF63CC284F214629`. See
  `hardware/bringup/CTRL-RD-02.md`.
- `BRAIN-PERF-01`: prototype Brain perfboard assembled. I2C discovery, RTC
  read/set, configured 1 Hz SQW heartbeat, and Audio FX UART/list/play-command
  tests have passed. Physical NeoPixel, button, and audible Audio FX tests also
  pass. Raw sensor response, close interrupt assertion, and the physical red
  antenna outputs and USB/external-5 V isolation also pass. Sensor interrupt
  integration is intentionally deferred. An integrated scan with both Rev D
  targets also passed, finding Eyes `0x30`, Mouth `0x31`, VCNL4200 `0x51`, and
  DS3231 `0x68`. See
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
- Rev D deliberately slow valid-DotStar mouth test:
  `BU22_Mouth/tests/display_controller_rev_d_slow_dotstar/`
- Rev D 9x16 eye-tile visual test:
  `BU22_Eyes/tests/display_controller_rev_d_eye_tile/`
- Rev D 9x16 repeating eye-blink animation test:
  `BU22_Eyes/tests/display_controller_rev_d_eye_blink/`
- Rev D six-channel CircuitPython DotStar performance benchmark:
  `BU22_Eyes/tests/display_controller_rev_d_dotstar_benchmark/`
- Rev D one-GPIO-at-a-time physical output locator:
  `BU22_Eyes/tests/display_controller_rev_d_gpio_locator/`
- Rev D CH6 full-array LED validation:
  `BU22_Eyes/tests/display_controller_rev_d_ch6_array_test/`
- Rev D combined CH5/CH6 hardware-SPI full-array validation:
  `BU22_Eyes/tests/display_controller_rev_d_spi1_array_test/`
- Rev D geometry-aware 10 FPS tiled line scan:
  `BU22_Eyes/tests/display_controller_rev_d_tiled_line_scan/`
- Rev D stored-frame I2C animation receiver:
  `BU22_Eyes/tests/display_controller_rev_d_i2c_animation/`
- Brain perfboard bring-up test:
  `BU22_Brain/tests/brain_board_bringup/`
- Rev D half-scale static Eyes I2C test:
  `BU22_Eyes/tests/display_controller_rev_d_static_i2c/`
- Rev D half-scale static Mouth I2C test:
  `BU22_Mouth/tests/display_controller_rev_d_static_i2c/`

The controller test source no longer enables the KB2040 heartbeat input's
internal pull-up. A disconnected heartbeat LED should therefore remain off.
Confirm that this corrected source is deployed before interpreting the LED.

## Immediate next steps

1. Continue firmware development with each complete half-size array on one
   hardware-SPI chain: 288 Eyes pixels and 165 Mouth pixels both pass at 4 MHz
   on the combined CH5-clock/CH6-data SPI1 path. The earlier dual-chain test
   passed visually in sync at 4 MHz, supporting a two-hardware-SPI-channel
   target for Rev E. On Rev D, SPI0 is physically on CH4 and SPI1 uses CH5
   clock plus CH6 data.
   Geometry-aware horizontal and vertical line scans also pass visually at
   10 FPS across the 18x16 Eyes and 15x11 Mouth layouts.
2. Continue the successful stored-frame Eyes/Mouth command path into the
   simulator export workflow and higher-level Brain behavior. Brain v0.12 now
   loops an eight-second performance at 10 FPS, sends matching tagged I2C frame
   commands to both controllers, and both render their complete half-size
   arrays locally over 4 MHz SPI1.
3. Develop compiled or hardware-assisted controller output to meet the
   six-channel 10 FPS animation target; this is separate from hardware
   validation.
4. Optionally measure Brain I2C pull-up strength. Sensor interrupt integration
   is intentionally deferred.

## Two-Mac workflow

1. Pull with `git pull --ff-only` before beginning work.
2. Work from repository files and copy them to `CIRCUITPY` only for deployment.
3. Record physical results under `hardware/bringup/`.
4. Commit and push before moving to the other Mac.
5. Avoid editing the same file concurrently on both machines.
