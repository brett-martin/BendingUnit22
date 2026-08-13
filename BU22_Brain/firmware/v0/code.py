"""BU-22 Brain v0 exerciser for the first clean Eyes protocol slice."""

import time
import board
import busio

EYES = 0x30
SHOW_NORMAL = 0x10
SHOW_EXPRESSION = 0x11
PLAY_ANIMATION = 0x12
STOP = 0x14
SET_OFF = 0x15
PLAY_VISOR_DOWN = 0x16
PLAY_VISOR_UP = 0x17

NORMAL = 0
LOOK_LEFT = 2
LOOK_RIGHT = 3
ANGRY_1 = 4
ANGRY_2 = 5
BLINK = 0
DOUBLE_BLINK = 1
ANIM_LOOK_LEFT = 4
ANIM_LOOK_RIGHT = 5
MISSING_ANIMATION = 999

i2c = busio.I2C(board.SCL, board.SDA, frequency=100_000)
tag = 0


def lock():
    while not i2c.try_lock():
        pass


def scan():
    lock()
    try:
        return i2c.scan()
    finally:
        i2c.unlock()


def wait_for_eyes():
    while EYES not in scan():
        print("Waiting for Eyes")
        time.sleep(1)
    print("Eyes found at 0x30")


def next_tag():
    global tag
    tag = (tag + 1) & 255
    return tag


def send(*values):
    lock()
    try:
        i2c.writeto(EYES, bytes(values))
    finally:
        i2c.unlock()
    time.sleep(0.02)


def visual(command, content_id=None):
    request_tag = next_tag()
    if content_id is None:
        send(command, request_tag)
    else:
        send(command, request_tag, content_id >> 8, content_id & 255)
    return request_tag


def visor(command, step_ms=150):
    request_tag = next_tag()
    send(command, request_tag, step_ms >> 8, step_ms & 255)
    return request_tag


def status():
    response = bytearray(20)
    lock()
    try:
        i2c.readfrom_into(EYES, response)
    finally:
        i2c.unlock()
    print("STATUS", tuple(response))
    print(" state=", response[7], "activity=", response[8],
          "tag=", response[9], "error=", response[11],
          "last_command=0x%02X" % response[10],
          "content_or_missing_id=", (response[12] << 8) | response[13])


wait_for_eyes()

while True:
    for expression_id, name in ((NORMAL, "NORMAL"), (LOOK_LEFT, "LOOK LEFT"),
                                (LOOK_RIGHT, "LOOK RIGHT"),
                                (ANGRY_1, "ANGRY 1"), (ANGRY_2, "ANGRY 2")):
        print("SHOW", name)
        visual(SHOW_EXPRESSION, expression_id)
        time.sleep(1)

    for animation_id, name in ((BLINK, "BLINK"),
                               (DOUBLE_BLINK, "DOUBLE BLINK"),
                               (ANIM_LOOK_LEFT, "LOOK LEFT"),
                               (ANIM_LOOK_RIGHT, "LOOK RIGHT")):
        print("PLAY", name)
        visual(PLAY_ANIMATION, animation_id)
        time.sleep(1.5)

    print("PLAY LOOK then interrupt with STOP")
    visual(PLAY_ANIMATION, ANIM_LOOK_LEFT)
    time.sleep(0.2)
    visual(STOP)
    time.sleep(1)

    print("SET OFF")
    visual(SET_OFF)
    time.sleep(1)
    print("SHOW NORMAL")
    visual(SHOW_NORMAL)
    time.sleep(1)

    print("VISOR DOWN: rows turn off top-to-bottom")
    visor(PLAY_VISOR_DOWN)
    time.sleep(1.5)
    print("VISOR UP: Normal reveals bottom-to-top")
    visor(PLAY_VISOR_UP)
    time.sleep(1.5)

    print("REQUEST MISSING ANIMATION 999")
    visual(PLAY_ANIMATION, MISSING_ANIMATION)
    time.sleep(1)
    status()
    time.sleep(2)

    print("RECOVER WITH NORMAL")
    visual(SHOW_NORMAL)
    status()
    time.sleep(2)
