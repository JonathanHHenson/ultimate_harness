"""Exercise harness environment setup in an isolated project."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "init_venv.py"


def copy_bootstrap(root: Path) -> Path:
    scripts = root / ".harness" / "scripts"
    scripts.mkdir(parents=True)
    for name in ("init_venv.py", "_local_files.py"):
        _ = shutil.copyfile(SCRIPT.with_name(name), scripts / name)
    (scripts / "requirements.txt").touch()
    return scripts / SCRIPT.name


class HarnessEnvironmentTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("uv"), "uv is unavailable")
    def test_uv_setup_succeeds_without_a_user_cache_or_project_uv_settings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            bootstrap = copy_bootstrap(root)
            unavailable = root / "not-a-cache-directory"
            unavailable.touch()
            _ = (root / "uv.toml").write_text('resolution = "invalid-project-setting"\n')
            env = dict(os.environ, XDG_CACHE_HOME=str(unavailable), UV_OFFLINE="1")
            env.pop("UV_CACHE_DIR", None)
            env.pop("UV_NO_CACHE", None)

            result = subprocess.run(
                [sys.executable, bootstrap], cwd=root, env=env, capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            interpreter = bootstrap.parents[1] / ".venv" / "bin" / "python"
            _ = subprocess.run([interpreter, "-c", "import sys"], check=True, timeout=30)

    def test_setup_without_uv_creates_and_reuses_only_the_harness_environment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            bootstrap = copy_bootstrap(root)
            _ = (root / "requirements.txt").write_text("this is not a valid requirement\n")
            project_env = root / ".venv"
            project_env.mkdir()
            marker = project_env / "keep"
            _ = marker.write_text("project environment")
            harness_env = bootstrap.parents[1] / ".venv"
            env = dict(os.environ, PATH=str(bootstrap.parent), VIRTUAL_ENV=str(project_env))

            def initialize() -> None:
                result = subprocess.run(
                    [sys.executable, bootstrap], cwd=root, env=env, capture_output=True, text=True, timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

            initialize()
            interpreter = harness_env / "bin" / "python"
            result = subprocess.run(
                [interpreter, "-c", "import sys; print(sys.prefix)"],
                check=True, capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(Path(result.stdout.strip()).resolve(), harness_env)
            harness_marker = harness_env / "keep"
            harness_marker.touch()
            initialize()
            self.assertTrue(harness_marker.is_file())
            self.assertEqual(tuple(project_env.iterdir()), (marker,))
            self.assertEqual(marker.read_text(), "project environment")

    def test_existing_environment_that_enables_system_packages_is_preserved_and_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            bootstrap = copy_bootstrap(root)
            environment = bootstrap.parents[1] / ".venv"
            environment.mkdir()
            configuration = environment / "pyvenv.cfg"
            original = "include-system-site-packages = true\n"
            _ = configuration.write_text(original)
            result = subprocess.run(
                [sys.executable, bootstrap], cwd=root, capture_output=True, text=True, timeout=30,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("system site packages", result.stderr)
            self.assertEqual(configuration.read_text(), original)
            self.assertFalse((environment / "bin").exists())


if __name__ == "__main__":
    unittest.main()
