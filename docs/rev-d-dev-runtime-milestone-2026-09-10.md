# Rev D development-runtime milestone

Date: 2026-09-10

The complete BU-22 V2 development hardware stack has passed its first stable,
button-driven runtime test:

- Brain perfboard discovered Eyes `0x30`, Mouth `0x31`, VCNL4200 `0x51`, and
  DS3231 `0x68` together and exchanged valid status and display commands.
- Both Rev D display controllers drove their complete development arrays from
  the validated 4 MHz SPI1 path: Eyes `18 x 16` (288 LEDs) and Mouth `15 x 11`
  (165 LEDs).
- Controller TARGET, TEST, and BENDER modes passed, including mode labels,
  line sweeps, module-local serpentine chase, solid colors, and static Bender
  artwork.
- Brain CLOCK, SETTINGS, BENDER, PLAY placeholder, and nested TEST modes run
  from physical buttons without requiring terminal commands.
- The temporary centered 3x5 font, three-second scrolling mode announcements,
  and fixed-position flashing clock colon were exercised on the development
  stack. Persistent settings, UTC RTC storage, North American time zones,
  manual DST, and 12/24-hour display are now implemented for the next detailed
  settings pass.
- Bench-verified Brain button mapping is `D5=MODE`, `D9=ENTER`, `D6=UP`, and
  `D10=DOWN`.

Logging and semantic I2C mirroring are present but disabled by default. The
firmware continues to answer status requests in local display modes and reports
named TARGET, TEST, or BENDER state through the fixed protocol status record.

## Next integration milestone

The next milestone is simulator-to-hardware animation delivery at the planned
10 FPS. Add a simulator development-board target matching the proven `18 x 16`
Eyes and `15 x 11` Mouth geometry while retaining the production-layout target.
Start with independently exported, loopable stored animations:

1. Eyes normal-to-angry-to-normal loop.
2. Mouth talking loop covering the chosen openness shapes.
3. A short combined performance referencing those stored animation IDs before
   adding synchronized audio.

This order validates geometry, pixel mapping, file representation, storage,
content identifiers, and loop timing before audio synchronization adds another
variable.

## Known development limitation

Powering all three RP2040 boards through one USB hub can backfeed or cause macOS
to remount every CIRCUITPY filesystem read-only. A host reboot or full hub power
cycle may be required before deployment. This is a hardware-development issue,
not an animation-protocol failure.
