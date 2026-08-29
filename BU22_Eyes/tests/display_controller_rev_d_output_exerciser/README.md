# Display Controller Rev D output exerciser

Slow direct-GPIO test for measuring all six buffered clock and data outputs
before connecting LED arrays. It uses the exact Rev D PCB map and does not use
the DotStar library.

## Safety

- Do not connect LED arrays during this test.
- Current-limit the external 5 V supply.
- Verify `LOGIC_5V` at each AHCT125 before enabling outputs.
- Confirm `boot_out.txt` identifies the mounted board as the controller KB2040
  before copying the test.

The test holds the AHCT buffers disabled for five seconds, initializes all 12
signal GPIOs low, and then enables the buffers.

## Repeating phases

Each phase lasts two seconds and applies to every channel simultaneously:

| Phase | All clocks | All data |
|---|---|---|
| 0 | Low | Low |
| 1 | High | Low |
| 2 | Low | High |
| 3 | High | High |

Measure each channel connector relative to its ground pin. Expected buffered
levels are near 0 V when low and near `LOGIC_5V` when high. Record the actual
clock and data levels for CH1 through CH6; do not infer unmeasured channels.

## Install

Copy this directory's `code.py` and `config.py` to the controller KB2040's
`CIRCUITPY` drive. CircuitPython reloads automatically.
