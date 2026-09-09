# CTRL-RD-01 bring-up record

Last updated: 2026-09-09

## Identity

- Assembly: first hand-assembled universal display controller
- PCB: BU-22 Display Controller Rev D
- MCU: socketed Adafruit KB2040
- KB2040 UID observed over USB: `DF63CC284F66402B`
- Current development role: Mouth controller
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
- With the slow four-phase output exerciser, all six channels on the completed
  board cycle between approximately 0 V and 4.7 V as commanded for both clock
  and data.

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

The deliberately slow valid-DotStar mouth test is being deployed from:
`BU22_Mouth/tests/display_controller_rev_d_slow_dotstar/`

It bypasses `adafruit_dotstar`, sends identical valid 55-pixel frames to all
six channels at a nominal 1 kHz clock, and cycles red, green, blue, dim white,
and black. Only U3/CH5–6 operated; CH1–4 still failed, ruling out excessive
clock rate as the sole cause. Version `0.2-swap-ch1-4` was then prepared and
deployed with clock/data intentionally reversed only on CH1–4. The same mouth
tile then worked on all six channels, confirming the original CH1–4 firmware
clock/data assignments were reversed. The corrected Rev D mapping is now
standardized in repository configurations; see ERRATA E3.

5x11 tooth-module visual test previously deployed:
`BU22_Mouth/tests/display_controller_rev_d_tooth_module/`

It sends identical 55-pixel frames to all six channels, with a sequential
path chase, column sweep, row sweep, conservative all-on colors, and blackout.
The test was deployed to the controller KB2040 for initial use with only the
same tooth module moved between channels. CH5 and CH6 passed visually. CH3 and
CH4 powered the module and showed expected slow/static signal voltages but
produced no visible DotStar output. This localizes the visual/high-speed failure
to the U2 channel group; the specific waveform or hardware cause is unresolved.

The all-channel electrical output exerciser is currently deployed from:
`BU22_Eyes/tests/display_controller_rev_d_output_exerciser/`

It keeps the buffers disabled for five seconds, initializes all Rev D clock and
data GPIOs low, enables the buffers, and repeats four two-second phases across
all six channels: low/low, high/low, low/high, and high/high. Deployment to
KB2040 UID `DF63CC284F66402B` was reconfirmed on 2026-09-06. After reflow work,
both clock and data outputs
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
- The half-scale static Mouth I2C test was run with three `5 x 11` tiles mapped
  CH6, CH5, and CH4 from physical left to right. Brain-commanded Normal and
  Open images looked correct on the illuminated tiles after shifting the grid
  to repeat three lit rows/columns followed by one dark separator. CH4 produced
  no visible output in this three-tile configuration. This conflicts with its
  earlier successful duplicated-channel visual test; the current tile/cable
  versus channel path has not yet been isolated.
- A subsequent diagnostic version initialized all six DotStar channel objects,
  kept CH6 as the left pattern and CH5 as the center pattern, and duplicated
  the rightmost pattern on CH1 through CH4. Without moving the tile that was
  already connected to CH3, Mouth output began working. Moving the same tile
  through CH1, CH2, CH3, and CH4 then produced correct output on all four
  channels. Initializing/transmitting all six channels is correlated with the
  recovery, but the cause of the earlier selective failure is not established.
- The full-capacity mixed automatic-SPI benchmark transmitted 55 pixels on all
  six channels (330 total). Adafruit DotStar selected hardware SPI for CH1 and
  software SPI for CH2–CH6. The completed run measured approximately 204.7 ms
  per rendered controller frame (4.89 FPS maximum; 3.91 FPS at the 80% budget),
  missed every scheduled deadline from 10 through 60 FPS, and measured a 1.99×
  clear-then-show penalty. The attached CH4–CH6 panels visibly showed moving
  colored pixels; no visual frame-rate measurement is inferred.

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
`0x33`, and both shunts is Spare `0x32`. With CTRL-RD-01 selected as Mouth and
running this target firmware, the Brain discovered it at `0x31` in a complete
four-device scan. The Development, Spare, and raw ADC levels remain unobserved.

JP1 was confirmed to have a Rev D copper/label orientation error. The intended
interface is one vertical left-column shunt for Eyes and one vertical
right-column shunt for Mouth, with none and both reserved for extra states.
Fabricated Rev D boards only select their resistor paths with horizontal row
shunts. See `hardware/display-controller-rev-d/ERRATA.md` E2.

## Next test

1. Preserve all-six-channel initialization while developing the integrated
   controller firmware and watch for recurrence of selective output loss.
2. Repeat the corrected slow valid-DotStar test across CH1–CH6 on CTRL-RD-02.
3. Audit MCU1B socket pad numbering/orientation against actual KB2040 pin names
   before releasing the next PCB revision.
4. Do not treat the 0/4.7 V static pass as a dynamic LED-array pass.
5. Record the target test's remaining A1/both-shunts ADC levels.
6. Redeploy the corrected standalone heartbeat-input firmware.
7. Connect additional LED modules only after all channel faults pass.
