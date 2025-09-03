import importlib.util
from pathlib import Path
import sys
import unittest
_spec = importlib.util.spec_from_file_location('lab_' + Path(__file__).parent.name.replace('-', '_'), Path(__file__).with_name('main.py'))
m = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = m
_spec.loader.exec_module(m)

class SagaTests(unittest.TestCase):

    @staticmethod
    def fail():
        raise RuntimeError('synthetic failure')

    def test_all_success_no_compensation(self):
        calls = []
        r = m.run([m.Step('a', lambda : 7, lambda value: calls.append(value))])
        self.assertEqual(r['status'], 'complete')
        self.assertEqual(calls, [])

    def test_reverse_compensation(self):
        calls = []
        r = m.run([m.Step('a', lambda : 1, lambda value: calls.append(value)), m.Step('b', lambda : 2, lambda value: calls.append(value)), m.Step('c', self.fail, lambda value: None)])
        self.assertEqual(calls, [2, 1])
        self.assertEqual(r['status'], 'compensated')

    def test_compensation_failure_does_not_skip_remaining(self):
        calls = []

        def bad(value):
            raise RuntimeError('undo failed')
        r = m.run([m.Step('a', lambda : 1, lambda value: calls.append(value)), m.Step('b', lambda : 2, bad), m.Step('c', self.fail, lambda value: None)])
        self.assertEqual(calls, [1])
        self.assertEqual(r['failed_compensations'], ['b'])
        self.assertEqual(r['status'], 'compensation_incomplete')

    def test_failing_step_not_compensated(self):
        calls = []
        m.run([m.Step('a', self.fail, lambda value: calls.append(value))])
        self.assertEqual(calls, [])

    def test_validates_before_any_action(self):
        calls = []
        step = m.Step('a', lambda : calls.append('effect'), lambda value: None)
        with self.assertRaises(ValueError):
            m.run([step, step])
        self.assertEqual(calls, [])

if __name__ == '__main__':
    unittest.main()
