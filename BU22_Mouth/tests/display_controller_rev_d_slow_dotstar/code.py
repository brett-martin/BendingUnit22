"""Deliberately slow valid DotStar frames on all Rev D output channels."""

import time
import digitalio

import config


VERSION = "0.2-swap-ch1-4"
COLORS = (
    ("RED", (160, 0, 0)),
    ("GREEN", (0, 160, 0)),
    ("BLUE", (0, 0, 160)),
    ("DIM WHITE", (48, 48, 48)),
    ("BLACK", (0, 0, 0)),
)


def make_output(pin):
    output = digitalio.DigitalInOut(pin)
    output.switch_to_output(value=False)
    return output


def set_all(outputs, value):
    for output in outputs:
        output.value = value


def send_bit(clocks, data, value):
    set_all(data, value)
    time.sleep(config.BIT_HALF_PERIOD_SECONDS)
    set_all(clocks, True)
    time.sleep(config.BIT_HALF_PERIOD_SECONDS)
    set_all(clocks, False)


def send_byte(clocks, data, value):
    for shift in range(7, -1, -1):
        send_bit(clocks, data, bool(value & (1 << shift)))


def send_frame(clocks, data, color):
    red, green, blue = color

    # APA102/SK9822 start frame: at least 32 zero bits.
    for _ in range(4):
        send_byte(clocks, data, 0x00)

    # Each pixel is 111 + five-bit global brightness, then B, G, R.
    header = 0xE0 | config.GLOBAL_BRIGHTNESS
    for _ in range(config.PIXELS_PER_CHANNEL):
        send_byte(clocks, data, header)
        send_byte(clocks, data, blue)
        send_byte(clocks, data, green)
        send_byte(clocks, data, red)

    # More than 55/2 end clocks, with data high, safely latches 55 pixels.
    for _ in range(4):
        send_byte(clocks, data, 0xFF)

    set_all(data, False)


print("\nBU-22 REV D SLOW 55-PIXEL DOTSTAR TEST", VERSION)
print("Identical valid frames on CH1 through CH6")
print("DIAGNOSTIC: CH1-CH4 clock/data swapped; CH5-CH6 normal")
print("Nominal clock:", int(1 / (2 * config.BIT_HALF_PERIOD_SECONDS)), "Hz")
print("Move the same known-good mouth tile between channel connectors.")

output_enable = digitalio.DigitalInOut(config.BUFFER_ENABLE)
output_enable.switch_to_output(value=False)
clocks = tuple(make_output(pair[0]) for pair in config.CHANNEL_PINS)
data = tuple(make_output(pair[1]) for pair in config.CHANNEL_PINS)
print("AHCT outputs: DISABLED")

for remaining in range(config.SAFE_START_SECONDS, 0, -1):
    print("Enabling outputs in", remaining)
    time.sleep(1)

# Prepare and latch black before enabling the level-shifter outputs.
send_frame(clocks, data, (0, 0, 0))
output_enable.value = True
send_frame(clocks, data, (0, 0, 0))
print("AHCT outputs: ENABLED after valid black frame")

while True:
    for name, color in COLORS:
        started = time.monotonic()
        send_frame(clocks, data, color)
        elapsed = time.monotonic() - started
        print(name, "frame sent in %.2f seconds" % elapsed)
        time.sleep(config.COLOR_HOLD_SECONDS)
