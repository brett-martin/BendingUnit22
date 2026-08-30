# Display Controller Rev D scan-only I2C target

Minimal fail-dark target test for confirming that a Brain can discover a Rev D
controller over I2C. It does not initialize any SK9822/APA102 clock or data pin
and holds the AHCT buffers disabled for the entire run.

## Address selection — Rev D workaround

Rev D has a known JP1 copper/label orientation error. Its `EYES` and `MOUTH`
labels imply vertical column shunts, but fabricated boards only select resistor
levels with horizontal row shunts. See
`hardware/display-controller-rev-d/ERRATA.md` E2. The mapping below is only the
Rev D test workaround; it is not the desired next-revision user interface.

The A3 resistor network is decoded at startup:

| A1 shunt | A0 shunt | Role | Address | Nominal ADC |
|---|---|---|---:|---:|
| Open | Open | Development | `0x33` | 65535 |
| Open | Closed | Mouth | `0x31` | 32768 |
| Closed | Open | Eyes | `0x30` | 43690 |
| Closed | Closed | Spare display | `0x32` | 26214 |

Thresholds are midpoints between nominal levels. Confirm the printed raw ADC
value on assembled hardware before treating all four selections as validated.
Changing shunts requires a controller reset because the address is selected
only at startup.

## Wiring

Power both boards down before connecting:

- Brain GND to controller GND
- Brain SDA to controller SDA / KB2040 TX
- Brain SCL to controller SCL / KB2040 RX
- Do not connect the boards' 5 V rails

The controller may use external regulated 5 V while the Brain uses USB. This
keeps the Brain USB serial console available for the `s` scan command.

## Install

Confirm `boot_out.txt` identifies the mounted board as an Adafruit KB2040, then
copy this test's `code.py` and `config.py` to that controller's `CIRCUITPY`.
Do not copy these files while the Brain Feather is the mounted `CIRCUITPY`.
