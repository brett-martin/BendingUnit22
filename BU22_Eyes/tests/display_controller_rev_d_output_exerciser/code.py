"""Slow, meter-friendly output exerciser for Display Controller Rev D."""

import time
import digitalio

import config


VERSION = "0.1"


def make_output(pin):
    output = digitalio.DigitalInOut(pin)
    output.switch_to_output(value=False)
    return output


def set_all(clocks, data, clock_value, data_value):
    for output in clocks:
        output.value = clock_value
    for output in data:
        output.value = data_value


def run_phase(clocks, data, name, clock_value, data_value):
    set_all(clocks, data, clock_value, data_value)
    print(
        "%s: CLOCK=%s DATA=%s for %.1f seconds"
        % (
            name,
            "HIGH" if clock_value else "LOW",
            "HIGH" if data_value else "LOW",
            config.PHASE_SECONDS,
        )
    )
    time.sleep(config.PHASE_SECONDS)


print("\nBU-22 DISPLAY CONTROLLER REV D OUTPUT EXERCISER", VERSION)
print("No LED arrays should be connected.")

# Hold AHCT outputs disabled before initializing any signal GPIO.
output_enable = digitalio.DigitalInOut(config.BUFFER_ENABLE)
output_enable.switch_to_output(value=False)
print("AHCT outputs: DISABLED")

clocks = tuple(make_output(pair[0]) for pair in config.CHANNEL_PINS)
data = tuple(make_output(pair[1]) for pair in config.CHANNEL_PINS)
set_all(clocks, data, False, False)

for remaining in range(config.SAFE_START_SECONDS, 0, -1):
    print("Enabling outputs in", remaining)
    time.sleep(1)

output_enable.value = True
print("AHCT outputs: ENABLED")

while True:
    run_phase(clocks, data, "PHASE 0", False, False)
    run_phase(clocks, data, "PHASE 1", True, False)
    run_phase(clocks, data, "PHASE 2", False, True)
    run_phase(clocks, data, "PHASE 3", True, True)
