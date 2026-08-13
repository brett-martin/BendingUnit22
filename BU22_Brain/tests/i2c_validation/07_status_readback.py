"""Interleave five-byte Eye status reads with 10 FPS frame writes."""

import time
import common

i2c = common.make_i2c()
common.wait_for_eyes(i2c)
common.send(i2c, common.CLEAR)
common.status(i2c)
while True:
    started = time.monotonic()
    for frame in range(100):
        values = tuple(160 if (pixel + frame) % 2 == 0 else 0 for pixel in range(24))
        common.send(i2c, common.SET_FRAME, *values)
        if (frame + 1) % 10 == 0:
            common.status(i2c)
        remaining = started + ((frame + 1) * 0.1) - time.monotonic()
        if remaining > 0:
            time.sleep(remaining)
    common.send(i2c, common.CLEAR)
    common.status(i2c)
    time.sleep(2)
