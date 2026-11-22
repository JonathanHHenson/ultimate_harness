"""Behavior checks for the portable adoption wording preflight."""

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

CHECKER = Path(__file__).resolve().parents[1] / "check_adoption_options.py"


class AdoptionOptionTests(unittest.TestCase):
    def check_page(
        self, decisions: dict[str, dict[str, str]]
    ) -> subprocess.CompletedProcess[str]:
        fields = [
            {
                "id": decision,
                "type": "radio",
                "label": f"How should we handle {decision}?",
                "options": [
                    {"value": value, "label": label} for value, label in options.items()
                ],
            }
            for decision, options in decisions.items()
        ]
        with TemporaryDirectory() as directory:
            page = Path(directory) / "page.json"
            _ = page.write_text(
                json.dumps({"title": "Adoption", "fields": fields}), encoding="utf-8"
            )
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(page)],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
            self.assertEqual(list(Path(directory).iterdir()), [page])
            return result

    def test_specific_choices_pass(self) -> None:
        result = self.check_page(
            {
                "merge-gate": {
                    "ci": "Block pull requests while a feature is unfinished (Recommended)",
                    "local": "Keep the feature completion check local",
                    "skip": "Skip the completion check; reviewers verify feature status manually",
                },
                "ledger": {
                    "link": "Link feature records to council ticket IDs",
                    "native": "Keep the council ledger as the only feature record",
                },
            }
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_stock_and_copied_choices_identify_every_affected_field(self) -> None:
        result = self.check_page(
            {
                "scratch-space": {
                    "adopt": "Include in the planned harness (Recommended)",
                    "defer": "Defer; leave this capability unavailable",
                    "copy": "Keep the project workflow as it is",
                },
                "feature-memory": {
                    "adopt": "Add dated feature records to the project",
                    "copy": "Keep the project workflow as it is (recommended)",
                },
            }
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for option in (
            "scratch-space/adopt",
            "scratch-space/defer",
            "scratch-space/copy",
            "feature-memory/copy",
        ):
            self.assertIn(option, result.stdout)
        self.assertNotIn("feature-memory/adopt", result.stdout)
