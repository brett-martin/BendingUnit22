# CTRL-RD-01 bring-up record

Last updated: 2026-09-06

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

- Reflow restored supply voltage at U1 pin 14, but all four U1-buffered outputs
  currently swing only between approximately 0 and 1.5 V instead of reaching
  `LOGIC_5V`. U1 power, ground, OE, and input levels remain to be isolated.
- The heartbeat LED appeared solid because the deployed temporary firmware used
  the KB2040 internal pull-up. Repository source has been corrected but its
  deployment has not yet been recorded.
- After microscope inspection and hot-air/liquid-flux reflow of visible trace
  and solder connections, no obvious remaining physical PCB flaw was observed.
  LED-array testing still passes only U3/CH5 and CH6; U1/CH1 and CH2 and
  U2/CH3 and CH4 do not drive the tested arrays.

## Current firmware source

5x11 tooth-module visual test currently deployed:
`BU22_Mouth/tests/display_controller_rev_d_tooth_module/`

It sends identical 55-pixel frames to all six channels, with a sequential
path chase, column sweep, row sweep, conservative all-on colors, and blackout.
The test was deployed to the controller KB2040 for initial use with only the
same tooth module moved between channels. CH5 and CH6 passed visually. CH3 and
CH4 powered the module and showed expected slow/static signal voltages but
produced no visible DotStar output. This localizes the visual/high-speed failure
to the U2 channel group; the specific waveform or hardware cause is unresolved.

The all-channel electrical output exerciser remains available at:
`BU22_Eyes/tests/display_controller_rev_d_output_exerciser/`

It keeps the buffers disabled for five seconds, initializes all Rev D clock and
data GPIOs low, enables the buffers, and repeats four two-second phases across
all six channels: low/low, high/low, low/high, and high/high. Deployment to the
controller KB2040 was confirmed. After reflow work, both clock and data outputs
are now reported working on CH3 through CH6. CH1 and CH2 remain faulty because
all four U1 outputs swing only from approximately 0 to 1.5 V.
- Follow-up probing reported U2 itself working correctly, including the CH4
  side. Subsequent measurements found the CH4 signals failing across the R7
  and R8 series-resistor paths. Additional path testing indicates an open
  solder-pad connection between U2's CH4 outputs and the U2-side pads of R7/R8.
  Reflow restored CH4, and CH3 through CH6 now pass.
- C1's left pad showed continuity to the known `LOGIC_5V` reference, while the
  C1-left-to-U1-pin-14-lead measurement was approximately 3 MOhm. This confirms
  an effectively open path to the U1 VCC lead; the distinction between an
  unsoldered lead and an open PCB pad/feed remains to be verified after reflow.

The scan-only target test remains available at:
`BU22_Eyes/tests/display_controller_rev_d_i2c_target/`

The test keeps all AHCT outputs disabled, uses the Rev D RX/TX I2C routing,
and selects `0x30` through `0x33` from the A3 address network. Deployment to
the controller KB2040 was confirmed. Open/open correctly decodes as Eyes, and
the top-row A0 shunt correctly decodes as Mouth. The bottom-row A1 shunt does
not produce its expected Spare selection. Raw ADC values have not yet been
provided. Brain discovery and the remaining A1/both-shunts address levels are
unconfirmed.

Target test v0.2 changes the intended state mapping: one A1/left-role shunt is
Eyes `0x30`, one A0/right-role shunt is Mouth `0x31`, no shunts is Development
`0x33`, and both shunts is Spare `0x32`. These v0.2 selections have not yet
been observed on the physical board.

JP1 was confirmed to have a Rev D copper/label orientation error. The intended
interface is one vertical left-column shunt for Eyes and one vertical
right-column shunt for Mouth, with none and both reserved for extra states.
Fabricated Rev D boards only select their resistor paths with horizontal row
shunts. See `hardware/display-controller-rev-d/ERRATA.md` E2.

## Next test

1. Compare one failing channel with CH5 during the same slow exerciser phase:
   measure its KB2040-side 3.3 V data/clock nets at the buffer input pins, then
   the corresponding 5 V buffer output pins and connector pins.
2. Check continuity from the MCU1B socket pads to the U1/U2 input pins and
   compare it with MCU1A-to-U3. All four failing channels originate on MCU1B;
   both working channels originate on MCU1A.
3. Compare U1/U2 and U3 package markings, pin-1 orientation, pin 14/VCC, pin
   7/GND, and OE pins 1/4/10/13 without assuming the cause.
4. Record the target test's remaining A1/both-shunts ADC levels.
5. With independently powered boards and shared GND/SDA/SCL only, scan for the
   selected controller address from the Brain.
6. Redeploy the corrected standalone heartbeat-input firmware.
7. Connect additional LED modules only after all channel faults pass.
