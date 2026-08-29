# BU-22 Brain Perfboard V1

Prototype carrier for the BU-22 Brain. This version is intended for a 24 x 56
hole stripboard with copper strips running in the 56-hole direction.

## Design intent

- Adafruit Feather RP2040 is socketed and removable.
- Adafruit Audio FX Sound Board + 2x2 W Amp, 16 MB is socketed and removable.
- Adafruit DS3231 Precision RTC is socketed and removable.
- No display LED current passes through this board.
- The Feather is powered from either USB-C or an external regulated 5 V input.
- External 5 V is isolated from Feather USB VBUS by a Schottky diode.
- The RTC SQW output is the system heartbeat source.
- All external wiring uses 2.54 mm headers except the Feather's built-in Qwiic
  connector.

## Board orientation

View all coordinates from the component side, with the 56-hole dimension left
to right and the long copper strips also running left to right. Columns are
numbered 1-56. Rows are lettered A-X.

The recommended placement is shown in `component-layout.svg`. The Audio FX
board occupies the far-left position. The Feather is central so its GPIO is
close to the RTC, heartbeat circuitry, buttons, antenna, sensor, and spare-I/O
headers on the right. Both long modules are rotated so their long axes run from
top to bottom, putting each pin on a different copper strip. Their USB
connectors remain exposed at the lower board edge. The RTC SQW/heartbeat area
sits directly above the button header.

The exact socket coordinates, copper cuts, and point-to-point jumper list are
in `cuts-and-jumpers.md`. Do not infer copper-side coordinates directly from
the component-side drawing: the copper side is horizontally mirrored.

For readable assembly, the wiring is also separated into four maps:

- `brain-layer-power.svg`
- `brain-layer-audio-control.svg`
- `brain-layer-buttons.svg`
- `brain-layer-rtc-heartbeat.svg`
- `brain-layer-antenna-sensor.svg`

The spare header is intentionally omitted from these maps for now.
These separated maps are the primary assembly references; `stripboard-map.svg`
is retained only as a combined connectivity overview.

## Functional wiring

### Power

| Net | Connection |
|---|---|
| EXT_5V | External regulated 5 V screw terminal/header positive |
| GND | External input negative, Feather GND, Audio FX GND, RTC GND, all headers |
| LOGIC_5V | D1 cathode, Feather USB pin, Audio FX VIN |
| 3V3 | Feather 3.3 V, RTC VIN, heartbeat pull-up, sensor/header logic power |

Power path:

`EXT_5V -> D1 (1N5817) -> LOGIC_5V -> Feather USB pin`

The diode's banded cathode faces `LOGIC_5V` / the Feather. When USB-C is
connected, D1 prevents USB power from flowing back into the external 5 V
terminal. The Audio FX board is powered from `LOGIC_5V`, so it is available
under either USB or external power.

Do not connect an external 5 V supply to the Feather 3.3 V pin or BAT pin.

### I2C and RTC

| Signal | Feather | RTC | External |
|---|---|---|---|
| SDA | SDA / GP2 | SDA | Feather Qwiic |
| SCL | SCL / GP3 | SCL | Feather Qwiic |
| 3.3 V | 3V | VIN | Feather Qwiic |
| Ground | GND | GND | Feather Qwiic |
| Heartbeat | D13 / GP13 | SQW | J_HB pin 1 |

R_HB is an optional 10 kOhm pull-up from `HEARTBEAT` to 3.3 V. Populate it for
the DS3231 SQW open-drain output unless the exact RTC module is confirmed to
provide its own SQW pull-up. The RTC's SDA/SCL pull-ups are separate and do not
pull up SQW.

### Audio FX UART

| Signal | Feather | Audio FX |
|---|---|---|
| Brain TX | TX / GP0 | RX |
| Brain RX | RX / GP1 | TX |
| Activity | D24 / GP24 | ACT (active low) |
| Reset | D25 / GP25 | RST (active low) |
| UART mode | Ground | UG |
| Power | LOGIC_5V | VIN |
| Ground | Ground | Ground |

The amplifier version's speaker outputs go directly to the two speaker
headers. Do not tie either speaker lead to ground.

### Buttons

J_BUTTONS is an 8-pin 2.54 mm header. The button daughterboard shares ground;
firmware uses internal pull-ups.

| Pin | Signal | Feather |
|---:|---|---|
| 1 | Ground | GND |
| 2 | Down / logical button 4 | D4 / GP6 |
| 3 | Up / logical button 3 | D5 / GP7 |
| 4 | Enter / logical button 2 | D6 / GP8 |
| 5 | Mode / logical button 1 | D9 / GP9 |
| 6 | Button 5 | D10 / GP10 |
| 7 | Button 6 | D11 / GP11 |
| 8 | Button 7 | D12 / GP12 |

### Other I/O

| Header | Pinout | Feather |
|---|---|---|
| J_HB | 1 Heartbeat, 2 Ground | D13 / GP13 |
| J_ANT | 1 Red, 2 Green, 3 Blue/spare, 4 Ground | A0/GP26, A1/GP27, A2/GP28 |
| J_SENSOR | 1 3.3 V, 2 Ground, 3 Signal, 4 Spare | A3/GP29, spare D25/GP25 if audio reset is omitted |
| J_SPARE | 1 SCK/GP18, 2 MO/GP19, 3 MI/GP20, 4 D25/GP25, 5 Ground | as labeled |

Use a resistor or transistor driver appropriate to the final antenna LED. The
header signals themselves are 3.3 V GPIO and are not intended to power a high
current LED directly.

## Parts added by this carrier

| Ref | Part | Notes |
|---|---|---|
| D1 | 1N5817 Schottky diode | External 5 V isolation |
| R_HB | 10 kOhm, through-hole | Optional SQW pull-up to 3.3 V |
| C1 | 100 uF, >= 10 V electrolytic | Near external input / Audio FX VIN |
| C2 | 100 nF ceramic | Near Audio FX VIN |
| J_PWR | 2-pin screw terminal or 2.54 mm header | 5 V, Ground |
| J_BUTTONS | 1x8 2.54 mm header | Ground + seven buttons |
| J_HB | 1x2 2.54 mm header | Heartbeat + ground |
| J_ANT | 1x4 2.54 mm header | RGB/spare + ground |
| J_SENSOR | 1x4 2.54 mm header | 3.3 V, ground, signal, spare |
| J_SPARE | 1x5 2.54 mm header | Spare GPIO + ground |
| SPK_L, SPK_R | 1x2 headers or screw terminals | Floating amplified speaker pairs |

## Assembly sequence

1. Place the unpowered modules over the printed plan and confirm their real
   header spacing before drilling/cutting any track.
2. Mark the component-side board origin and transfer all socket positions.
3. Fit female sockets and verify that all three modules insert without force.
4. Make strip cuts beneath socket regions before installing sockets.
5. Meter every adjacent socket pin for isolation.
6. Install wire links and passive parts, but leave all modules removed.
7. Verify D1 polarity and continuity from external 5 V to LOGIC_5V.
8. Apply current-limited 5 V and verify LOGIC_5V before inserting modules.
9. Insert only the Feather; test USB and external-power switchover.
10. Insert RTC and verify I2C plus SQW heartbeat.
11. Insert Audio FX last; test UART, ACT, reset, then speakers at low volume.

## Important physical check

The layout intentionally treats the RTC and Audio FX modules as socketed
rectangles. Before soldering, place the exact boards on the stripboard and
transfer their real header locations. Adafruit revisions preserve electrical
pin functions but the available header holes and USB/terminal hardware can
change the practical socket footprint.
