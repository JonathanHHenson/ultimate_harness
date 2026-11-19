"""Exercise the project skill package check through its command line."""

from functools import cached_property
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "check_skill_packages.py"


class SkillPackageTests(unittest.TestCase):
    @cached_property
    def root(self) -> Path:
        return Path(self.enterContext(tempfile.TemporaryDirectory()))

    @property
    def packages(self) -> Path:
        return self.root / ".agents" / "skills"

    def setUp(self) -> None:
        self.packages.mkdir(parents=True)

    def add_package(self, name: str, content: str | None = None) -> None:
        directory = self.packages / name
        directory.mkdir()
        if content is not None:
            (directory / "SKILL.md").write_text(content, encoding="utf-8")

    def run_check(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, SCRIPT], cwd=self.root, capture_output=True, text=True, timeout=30,
        )

    def test_valid_skills_may_include_additional_metadata(self):
        self.add_package("build-project", "---\nname: build-project\ndescription: Build the project.\n"
                         "compatibility: Run with a configured compiler.\n---\nUse the project build command.\n")
        self.add_package("review-project", "---\nname: review-project\ndescription: >\n"
                         "  Review project changes.\n---\nReview the changed interfaces.\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_bad_packages_fail_and_identify_each_package(self):
        self.add_package("missing-file")
        self.add_package("empty-description", '---\nname: empty-description\ndescription: " "\n---\nInstructions\n')
        self.add_package("mismatched-folder", "---\nname: another-name\ndescription: Inspect changes.\n---\nInstructions\n")
        self.add_package("invalid-yaml", "---\nname: [\n---\nInstructions\n")
        self.add_package("missing-body", "---\nname: missing-body\ndescription: Inspect changes.\n---\n")
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        for package in self.packages.iterdir():
            with self.subTest(package=package.name):
                self.assertIn(package.name, result.stderr)

    def test_empty_directory_fails(self):
        self.assertNotEqual(self.run_check().returncode, 0)

    def test_duplicate_metadata_is_rejected(self) -> None:
        self.add_package(
            "build-project",
            "---\nname: other-project\nname: build-project\ndescription: Build.\n---\nInstructions\n",
        )
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("build-project", result.stderr)
        self.assertIn("duplicate key", result.stderr)

    def test_yaml_errors_identify_the_package_without_echoing_content(self) -> None:
        self.add_package("malformed", "---\nname: malformed\ndescription: [unclosed-example\n---\nInstructions\n")
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("malformed", result.stderr)
        self.assertNotIn("unclosed-example", result.stderr)


if __name__ == "__main__":
    unittest.main()
