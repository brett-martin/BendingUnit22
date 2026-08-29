# CTRL-RD-01 bring-up record

Last updated: 2026-08-29

## Identity

- Assembly: first hand-assembled universal display controller
- PCB: BU-22 Display Controller Rev D
- MCU: socketed Adafruit KB2040
- Intended initial role: standalone controller hardware validation

## Assembly notes

- D1 and D2 were initially installed according to incorrect `+` silkscreen
  marks and were subsequently rotated 180 degrees.
- Correct LED polarity is left square pad 1 = cathode/GND and right round pad 2
  = anode/positive.
- See `hardware/display-controller-rev-d/ERRATA.md`.

## Tests passed

- Input `SYSTEM_5V` to GND did not show a hard short. Resistance increased from
  approximately 2 kOhm through 3 kOhm and 4 kOhm as the capacitors charged from
  the meter.
- With only external 5 V connected, all six channel power pins measured as
  expected.
- U2 and U3 logic-supply measurements passed.
- Q1 output-enable behavior passed with the KB2040 and temporary test firmware:
  the collector/OE voltage remained high during the five-second fail-dark
  interval and changed correctly when firmware enabled the buffers.

## Open issues

- U1 did not measure `LOGIC_5V` where expected. Recheck the exact pin-14
  location, solder joint, C1 area, and local connection before attaching LEDs.
- The heartbeat LED appeared solid because the deployed temporary firmware used
  the KB2040 internal pull-up. Repository source has been corrected but its
  deployment has not yet been recorded.

## Current firmware source

Scan-only target test currently deployed:
`BU22_Eyes/tests/display_controller_rev_d_i2c_target/`

The test keeps all AHCT outputs disabled, uses the Rev D RX/TX I2C routing,
and selects `0x30` through `0x33` from the A3 address network. Deployment to
the controller KB2040 was confirmed, but Brain discovery and the assembled
board's ADC address levels have not yet been observed.

## Next test

1. Resolve and record U1 pin-14 supply voltage.
2. Record the target test's raw address ADC value and selected role.
3. With independently powered boards and shared GND/SDA/SCL only, scan for the
   selected controller address from the Brain.
4. Redeploy the corrected standalone heartbeat-input firmware.
5. Connect one known-good four-pixel strip to CH1 and run the suite.
6. Move the same strip through CH2–CH6, powering down between connectors.
