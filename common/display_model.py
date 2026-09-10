"""Pure framebuffer and state helpers shared by display-controller firmware."""

from .font3x5 import centered_text, draw_text, scroll_positions, text_width
from .protocol import LOCAL_BENDER, LOCAL_TARGET, LOCAL_TEST


class DisplayGeometry:
    def __init__(self, module_count, module_width, module_height):
        self.module_count = module_count
        self.module_width = module_width
        self.height = module_height
        self.width = module_count * module_width
        self.pixel_count = self.width * self.height

    def pixel_index(self, x, y):
        module = x // self.module_width
        local_x = x % self.module_width
        base = module * self.module_width * self.height
        local_y = y if local_x % 2 == 0 else self.height - 1 - y
        return base + local_x * self.height + local_y


class LocalModeState:
    def __init__(self):
        self.mode = LOCAL_TARGET

    def advance(self):
        self.mode = (self.mode + 1) % 3
        return self.mode

    @property
    def accepts_visual_commands(self):
        return self.mode == LOCAL_TARGET


def blank_frame(geometry):
    return bytearray(geometry.pixel_count)


def text_frame(geometry, text):
    frame = blank_frame(geometry)
    centered_text(frame, geometry.width, geometry.height, text)
    return frame


def scrolling_frames(geometry, text):
    y = (geometry.height - 5) // 2
    for x in scroll_positions(text, geometry.width):
        frame = blank_frame(geometry)
        draw_text(frame, geometry.width, geometry.height, text, x, y)
        yield frame


def scrolling_frame_count(geometry, text):
    return geometry.width + text_width(text) + 1


def scrolling_frame_at(geometry, text, index):
    count = scrolling_frame_count(geometry, text)
    if not 0 <= index < count:
        raise IndexError("scroll frame index out of range")
    frame = blank_frame(geometry)
    y = (geometry.height - 5) // 2
    draw_text(frame, geometry.width, geometry.height, text,
              geometry.width - index, y)
    return frame


def clock_frame(geometry, hour, minute, colon=True):
    # Semicolon is a blank glyph with the same one-column advance as colon.
    # Keeping that cell in the layout prevents the digits from shifting as it
    # flashes.
    text = "%02d%s%02d" % (hour, ":" if colon else ";", minute)
    return text_frame(geometry, text)


def local_mode_label(mode):
    return ("TARGET", "TEST", "BENDER")[mode]
