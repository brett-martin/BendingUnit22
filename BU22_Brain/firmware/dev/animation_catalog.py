"""Generated display-animation index for the Brain; do not hand edit."""

DEFAULT_ANIMATION_FPS = 10
# (animation ID, target, display name, complete entry/exit frame count)
ANIMATIONS = (
    (0, 'eyes', 'Angry', 5),
    (1, 'eyes', 'Bored', 7),
    (2, 'eyes', 'Shocked', 3),
    (3, 'eyes', 'Blink', 9),
    (4, 'eyes', 'Look Left', 9),
    (5, 'eyes', 'Look Right', 9),
    (6, 'eyes', 'Visor Close', 33),
    (7, 'mouth', 'OOOOOh', 17),
    (8, 'mouth', 'Blah blah', 19),
    (9, 'mouth', 'Whaaat / Whoooh', 21),
    (10, 'eyes', 'Very Angry', 7),
    (11, 'eyes', 'Slight Look Up', 3),
    (12, 'eyes', 'Slight Look Down', 3),
    (13, 'eyes', 'Look Up', 7),
    (14, 'eyes', 'Look Down', 7),
    (15, 'eyes', 'Slight Look Right', 5),
    (16, 'eyes', 'Slight Look Left', 5),
)

AUDIO_SLOTS = {20: 0, 25: 1, 26: 2}
# Event: (start ms, kind, target/audio ID, animation ID/slot, entry, hold, exit)
# kind 0 = animation; kind 1 = audio
PERFORMANCES = (
    (0, 'Im a bender', 3956, (
        (100, 0, 1, 1, 500, 100, 500),
        (200, 0, 2, 7, 500, 100, 500),
        (300, 1, 20, 0, 0, 0, 0),
        (1400, 0, 1, 2, 100, 400, 100),
        (1400, 0, 2, 8, 600, 100, 500),
        (2100, 0, 1, 5, 400, 300, 300),
        (2700, 0, 2, 7, 700, 100, 300),
        (3200, 0, 1, 2, 100, 200, 200),
    )),
    (1, 'Im a bender Long', 7200, (
        (100, 0, 1, 1, 500, 100, 500),
        (200, 0, 2, 7, 500, 100, 500),
        (300, 1, 20, 0, 0, 0, 0),
        (1400, 0, 1, 2, 100, 400, 100),
        (1400, 0, 2, 8, 600, 100, 500),
        (2100, 0, 1, 5, 400, 300, 300),
        (2700, 0, 2, 7, 700, 100, 300),
        (3200, 0, 1, 2, 100, 200, 200),
        (4000, 0, 1, 11, 200, 500, 500),
        (4100, 0, 2, 8, 500, 500, 500),
        (4100, 1, 25, 1, 0, 0, 0),
        (5800, 0, 1, 12, 500, 100, 500),
        (6000, 0, 2, 7, 500, 200, 500),
        (6000, 1, 26, 2, 0, 0, 0),
    )),
)
