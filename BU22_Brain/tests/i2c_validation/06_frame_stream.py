"""Stream complete 24-pixel frames at 10 FPS and report timing."""

import time
import common

FPS = 10
FRAME_TIME = 1 / FPS
PIXELS = 24

i2c = common.make_i2c()
common.wait_for_eyes(i2c)
while True:
    started = time.monotonic()
    late = 0
    for frame in range(300):
        if frame < 100:
            values = tuple(160 if (pixel + frame) % 2 == 0 else 0 for pixel in range(PIXELS))
        elif frame < 200:
            selected = (frame - 100) % PIXELS
            values = tuple(200 if pixel == selected else 4 for pixel in range(PIXELS))
        else:
            levels = (0, 8, 24, 56, 112, 200)
            values = tuple(levels[((pixel // 4) + frame) % 6] for pixel in range(PIXELS))
        common.send(i2c, common.SET_FRAME, *values)
        deadline = started + ((frame + 1) * FRAME_TIME)
        remaining = deadline - time.monotonic()
        if remaining > 0:
            time.sleep(remaining)
        else:
            late += 1
    elapsed = time.monotonic() - started
    print("frames=300 elapsed=", elapsed, "late=", late, "fps=", 300 / elapsed)
    common.send(i2c, common.CLEAR)
    time.sleep(2)
