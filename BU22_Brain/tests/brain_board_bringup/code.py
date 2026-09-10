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


VERSION = "0.12"
RTC_CONTROL_REGISTER = 0x0E
RTC_SQW_1HZ_MASK = 0x1C
SHOW_NORMAL = 0x10
SHOW_EXPRESSION = 0x11
SET_OFF = 0x15
EYES_NORMAL = 0
EYES_ANGRY = 5
MOUTH_NORMAL = 0
MOUTH_OPEN = 1
display_tag = 0

# Eight-second, 10 FPS stored-frame performance. Each tuple is
# (Eyes content ID, Mouth openness 0..4).
PERFORMANCE_FPS = 10
PERFORMANCE_FRAMES = (
    ((EYES_NORMAL, 0),) * 5
    + ((2, 1),) * 5
    + ((2, 2),) * 10
    + ((EYES_NORMAL, 3),) * 5
    + ((3, 4),) * 5
    + ((3, 3),) * 10
    + ((EYES_NORMAL, 2),) * 5
    + ((EYES_NORMAL, 1),) * 5
    + ((EYES_NORMAL, 0),) * 30
)


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


def next_display_tag():
    global display_tag
    display_tag = (display_tag + 1) & 0xFF
    return display_tag


def display_write(i2c, address, command, content_id=None, tag=None, verbose=True):
    if tag is None:
        tag = next_display_tag()
    if content_id is None:
        payload = bytes((command, tag))
    else:
        payload = bytes((command, tag, content_id >> 8, content_id & 0xFF))
    while not i2c.try_lock():
        time.sleep(0.001)
    try:
        i2c.writeto(address, payload)
    except OSError as error:
        print("Display 0x%02X write ERROR:" % address, repr(error))
        return False
    finally:
        i2c.unlock()
    if verbose:
        print("Display 0x%02X command sent; tag=%d" % (address, tag))
    return True


def display_status(i2c, address):
    response = bytearray(20)
    while not i2c.try_lock():
        time.sleep(0.001)
    try:
        i2c.readfrom_into(address, response)
    except OSError as error:
        print("Display 0x%02X status ERROR:" % address, repr(error))
        return False
    finally:
        i2c.unlock()
    if response[0] != 0x22:
        print("Display 0x%02X invalid status:" % address, tuple(response))
        return False
    print(
        "Display 0x%02X status: module=%d state=%d activity=%d tag=%d "
        "command=0x%02X error=%d content=%d address=0x%02X"
        % (
            address, response[3], response[7], response[8], response[9],
            response[10], response[11], (response[12] << 8) | response[13],
            response[17],
        )
    )
    return True


def eyes_command(i2c, value):
    value = value.lower()
    if value == "normal":
        return display_write(i2c, config.EYES_ADDRESS, SHOW_NORMAL)
    if value == "angry":
        return display_write(i2c, config.EYES_ADDRESS, SHOW_EXPRESSION, EYES_ANGRY)
    if value == "off":
        return display_write(i2c, config.EYES_ADDRESS, SET_OFF)
    print("Use: e normal, e angry, or e off")
    return False


def mouth_command(i2c, value):
    value = value.lower()
    if value == "normal":
        return display_write(i2c, config.MOUTH_ADDRESS, SHOW_NORMAL)
    if value == "open":
        return display_write(i2c, config.MOUTH_ADDRESS, SHOW_EXPRESSION, MOUTH_OPEN)
    if value == "off":
        return display_write(i2c, config.MOUTH_ADDRESS, SET_OFF)
    print("Use: m normal, m open, or m off")
    return False


def display_query(i2c, value):
    value = value.lower()
    if value in ("eyes", "eye", "e"):
        return display_status(i2c, config.EYES_ADDRESS)
    if value in ("mouth", "m"):
        return display_status(i2c, config.MOUTH_ADDRESS)
    print("Use: q eyes or q mouth")
    return False


def performance_frame(i2c, frame_index):
    eyes_content, mouth_content = PERFORMANCE_FRAMES[frame_index]
    tag = next_display_tag()
    eyes_ok = display_write(
        i2c, config.EYES_ADDRESS, SHOW_EXPRESSION, eyes_content,
        tag=tag, verbose=False
    )
    mouth_ok = display_write(
        i2c, config.MOUTH_ADDRESS, SHOW_EXPRESSION, mouth_content,
        tag=tag, verbose=False
    )
    if frame_index % PERFORMANCE_FPS == 0:
        print(
            "Performance %.1fs: eyes=%d mouth=%d tag=%d"
            % (frame_index / PERFORMANCE_FPS, eyes_content, mouth_content, tag)
        )
    return eyes_ok and mouth_ok


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


