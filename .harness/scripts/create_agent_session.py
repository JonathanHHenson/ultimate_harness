"""Create one unique persistent agent workspace below the project's .scratch/."""

import argparse
from datetime import UTC, datetime
from pathlib import Path
from tempfile import mkdtemp


def create_workspace(project: Path) -> Path:
    scratch = project.resolve(strict=True) / ".scratch"
    sessions = scratch / "agent_sessions"
    if scratch.is_symlink() or sessions.is_symlink():
        raise ValueError("Scratch storage and agent_sessions must be local directories")
    sessions.mkdir(mode=0o700, parents=True, exist_ok=True)
    prefix = datetime.now(UTC).strftime("%Y%m%d-%H%M%S-")
    return Path(mkdtemp(prefix=prefix, dir=sessions))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project root (default: current directory)")
    root = Path(parser.parse_args().root)
    try:
        print(create_workspace(root))
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error creating session workspace: {error}\n")


if __name__ == "__main__":
    main()
