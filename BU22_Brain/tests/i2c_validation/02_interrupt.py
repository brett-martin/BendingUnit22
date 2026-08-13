"""Start a six-second local pattern and interrupt it after two seconds."""

import time
import common

i2c = common.make_i2c()
common.wait_for_eyes(i2c)
while True:
    print("START pattern")
    common.send(i2c, common.START_LONG_PATTERN)
    time.sleep(2)
    print("INTERRUPT with CLEAR")
    common.send(i2c, common.CLEAR)
    time.sleep(3)
