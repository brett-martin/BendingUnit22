"""Discovery plus one-byte CLEAR and IDENTIFY commands."""

import time
import common

i2c = common.make_i2c()
common.wait_for_eyes(i2c)
while True:
    common.send(i2c, common.CLEAR)
    time.sleep(2)
    common.send(i2c, common.IDENTIFY)
    time.sleep(3)
