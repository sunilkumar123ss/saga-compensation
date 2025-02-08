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




if __name__ == '__main__':
    unittest.main()
