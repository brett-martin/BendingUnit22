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


VERSION = "0.5"
RTC_CONTROL_REGISTER = 0x0E
RTC_SQW_1HZ_MASK = 0x1C


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


def rtc_device(i2c):
    import adafruit_ds3231
    return adafruit_ds3231.DS3231(i2c)


def configure_rtc_sqw_1hz(rtc):
    """Select the powered 1 Hz square-wave output without changing other bits."""
    register = bytearray((RTC_CONTROL_REGISTER,))
    control = bytearray(1)
    with rtc.i2c_device as device:
        device.write_then_readinto(register, control)
        control[0] &= ~RTC_SQW_1HZ_MASK
        device.write(bytearray((RTC_CONTROL_REGISTER, control[0])))
    print("RTC SQW: configured for 1 Hz")


def weekday(year, month, day):
    """Return Monday=0 through Sunday=6 for a Gregorian calendar date."""
    if month < 3:
        year -= 1
        month += 12
    sunday_zero = (
        day + (13 * (month + 1)) // 5 + year + year // 4 - year // 100
        + year // 400
    ) % 7
    return (sunday_zero + 5) % 7


def read_command_tail(timeout=1.0):
    characters = []
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if supervisor.runtime.serial_bytes_available:
            character = sys.stdin.read(1)
            if character in ("\r", "\n"):
                if characters:
                    break
                continue
            characters.append(character)
        else:
            time.sleep(0.01)
    return "".join(characters).strip()


def set_rtc_from_text(i2c, value):
    try:
        date_text, time_text = value.split(" ")
        year, month, day = (int(item) for item in date_text.split("-"))
        hour, minute, second = (int(item) for item in time_text.split(":"))
        new_time = time.struct_time(
            (year, month, day, hour, minute, second,
             weekday(year, month, day), -1, -1)
        )
        rtc = rtc_device(i2c)
        rtc.datetime = new_time
        print("RTC set from local wall clock:", value)
        print_rtc(i2c)
        return True
    except (ValueError, TypeError) as error:
        print("RTC set ERROR:", repr(error))
        print("Use: t YYYY-MM-DD HH:MM:SS")
        return False


def heartbeat_test(sqw, pixel=None, seconds=4.5):
    print("Heartbeat: watching D13 for %.1f seconds" % seconds)
    edges = []
    previous = sqw.value
    started = time.monotonic()
    while time.monotonic() - started < seconds:
        value = sqw.value
        set_pixel(pixel, (25, 0, 0) if value else (0, 0, 0))
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
            "%s=%s"
            % (config.BUTTON_NAMES[index], "DOWN" if button_states[index] else "up")
        )
    print("Buttons:", " ".join(states))
    print("Audio ACT:", "PLAYING/LOW" if not audio_act.value else "idle/high")
    print("Sensor/INT A3:", "LOW" if not sensor.value else "high")


def sensor_monitor(i2c, interrupt_pin):
    print("Sensor monitor: starting; press any key to stop")
    try:
        import adafruit_vcnl4200
        vcnl = adafruit_vcnl4200.Adafruit_VCNL4200(i2c)
        vcnl.prox_int_threshold_low = config.SENSOR_PROX_AWAY
        vcnl.prox_int_threshold_high = config.SENSOR_PROX_CLOSE
        vcnl.prox_persistence = adafruit_vcnl4200.PS_PERS["2"]
        vcnl.prox_interrupt_logic_mode = False
        vcnl.prox_interrupt = adafruit_vcnl4200.PS_INT["BOTH"]
    except ImportError:
        print("Sensor monitor: adafruit_vcnl4200 library is not installed")
        return
    except Exception as error:
        print("Sensor monitor ERROR:", repr(error))
        return

    print(
        "Sensor interrupt: active-low, away<=%d, close>=%d, persistence=2"
        % (config.SENSOR_PROX_AWAY, config.SENSOR_PROX_CLOSE)
    )
    # Discard the newline that completed the command before watching for a key.
    read_command_tail(timeout=0.2)
    while True:
        try:
            interrupt_level = interrupt_pin.value
            flags = vcnl.interrupt_flags if not interrupt_level else None
            print(
                "proximity=%d white=%d lux=%.2f INT=%s flags=%s"
                % (
                    vcnl.proximity,
                    vcnl.white_light,
                    vcnl.lux,
                    "LOW" if not interrupt_level else "high",
                    flags if flags is not None else "-",
                )
            )
        except Exception as error:
            print("Sensor read ERROR:", repr(error))
            break

        deadline = time.monotonic() + 0.2
        while time.monotonic() < deadline:
            if supervisor.runtime.serial_bytes_available:
                sys.stdin.read(1)
                read_command_tail(timeout=0.1)
                print("Sensor monitor: stopped")
                return
            time.sleep(0.01)


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


