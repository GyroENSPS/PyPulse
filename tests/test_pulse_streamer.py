# Tests unitaires pour le driver PulseStreamer (sans matériel)
import unittest
from unittest.mock import MagicMock, patch
from hardware.pulse_streamer import Pattern, PulseStreamerDriver


class TestPattern(unittest.TestCase):

    def test_get_length_single_channel(self):
        p = Pattern()
        p.set_digital(0, [(100, 1), (200, 0)])
        self.assertEqual(p.get_length(0), 300)

    def test_equalize(self):
        p = Pattern()
        p.set_digital(0, [(100, 1)])
        p.set_digital(1, [(50, 1)])
        p.equalize()
        self.assertEqual(p.get_length(0), p.get_length(1))

    def test_repeat(self):
        p = Pattern()
        p.set_digital(0, [(100, 1), (100, 0)])
        p.repeat(3)
        self.assertEqual(p.get_length(0), 600)


class TestPulseStreamerDriver(unittest.TestCase):

    @patch('hardware.pulse_streamer.PulseStreamer')
    def test_connect(self, mock_ps_class):
        driver = PulseStreamerDriver(ip="169.254.8.2")
        result = driver.connect()
        self.assertTrue(result)
        self.assertTrue(driver.connected)

    @patch('hardware.pulse_streamer.PulseStreamer')
    def test_load_pattern_not_connected(self, mock_ps_class):
        driver = PulseStreamerDriver()
        with self.assertRaises(RuntimeError):
            driver.load_pattern([[]] * 10)


if __name__ == '__main__':
    unittest.main()
