import unittest

from common import protocol
from common.brain_state import AntennaSequence, BrainState, MODE_CLOCK, MODE_TEST, TEST_ANTENNA
from common.brain_settings import ClockSettings, local_hour, utc_hour
from common.display_model import DisplayGeometry, LocalModeState, clock_frame, scrolling_frame_at, scrolling_frame_count, scrolling_frames, text_frame
from common.font3x5 import text_width


class DisplayModelTests(unittest.TestCase):
    def test_serpentine_geometry_maps_every_pixel_once(self):
        geometry = DisplayGeometry(3, 5, 11)
        indices = {geometry.pixel_index(x, y) for y in range(geometry.height) for x in range(geometry.width)}
        self.assertEqual(indices, set(range(165)))

    def test_mode_cycle_defaults_to_target(self):
        state = LocalModeState()
        self.assertEqual(state.mode, protocol.LOCAL_TARGET)
        self.assertTrue(state.accepts_visual_commands)
        self.assertEqual(state.advance(), protocol.LOCAL_TEST)
        self.assertFalse(state.accepts_visual_commands)
        self.assertEqual(state.advance(), protocol.LOCAL_BENDER)
        self.assertEqual(state.advance(), protocol.LOCAL_TARGET)

    def test_boot_identity_fits_both_development_displays(self):
        self.assertLessEqual(text_width("E30"), 18)
        self.assertLessEqual(text_width("M31"), 15)

    def test_scrolling_target_mode_enters_and_leaves_viewport(self):
        geometry = DisplayGeometry(3, 5, 11)
        frames = tuple(scrolling_frames(geometry, "TARGET MODE"))
        self.assertFalse(any(frames[0]))
        self.assertTrue(any(any(frame) for frame in frames[1:-1]))
        self.assertFalse(any(frames[-1]))
        self.assertEqual(len(frames), scrolling_frame_count(geometry, "TARGET MODE"))
        self.assertEqual(frames[3], scrolling_frame_at(geometry, "TARGET MODE", 3))

    def test_centered_text_and_clock_stay_in_bounds(self):
        eyes = DisplayGeometry(2, 9, 16)
        mouth = DisplayGeometry(3, 5, 11)
        self.assertEqual(len(text_frame(eyes, "E30")), 288)
        self.assertEqual(len(text_frame(mouth, "M31")), 165)
        self.assertEqual(len(clock_frame(eyes, 12, 34, True)), 288)

    def test_clock_digits_do_not_move_when_colon_blinks(self):
        eyes = DisplayGeometry(2, 9, 16)
        colon_on = clock_frame(eyes, 12, 34, True)
        colon_off = clock_frame(eyes, 12, 34, False)
        differing = [index for index, pair in enumerate(zip(colon_on, colon_off))
                     if pair[0] != pair[1]]
        self.assertEqual(len(differing), 2)
        self.assertTrue(all(colon_on[index] and not colon_off[index]
                            for index in differing))


class ProtocolTests(unittest.TestCase):
    def test_clock_packet_and_validation(self):
        self.assertEqual(protocol.clock_packet(7, 12, 34), bytes((0x20, 7, 12, 34, 1)))
        with self.assertRaises(ValueError):
            protocol.clock_packet(7, 24, 0)

    def test_development_text_packet(self):
        self.assertEqual(protocol.dev_text_packet(9, "test rtc"), b"\x75\x09TEST RTC")
        with self.assertRaises(ValueError):
            protocol.dev_text_packet(9, "")

    def test_status_flags_decode_named_local_modes(self):
        self.assertEqual(protocol.local_mode_from_status(protocol.LIFECYCLE_WAITING_FOR_BRAIN, 0), protocol.LOCAL_TARGET)
        self.assertEqual(protocol.local_mode_from_status(protocol.LIFECYCLE_LOCAL_TEST, protocol.STATUS_FLAG_LOCAL_TEST), protocol.LOCAL_TEST)
        self.assertEqual(protocol.local_mode_from_status(protocol.LIFECYCLE_STANDALONE_NORMAL, protocol.STATUS_FLAG_LOCAL_BENDER), protocol.LOCAL_BENDER)


class BrainStateTests(unittest.TestCase):
    def test_top_level_mode_and_test_selection_cycles(self):
        state = BrainState()
        self.assertEqual(state.mode, MODE_CLOCK)
        for _ in range(4):
            state.next_mode()
        self.assertEqual(state.mode, MODE_TEST)
        self.assertEqual(state.select_next_test(1), TEST_ANTENNA)

    def test_antenna_sequence_has_three_rgb_cycles_and_finishes_off(self):
        sequence = AntennaSequence(3)
        states = [sequence.start(0.0)]
        while sequence.running:
            changed, output = sequence.update(sequence.next_at)
            self.assertTrue(changed)
            states.append(output)
        self.assertEqual(states.count(0), 3)
        self.assertEqual(states.count(1), 3)
        self.assertEqual(states.count(2), 3)
        self.assertIsNone(states[-1])

    def test_mouth_chase_visits_every_led_without_skipping(self):
        mouth = DisplayGeometry(3, 5, 11)
        path = []
        for logical in range(mouth.pixel_count):
            x = logical // mouth.height
            local_y = logical % mouth.height
            module_x = x % mouth.module_width
            y = local_y if module_x % 2 == 0 else mouth.height - 1 - local_y
            path.append(mouth.pixel_index(x, y))
        self.assertEqual(path, list(range(mouth.pixel_count)))

    def test_clock_settings_round_trip_and_utc_conversion(self):
        storage = bytearray(32)
        settings = ClockSettings()
        settings.timezone = 3
        settings.dst = True
        settings.use_24_hour = True
        settings.save(storage)
        restored = ClockSettings()
        self.assertTrue(restored.load(storage))
        self.assertEqual(restored.timezone, 3)
        self.assertTrue(restored.dst)
        self.assertTrue(restored.use_24_hour)
        for hour in range(24):
            self.assertEqual(
                local_hour(utc_hour(hour, 3, True), 3, True), hour
            )


if __name__ == "__main__":
    unittest.main()
