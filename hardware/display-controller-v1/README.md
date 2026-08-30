# BU-22 Universal Display Controller V1

This is the hand-assembled prototype controller for either the BU-22 eyes or
mouth. Two identical boards are intended for the first complete bench system.
Pixel hardware is external: six independent SK9822/APA102-compatible LED
strings connect through four-pin JST-XH cables.

## Prototype goals

- Validate full, pixel-accurate eye and mouth animations before ordering dense
  assembled LED PCBs.
- Keep expensive LED assemblies electrically simple and reusable.
- Use through-hole parts wherever practical so five bare PCBs can be ordered
  and at least two assembled by hand.
- Keep display power distribution outside the Brain. The controller receives a
  fused 5 V branch and distributes it to its six display connectors.
- Remain usable as either Eyes (`0x30`) or Mouth (`0x31`) by changing one
  address jumper.

## Board envelope and placement

- Two-layer FR-4, 140 mm x 65 mm, with lightly rounded 3 mm corners.
- Four M3 mounting holes, 5 mm from each corner.
- Six outward-facing JST-XH outputs along the top edge.
- 5 V screw terminal, local bulk capacitors, power LED, and KB2040 USB access
  on the left side.
- Heartbeat indicator, TEST, and RESET controls along the lower-left edge.
- Four-position address selection and I2C connections along the lower edge.
- No components or connectors on the bottom side.
- Right-side silkscreen equipment mark: `BENDING UNIT 22`, `DISPLAY CONTROL
  MODULE`, and canonical serial number `2716057`, accompanied by a small
  heart/smile factory emblem no larger than the 10 mm bulk capacitor.

The 65 mm height is provisional. It fits inside the approximately 75 mm visor
opening with more than 5 mm clearance at the top and bottom. It must still be
checked against the physical print before fabrication.

## Interfaces

### LED outputs J1-J6

All six channels are independent. Pin numbering is printed on the PCB.

| Pin | Signal |
|---:|---|
| 1 | +5V display power |
| 2 | GND |
| 3 | DATA (5 V logic) |
| 4 | CLOCK (5 V logic) |

The footprint uses the common 2.50 mm XH pin row shared by the vertical
`B4B-XH-A` and right-angle `S4B-XH-A` headers. Connector body clearance must be
confirmed for the exact purchased parts before ordering.

### I2C input

`I2C IN` has both a Qwiic socket and a parallel 1x4 2.54 mm test header.
The Brain-provided 3.3 V is exposed only at the test header and is deliberately
not connected to the controller MCU. The controller uses a custom I2C object on
the socketed TX/RX pins; the KB2040's onboard STEMMA QT connector remains free.

| Signal | Destination |
|---|---|
| GND | Controller ground |
| 3V3 from Brain | Test header only |
| SDA | KB2040 TX / GP0 |
| SCL | KB2040 RX / GP1 |

No I2C pull-up resistors are fitted. The Brain is the only pull-up source.

### I2C through

`I2C THRU` carries GND, SDA, and SCL. Its Qwiic 3.3 V pin is intentionally not
connected and is labeled `NO POWER`. This permits display-controller daisy
chaining without using a display MCU as an accessory power source.

### Service input

A single four-pin JST-PH service connector is aligned vertically beside the
I2C test header. It exposes GND, the RTC-derived HEARTBEAT input, TEST, and
RESET. There is no duplicate heartbeat header.

| Pin | Signal |
|---:|---|
| 1 | GND |
| 2 | HEARTBEAT |
| 3 | TEST |
| 4 | RESET |

All socket-row GPIOs are already assigned in this six-channel design, so TEST
and RESET are exposed as useful service signals rather than claiming unused
GPIOs that do not exist.

## KB2040 GPIO assignment

This preserves the six-channel wiring proven on the breadboard.

| Function | KB2040 pin |
|---|---|
| CH1 clock / data | D3 / D2 |
| CH2 clock / data | D5 / D4 |
| CH3 clock / data | D7 / D6 |
| CH4 clock / data | D9 / D8 |
| CH5 clock / data | A0 / SCK |
| CH6 clock / data | A2 / A1 |
| I2C SCL / SDA | RX / TX |
| Address jumper network | A3 |
| Heartbeat input | D10 |
| Test button | MISO |
| Buffer enable | MOSI |

### Address selection

A 2x2 address header provides two independent vertical shunt columns while
consuming only the analog-capable A3 pin. A resistor network produces four
distinct ADC levels for firmware to decode. The physical user interface is:

| Left/Eyes column | Right/Mouth column | Intended role/address |
|---|---|---|
| Closed | Open | Eyes `0x30` |
| Open | Closed | Mouth `0x31` |
| Open | Open | Development `0x33` |
| Closed | Closed | Spare display `0x32` |

Display Controller Rev D does not implement this orientation correctly; its
fabricated copper requires horizontal-row shunts as a temporary workaround.
See `hardware/display-controller-rev-d/ERRATA.md` E2.

The ADC thresholds must be verified on assembled hardware before this becomes
the production address scheme.

## Fail-dark behavior

The three AHCT125 output-enable pins are pulled high at 5 V, disabling every
LED signal during reset. A 2N3904 controlled by KB2040 MOSI pulls `OE_N` low
only after firmware has initialized and sent a black frame. The 5 V enable net
never connects directly to a 3.3 V GPIO.

No separate 5 V sense is required in Revision A. With display power absent the
AHCT devices are unpowered. When 5 V appears, its hardware pull-up immediately
holds `OE_N` disabled until firmware explicitly enables the outputs.

## Power and service rules

- J7 accepts regulated 5 V through a 5.08 mm two-pin screw terminal.
- The external 5 V branch is fused outside this PCB.
- The controller powers the KB2040 through `RAW` and powers all six LED ports.
- Do not power LED strips from a computer USB port.
- During early bring-up, disconnect I2C/heartbeat before USB-programming an
  otherwise unpowered Brain. Simultaneous wall power and USB must be validated
  before treating it as a supported service mode.

## Status and controls

- Green 3 mm LED: external 5 V present.
- Red 3 mm LED: hardware heartbeat input.
- TEST button: local diagnostic-mode override.
- RESET button: KB2040 reset.
- Two address shunts select Eyes, Mouth, Spare, or Development addresses.

## Fabrication status

Revision A is an engineering layout, not yet released for ordering. Routing is
in progress: the 5 V distribution network, rear ground plane, twelve
resistor-to-display output runs, and the first clean automatic signal-routing
pass are complete. Forty-one ratsnest connections remain for deliberate manual
routing around the dense MCU/buffer/control area. Before fabrication:

1. Measure the actual 5.08 mm screw terminal body.
2. Confirm the exact Adafruit Qwiic connector footprint/part number on hand.
3. Check the 140 x 65 mm outline against the physical visor.
4. Complete routing and obtain a clean KiCad DRC.
5. Print the board 1:1 and physically place the KB2040, DIP sockets, XH
   connectors, and terminal on the paper check.