def read_command_tail(timeout=10.0):
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
        # Close-only avoids immediately latching an away event while INT is
        # being tested directly and is not yet connected to A3.
        vcnl.prox_interrupt = adafruit_vcnl4200.PS_INT["CLOSE"]
        cleared_flags = vcnl.interrupt_flags
    except ImportError:
        print("Sensor monitor: adafruit_vcnl4200 library is not installed")
        return
    except Exception as error:
        print("Sensor monitor ERROR:", repr(error))
        return

    print(
        "Sensor interrupt: active-low CLOSE-only, close>%d, persistence=2"
        % config.SENSOR_PROX_CLOSE
    )
    print("Sensor interrupt: cleared prior flags:", cleared_flags)
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


def clear_sensor_interrupt(i2c):
    try:
        import adafruit_vcnl4200
        vcnl = adafruit_vcnl4200.Adafruit_VCNL4200(i2c)
        print("Sensor interrupt flags (read/cleared):", vcnl.interrupt_flags)
    except ImportError:
        print("Sensor interrupt: adafruit_vcnl4200 library is not installed")
    except Exception as error:
        print("Sensor interrupt clear ERROR:", repr(error))


def antenna_test(outputs, value):
    names = {
        "r": 0,
        "red": 0,
        "g": 1,
        "green": 1,
        "b": 2,
        "blue": 2,
    }
    index = names.get(value.lower())
    if index is None:
        print("Use: a red, a green, or a blue")
        return False

    # Explicitly hold every unrequested antenna output low.
    for output in outputs:
        output.value = False
    print("Antenna %s: HIGH for 3 seconds" % config.ANTENNA_NAMES[index])
    outputs[index].value = True
    time.sleep(3.0)
    outputs[index].value = False
    print("Antenna %s: LOW" % config.ANTENNA_NAMES[index])
    return True


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
    print("  f  read and clear latched VCNL4200 interrupt flags")
    print("  a COLOR  hold red, green, or blue antenna output high for 3 seconds")
    print("  l  request Audio FX track list")
    print("  p NUMBER  play Txx.WAV (for example, p 3 plays T03.WAV)")
    print("  x  reset Audio FX board")
    print("  e normal|angry|off  set the static Eyes image")
    print("  m normal|open|off   set the static Mouth image")
    print("  q eyes|mouth        read display-controller status")
    print("  g                    start/stop the stored 10 FPS performance loop")
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
heartbeat_ok = heartbeat_test(sqw) if rtc_ok else False
set_pixel(pixel, (0, 0, 0))

print_help()

performance_running = False
performance_index = 0
performance_next_frame = time.monotonic()

while True:
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
            heartbeat_test(sqw)
        elif command == "i":
            print_inputs(button_states, audio_act, sensor)
        elif command == "v":
            sensor_monitor(i2c, sensor)
        elif command == "f":
            clear_sensor_interrupt(i2c)
        elif command == "a":
            antenna_test(antenna, read_command_tail())
        elif command == "l":
            audio_list(uart)
        elif command == "p":
            audio_play_track(uart, read_command_tail())
        elif command == "x":
            audio_reset(audio_reset_pin)
        elif command == "e":
            eyes_command(i2c, read_command_tail())
        elif command == "m":
            mouth_command(i2c, read_command_tail())
        elif command == "q":
            display_query(i2c, read_command_tail())
        elif command == "g":
            performance_running = not performance_running
            performance_index = 0
            performance_next_frame = time.monotonic()
            if performance_running:
                print("Stored performance LOOP START: 8.0 seconds at 10 FPS")
            else:
                print("Stored performance STOP; returning displays to normal")
                display_write(i2c, config.EYES_ADDRESS, SHOW_NORMAL)
                display_write(i2c, config.MOUTH_ADDRESS, SHOW_NORMAL)
        else:
            print_help()

    if performance_running and time.monotonic() >= performance_next_frame:
        performance_frame(i2c, performance_index)
        performance_index = (performance_index + 1) % len(PERFORMANCE_FRAMES)
        performance_next_frame += 1.0 / PERFORMANCE_FPS
        if time.monotonic() - performance_next_frame > 0.5:
            performance_next_frame = time.monotonic()

    time.sleep(0.005)
