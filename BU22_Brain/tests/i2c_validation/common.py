"""Shared controller helpers for the disposable BU-22 I2C validation tests."""

import time

import board
import busio


EYES_ADDRESS = 0x30
INTER_PACKET_GAP = 0.02

CLEAR = 0x00
IDENTIFY = 0x01
START_LONG_PATTERN = 0x02
SET_BRIGHTNESS = 0x03
SET_CHANNEL_COLOR = 0x04
SET_PIXEL = 0x05
SET_FRAME = 0x06
GET_STATUS = 0x07
SHOW_EXPRESSION = 0x08
PLAY_BLINK = 0x09


def make_i2c():
    return busio.I2C(board.SCL, board.SDA, frequency=100_000)


def lock(i2c):
    while not i2c.try_lock():
        pass


def scan(i2c):
    lock(i2c)
    try:
        return i2c.scan()
    finally:
        i2c.unlock()


def wait_for_eyes(i2c):
    while True:
        found = scan(i2c)
        if EYES_ADDRESS in found:
            print("EYES FOUND at 0x%02X" % EYES_ADDRESS)
            return
        print("Waiting; found:", ["0x%02X" % value for value in found])
        time.sleep(1.0)


def send(i2c, *values):
    lock(i2c)
    try:
        i2c.writeto(EYES_ADDRESS, bytes(values))
    finally:
        i2c.unlock()
    time.sleep(INTER_PACKET_GAP)


def status(i2c):
    send(i2c, GET_STATUS)
    response = bytearray(5)
    lock(i2c)
    try:
        i2c.readfrom_into(EYES_ADDRESS, response)
    finally:
        i2c.unlock()
    print("STATUS", tuple(response))
    return tuple(response)
