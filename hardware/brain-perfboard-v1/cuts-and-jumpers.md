# BU-22 Brain Stripboard Cut and Jumper Plan

This is the exact first-pass hole map for a 56-column by 24-row stripboard.
Coordinates are always viewed from the **component side**:

- Columns: `1` through `56`, left to right
- Rows: `A` through `X`, top to bottom
- Copper strips: run left to right
- USB edge: row `X`

When working on the copper side, mirror the columns. Mark the component-side
origin permanently before turning the board over.

## Socket coordinates

### Audio FX 16 MB + 2x2 W amplifier - far left

The Audio FX module is rotated with its USB connector toward row X.

| Module header | Stripboard column | Occupied rows |
|---|---:|---|
| GPIO / trigger row | 4 | H through U |
| Control / UART row | 12 | H through U |

Audio pin map:

| Row | Col 4 GPIO header | Col 12 control header |
|---|---|---|
| H | GND | GND |
| I | ACT | L line out |
| J | Trigger 10 | R line out |
| K | Trigger 9 | GND |
| L | Trigger 8 | CS - do not connect |
| M | Trigger 7 | Volume - |
| N | Trigger 6 | Volume + |
| O | Trigger 5 | UG - connect to GND for UART |
| P | Trigger 4 | RX - from Brain TX |
| Q | Trigger 3 | TX - to Brain RX |
| R | Trigger 2 | PB |
| S | Trigger 1 | USB BUS - leave unconnected |
| T | Trigger 0 | GND |
| U | RST | VIN / LOGIC_5V |

The module's built-in speaker terminal blocks remain accessible; the carrier
does not duplicate them.

### Feather RP2040 Brain - center

The Feather is rotated with USB-C toward row X.

| Feather header | Stripboard column | Occupied rows |
|---|---:|---|
| 1x16 / analog side | 17 | F through U |
| 1x12 / digital side | 25 | F through Q |

| Row | Col 17, 1x16 side | Col 25, 1x12 side |
|---|---|---|
| F | D4 / Button 1 | SDA |
| G | TX / GP0 | SCL |
| H | RX / GP1 | D5 / Button 2 |
| I | MISO / GP20 | D6 / Button 3 |
| J | MOSI / GP19 | D9 / Button 4 |
| K | SCK / GP18 | D10 / Button 5 |
| L | D25 / Audio reset | D11 / Button 6 |
| M | D24 / Audio activity | D12 / Button 7 |
| N | A3 / GP29 / Sensor | D13 / Heartbeat input |
| O | A2 / GP28 / Antenna blue | USB / VBUS |
| P | A1 / GP27 / Antenna green | EN |
| Q | A0 / GP26 / Antenna red | BAT |
| R | GND | - |
| S | 3.3 V | - |
| T | 3.3 V | - |
| U | RESET | - |

### DS3231 Precision RTC - upper right

Use the original Adafruit header-only DS3231 breakout orientation. The 1x8
header is vertical at column 31.

| Coordinate | RTC signal |
|---|---|
| 31-E | 3.3 V / VIN |
| 31-F | GND |
| 31-G | SCL |
| 31-H | SDA |
| 31-I | VBAT - no carrier connection |
| 31-J | 32 kHz - no carrier connection |
| 31-K | SQW / HEARTBEAT |
| 31-L | RTC reset - no carrier connection |

If the actual RTC is the newer STEMMA QT revision, do not force it into this
socket. Use the Feather Qwiic connector and a two-pin SQW/GND pigtail instead.

## External headers

All headers are vertical so every pin begins on a different copper strip.

| Header | Coordinates, top to bottom | Pin order |
|---|---|---|
| J_BUTTONS | 38-N through 38-U | GND, B1, B2, B3, B4, B5, B6, B7 |
| J_HEART | 42-N through 42-O | HEARTBEAT, GND |
| J_ANT | 46-N through 46-Q | RED, GREEN, BLUE/SPARE, GND |
| J_SENSOR | 50-N through 50-Q | 3.3 V, GND, SIGNAL, SPARE |
| J_SPARE | 54-N through 54-R | GP18, GP19, GP20, GP25/shared, GND |
| J_POWER | 54-D through 54-E | External +5 V, GND |

`GP25/shared` is connected to Audio FX reset in this revision. It is exposed
for measurement or alternate firmware, not for simultaneous unrelated use.

## Copper cuts

### Continuous isolation grooves

Cut and verify these copper strips before installing sockets. A narrow rotary
tool groove is acceptable for the continuous cuts; otherwise use a proper
stripboard cutter at every listed row.

| Cut column | Rows | Purpose |
|---:|---|---|
| 14 | A-X | Isolate Audio FX zone from Feather zone |
| 27 | A-X | Isolate Feather zone from RTC/I/O zone |
| 35 | D-U | Isolate RTC zone from button zone |
| 40 | D-U | Isolate buttons from heartbeat header |
| 44 | D-U | Isolate heartbeat from antenna header |
| 48 | D-U | Isolate antenna from sensor header |
| 52 | D-U | Isolate sensor from spare/power header |

### Cuts between module socket rows

| Cut column | Rows | Purpose |
|---:|---|---|
| 8 | H-U | Separate the two Audio FX socket rows |
| 21 | F-U | Separate the two Feather socket rows |

After cutting, check every pair of adjacent zones with continuity mode. There
must be no continuity across any cut.

## Insulated jumper list

