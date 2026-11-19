"""Behavior tests for feature memory, executed in isolated temporary projects."""

from concurrent.futures import ThreadPoolExecutor
from functools import cached_property
from pathlib import Path
import subprocess
import sys
import tempfile
from threading import Barrier
import tomllib
import unittest

import tomlkit
import yaml

SCRIPTS = Path(__file__).resolve().parents[1]
PHASES = ("RESEARCH", "DESIGN", "IMPLEMENT", "TEST", "DONE")

DEFINITION = '''description = "Cache build results by input digest so unchanged projects avoid compilation."
documentation = ["docs/build-cache.md", "https://example.com/build-interface"]
status = "RESEARCH"

[[requirements]]
id = "F-1"
kind = "functional"
description = "Return a cached artifact when source files and compiler options match."
definition_of_done = "An unchanged build returns the same artifact without invoking the compiler."
status = "TODO"
blocked_reason = ""

[[requirements]]
id = "NF-1"
kind = "non-functional"
description = "Reject corrupt cache entries and rebuild without losing the diagnostic."
definition_of_done = "A corrupt entry triggers a successful rebuild and a visible diagnostic."
status = "TODO"
blocked_reason = ""
'''


class FeatureMemoryTests(unittest.TestCase):
    @cached_property
    def root(self) -> Path:
        return Path(self.enterContext(tempfile.TemporaryDirectory()))

    @property
    def source(self) -> Path:
        return self.root / "initial.toml"

    @property
    def feature(self) -> Path:
        return self.root / ".harness/features/build-cache"

    def setUp(self) -> None:
        _ = self.source.write_text(DEFINITION)

    def command(self, script: str, *arguments: str, success: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / script), "build-cache", "--root", str(self.root), *arguments],
            capture_output=True, text=True, timeout=30,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def create(self) -> None:
        self.command("create_feature.py", "--definition", str(self.source))

    def definition(self):
        return tomllib.loads((self.feature / "DEFINITION.toml").read_text())

    def log(self):
        return yaml.safe_load((self.feature / "WORKLOG.yaml").read_text())

    def seed(self, phase: str = "RESEARCH", state: str = "TODO", blocked_from: str = "WIP") -> None:
        definition = tomlkit.parse(DEFINITION)
        definition["status"] = phase
        for requirement in definition["requirements"]:
            requirement["status"] = state
            if state == "BLOCKED":
                requirement["blocked_reason"] = "Compiler access requires the build team's account grant."
                requirement["blocked_from"] = blocked_from
        (self.feature / "DEFINITION.toml").write_text(tomlkit.dumps(definition))

    def snapshot(self) -> dict[str, bytes]:
        return {path.name: path.read_bytes() for path in self.feature.iterdir()}

    def test_creation_has_three_readable_files_and_research_history(self):
        self.create()
        self.assertEqual(set(self.snapshot()), {"DEFINITION.toml", "DESIGN.md", "WORKLOG.yaml"})
        self.assertEqual(self.definition()["status"], "RESEARCH")
        for requirement in self.definition()["requirements"]:
            self.assertIn(requirement["id"], (self.feature / "DESIGN.md").read_text())
        self.assertIn("Cache build results", self.log()[0]["details"])

    def test_duplicate_creation_preserves_all_existing_memory(self):
        self.create()
        before = self.snapshot()
        self.command("create_feature.py", "--definition", str(self.source), success=False)
        self.assertEqual(self.snapshot(), before)

    def test_invalid_names_cannot_escape_feature_directory(self):
        for name in ("Build-Cache", "../outside", "build_cache", "build--cache", "-build"):
            with self.subTest(name=name):
                result = subprocess.run(
                    [sys.executable, str(SCRIPTS / "create_feature.py"), name,
                     "--root", str(self.root), "--definition", str(self.source)],
                    capture_output=True, text=True,
                )
                self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / ".harness/features").exists())

    def test_invalid_definitions_fail_before_creating_memory(self):
        cases = (
            DEFINITION.replace('status = "RESEARCH"', 'status = "DESIGN"'),
            DEFINITION.replace('status = "TODO"', 'status = "DONE"'),
            DEFINITION.replace('id = "NF-1"', 'id = "F-1"'),
            DEFINITION.replace('kind = "functional"', 'kind = "other"'),
            DEFINITION.replace('description = "Return a cached artifact when source files and compiler options match."', 'description = ""'),
            DEFINITION.replace('documentation = ["docs/build-cache.md", "https://example.com/build-interface"]', 'documentation = "not a list"'),
            'status = [invalid TOML',
        )
        for index, content in enumerate(cases):
            with self.subTest(index=index):
                self.source.write_text(content)
                self.command("create_feature.py", "--definition", str(self.source), success=False)
                self.assertFalse(self.feature.exists())

    def test_feature_transition_graph_all_pairs(self):
        self.create()
        for current_index, current in enumerate(PHASES):
            for target_index, target in enumerate(PHASES):
                with self.subTest(current=current, target=target):
                    self.seed(current, "DONE")
                    before = self.snapshot()
                    allowed = target_index < current_index or target_index == current_index + 1
                    self.command("set_feature_status.py", target, "--reason",
                                 "Reconciled the design and verification evidence for this phase.", success=allowed)
                    if allowed:
                        self.assertEqual(self.definition()["status"], target)
                        self.assertEqual(self.log()[-1]["phase"], target)
                    else:
                        self.assertEqual(self.snapshot(), before)

    def test_done_requires_every_requirement_done(self):
        self.create()
        for state in ("TODO", "WIP", "BLOCKED"):
            with self.subTest(state=state):
                self.seed("TEST", state)
                before = self.snapshot()
                self.command("set_feature_status.py", "DONE", "--reason", "Validation finished", success=False)
                self.assertEqual(self.snapshot(), before)
        self.seed("TEST", "DONE")
        self.command("set_feature_status.py", "DONE", "--reason", "All acceptance checks passed")
        self.assertEqual(self.definition()["status"], "DONE")

    def test_backward_phase_requires_ordered_forward_progress_again(self):
        self.create()
        self.seed("TEST", "DONE")
        self.command("set_feature_status.py", "RESEARCH", "--reason", "New platform constraints require research")
        self.command("set_feature_status.py", "TEST", "--reason", "Resume testing", success=False)
        for phase in ("DESIGN", "IMPLEMENT", "TEST", "DONE"):
            self.command("set_feature_status.py", phase, "--reason", "Completed the work for the preceding phase")

    def test_requirement_transition_graph_all_pairs(self):
        self.create()
        states = ("TODO", "WIP", "BLOCKED", "DONE")
        for current in states:
            for target in states:
                with self.subTest(current=current, target=target):
                    self.seed(state=current)
                    before = self.snapshot()
                    allowed = (current, target) in {
                        ("TODO", "WIP"), ("TODO", "BLOCKED"), ("WIP", "DONE"),
                        ("WIP", "BLOCKED"), ("BLOCKED", "WIP"), ("BLOCKED", "BLOCKED"),
                    }
                    arguments = ["F-1", target, "--reason", "Updated the cache implementation and its acceptance evidence."]
                    if target == "BLOCKED":
                        arguments += ["--blocked-reason", "The integration environment is unavailable; restore its credentials."]
                    self.command("set_requirement_status.py", *arguments, success=allowed)
                    if allowed:
                        self.assertEqual(self.definition()["requirements"][0]["status"], target)
                        self.assertEqual(self.definition()["requirements"][1]["status"], current)
                    else:
                        self.assertEqual(self.snapshot(), before)

    def test_blocked_requirement_resumes_its_exact_prior_state(self):
        self.create()
        for prior in ("TODO", "WIP"):
            with self.subTest(prior=prior):
                self.seed(state=prior)
                self.command("set_requirement_status.py", "F-1", "BLOCKED", "--reason", "Access request escalated",
                             "--blocked-reason", "The artifact store requires credentials from the platform team.")
                requirement = self.definition()["requirements"][0]
                self.assertEqual(requirement["blocked_from"], prior)
                self.assertIn("credentials", requirement["blocked_reason"])
                self.command("set_requirement_status.py", "F-1", "DONE", "--reason", "Access restored", success=False)
                self.command("set_requirement_status.py", "F-1", prior, "--reason", "Platform team granted artifact access")
                requirement = self.definition()["requirements"][0]
                self.assertEqual(requirement["status"], prior)
                self.assertFalse(requirement["blocked_reason"])
                self.assertFalse(requirement["blocked_from"])

    def test_blocking_requires_a_reason_and_invalid_changes_preserve_memory(self):
        self.create()
        for arguments in (
            ("F-1", "BLOCKED", "--reason", "Access unavailable"),
            ("F-1", "BLOCKED", "--reason", "Access unavailable", "--blocked-reason", "  "),
            ("F-1", "BLOCKED", "--reason", "", "--blocked-reason", "Waiting for credentials"),
            ("unknown-id", "WIP", "--reason", "Starting work"),
            ("F-1", "WIP", "--reason", "Starting work", "--blocked-reason", "Unexpected reason"),
        ):
            with self.subTest(arguments=arguments):
                before = self.snapshot()
                self.command("set_requirement_status.py", *arguments, success=False)
                self.assertEqual(self.snapshot(), before)

    def test_progress_entries_preserve_history_and_reject_empty_or_duplicate_updates(self):
        self.create()
        history = self.log()
        arguments = ("--summary", "Cache key excludes the output directory", "--details",
                     "Compared two builds in separate directories; hashes match. Next, test changed compiler options.")
        self.command("append_worklog.py", *arguments)
        self.assertEqual(self.log()[:-1], history)
        before = self.snapshot()
        self.command("append_worklog.py", *arguments, success=False)
        self.command("append_worklog.py", "--summary", "  ", "--details", "Evidence", success=False)
        self.assertEqual(self.snapshot(), before)

    def test_flow_yaml_history_remains_readable_after_append(self):
        self.create()
        history = self.log()
        (self.feature / "WORKLOG.yaml").write_text(yaml.safe_dump(history, default_flow_style=True))
        self.command("append_worklog.py", "--summary", "Compared cache formats", "--details", "Selected the versioned format to support future migrations.")
        self.assertEqual(self.log()[:-1], history)

    def test_concurrent_appends_preserve_every_successful_update(self):
        self.create()
        previous = self.log()
        summaries = [f"Independent build {number} finished" for number in range(12)]
        start = Barrier(len(summaries), timeout=10)

        def append(summary):
            start.wait()
            self.command("append_worklog.py", "--summary", summary, "--details",
                         "Verified build output in an isolated directory.")

        with ThreadPoolExecutor(max_workers=len(summaries)) as workers:
            list(workers.map(append, summaries))

        history = self.log()
        self.assertEqual(history[:len(previous)], previous)
        self.assertCountEqual([item["summary"] for item in history[len(previous):]], summaries)

    def test_malformed_worklog_prevents_status_changes(self):
        self.create()
        (self.feature / "WORKLOG.yaml").write_text("not-a-list: true\n")
        before = self.snapshot()
        self.command("set_feature_status.py", "DESIGN", "--reason", "Research completed", success=False)
        self.assertEqual(self.snapshot(), before)

    def test_redirected_records_are_rejected_and_left_untouched(self) -> None:
        self.create()
        path = self.feature / "WORKLOG.yaml"
        external = self.root / "separate-record.yaml"
        original = path.read_bytes()
        _ = path.rename(external)
        path.symlink_to(external)
        self.command("set_feature_status.py", "DESIGN", "--reason", "Research completed", success=False)
        self.assertEqual(self.definition()["status"], "RESEARCH")
        self.assertEqual(external.read_bytes(), original)
        self.assertTrue(path.is_symlink())

    def interrupt_status_update(self) -> None:
        transition = SCRIPTS / "set_feature_status.py"
        fail_worklog_replacement = """
from pathlib import Path
import runpy
import sys
from unittest.mock import patch

script = Path(sys.argv[1])
sys.argv = sys.argv[1:]
sys.path.insert(0, str(script.parent))
replace = Path.replace

def replace_with_failure(path, target):
    if Path(target).name == "WORKLOG.yaml":
        raise OSError("Simulated interruption while replacing the worklog")
    return replace(path, target)

with patch.object(Path, "replace", replace_with_failure):
    runpy.run_path(str(script), run_name="__main__")
"""
        interrupted = subprocess.run(
            [sys.executable, "-c", fail_worklog_replacement, str(transition), "build-cache",
             "--root", str(self.root), "DESIGN", "--reason", "Research completed"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertNotEqual(interrupted.returncode, 0)
        self.assertIn("Simulated interruption", interrupted.stderr)

    def test_next_command_recovers_status_and_history_after_an_interrupted_write(self) -> None:
        self.create()
        history = self.log()
        self.interrupt_status_update()
        self.command("append_worklog.py", "--summary", "Continued from recovered status",
                     "--details", "Reviewed the design in a fresh process.")
        self.assertEqual(self.definition()["status"], "DESIGN")
        entries = self.log()
        self.assertEqual(entries[:-2], history)
        self.assertEqual(entries[-2]["details"], "Research completed")
        self.assertEqual(entries[-2]["phase"], "DESIGN")
        self.assertEqual(entries[-1]["phase"], "DESIGN")

    def test_recovery_preserves_a_record_edited_after_an_interrupted_update(self) -> None:
        self.create()
        self.interrupt_status_update()
        path = self.feature / "WORKLOG.yaml"
        with path.open("a") as output:
            _ = output.write("# Reviewed manually after the interruption\n")
        before = self.snapshot()
        result = self.command("append_worklog.py", "--summary", "Tried to continue",
                              "--details", "Reviewed in another process.", success=False)
        self.assertIn("conflicts with WORKLOG.yaml", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_unrelated_definition_fields_survive_status_updates(self):
        self.create()
        with (self.feature / "DEFINITION.toml").open("a") as output:
            output.write('\n[context]\nowner = "build-team"\n')
        self.command("set_feature_status.py", "DESIGN", "--reason", "Confirmed the cache interface constraints")
        self.assertEqual(self.definition()["context"], {"owner": "build-team"})

    def test_feature_memory_is_ignored_but_harness_scripts_remain_trackable(self):
        self.create()
        (self.root / ".gitignore").write_text((SCRIPTS.parents[1] / ".gitignore").read_text())
        subprocess.run(["git", "init", "-q", str(self.root)], check=True, capture_output=True)
        memory = subprocess.run(
            ["git", "-C", str(self.root), "check-ignore", ".harness/features/build-cache/DEFINITION.toml"],
            capture_output=True, text=True,
        )
        scripts = subprocess.run(
            ["git", "-C", str(self.root), "check-ignore", ".harness/scripts/create_feature.py"],
            capture_output=True, text=True,
        )
        self.assertEqual(memory.returncode, 0, memory.stderr)
        self.assertEqual(scripts.returncode, 1, scripts.stderr)

    def test_unchanged_blocking_reason_does_not_repeat_history(self):
        self.create()
        self.seed(state="BLOCKED")
        before = self.snapshot()
        self.command("set_requirement_status.py", "F-1", "BLOCKED", "--reason", "Still waiting",
                     "--blocked-reason", "Compiler access requires the build team's account grant.", success=False)
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
