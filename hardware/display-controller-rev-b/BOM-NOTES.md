# BU-22 Display Controller Rev B BOM notes

The CSV in this directory is the purchasing BOM for the approved Rev B board.
It lists quantities per controller, quantities for two controllers, and a
practical recommended purchase quantity including inexpensive spares.

## Critical substitutions

- U1-U3 must be **74AHCT125** devices in the 3.9 mm SOIC-14 package. AHCT is
  important because the buffers run at 5 V while accepting 3.3 V RP2040 logic.
  Do not substitute a 74HC125 without rechecking its input-high threshold.
- Q1 must have the TO-92 lead order **E-B-C on pins 1-2-3**. The PCB connects
  pad 1 to ground, pad 2 to the base resistor, and pad 3 to the common OE line.
- J8 and J9 are the 1.0 mm JST-SH top-entry footprint commonly used for Qwiic.
  They are small SMD parts and will be the most delicate hand-soldering job.
- The KB2040 requires two 1x13 female 2.54 mm socket rows. Do not solder the
  module directly to the controller board.

## User-supplied parts

- Adafruit KB2040 module
- 5.08 mm power screw terminal
- Six `B4B-XH-A` channel headers per board; 24 are already owned

## Suggested build order

1. Solder all 0805 resistors and capacitors.
2. Solder U1-U3 and the two Qwiic headers.
3. Check for 5 V/GND shorts before adding through-hole parts.
4. Add Q1, LEDs, switches, electrolytic capacitors and connectors.
5. Install the female KB2040 socket rows last, using the module to hold their
   alignment while soldering only if the entire board is unpowered.

## Quantities

The recommended quantities target two assembled display controllers with
spares. For a single controller, use the `Qty per board` column directly.
