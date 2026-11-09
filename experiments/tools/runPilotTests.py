"""Checks for resource accounting and independent change detection in the pilot runner."""
import json
from pathlib import Path
import tempfile
import unittest
import shutil
import subprocess
import runPilot


class UsageAccountingTests(unittest.TestCase):
    def parse(self, events):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            path.write_text("\n".join(json.dumps(event) for event in events))
            return runPilot.usage_from_events(path)

    def test_cached_and_reasoning_tokens_are_subsets(self):
        result = self.parse([{"type": "turn.completed", "usage": {"input_tokens": 100,
            "cached_input_tokens": 80, "output_tokens": 20, "reasoning_output_tokens": 10}}])
        self.assertEqual(result["totalTokens"], 120)
        self.assertEqual(result["cachedInputTokens"], 80)
        self.assertEqual(result["reasoningOutputTokens"], 10)

    def test_missing_usage_is_unknown(self):
        result = self.parse([{"type": "turn.failed", "error": {"message": "interrupted"}}])
        self.assertIsNone(result["totalTokens"])
        self.assertEqual(result["failedTurnEvents"], 1)

    def test_zero_is_observed_zero(self):
        result = self.parse([{"type": "turn.completed", "usage": {"input_tokens": 0, "output_tokens": 0}}])
        self.assertEqual(result["totalTokens"], 0)
        self.assertIsNone(result["reasoningOutputTokens"])

    def test_distinct_completed_turns_are_counted_once(self):
        result = self.parse([{"type": "item.completed", "usage": {"input_tokens": 999}},
            {"type": "turn.completed", "usage": {"input_tokens": 100, "output_tokens": 20}},
            {"type": "turn.completed", "usage": {"input_tokens": 50, "output_tokens": 10}}])
        self.assertEqual(result["completedTurns"], 2)
        self.assertEqual(result["totalTokens"], 180)

    def test_change_scope_does_not_trust_candidate_index_flags(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            project = destination / "project"
            baseline = runPilot.ROOT / "experiments/existingWorkflow/memos"
            shutil.copytree(baseline, project)
            name = "web/src/lib/release-version.ts"
            target = project / name
            target.write_text(target.read_text() + "\n// unexpected change\n")
            subprocess.run(["git", "-C", str(project), "update-index", "--assume-unchanged", name], check=True)
            record = runPilot.capture_changes(project, destination, {"snapshot": runPilot.SNAPSHOT["commit"],
                "permittedProductionChanges": ["web/src/lib/suggestion-expression.ts"], "permittedTestChangesPrefix": "web/tests/"})
            self.assertIn(name, record["files"])
            self.assertFalse(record["permitted"])
            self.assertIn(b"unexpected change", (destination / "changes.patch").read_bytes())


if __name__ == "__main__":
    unittest.main()
