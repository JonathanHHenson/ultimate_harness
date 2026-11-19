"""Exercise the Python complexity checker through its command-line interface."""

from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

SCRIPT = Path(__file__).resolve().parents[3] / ".agents/skills/python-development/scripts/check_complexity.py"


class PythonComplexityTests(unittest.TestCase):
    def check(self, files: dict[str, str], *arguments: str) -> subprocess.CompletedProcess[str]:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for name, code in files.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                _ = target.write_text(code, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPT), *arguments], cwd=root,
                capture_output=True, text=True, timeout=10,
            )

    def test_default_blocks_only_functions_above_the_limit(self) -> None:
        def function(name: str, branches: int) -> str:
            lines = [f"def {name}(value):\n"]
            lines.extend(f"    if value == {case}:\n        return {case}\n" for case in range(branches))
            return "".join(lines) + "    return None\n"

        files = {
            "package/example.py": "raise RuntimeError('Must never import this file')\n"
            + function("at_limit", 9) + function("too_complex", 10),
        }
        failure = self.check(files, "package")
        self.assertEqual(failure.returncode, 1)
        self.assertIn("package/example.py", failure.stderr)
        self.assertIn("too_complex has complexity 11 (limit 10)", failure.stderr)
        self.assertNotIn("at_limit", failure.stderr)
        self.assertEqual(self.check(files, "--max-complexity", "11", "package").returncode, 0)

    def test_nested_functions_have_independent_scores(self) -> None:
        result = self.check({
            "example.py": "def outer():\n"
            "    async def filtered(items):\n"
            "        return [item for item in items if item and (item < 3 or item > 5)]\n"
            "    return filtered\n",
        }, "--max-complexity", "4", "example.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("filtered has complexity 5", result.stderr)
        self.assertNotIn("outer has complexity", result.stderr)

    def test_pattern_matching_counts_alternatives_and_guards(self) -> None:
        result = self.check({
            "example.py": "def select(value):\n"
            "    match value:\n"
            "        case 1 | 2:\n"
            "            return True\n"
            "        case amount if amount > 10:\n"
            "            return False\n"
            "        case _:\n"
            "            return None\n",
        }, "--max-complexity", "4", "example.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("select has complexity 5", result.stderr)

    def test_unreadable_and_invalid_sources_fail_the_check(self) -> None:
        result = self.check({"broken.py": "def (:\n"}, "broken.py", "missing.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("broken.py", result.stderr)
        self.assertIn("missing.py", result.stderr)
        self.assertIn("could not parse Python source", result.stderr)
