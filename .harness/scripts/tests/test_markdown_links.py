"""Observable behavior of the local inline-reference checker."""

from functools import cached_property
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "check_markdown_links.py"


class MarkdownLinkTests(unittest.TestCase):
    @cached_property
    def root(self) -> Path:
        return Path(self.enterContext(tempfile.TemporaryDirectory()))

    def command(self, *paths: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, paths)], capture_output=True, text=True, timeout=30,
        )

    def test_existing_relative_encoded_and_angle_wrapped_targets(self):
        (self.root / "target file.md").write_text("# Target\n")
        directory = self.root / "nested"
        directory.mkdir()
        (directory / "links.md").write_text(
            '[encoded](../target%20file.md#section)\n'
            '[angle](<../target file.md>)\n'
            '[title](../target%20file.md "Target")\n'
            '![image](../target%20file.md)\n'
        )
        result = self.command(directory)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_target_fails_and_identifies_source_document(self):
        document = self.root / "broken.md"
        document.write_text("# Links\n\n[missing](missing.md)\n")
        result = self.command(document)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(str(document), result.stderr)
        self.assertIn("missing.md", result.stderr)

    def test_missing_target_diagnostic_excludes_query_and_fragment(self) -> None:
        document = self.root / "links.md"
        _ = document.write_text("[missing](missing.md?reference=example-query#example-fragment)\n")
        result = self.command(document)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing.md", result.stderr)
        self.assertNotIn("example-query", result.stderr)
        self.assertNotIn("example-fragment", result.stderr)

    def test_directory_scan_rejects_a_redirected_markdown_document(self) -> None:
        directory = self.root / "docs"
        directory.mkdir()
        external = self.root / "external.md"
        _ = external.write_text("[outside](unrelated-content.md)\n")
        (directory / "redirect.md").symlink_to(external)
        result = self.command(directory)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("redirect.md", result.stderr)
        self.assertNotIn("unrelated-content.md", result.stderr)

    def test_examples_external_links_and_anchor_only_links_are_not_local_targets(self):
        document = self.root / "examples.md"
        document.write_text(
            '[external](https://example.com/absent)\n'
            '[email](mailto:person@example.com)\n'
            '[host](//example.com/absent)\n'
            '[section](#missing-heading)\n'
            '`[inline](absent.md)`\n'
            '```markdown\n[example](absent.md)\n```\n'
            '~~~markdown\n[other](absent.md)\n~~~\n'
        )
        result = self.command(document)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_directory_check_detects_broken_links_in_nested_documents(self):
        nested = self.root / "nested"
        nested.mkdir()
        (self.root / "good.md").write_text("[nested](nested/broken.md)\n")
        (nested / "broken.md").write_text("[absent](absent.md)\n")
        self.assertNotEqual(self.command(self.root).returncode, 0)

    def test_missing_input_or_non_markdown_file_fails(self):
        other = self.root / "other.txt"
        other.write_text("Text")
        for path in (self.root / "missing.md", other):
            with self.subTest(path=path):
                self.assertNotEqual(self.command(path).returncode, 0)


if __name__ == "__main__":
    unittest.main()
