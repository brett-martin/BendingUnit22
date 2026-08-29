# BRAIN-PERF-01 bring-up record

Last updated: 2026-08-29

## Identity

- Assembly: BU-22 Brain prototype perfboard
- MCU: Adafruit Feather RP2040
- Test source: `BU22_Brain/tests/brain_board_bringup/`

## Status

- Board assembly has been reported complete.
- Basic continuity checks have been reported as passing.
- The Feather identifies as `adafruit_feather_rp2040`, UID
  `DF6548405F63432D`, under CircuitPython 10.2.1.
- The powered I2C scan found the VCNL4200 at `0x51` and DS3231 at `0x68`.
- Configuring the DS3231 SQW output for 1 Hz produced nine transitions in 4.5
  seconds, with measured edge intervals of approximately 0.498–0.501 seconds.
- The RTC was set once from the Mac's local wall clock to
  `2026-08-29 11:24:03`, with no timezone or DST conversion. The subsequent
  read matched, and the RTC lost-power flag cleared.
- All seven buttons reported released, Audio FX ACT reported idle/high, and the
  sensor input reported high during the static input-state check. Button
  press/release operation has not yet been observed.
- Initial named-button testing showed a one-position firmware offset: the
  physical Mode control reported as Button 5, Enter reported as Mode, Up
  reported as Enter, and Down reported as Up. Firmware was reordered from
  those observations so Mode, Enter, Up, and Down use D10, D9, D6, and D5,
  respectively. The function connected to D4 has not yet been identified.
- Retesting confirmed that Mode, Enter, Up, and Down now report their correct
  names in the serial console.
- The Audio FX board returned a list of 14 WAV files, `T00` through `T13`. It
  accepted the play-track-0 command and replied that it started `T00.WAV`.
  Audible speaker output has not yet been confirmed.
- The test firmware now mirrors the RTC SQW level in red on the Feather
  NeoPixel.
  Visible synchronized blinking has not yet been confirmed at the bench.

## Planned checks

- External 5 V versus USB power isolation
- I2C pull-up electrical measurements
- Visible NeoPixel synchronization with the DS3231 SQW heartbeat
- Button press/release operation for all seven buttons
- Antenna output
- Audible Audio FX speaker output
- Sensor input transition
- Eyes and Mouth controller discovery after their standalone tests pass
