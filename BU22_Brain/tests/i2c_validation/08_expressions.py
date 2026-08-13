"""Request locally stored 3x4 expressions and a locally timed blink."""

import time
import common

NORMAL = 0
LEFT = 1
RIGHT = 2
SEQUENCE = ((NORMAL, "NORMAL"), (LEFT, "LEFT"), (NORMAL, "NORMAL"),
            (RIGHT, "RIGHT"), (NORMAL, "NORMAL"))

i2c = common.make_i2c()
common.wait_for_eyes(i2c)
while True:
    for expression, name in SEQUENCE:
        print(name)
        common.send(i2c, common.SHOW_EXPRESSION, expression)
        time.sleep(2)
    print("BLINK")
    common.send(i2c, common.PLAY_BLINK)
    time.sleep(3)
