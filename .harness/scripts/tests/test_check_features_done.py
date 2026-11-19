"""Verify the standalone CI command against isolated checkout fixtures."""

from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

SOURCE = Path(__file__).resolve().parents[3] / "scripts/check_features_done.py"


class CheckFeaturesDoneTests(unittest.TestCase):
    def run_check(
        self, *records: tuple[str, str | None], pending: bool = False, linked_definition: bool = False
    ) -> subprocess.CompletedProcess[str]:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            command = root / "scripts" / SOURCE.name
            command.parent.mkdir()
            _ = shutil.copyfile(SOURCE, command)
            features = root / ".harness/features"
            for name, contents in records:
                feature = features / f"2026-11-19-{name}"
                feature.mkdir(parents=True)
                if contents is not None:
                    definition = feature / "DEFINITION.toml"
                    if linked_definition:
                        target = root / "other.toml"
                        _ = target.write_text(contents, encoding="utf-8")
                        definition.symlink_to(target)
                    else:
                        _ = definition.write_text(contents, encoding="utf-8")
                if pending:
                    _ = (feature / ".status-pending.json").write_text("{}", encoding="utf-8")
            # A CI job can invoke the script from a different working directory.
            return subprocess.run(
                [sys.executable, str(command)], cwd=command.parent, capture_output=True,
                text=True, timeout=30,
            )

    def test_done_and_empty_checkouts_pass(self) -> None:
        complete = 'status = "DONE"\n[[requirements]]\nid = "R1"\nstatus = "DONE"\n'
        for result in (self.run_check(), self.run_check(("complete", complete))):
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_reports_each_unfinished_feature_and_requirement(self) -> None:
        testing = 'status = "TEST"\nrequirements = []\n'
        blocked = 'status = "DONE"\n[[requirements]]\nid = "R1"\nstatus = "BLOCKED"\n'
        result = self.run_check(("in-testing", testing), ("blocked-requirement", blocked))
        self.assertEqual(result.returncode, 1)
        for message in ("in-testing", "TEST", "blocked-requirement", "R1", "BLOCKED"):
            self.assertIn(message, result.stderr)

    def test_rejects_malformed_and_missing_definitions_and_requirements(self) -> None:
        result = self.run_check(
            ("invalid", 'status = "unfinished-example\n'),
            ("missing", None),
            ("missing-requirements", 'status = "DONE"\n'),
            ("invalid-status", 'status = "unexpected-example"\nrequirements = []\n'),
        )
        self.assertEqual(result.returncode, 1)
        for feature in ("invalid", "missing", "missing-requirements", "invalid-status"):
            self.assertIn(feature, result.stderr)
        self.assertNotIn("unfinished-example", result.stderr)
        self.assertNotIn("unexpected-example", result.stderr)

    def test_pending_update_fails_even_when_record_says_done(self) -> None:
        result = self.run_check(("interrupted", 'status = "DONE"\nrequirements = []\n'), pending=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("interrupted", result.stderr)
        self.assertIn("status update pending", result.stderr)

    def test_rejects_a_symlinked_definition(self) -> None:
        result = self.run_check(("linked", 'status = "DONE"\nrequirements = []\n'), linked_definition=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("linked", result.stderr)


if __name__ == "__main__":
    unittest.main()
