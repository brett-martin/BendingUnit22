"""Small shared subset of the BU-22 wire protocol used by development firmware."""

MAGIC = 0x22
PROTOCOL_MAJOR = 0
PROTOCOL_MINOR = 2

EYES_ADDRESS = 0x30
MOUTH_ADDRESS = 0x31

MODULE_EYES = 1
MODULE_MOUTH = 2

SHOW_NORMAL = 0x10
SHOW_EXPRESSION = 0x11
PLAY_ANIMATION = 0x12
SET_OFF = 0x15
SHOW_CLOCK = 0x20
SHOW_DEV_TEXT = 0x75
PLAY_ANIMATION_TIMED = 0x18

ERROR_NONE = 0
ERROR_UNKNOWN_COMMAND = 1
ERROR_BAD_LENGTH = 2
ERROR_INVALID_ARGUMENT = 3
ERROR_UNKNOWN_CONTENT = 4
ERROR_LOCAL_MODE_BUSY = 10

LOCAL_TARGET = 0
LOCAL_TEST = 1
LOCAL_BENDER = 2
LOCAL_MODE_NAMES = ("TARGET", "TEST", "BENDER")

DISPLAY_NORMAL = 0
DISPLAY_EXPRESSION = 1
DISPLAY_ANIMATION = 2
DISPLAY_CLOCK = 4
DISPLAY_MESSAGE = 5
DISPLAY_OFF = 6
DISPLAY_LOCAL_TEST = 8

ACTIVITY_IDLE = 0
ACTIVITY_RUNNING = 1
ACTIVITY_COMPLETE = 2

LIFECYCLE_WAITING_FOR_BRAIN = 1
LIFECYCLE_STANDALONE_NORMAL = 2
LIFECYCLE_BRAIN_CONTROLLED = 3
LIFECYCLE_LOCAL_TEST = 4

STATUS_FLAG_BRAIN_SEEN = 1 << 0
STATUS_FLAG_LOCAL_TEST = 1 << 1
STATUS_FLAG_ACTIVITY_COMPLETE = 1 << 5
STATUS_FLAG_LOCAL_BENDER = 1 << 6


def local_mode_name(value):
    if 0 <= value < len(LOCAL_MODE_NAMES):
        return LOCAL_MODE_NAMES[value]
    return "UNKNOWN"


def local_mode_from_status(lifecycle, flags):
    if lifecycle == LIFECYCLE_LOCAL_TEST or flags & STATUS_FLAG_LOCAL_TEST:
        return LOCAL_TEST
    if flags & STATUS_FLAG_LOCAL_BENDER:
        return LOCAL_BENDER
    return LOCAL_TARGET


def visual_packet(command, tag, content_id=None):
    if content_id is None:
        return bytes((command, tag))
    return bytes((command, tag, content_id >> 8, content_id & 0xFF))


def timed_animation_packet(tag, content_id, entry_duration,
                           hold_duration, exit_duration):
    values = (content_id, entry_duration, hold_duration, exit_duration)
    if any(not 0 <= value <= 0xFFFF for value in values):
        raise ValueError("timed animation values must fit unsigned 16 bits")
    return bytes((
        PLAY_ANIMATION_TIMED, tag,
        content_id >> 8, content_id & 0xFF,
        entry_duration >> 8, entry_duration & 0xFF,
        hold_duration >> 8, hold_duration & 0xFF,
        exit_duration >> 8, exit_duration & 0xFF,
    ))


def clock_packet(tag, hour, minute, flags=1):
    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise ValueError("invalid clock time")
    return bytes((SHOW_CLOCK, tag, hour, minute, flags & 0x03))


def dev_text_packet(tag, text):
    encoded = text.upper().encode("ascii")
    if not encoded or len(encoded) > 29:
        raise ValueError("development text must be 1..29 ASCII bytes")
    return bytes((SHOW_DEV_TEXT, tag)) + encoded
