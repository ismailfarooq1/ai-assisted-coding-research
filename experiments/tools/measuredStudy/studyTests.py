"""Meaningful failure-boundary checks for timers, usage and frozen design inputs."""
import json
from pathlib import Path
import tempfile
import unittest

import studyRunner as study
from reviewServer import ReviewTimer

class TimerTests(unittest.TestCase):
    def setUp(self):
        self.tick = 0
        self.timer = ReviewTimer(lambda: self.tick)

    def test_idle_and_breaks_are_not_human_work(self):
        self.tick = 100
        self.assertEqual(self.timer.value()['activeSeconds'], 0)
        self.timer.resume(); self.tick = 105; self.timer.heartbeat(); self.tick = 108; self.timer.pause()
        self.tick = 900
        self.assertEqual(self.timer.value()['activeSeconds'], 8)
        self.timer.resume(); self.tick = 903; self.timer.pause()
        self.assertEqual(self.timer.value()['activeSeconds'], 11)

    def test_lost_browser_is_bounded_by_last_heartbeat(self):
        self.timer.resume(); self.tick = 3; self.timer.heartbeat(); self.tick = 1000
        result = self.timer.value()
        self.assertFalse(result['active'])
        self.assertEqual(result['activeSeconds'], 13)

class AccountingTests(unittest.TestCase):
    def parse(self, events, resource):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / 'events.jsonl').write_text('\n'.join(json.dumps(e) for e in events))
            study.write(output / 'resource.json', resource)
            return study.event_usage(output)

    def test_completed_usage_subsets_not_double_counted(self):
        result = self.parse([{'type':'turn.completed','usage':{'input_tokens':100,'cached_input_tokens':80,'output_tokens':20,'reasoning_output_tokens':5}}], {'timedOut':False,'rolloutUsageObservations':[{'input_tokens':100,'output_tokens':20,'total_tokens':120}]})
        self.assertEqual(result['totalTokens'], 120)
        self.assertTrue(result['crossCheckMatches'])

    def test_failure_recovers_cumulative_usage_without_summing_snapshots(self):
        result = self.parse([{'type':'turn.failed'}], {'timedOut':True,'rolloutUsageObservations':[{'input_tokens':100,'output_tokens':20,'total_tokens':120},{'input_tokens':150,'output_tokens':30,'total_tokens':180}]})
        self.assertEqual(result['totalTokens'], 180)
        self.assertEqual(result['coverage'], 'partial-or-unreported')

    def test_missing_usage_is_not_zero(self):
        self.assertIsNone(self.parse([], {})['totalTokens'])

    def test_pack_rejects_unsourced_claims(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                study.render_pack({'claims':[{'id':'c1','topic':'x','text':'invented','sources':['outside.md']}]},Path(directory),[])

if __name__ == '__main__':
    unittest.main()
