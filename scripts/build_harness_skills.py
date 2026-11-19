"""Build both portable harness skill payloads from the checked-out harness."""

from pathlib import Path
from shutil import copy2
import sys
from tempfile import TemporaryDirectory
import tomllib
from typing import cast

SKILLS = ("install-harness", "evolve-harness")


def local_file(root: Path, name: str) -> Path:
    relative = Path(name)
    if not relative.parts or relative.is_absolute() or ".." in relative.parts or relative.as_posix() != name:
        raise ValueError(f"Expected a repository-relative file path: {name!r}")
    path = root / relative
    if path.resolve() != path or not path.is_file():
        raise ValueError(f"Expected a regular file in the source tree: {name!r}")
    return path


def payload_files(root: Path, catalog: Path) -> list[str]:
    components = tomllib.loads(catalog.read_text(encoding="utf-8"))
    files: set[str] = set()
    for component, entry in components.items():
        if not isinstance(entry, dict):
            raise ValueError(f"Expected a table for component {component!r}")
        fields = cast(dict[str, object], entry)
        paths = fields.get("files")
        if not isinstance(paths, list) or not paths:
            raise ValueError(f"Expected export files for component {component!r}")
        for name in cast(list[object], paths):
            if not isinstance(name, str):
                raise ValueError(f"Export paths must be strings in component {component!r}")
            _ = local_file(root, name)
            files.add(name)
    if not files:
        raise ValueError("The component catalog has no export files")
    return sorted(files)


def publish_payload(root: Path, catalog: Path, files: list[str], destination: Path) -> None:
    destination.parent.mkdir(exist_ok=True)
    with TemporaryDirectory(prefix=".build-harness-", dir=destination.parent) as directory:
        staging = Path(directory)
        payload = staging / "harness"
        payload.mkdir()
        for name in files:
            target = payload / name
            target.parent.mkdir(parents=True, exist_ok=True)
            _ = copy2(local_file(root, name), target)
        _ = copy2(catalog, payload / "catalog.toml")

        previous = staging / "previous"
        if destination.exists():
            _ = destination.rename(previous)
        try:
            _ = payload.rename(destination)
        except OSError:
            if previous.exists():
                _ = previous.rename(destination)
            raise


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        catalog = local_file(root, "skills_src/harness-files.toml")
        files = payload_files(root, catalog)
        destinations: list[Path] = []
        for skill in SKILLS:
            entry = local_file(root, f"skills_src/{skill}/SKILL.md")
            destination = entry.parent / "assets/harness"
            if destination.resolve() != destination or (destination.exists() and not destination.is_dir()):
                raise ValueError(f"Expected a local generated asset directory for {skill}")
            destinations.append(destination)
        for destination in destinations:
            publish_payload(root, catalog, files, destination)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Could not build harness skills: {error}", file=sys.stderr)
        return 1
    print(f"Built {len(destinations)} harness skills with {len(files)} exported files each.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
