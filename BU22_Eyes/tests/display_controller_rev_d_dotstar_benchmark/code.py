"""Measure CircuitPython DotStar output time for every Rev D channel."""

import time
import digitalio

import adafruit_dotstar

import config


VERSION = "0.1"
BLACK = (0, 0, 0)
TEST_COLOR = (80, 20, 0)


def make_channels():
    channels = []
    for clock, data in config.CHANNEL_PINS:
        channels.append(
            adafruit_dotstar.DotStar(
                clock,
                data,
                config.PIXELS_PER_CHANNEL,
                brightness=config.GLOBAL_BRIGHTNESS,
                auto_write=False,
            )
        )
    return tuple(channels)


def output_backend(channel):
    # The Adafruit library stores a busio.SPI object in _spi when the requested
    # pins support hardware SPI. A None value selects its software GPIO path.
    return "hardware SPI" if channel._spi is not None else "software GPIO"


def benchmark_one(channel, samples):
    started = time.monotonic_ns()
    for _ in range(samples):
        channel.show()
    elapsed_ns = time.monotonic_ns() - started
    return elapsed_ns / samples / 1_000_000


def benchmark_all(channels, samples):
    started = time.monotonic_ns()
    for _ in range(samples):
        for channel in channels:
            channel.show()
    elapsed_ns = time.monotonic_ns() - started
    average_ms = elapsed_ns / samples / 1_000_000
    return average_ms, 1000 / average_ms


def run_benchmark(channels):
    print("\nPER-CHANNEL SHOW TIME")
    total_ms = 0.0
    for index, channel in enumerate(channels):
        channel.fill(TEST_COLOR)
        average_ms = benchmark_one(channel, config.SAMPLES_PER_CHANNEL)
        total_ms += average_ms
        print(
            " CH%d: %-13s %8.2f ms/show  %7.2f max FPS"
            % (index + 1, output_backend(channel), average_ms, 1000 / average_ms)
        )

    aggregate_ms, aggregate_fps = benchmark_all(
        channels, config.AGGREGATE_SAMPLES
    )
    print(" Sum of individual averages: %.2f ms" % total_ms)
    print(" Six-channel measured frame: %.2f ms" % aggregate_ms)
    print(" Six-channel maximum rate: %.2f FPS" % aggregate_fps)
    print(" 10 FPS budget: 100.00 ms")
    print(" 10 FPS result:", "PASS" if aggregate_ms <= 100 else "FAIL")

    for channel in channels:
        channel.fill(BLACK)
        channel.show()


print("\nBU-22 REV D CIRCUITPYTHON DOTSTAR BENCHMARK", VERSION)
print("Pixels per channel:", config.PIXELS_PER_CHANNEL)
print("Channels: 6")

output_enable = digitalio.DigitalInOut(config.BUFFER_ENABLE)
output_enable.switch_to_output(value=False)
print("AHCT outputs: DISABLED")

for remaining in range(config.SAFE_START_SECONDS, 0, -1):
    print("Starting in", remaining)
    time.sleep(1)

channels = make_channels()
for channel in channels:
    channel.fill(BLACK)
    channel.show()
output_enable.value = True
print("AHCT outputs: ENABLED after black frames")

while True:
    run_benchmark(channels)
    time.sleep(config.REPEAT_PAUSE_SECONDS)
