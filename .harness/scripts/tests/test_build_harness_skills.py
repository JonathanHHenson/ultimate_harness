"""Exercise the builder with isolated checkouts and inspect what it publishes."""

from functools import cached_property
from pathlib import Path
from shutil import copy2
import subprocess
import sys
from tempfile import TemporaryDirectory
import tomllib
from typing import cast
import unittest

REPO = Path(__file__).resolve().parents[3]
SKILLS = ("install-harness", "evolve-harness")
CATALOG = "skills_src/harness-files.toml"
BUILDER = "scripts/build_harness_skills.py"


class BuildHarnessSkillsTests(unittest.TestCase):
    @cached_property
    def checkout(self) -> Path:
        return Path(self.enterContext(TemporaryDirectory()))

    @cached_property
    def exported(self) -> set[str]:
        catalog = tomllib.loads((REPO / CATALOG).read_text(encoding="utf-8"))
        return {name for component in catalog.values() for name in cast(list[str], component["files"])}

    def setUp(self) -> None:
        entrypoints = {f"skills_src/{skill}/SKILL.md" for skill in SKILLS}
        for name in self.exported | entrypoints | {CATALOG, BUILDER}:
            target = self.checkout / name
            target.parent.mkdir(parents=True, exist_ok=True)
            _ = copy2(REPO / name, target)

    def payload(self, skill: str) -> Path:
        return self.checkout / "skills_src" / skill / "assets/harness"

    def build(self, *, successful: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(self.checkout / BUILDER)],
            cwd=self.checkout / "skills_src", capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0 if successful else 1, result.stderr)
        return result

    def test_both_skills_export_only_catalogued_files(self) -> None:
        excluded = (
            "AGENTS.md", "README.md", ".gitignore", ".harness/VALIDATE.md",
            ".harness/features/2026-11-19-project-history/DEFINITION.toml",
            ".harness/.venv/pyvenv.cfg", ".harness/scripts/project-task.py",
            ".harness/validation/harness-guidance.md", ".harness/validation/harness-scripts.md",
            ".scratch/session/private.md", "docs/TECHNICAL.md", "docs/agents/closeout.md",
            ".github/workflows/private.yml",
        )
        for name in excluded:
            source = self.checkout / name
            source.parent.mkdir(parents=True, exist_ok=True)
            _ = source.write_text("Project-specific fixture\n", encoding="utf-8")

        self.build()

        for skill in SKILLS:
            payload = self.payload(skill)
            actual = {path.relative_to(payload).as_posix() for path in payload.rglob("*") if path.is_file()}
            self.assertEqual(actual, self.exported | {"catalog.toml"})
            self.assertTrue(actual.isdisjoint(excluded))
            for name in self.exported:
                self.assertEqual((payload / name).read_bytes(), (self.checkout / name).read_bytes())
            self.assertEqual((payload / "catalog.toml").read_bytes(), (self.checkout / CATALOG).read_bytes())

    def test_rebuild_refreshes_sources_and_removes_stale_assets(self) -> None:
        self.build()
        source = self.checkout / ".harness/validation/security-review.md"
        changed = b"# Updated guidance\n"
        _ = source.write_bytes(changed)
        for skill in SKILLS:
            _ = (self.payload(skill) / "obsolete.md").write_text("Old output", encoding="utf-8")

        self.build()

        for skill in SKILLS:
            self.assertEqual((self.payload(skill) / source.relative_to(self.checkout)).read_bytes(), changed)
            self.assertFalse((self.payload(skill) / "obsolete.md").exists())
            self.assertEqual(
                (self.payload(skill).parents[1] / "SKILL.md").read_bytes(),
                (REPO / "skills_src" / skill / "SKILL.md").read_bytes(),
            )

    def test_invalid_input_preserves_an_existing_build(self) -> None:
        self.build()
        relative = ".harness/scripts/init_venv.py"
        source = self.checkout / relative
        original = source.read_bytes()
        source.unlink()
        self.assertIn(relative, self.build(successful=False).stderr)
        target = self.checkout / "unlisted.py"
        _ = target.write_text("Unlisted content", encoding="utf-8")
        source.symlink_to(target)
        self.assertIn(relative, self.build(successful=False).stderr)

        for skill in SKILLS:
            self.assertEqual((self.payload(skill) / relative).read_bytes(), original)

    def test_linked_destination_is_left_untouched(self) -> None:
        destination = self.payload(SKILLS[1])
        destination.parent.mkdir()
        unrelated = self.checkout / "unrelated"
        unrelated.mkdir()
        destination.symlink_to(unrelated, target_is_directory=True)

        self.build(successful=False)

        self.assertTrue(destination.is_symlink())
        self.assertEqual(list(unrelated.iterdir()), [])
        self.assertFalse(self.payload(SKILLS[0]).exists())
