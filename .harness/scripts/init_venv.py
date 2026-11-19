"""Create or refresh the harness's isolated Python environment."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

from _local_files import exclusive_lock, read_text

PROBE = (
    "import pathlib, sys; "
    "sys.exit(sys.version_info < (3, 11) or sys.prefix == sys.base_prefix or "
    "pathlib.Path(sys.prefix).resolve() != pathlib.Path(sys.argv[1]))"
)


def uv_environment(cache: Path) -> dict[str, str]:
    environment = os.environ.copy()
    if "UV_CACHE_DIR" not in environment:
        if cache.is_symlink():
            raise ValueError(f"Expected a local default uv cache at {str(cache)!r}")
        environment["UV_CACHE_DIR"] = str(cache)
    return environment


def create_environment(directory: Path, uv: str | None, environment: dict[str, str]) -> None:
    if uv:
        _ = subprocess.run(
            [uv, "--no-config", "venv", "--no-project", "--allow-existing",
             "--python", sys.executable, directory],
            env=environment,
            check=True,
        )
        return
    result = subprocess.run([sys.executable, "-Im", "venv", directory], env=environment)
    if result.returncode:
        _ = subprocess.run([sys.executable, "-EPm", "virtualenv", directory], env=environment, check=True)


def check_isolation(configuration: str) -> None:
    for line in configuration.splitlines():
        name, _, value = line.partition("=")
        if name.strip().lower() == "include-system-site-packages" and value.strip().lower() != "false":
            raise ValueError("The harness environment must keep system site packages disabled")


def install_requirements(
    python: Path, requirements: Path, uv: str | None, environment: dict[str, str]
) -> None:
    if uv:
        command = [uv, "--no-config", "pip", "install", "--python", python]
    else:
        environment = dict(environment, PIP_CONFIG_FILE=os.devnull)
        probe = subprocess.run(
            [python, "-Im", "pip", "--version"], env=environment, capture_output=True,
        )
        if probe.returncode:
            _ = subprocess.run([python, "-Im", "ensurepip"], env=environment, check=True)
        command = [python, "-Im", "pip", "--isolated", "install"]
    _ = subprocess.run([*command, "-r", requirements], check=True, env=environment)


def prepare_environment(directory: Path, requirements: Path) -> None:
    binaries = directory / "bin"
    python = binaries / "python"
    configuration = directory / "pyvenv.cfg"
    if directory.is_symlink() or binaries.is_symlink():
        raise ValueError(f"Expected a local virtual environment at {str(directory)!r}")
    _ = read_text(requirements)
    # Inspect existing settings before running the interpreter.
    if configuration.exists() or configuration.is_symlink():
        check_isolation(read_text(configuration))

    uv = shutil.which("uv")
    environment = uv_environment(directory.parent / ".uv-cache") if uv else os.environ.copy()
    if not python.is_file() or not configuration.is_file():
        create_environment(directory, uv, environment)
    check_isolation(read_text(configuration))
    _ = subprocess.run([python, "-I", "-c", PROBE, directory], check=True, env=environment)
    install_requirements(python, requirements, uv, environment)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.parse_args()
    if sys.version_info < (3, 11):
        parser.exit(1, "Harness setup requires Python 3.11 or later.\n")
    harness = Path(__file__).resolve().parents[1]
    try:
        with exclusive_lock(harness / ".venv.lock"):
            prepare_environment(harness / ".venv", harness / "scripts" / "requirements.txt")
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Harness environment setup failed: {error}\n")


if __name__ == "__main__":
    main()
