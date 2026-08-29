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

All-channel output exerciser currently deployed:
`BU22_Eyes/tests/display_controller_rev_d_output_exerciser/`

It keeps the buffers disabled for five seconds, initializes all Rev D clock and
data GPIOs low, enables the buffers, and repeats four two-second phases across
all six channels: low/low, high/low, low/high, and high/high. Deployment to the
controller KB2040 was confirmed. Connector testing found both clock and data
outputs working on CH3, CH5, and CH6. Both outputs failed the exercise on CH1,
CH2, and CH4. Exact failed-channel voltages and whether they were stuck low,
stuck high, or intermediate were not reported.
- Follow-up probing reported U2 itself working correctly, including the CH4
  side. Subsequent measurements found the CH4 signals failing across the R7
  and R8 series-resistor paths. Additional path testing indicates an open
  solder-pad connection between U2's CH4 outputs and the U2-side pads of R7/R8;
  reflow is planned but has not yet been reported or verified. U1 failed its
  IC-level check, but the specific supply, input, OE, and output measurements
  have not yet been provided.

The scan-only target test remains available at:
`BU22_Eyes/tests/display_controller_rev_d_i2c_target/`

The test keeps all AHCT outputs disabled, uses the Rev D RX/TX I2C routing,
and selects `0x30` through `0x33` from the A3 address network. Deployment to
the controller KB2040 was confirmed. Open/open correctly decodes as Eyes, and
the top-row A0 shunt correctly decodes as Mouth. The bottom-row A1 shunt does
not produce its expected Spare selection. Raw ADC values have not yet been
provided. Brain discovery and the remaining A1/both-shunts address levels are
unconfirmed.

## Next test

1. Resolve and record U1 pin-14 supply voltage.
2. Diagnose U1 by recording pin-14 supply, representative input, OE, and output
   levels during the exerciser.
3. With power removed, reflow the suspected U2-to-R7/R8 solder connections and
   inspect for adjacent-pin bridges.
4. Verify continuity from U2 pin 8 to R7's U2-side pad and U2 pin 11 to R8's
   U2-side pad, then verify each resistor is approximately 100 ohms end-to-end.
5. Rerun the exerciser and confirm CH4 at J4 pins 3/data and 2/clock.
3. Record the target test's remaining A1/both-shunts ADC levels.
4. With independently powered boards and shared GND/SDA/SCL only, scan for the
   selected controller address from the Brain.
5. Redeploy the corrected standalone heartbeat-input firmware.
6. Connect one known-good four-pixel strip to CH1 and run the suite.
7. Move the same strip through CH2–CH6, powering down between connectors.
