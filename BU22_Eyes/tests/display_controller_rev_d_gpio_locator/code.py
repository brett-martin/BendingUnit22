"""Empirically locate Rev D CH1-CH4 outputs without assuming socket mapping."""

import time

import board
import digitalio
import supervisor


supervisor.runtime.autoreload = False

HIGH_SECONDS = 3.0
LOW_SECONDS = 1.0
PINS = (
    ("D2", board.D2),
    ("D3", board.D3),
    ("D4", board.D4),
    ("D5", board.D5),
    ("D6", board.D6),
    ("D7", board.D7),
    ("D8", board.D8),
    ("D9", board.D9),
)


def make_output(pin):
    signal = digitalio.DigitalInOut(pin)
    signal.switch_to_output(value=False)
    return signal


print("\nBU-22 REV D GPIO-TO-OUTPUT LOCATOR")
print("Probe one connector signal pin and note which named GPIO makes it HIGH.")

enable = make_output(board.MOSI)
outputs = tuple((name, make_output(pin)) for name, pin in PINS)

for remaining in range(5, 0, -1):
    print("Enabling AHCT outputs in", remaining)
    time.sleep(1)

enable.value = True
print("AHCT outputs enabled")

while True:
    for name, active in outputs:
        for _, signal in outputs:
            signal.value = False
        print("ALL LOW for", LOW_SECONDS, "second")
        time.sleep(LOW_SECONDS)
        active.value = True
        print(name, "HIGH for", HIGH_SECONDS, "seconds; all other candidates LOW")
        time.sleep(HIGH_SECONDS)
        active.value = False
