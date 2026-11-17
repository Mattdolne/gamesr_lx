import unittest
import copy
import json
from pathlib import Path
import re
import tempfile
from types import SimpleNamespace
from unittest.mock import Mock

from tools.map_buttons import KeyState, find_device, load


class KeyStateTests(unittest.TestCase):
    def create(self, mode):
        self.events = []
        return KeyState({167: 87}, mode, lambda key, value: self.events.append((key, value)))

    def test_tap_ignores_repeat_duplicate_press_and_release(self):
        state = self.create('tap')
        for value in (1, 1, 2, 2, 0, 0):
            state.event(167, value)
        self.assertEqual(self.events, [(87, 1), (87, 0)])
        state.event(167, 1)
        self.assertEqual(self.events, [(87, 1), (87, 0)] * 2)

    def test_tap_disconnect_does_not_emit_an_extra_release(self):
        state = self.create('tap')
        state.event(167, 1)
        state.release_all()
        self.assertEqual(self.events, [(87, 1), (87, 0)])
        self.assertFalse(state.down)
        self.assertFalse(state.held)

    def test_hold_cleanup_releases_once_and_allows_new_press(self):
        state = self.create('hold')
        for value in (1, 1, 2):
            state.event(167, value)
        self.assertEqual(self.events, [(87, 1)])
        state.release_all()
        state.release_all()
        state.event(167, 0)
        self.assertEqual(self.events, [(87, 1), (87, 0)])
        state.event(167, 1)
        state.event(167, 0)
        self.assertEqual(self.events, [(87, 1), (87, 0)] * 2)

    def test_conventional_buttons_are_ignored(self):
        state = self.create('tap')
        for source in (304, 305):
            state.event(source, 1)
            state.event(source, 0)
        self.assertEqual(self.events, [])


class ConfigurationAndCaptureTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.config = json.loads((self.root / 'config/mapping.json').read_text())

    def read_config(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'mapping.json'
            path.write_text(json.dumps(data))
            return load(path)

    def test_configured_share_source_and_target(self):
        _, mapping = self.read_config(self.config)
        self.assertEqual(mapping, {167: 87})

    def test_rear_aliases_to_a_or_b_are_rejected(self):
        for button, source, target in [('L4', 'BTN_SOUTH', 'KEY_F9'),
                                        ('R4', 'BTN_EAST', 'KEY_F10')]:
            with self.subTest(button=button):
                config = copy.deepcopy(self.config)
                config['mapping'][button] = target
                config['verified_sources'][button] = source
                with self.assertRaisesRegex(ValueError, 'origem independente não validada'):
                    self.read_config(config)

    def test_rear_without_source_is_rejected(self):
        for button in ('L4', 'R4'):
            with self.subTest(button=button):
                config = copy.deepcopy(self.config)
                config['mapping'][button] = 'KEY_F9'
                with self.assertRaisesRegex(ValueError, 'sem origem independente validada'):
                    self.read_config(config)

    def test_recorded_hardware_input_reaches_only_share_target(self):
        _, mapping = self.read_config(self.config)
        emitted = []
        state = KeyState(mapping, 'tap', lambda *event: emitted.append(event))
        seen = []
        log = self.root / 'evidence/001/evtest-post-restart.txt'
        for line in log.read_text().splitlines():
            match = re.search(r'type 1 \(EV_KEY\), code (\d+) .* value ([012])', line)
            if match:
                source, value = map(int, match.groups())
                seen.append((source, value))
                state.event(source, value)
        self.assertEqual(seen, [(304, 1), (304, 0), (305, 1), (305, 0),
                                (167, 1), (167, 0)])
        self.assertEqual(emitted, [(87, 1), (87, 0)])

    def test_disconnect_during_initial_state_read_closes_and_skips_device(self):
        failed = Mock(info=SimpleNamespace(vendor=0x3537, product=0x1010))
        failed.capabilities.return_value = {1: [167]}
        failed.active_keys.side_effect = OSError('device removed')
        ready = Mock(info=SimpleNamespace(vendor=0x3537, product=0x1010))
        ready.capabilities.return_value = {1: [167]}
        ready.active_keys.return_value = [167]
        device, blocked = find_device(self.config, {167: 87}, ['gone', 'ready'],
                                      opener=Mock(side_effect=[failed, ready]))
        self.assertIs(device, ready)
        self.assertEqual(blocked, {167})
        failed.close.assert_called_once()
        ready.close.assert_not_called()


if __name__ == '__main__':
    unittest.main()
