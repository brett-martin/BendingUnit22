"""Safe interactive bring-up test for the BU-22 Brain perfboard V1.

The default path only reads inputs and scans I2C. Tests that drive outputs or
reset the Audio FX board require an explicit serial-console command.
"""

import sys
import time
import board
import busio
import digitalio
import keypad
import supervisor

import config


VERSION = "0.1"


def status_pixel():
    try:
        import neopixel
        return neopixel.NeoPixel(
            board.NEOPIXEL, 1, brightness=0.06, auto_write=True
        )
    except (ImportError, AttributeError, RuntimeError):
        return None


def set_pixel(pixel, color):
    if pixel is not None:
        pixel[0] = color


def scan(i2c):
    while not i2c.try_lock():
        time.sleep(0.001)
    try:
        return tuple(i2c.scan())
    finally:
        i2c.unlock()


def address_name(address):
    names = {
        config.EYES_ADDRESS: "Eyes",
        config.MOUTH_ADDRESS: "Mouth",
        config.VCNL4200_ADDRESS: "VCNL4200",
        config.RTC_ADDRESS: "DS3231 RTC",
    }
    return names.get(address, "unknown")


def print_scan(i2c):
    addresses = scan(i2c)
    if not addresses:
        print("I2C: no devices found")
        return addresses
    print("I2C devices:")
    for address in addresses:
        print("  0x%02X  %s" % (address, address_name(address)))
    return addresses


def print_rtc(i2c):
    addresses = scan(i2c)
    if config.RTC_ADDRESS not in addresses:
        print("RTC: not found at 0x68")
        return False
    try:
        import adafruit_ds3231
        rtc = adafruit_ds3231.DS3231(i2c)
        value = rtc.datetime
        print(
            "RTC: %04d-%02d-%02d %02d:%02d:%02d"
            % (
                value.tm_year,
                value.tm_mon,
                value.tm_mday,
                value.tm_hour,
                value.tm_min,
                value.tm_sec,
            )
        )
        try:
            print("RTC lost power:", rtc.lost_power)
        except AttributeError:
            pass
        return True
    except ImportError:
        print("RTC: adafruit_ds3231 library is not installed")
    except Exception as error:
        print("RTC ERROR:", repr(error))
    return False


def heartbeat_test(sqw, seconds=4.5):
    print("Heartbeat: watching D13 for %.1f seconds" % seconds)
    edges = []
    previous = sqw.value
    started = time.monotonic()
    while time.monotonic() - started < seconds:
        value = sqw.value
        if value != previous:
            edges.append(time.monotonic())
            previous = value
        time.sleep(0.002)
    intervals = []
    for index in range(1, len(edges)):
        intervals.append(round(edges[index] - edges[index - 1], 3))
    print("Heartbeat transitions:", len(edges), "intervals:", intervals)
    passed = len(edges) >= 7 and all(0.35 <= item <= 0.65 for item in intervals)
    print("Heartbeat:", "PASS" if passed else "CHECK WIRING/SQW CONFIG")
    return passed


def print_inputs(button_states, audio_act, sensor):
    states = []
    for index in range(len(config.BUTTON_PINS)):
        states.append(
            "B%d=%s" % (index + 1, "DOWN" if button_states[index] else "up")
        )
    print("Buttons:", " ".join(states))
    print("Audio ACT:", "PLAYING/LOW" if not audio_act.value else "idle/high")
    print("Sensor/INT A3:", "LOW" if not sensor.value else "high")


def antenna_test(outputs):
    print("Antenna: each output goes high for 0.5 seconds")
    for index, output in enumerate(outputs):
        print("  ", config.ANTENNA_NAMES[index])
        output.value = True
        time.sleep(0.5)
        output.value = False
        time.sleep(0.2)
    print("Antenna: all outputs low")


