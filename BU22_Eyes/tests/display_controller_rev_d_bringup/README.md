# Display Controller Rev D bring-up

Temporary CircuitPython firmware for the first hand-assembled BU-22 universal
display-controller PCBs. It verifies the controller hardware; it is not the
production Eyes or Mouth firmware.

## Before loading firmware

1. Power the bare controller without the KB2040 and verify its rails first.
2. Install the KB2040 only after its socket voltages and polarity pass.
3. Current-limit the external 5 V supply.
4. Begin with one known-good four-pixel SK9822/APA102-compatible strip.
5. Verify the strip input order is `GND, CLOCK, DATA, +5V`.
6. Set `PIXELS_PER_CHANNEL` in `config.py` to the connected strip length.

Do not power LED arrays from the computer USB port.

## Install

Copy `code.py` and `config.py` to the KB2040 `CIRCUITPY` drive. Install the
`adafruit_dotstar` library and its dependencies in `lib/`.

The suite waits five seconds with the AHCT buffers disabled, establishes a
black frame, then repeatedly runs:

1. TEST button, address ADC, and optional heartbeat observation
2. Channel identity/crosstalk
3. First/last pixel and forward pixel order
4. RGB and mixed-color order
5. Conservative global-brightness ladder
6. Six-channel 10 FPS timing/load test
7. Commanded blackout and output-enable cycle

The TEST button repeats the suite immediately at the final pause. RESET should
restart the board and reproduce the fail-dark five-second startup interval.

The suite cannot prove I2C target behavior by itself. Test I2C separately with
the Brain after both controllers pass standalone electrical bring-up.
