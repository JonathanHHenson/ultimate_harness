"""Behavior tests for persistent local session workspaces and ignore rules."""

from functools import cached_property
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
SCRIPT = SCRIPTS / "create_agent_session.py"


class AgentSessionTests(unittest.TestCase):
    @cached_property
    def root(self) -> Path:
        return Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()

    def command(self, *arguments: str | Path, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, arguments)],
            cwd=cwd or self.root, capture_output=True, text=True, timeout=30,
        )

    def workspace(self, *arguments: str | Path, cwd: Path | None = None) -> Path:
        result = self.command(*arguments, cwd=cwd)
        self.assertEqual(result.returncode, 0, result.stderr)
        path = Path(result.stdout.strip())
        self.assertTrue(path.is_absolute())
        self.assertTrue(path.is_dir())
        return path

    def test_default_root_creates_usable_workspace_in_reserved_directory(self):
        path = self.workspace()
        self.assertEqual(path.parent, self.root / ".scratch/agent_sessions")
        (path / "notes.md").write_text("Session notes")
        self.assertEqual((path / "notes.md").read_text(), "Session notes")

    def test_new_sessions_are_unique_and_preserve_human_and_earlier_session_files(self):
        scratch = self.root / ".scratch"
        scratch.mkdir()
        human = scratch / "human-notes.md"
        human.write_text("Human working notes")
        first = self.workspace()
        artifact = first / "experiment.py"
        artifact.write_text("print('experiment')\n")
        second = self.workspace()
        self.assertNotEqual(first, second)
        self.assertEqual(human.read_text(), "Human working notes")
        self.assertEqual(artifact.read_text(), "print('experiment')\n")
        self.assertTrue(first.is_dir())

    def test_explicit_root_works_from_another_directory(self):
        project = self.root / "chosen-project"
        project.mkdir()
        workspace = self.workspace("--root", project)
        self.assertEqual(workspace.parent, project / ".scratch/agent_sessions")
        self.assertFalse((self.root / ".scratch").exists())

    def test_unusable_storage_fails_without_overwriting_existing_data(self):
        for parent in (".scratch", ".scratch/agent_sessions"):
            with self.subTest(parent=parent):
                project = self.root / parent.replace("/", "-")
                project.mkdir()
                conflict = project / parent
                conflict.parent.mkdir(parents=True, exist_ok=True)
                conflict.write_text("Existing document")
                result = self.command("--root", project)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(conflict.read_text(), "Existing document")

    def test_symlinked_storage_is_rejected_without_writing_to_its_target(self):
        for parent in (".scratch", ".scratch/agent_sessions"):
            with self.subTest(parent=parent):
                project = self.root / parent.replace("/", "-")
                project.mkdir()
                outside = project / "outside"
                outside.mkdir()
                sentinel = outside / "keep.md"
                sentinel.write_text("Keep this file")
                link = project / parent
                link.parent.mkdir(parents=True, exist_ok=True)
                link.symlink_to(outside, target_is_directory=True)
                self.assertNotEqual(self.command("--root", project).returncode, 0)
                self.assertEqual(list(outside.iterdir()), [sentinel])
                self.assertEqual(sentinel.read_text(), "Keep this file")

    def test_actual_ignore_file_excludes_shared_and_session_artifacts_only(self):
        (self.root / ".gitignore").write_text((SCRIPTS.parents[1] / ".gitignore").read_text())
        subprocess.run(["git", "init", "-q", str(self.root)], check=True, capture_output=True)
        for name in (".scratch/human-notes.md", ".scratch/agent_sessions/session/experiment.py"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Local artifact")
            result = subprocess.run(["git", "-C", str(self.root), "check-ignore", name], capture_output=True)
            self.assertEqual(result.returncode, 0)
        for name in ("AGENTS.md", ".harness/scripts/create_agent_session.py", "src/app.py"):
            result = subprocess.run(["git", "-C", str(self.root), "check-ignore", name], capture_output=True)
            self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
