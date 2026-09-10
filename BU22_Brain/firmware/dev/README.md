# BU-22 Brain stable development runtime

This button-driven runtime replaces serial commands for normal development.
Copy `code.py`, `config.py`, and generated `animation_catalog.py` to the Brain
`CIRCUITPY` root and copy the
repository `common` directory to `CIRCUITPY/common`. Install `adafruit_ds3231`
and its dependencies.

The Brain waits ten seconds before scanning I2C. MODE cycles `CLOCK`,
`SETTINGS`, `BENDER`, `PLAY`, and `TEST`.

PLAY begins with exported performances, followed by every named Eye and Mouth
animation. UP/DOWN browse the combined list and ENTER runs the selection. A
performance uses its millisecond timeline to send locally retimed animation
events to each controller and mapped `T00.WAV`-style commands to the Audio FX
board. The selection persists while changing modes.

BENDER selects non-repeating animations across both display catalogs. The
Brain sends one animation at a time and uses its exported frame count and
global FPS to wait for completion, followed by a random one-to-four-second
pause. This keeps both controllers under one scheduler and leaves room for
later coordinated expressions, audio, and antenna events.

Both the controller data and this Brain index are regenerated from one
simulator export with:

```sh
python3 tools/build_display_catalog.py \
  '../Catalog Exports' BU22_Display/firmware/dev_controller/catalog.py \
  --brain-output BU22_Brain/firmware/dev/animation_catalog.py
```

The current bench-verified development-board button mapping is `D5=MODE`,
`D9=ENTER`, `D6=UP`, and `D10=DOWN`.

SETTINGS follows `DST`, `ZONE`, `12/24 HOUR`, `HOUR`, `MINUTE`, conditional
`AM/PM`, `COLON`, and `EXIT`. UP/DOWN adjust the current item and ENTER advances.
The RTC stores UTC; the display converts to the selected Eastern, Central,
Mountain, or Pacific zone plus the manual DST setting. Settings persist in
RP2040 NVM. Time changes remain staged until the editor reaches COLON, and an
incomplete edit is discarded when MODE interrupts or the 60-second timeout
returns to CLOCK. Brightness remains at the development firmware default.

Within TEST, UP/DOWN select RTC or ANTENNA and ENTER starts/stops the selected
test. RTC displays live time with a locally flashing colon. ANTENNA performs
three nonblocking cycles of red, off, green, off, blue, off using 2-second
colors and 1-second off intervals.

The CLOCK display and RTC test both request a flashing colon from the display
controller. This makes a stopped/non-updating display visually distinct, but it
does not by itself prove that the DS3231 time is accurate. The Brain configures
the RTC SQW output for 1 Hz during initialization; direct SQW validation can be
added to the later expanded TEST menu.

`LOGGING` and `MIRROR_I2C` default to false. When enabled, logging reports
mode changes and semantic I2C traffic only; it never prints per-pixel or
per-frame animation data.