def audio_play_track(uart, value):
    try:
        track = int(value)
        if not 0 <= track <= 99:
            raise ValueError("track must be from 0 through 99")
    except ValueError as error:
        print("Audio FX track ERROR:", repr(error))
        print("Use: p NUMBER  (for example, p 0 plays T00.WAV)")
        return False

    filename = "T%02d     WAV" % track
    print("Audio FX: requesting T%02d.WAV" % track)
    uart.reset_input_buffer()
    uart.write(("P%s\n" % filename).encode("ascii"))
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
        return True
    else:
        print("Audio FX: no UART response; check power, UG ground, TX/RX crossover")
        return False


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
    print("  t YYYY-MM-DD HH:MM:SS  set RTC to local wall-clock time")
    print("  h  verify RTC SQW heartbeat")
    print("  i  print buttons, Audio ACT, and sensor/INT")
    print("  v  stream VCNL4200 proximity/light data; any key stops")
    print("  a  cycle antenna outputs")
    print("  l  request Audio FX track list")
    print("  p NUMBER  play Txx.WAV (for example, p 3 plays T03.WAV)")
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
rtc_ok = False
if config.RTC_ADDRESS in addresses:
    rtc_ok = print_rtc(i2c)
    if rtc_ok:
        try:
            configure_rtc_sqw_1hz(rtc_device(i2c))
        except Exception as error:
            print("RTC SQW CONFIG ERROR:", repr(error))
print_inputs(button_states, audio_act, sensor)
heartbeat_ok = heartbeat_test(sqw, pixel) if rtc_ok else False

if rtc_ok and heartbeat_ok:
    set_pixel(pixel, (25, 0, 0))
else:
    set_pixel(pixel, (30, 0, 0))

print_help()

while True:
    if rtc_ok:
        set_pixel(pixel, (25, 0, 0) if sqw.value else (0, 0, 0))

    event = buttons.events.get()
    if event is not None:
        button_states[event.key_number] = event.pressed
        print(
            "%s %s"
            % (
                config.BUTTON_NAMES[event.key_number],
                "PRESSED" if event.pressed else "released",
            )
        )

    if supervisor.runtime.serial_bytes_available:
        command = sys.stdin.read(1).lower()
        if command in ("\r", "\n", " "):
            continue
        if command == "s":
            print_scan(i2c)
        elif command == "r":
            print_rtc(i2c)
        elif command == "t":
            set_rtc_from_text(i2c, read_command_tail())
        elif command == "h":
            heartbeat_test(sqw, pixel)
        elif command == "i":
            print_inputs(button_states, audio_act, sensor)
        elif command == "v":
            sensor_monitor(i2c, sensor)
        elif command == "a":
            antenna_test(antenna)
        elif command == "l":
            audio_list(uart)
        elif command == "p":
            audio_play_track(uart, read_command_tail())
        elif command == "x":
            audio_reset(audio_reset_pin)
        else:
            print_help()

    time.sleep(0.005)
