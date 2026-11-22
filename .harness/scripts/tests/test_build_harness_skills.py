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
SKILL = "install-harness"
ENTRY = f"skills_src/{SKILL}/SKILL.md"
CATALOG = "skills_src/harness-files.toml"
BUILDER = "scripts/build_harness_skills.py"


class BuildHarnessSkillsTests(unittest.TestCase):
    @cached_property
    def checkout(self) -> Path:
        checkout = Path(self.enterContext(TemporaryDirectory()))
        for name in self.exported | {ENTRY, CATALOG, BUILDER}:
            target = checkout / name
            target.parent.mkdir(parents=True, exist_ok=True)
            _ = copy2(REPO / name, target)
        return checkout

    @cached_property
    def exported(self) -> set[str]:
        catalog = cast(
            dict[str, dict[str, list[str]]],
            tomllib.loads((REPO / CATALOG).read_text(encoding="utf-8")),
        )
        return {name for component in catalog.values() for name in component["files"]}

    def payload(self) -> Path:
        return self.checkout / "skills_src" / SKILL / "assets/harness"

    def build(self, *, successful: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(self.checkout / BUILDER)],
            cwd=self.checkout / "skills_src", capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0 if successful else 1, result.stderr)
        return result

    def test_install_harness_exports_only_catalogued_files(self) -> None:
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

        _ = self.build()

        payload = self.payload()
        actual = {path.relative_to(payload).as_posix() for path in payload.rglob("*") if path.is_file()}
        self.assertEqual(actual, self.exported | {"catalog.toml"})
        self.assertTrue(actual.isdisjoint(excluded))
        packages = {path.name for path in (self.checkout / "skills_src").iterdir() if path.is_dir()}
        self.assertEqual(packages, {SKILL})
        for name in self.exported:
            self.assertEqual((payload / name).read_bytes(), (self.checkout / name).read_bytes())
        self.assertEqual((payload / "catalog.toml").read_bytes(), (self.checkout / CATALOG).read_bytes())

    def test_rebuild_refreshes_sources_and_removes_stale_assets(self) -> None:
        _ = self.build()
        source = self.checkout / ".harness/validation/security-review.md"
        changed = b"# Updated guidance\n"
        _ = source.write_bytes(changed)
        payload = self.payload()
        _ = (payload / "obsolete.md").write_text("Old output", encoding="utf-8")

        _ = self.build()

        self.assertEqual((payload / source.relative_to(self.checkout)).read_bytes(), changed)
        self.assertFalse((payload / "obsolete.md").exists())
        self.assertEqual((self.checkout / ENTRY).read_bytes(), (REPO / ENTRY).read_bytes())

    def test_invalid_input_preserves_an_existing_build(self) -> None:
        _ = self.build()
        relative = ".harness/scripts/init_venv.py"
        source = self.checkout / relative
        original = source.read_bytes()
        source.unlink()
        self.assertIn(relative, self.build(successful=False).stderr)
        target = self.checkout / "unlisted.py"
        _ = target.write_text("Unlisted content", encoding="utf-8")
        source.symlink_to(target)
        self.assertIn(relative, self.build(successful=False).stderr)

        self.assertEqual((self.payload() / relative).read_bytes(), original)

    def test_linked_destination_is_left_untouched(self) -> None:
        destination = self.payload()
        destination.parent.mkdir()
        unrelated = self.checkout / "unrelated"
        unrelated.mkdir()
        destination.symlink_to(unrelated, target_is_directory=True)

        _ = self.build(successful=False)

        self.assertTrue(destination.is_symlink())
        self.assertEqual(list(unrelated.iterdir()), [])
