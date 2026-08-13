"""Survive an Eyes disconnect, rediscover it, and restart at Normal."""

import time
import common

NORMAL = 0
LEFT = 1
RIGHT = 2
SEQUENCE = ((NORMAL, "NORMAL"), (LEFT, "LEFT"), (NORMAL, "NORMAL"),
            (RIGHT, "RIGHT"), (NORMAL, "NORMAL"))

i2c = common.make_i2c()
connected = False
seen_before = False

while True:
    if not connected:
        try:
            found = common.scan(i2c)
        except OSError:
            found = ()
        if common.EYES_ADDRESS not in found:
            time.sleep(1)
            continue
        print("EYES FOUND AGAIN" if seen_before else "EYES FOUND")
        seen_before = True
        connected = True
        try:
            common.send(i2c, common.CLEAR)
            common.send(i2c, common.SHOW_EXPRESSION, NORMAL)
        except OSError:
            connected = False
            continue

    try:
        for expression, name in SEQUENCE:
            print(name)
            common.send(i2c, common.SHOW_EXPRESSION, expression)
            time.sleep(2)
        print("BLINK")
        common.send(i2c, common.PLAY_BLINK)
        time.sleep(3)
        common.status(i2c)
    except OSError as error:
        print("EYES LOST:", error)
        connected = False
        time.sleep(1)