def audio_list(uart):
    print("Audio FX: requesting track list (non-playing test)")
    uart.reset_input_buffer()
    uart.write(b"\n")
    time.sleep(0.2)
    uart.write(b"L\n")
    deadline = time.monotonic() + 2.0
    response = bytearray()
    while time.monotonic() < deadline:
        waiting = uart.in_waiting
        if waiting:
            data = uart.read(waiting)
            if data:
                response.extend(data)
        time.sleep(0.01)
    if response:
        print("Audio FX response:")
        print(bytes(response).decode("utf-8", "replace"))
    else:
        print("Audio FX: no UART response; check power, UG ground, TX/RX crossover")


def audio_reset(reset_pin):
    print("Audio FX: pulsing reset low")
    reset_pin.switch_to_output(value=False)
    time.sleep(0.1)
    reset_pin.switch_to_input(pull=None)
    time.sleep(1.0)
    print("Audio FX: reset released")


def print_help():
    print("\nCommands")
    print("  s  scan I2C")
    print("  r  read RTC")
    print("  h  verify RTC SQW heartbeat")
    print("  i  print buttons, Audio ACT, and sensor/INT")
    print("  a  cycle antenna outputs")
    print("  l  request Audio FX track list")
    print("  x  reset Audio FX board")
    print("  ?  show this help\n")


print("\nBU-22 Brain board bring-up", VERSION)
print("Board:", getattr(board, "board_id", "unknown"))

pixel = status_pixel()
set_pixel(pixel, (20, 12, 0))

i2c = busio.I2C(config.I2C_SCL, config.I2C_SDA, frequency=100_000)
uart = busio.UART(
    config.AUDIO_TX,
    config.AUDIO_RX,
    baudrate=9600,
    timeout=0,
    receiver_buffer_size=512,
)

sqw = digitalio.DigitalInOut(config.RTC_SQW)
sqw.switch_to_input(pull=digitalio.Pull.UP)
audio_act = digitalio.DigitalInOut(config.AUDIO_ACT)
audio_act.switch_to_input(pull=digitalio.Pull.UP)
audio_reset_pin = digitalio.DigitalInOut(config.AUDIO_RESET)
audio_reset_pin.switch_to_input(pull=None)
sensor = digitalio.DigitalInOut(config.SENSOR_SIGNAL)
sensor.switch_to_input(pull=digitalio.Pull.UP)

antenna = []
for pin in config.ANTENNA_PINS:
    output = digitalio.DigitalInOut(pin)
    output.switch_to_output(value=False)
    antenna.append(output)

buttons = keypad.Keys(
    config.BUTTON_PINS,
    value_when_pressed=False,
    pull=True,
    interval=0.02,
)
button_states = [False] * len(config.BUTTON_PINS)

addresses = print_scan(i2c)
rtc_ok = print_rtc(i2c) if config.RTC_ADDRESS in addresses else False
print_inputs(button_states, audio_act, sensor)
heartbeat_ok = heartbeat_test(sqw) if rtc_ok else False

if rtc_ok and heartbeat_ok:
    set_pixel(pixel, (0, 25, 0))
else:
    set_pixel(pixel, (30, 0, 0))

print_help()

while True:
    event = buttons.events.get()
    if event is not None:
        button_states[event.key_number] = event.pressed
        print("Button %d %s" % (event.key_number + 1, "PRESSED" if event.pressed else "released"))

    if supervisor.runtime.serial_bytes_available:
        command = sys.stdin.read(1).lower()
        if command in ("\r", "\n", " "):
            continue
        if command == "s":
            print_scan(i2c)
        elif command == "r":
            print_rtc(i2c)
        elif command == "h":
            heartbeat_test(sqw)
        elif command == "i":
            print_inputs(button_states, audio_act, sensor)
        elif command == "a":
            antenna_test(antenna)
        elif command == "l":
            audio_list(uart)
        elif command == "x":
            audio_reset(audio_reset_pin)
        else:
            print_help()

    time.sleep(0.005)