The notation `12-Q -> 17-H` means an insulated wire from column 12, row Q to
column 17, row H.

## Shared power buses

The separated layer drawings use three deliberately simple horizontal buses.
These supersede the earlier daisy-chain ground depiction:

| Bus | Row and extent | Required bridges |
|---|---|---|
| Protected LOGIC_5V | Row C, columns 3-51 | Bridge the cuts at columns 14 and 27 |
| 3.3 V | Row V, columns 15-51 | Bridge the cut at column 27 |
| Ground | Row W, columns 3-55 | Bridge the cuts at columns 14 and 27 |

The bridges are short insulated wires placed around the cut holes. Never rely
on a cut copper strip to carry a bus through the cut.

Connect the following points vertically to the buses:

| Bus | Connection points |
|---|---|
| LOGIC_5V | Audio VIN 12-U; Feather VBUS 25-O |
| 3.3 V | Feather 17-S; RTC 31-E; Sensor 50-N; heartbeat pull-up |
| Ground | Audio 4-H and 12-T; Feather 17-R; RTC 31-F; Buttons 38-N; Heartbeat 42-O; Antenna 46-Q; Sensor 50-O; Power 54-E |

### Audio UART/control

| From | To | Net |
|---|---|---|
| 12-Q | 17-H | Audio TX -> Brain RX |
| 12-P | 17-G | Brain TX -> Audio RX |
| 4-I | 17-M | Audio ACT -> Brain D24 |
| 4-U | 17-L | Brain D25 -> Audio RST |
| 12-O | GND bus | Audio UG held low for UART mode |
| 12-U | LOGIC_5V | Audio VIN |
| 12-T | GND bus | Audio ground |
| 4-H | GND bus | Audio ground |

### RTC and I2C

| From | To | Net |
|---|---|---|
| 31-E | 17-S | RTC 3.3 V |
| 31-F | GND bus | RTC ground |
| 31-G | 25-G | RTC SCL -> Feather SCL |
| 31-H | 25-F | RTC SDA -> Feather SDA |
| 31-K | 25-N | RTC SQW -> Feather heartbeat input |
| 31-K | 42-N | RTC SQW -> external heartbeat |

Install the optional heartbeat pull-up below the RTC:

- jumper `31-K -> 33-N`
- 10 kOhm resistor from `33-N -> 33-R`
- jumper `33-R -> 17-S` (3.3 V)

The DS3231 SQW output is open drain and requires a pull-up. This resistor is
independent of the RTC board's SDA/SCL pull-ups.

### Buttons

| Header coordinate | Feather coordinate | Net |
|---|---|---|
| 38-N | GND bus | Button common |
| 38-O | 17-F | Button 1 / D4 |
| 38-P | 25-H | Button 2 / D5 |
| 38-Q | 25-I | Button 3 / D6 |
| 38-R | 25-J | Button 4 / D9 |
| 38-S | 25-K | Button 5 / D10 |
| 38-T | 25-L | Button 6 / D11 |
| 38-U | 25-M | Button 7 / D12 |

### Antenna and sensor

| Header coordinate | Feather coordinate | Net |
|---|---|---|
| 46-N | 17-Q | Antenna red / A0 |
| 46-O | 17-P | Antenna green / A1 |
| 46-P | 17-O | Antenna blue or spare / A2 |
| 46-Q | GND bus | Antenna ground |
| 50-N | 17-S | Sensor 3.3 V |
| 50-O | GND bus | Sensor ground |
| 50-P | 17-N | Sensor signal / A3 |
| 50-Q | 17-I | Sensor spare / GP20 |

### Spare header

| Header coordinate | Feather coordinate | Net |
|---|---|---|
| 54-N | 17-K | GP18 / SCK |
| 54-O | 17-J | GP19 / MOSI |
| 54-P | 17-I | GP20 / MISO |
| 54-Q | 17-L | GP25 / shared Audio reset |
| 54-R | GND bus | Ground |

## Power wiring

1. Install D1, a 1N5817 Schottky diode, with its **anode** connected to
   `J_POWER +5 V` at 54-D.
2. The banded **cathode** lands at `51-D` and becomes `LOGIC_5V`.
3. Connect `51-D -> 51-C`, feeding the protected LOGIC_5V bus on row C.
4. Bridge the row-C cuts at columns 27 and 14 with insulated wire.
5. Connect the LOGIC_5V bus to Feather USB/VBUS at 25-O and Audio VIN at 12-U.
6. Connect J_POWER ground at 54-E to the row-W ground bus.
7. Connect Feather ground at 17-R to the row-W ground bus.
8. Place 100 uF from LOGIC_5V to ground near the Audio FX module.
9. Place 100 nF from LOGIC_5V to ground near Audio VIN.

This matches the display-controller isolation concept: external 5 V can power
the Feather through its USB/VBUS pin, while USB-C at the Feather supplies the
logic rail without feeding the external input through D1.

## Before inserting modules

1. Confirm every copper cut visually under magnification.
2. Check resistance from LOGIC_5V to ground; it must not be a short.
3. Check that no Audio socket pin is shorted to the opposing Audio socket row.
4. Check that no Feather socket pin is shorted to the opposing Feather row.
5. Apply current-limited 5 V with all modules removed.
6. Verify diode polarity and LOGIC_5V voltage.
7. Remove power, insert only the Feather, and test external/USB operation.
8. Add RTC, then Audio FX, one module at a time.
