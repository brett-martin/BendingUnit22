"""BU-22 Brain: smallest possible I2C command test.

Hardware:
  Adafruit Feather RP2040
  SDA, SCL, and GND connected to the Eye Controller
  4.7k pull-ups from SDA and SCL to this board's 3.3 V rail
  Do not connect the Qwiic red power wire during this test.
"""

import time

import board
import busio


EYES_ADDRESS = 0x30

COMMAND_CLEAR = 0x00
COMMAND_IDENTIFY = 0x01
COMMAND_START_LONG_PATTERN = 0x02
COMMAND_SET_BRIGHTNESS = 0x03
COMMAND_SET_CHANNEL_COLOR = 0x04
COMMAND_SET_PIXEL = 0x05
COMMAND_SET_FRAME = 0x06
COMMAND_GET_STATUS = 0x07
COMMAND_SHOW_EXPRESSION = 0x08
COMMAND_PLAY_BLINK = 0x09

EXPECTED_IDENTITY = 0x22
EXPECTED_TEST_VERSION = 0x01
STATUS_LENGTH = 5

SCAN_INTERVAL_SECONDS = 1.0
INTER_TRANSACTION_GAP_SECONDS = 0.02

EXPRESSION_NORMAL = 0
EXPRESSION_LOOK_LEFT = 1
EXPRESSION_LOOK_RIGHT = 2

EXPRESSION_SEQUENCE = (
    (EXPRESSION_NORMAL, "NORMAL"),
    (EXPRESSION_LOOK_LEFT, "LOOK LEFT"),
    (EXPRESSION_NORMAL, "NORMAL"),
    (EXPRESSION_LOOK_RIGHT, "LOOK RIGHT"),
    (EXPRESSION_NORMAL, "NORMAL"),
)
EXPRESSION_HOLD_SECONDS = 2.0
BLINK_TEST_SECONDS = 3.0


def wait_for_bus(i2c):
    while not i2c.try_lock():
        pass


def scan(i2c):
    wait_for_bus(i2c)
    try:
        return i2c.scan()
    finally:
        i2c.unlock()


def send_packet(i2c, *values):
    wait_for_bus(i2c)
    try:
        i2c.writeto(EYES_ADDRESS, bytes(values))
    finally:
        i2c.unlock()


def read_status(i2c):
    # First tell Eyes what the following read is asking for. The short pause is
    # required by the current CircuitPython target loop between transactions.
    send_packet(i2c, COMMAND_GET_STATUS)
    time.sleep(INTER_TRANSACTION_GAP_SECONDS)

    response = bytearray(STATUS_LENGTH)
    wait_for_bus(i2c)
    try:
        i2c.readfrom_into(EYES_ADDRESS, response)
    finally:
        i2c.unlock()

    identity, version, activity, last_command, error = response
    print(
        "STATUS id=0x%02X version=%d activity=%d last=0x%02X error=%d"
        % (identity, version, activity, last_command, error)
    )
    if identity != EXPECTED_IDENTITY:
        print("FAIL: unexpected Eye Controller identity")
    if version != EXPECTED_TEST_VERSION:
        print("FAIL: unexpected Eye test version")
    if error:
        print("FAIL: Eye Controller reports error", error)
    return tuple(response)


print("\nBU-22 Brain: basic I2C test")
print("Looking for Eye Controller at 0x%02X" % EYES_ADDRESS)

i2c = busio.I2C(board.SCL, board.SDA, frequency=100_000)
eyes_connected = False
eyes_seen_before = False

while True:
    if not eyes_connected:
        try:
            found = scan(i2c)
        except OSError as error:
            found = ()
            print("I2C scan error:", error)

        if EYES_ADDRESS not in found:
            time.sleep(SCAN_INTERVAL_SECONDS)
            continue

        if eyes_seen_before:
            print("EYES FOUND AGAIN at 0x%02X" % EYES_ADDRESS)
        else:
            print("EYES FOUND at 0x%02X" % EYES_ADDRESS)
            eyes_seen_before = True
        eyes_connected = True

        try:
            print("Restarting Eyes at NORMAL")
            send_packet(i2c, COMMAND_CLEAR)
            time.sleep(INTER_TRANSACTION_GAP_SECONDS)
            send_packet(i2c, COMMAND_SHOW_EXPRESSION, EXPRESSION_NORMAL)
            time.sleep(1.0)
        except OSError:
            print("EYES LOST during reconnect")
            eyes_connected = False
            time.sleep(SCAN_INTERVAL_SECONDS)
            continue

    try:
        for expression_id, name in EXPRESSION_SEQUENCE:
            print("SHOW", name)
            send_packet(i2c, COMMAND_SHOW_EXPRESSION, expression_id)
            time.sleep(EXPRESSION_HOLD_SECONDS)

        print("PLAY locally timed BLINK")
        send_packet(i2c, COMMAND_PLAY_BLINK)
        time.sleep(BLINK_TEST_SECONDS)

        print("Reading status")
        read_status(i2c)
        time.sleep(1.0)
    except OSError as error:
        print("EYES LOST:", error)
        eyes_connected = False
        time.sleep(SCAN_INTERVAL_SECONDS)
