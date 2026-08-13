"""Experimental pre-v1 6x4 content used by the first clean firmware slice."""

NORMAL = 0
CLOSED = 1
LOOK_LEFT = 2
LOOK_RIGHT = 3
ANGRY_1 = 4
ANGRY_2 = 5
BORED = 6
WORRIED = 7

EXPRESSIONS = {
    NORMAL: ((70, 220, 70), (220, 0, 220), (220, 0, 220), (70, 220, 70)),
    CLOSED: ((0, 0, 0), (0, 0, 0), (180, 255, 180), (0, 0, 0)),
    LOOK_LEFT: ((0, 220, 70), (0, 220, 220), (0, 220, 220), (0, 220, 70)),
    LOOK_RIGHT: ((70, 220, 0), (220, 220, 0), (220, 220, 0), (70, 220, 0)),
    ANGRY_1: ((0, 100, 180), (100, 0, 220), (220, 0, 220), (70, 220, 70)),
    ANGRY_2: ((0, 0, 160), (40, 0, 220), (220, 0, 220), (70, 220, 70)),
    BORED: ((0, 0, 0), (120, 0, 120), (220, 0, 220), (70, 220, 70)),
    WORRIED: ((70, 220, 70), (220, 0, 220), (120, 0, 120), (0, 0, 0)),
}

BLINK = 0
DOUBLE_BLINK = 1
WINK_LEFT = 2
WINK_RIGHT = 3
ANIM_LOOK_LEFT = 4
ANIM_LOOK_RIGHT = 5

# Each step is (expression ID, duration milliseconds). None means Off.
ANIMATIONS = {
    BLINK: ((CLOSED, 120), (NORMAL, 0)),
    DOUBLE_BLINK: ((CLOSED, 100), (NORMAL, 100), (CLOSED, 100), (NORMAL, 0)),
    WINK_LEFT: ((CLOSED, 180), (NORMAL, 0)),  # Placeholder on 6x4 test grid.
    WINK_RIGHT: ((CLOSED, 180), (NORMAL, 0)),
    ANIM_LOOK_LEFT: ((LOOK_LEFT, 700), (NORMAL, 0)),
    ANIM_LOOK_RIGHT: ((LOOK_RIGHT, 700), (NORMAL, 0)),
}

EXPRESSION_NAMES = {
    NORMAL: "NORMAL", CLOSED: "CLOSED", LOOK_LEFT: "LOOK_LEFT",
    LOOK_RIGHT: "LOOK_RIGHT", ANGRY_1: "ANGRY_1", ANGRY_2: "ANGRY_2",
    BORED: "BORED", WORRIED: "WORRIED",
}

ANIMATION_NAMES = {
    BLINK: "BLINK", DOUBLE_BLINK: "DOUBLE_BLINK",
    WINK_LEFT: "WINK_LEFT", WINK_RIGHT: "WINK_RIGHT",
    ANIM_LOOK_LEFT: "LOOK_LEFT", ANIM_LOOK_RIGHT: "LOOK_RIGHT",
}
