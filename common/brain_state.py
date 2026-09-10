"""Host-testable Brain UI state and timed antenna-test sequence."""

MODE_CLOCK = 0
MODE_SETTINGS = 1
MODE_BENDER = 2
MODE_PLAY = 3
MODE_TEST = 4
MODE_NAMES = ("CLOCK", "SETTINGS", "BENDER", "PLAY", "TEST")

TEST_RTC = 0
TEST_ANTENNA = 1
TEST_NAMES = ("RTC", "ANTENNA")


class BrainState:
    def __init__(self):
        self.mode = MODE_CLOCK
        self.test_selection = TEST_RTC

    def next_mode(self):
        self.mode = (self.mode + 1) % len(MODE_NAMES)
        return self.mode

    def select_next_test(self, direction):
        self.test_selection = (
            self.test_selection + direction
        ) % len(TEST_NAMES)
        return self.test_selection


class AntennaSequence:
    # (output index or None for Off, duration seconds)
    ONE_CYCLE = ((0, 2.0), (None, 1.0), (1, 2.0), (None, 1.0),
                 (2, 2.0), (None, 1.0))

    def __init__(self, repetitions=3):
        self.steps = self.ONE_CYCLE * repetitions
        self.index = 0
        self.next_at = None
        self.running = False

    def start(self, now):
        self.index = 0
        self.running = True
        self.next_at = now + self.steps[0][1]
        return self.steps[0][0]

    def stop(self):
        self.running = False
        self.next_at = None
        return None

    def update(self, now):
        if not self.running or now < self.next_at:
            return False, None
        self.index += 1
        if self.index >= len(self.steps):
            self.stop()
            return True, None
        output, duration = self.steps[self.index]
        self.next_at += duration
        return True, output
