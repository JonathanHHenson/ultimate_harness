"""Check the required metadata and instructions of repository skill packages."""

import argparse
from pathlib import Path
import re
from typing import cast

import yaml

from _local_files import read_text

NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def load_metadata(text: str) -> dict[str, object]:
    try:
        node: object = yaml.compose(text, Loader=yaml.SafeLoader)
        if not isinstance(node, yaml.MappingNode):
            raise ValueError("SKILL.md frontmatter must be a mapping")
        keys: set[str] = set()
        pairs = cast(list[tuple[yaml.Node, yaml.Node]], node.value)
        for key, _ in pairs:
            if isinstance(key, yaml.ScalarNode):
                if key.value in keys:
                    raise ValueError("SKILL.md frontmatter contains a duplicate key")
                keys.add(key.value)
        return cast(dict[str, object], yaml.safe_load(text))
    except (yaml.YAMLError, RecursionError):
        raise ValueError("Invalid YAML in SKILL.md frontmatter") from None


def check_skill_metadata(metadata: dict[str, object], directory_name: str) -> None:
    name = metadata.get("name")
    if not isinstance(name, str) or len(name) > 64 or not NAME.fullmatch(name):
        raise ValueError("name must be lowercase kebab-case and at most 64 characters")
    if name != directory_name:
        raise ValueError(f"name {name!r} must match the package directory")
    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip() or len(description) > 1024:
        raise ValueError("description must be nonempty text of at most 1024 characters")


def check_skill(directory: Path) -> None:
    if directory.is_symlink():
        raise ValueError("Expected a local skill package directory")
    lines = read_text(directory / "SKILL.md").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md must start with YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise ValueError("SKILL.md frontmatter needs a closing delimiter") from None
    check_skill_metadata(load_metadata("\n".join(lines[1:end])), directory.name)
    if not any(line.strip() for line in lines[end + 1:]):
        raise ValueError("SKILL.md must contain instructions after the frontmatter")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.add_argument(
        "directory", type=Path, nargs="?", default=Path(".agents/skills"),
        help="Directory containing skill packages (default: .agents/skills)",
    )
    directory = Path(parser.parse_args().directory)
    try:
        if directory.is_symlink():
            raise ValueError("Expected a local skill packages directory")
        packages = sorted(
            path for path in directory.iterdir()
            if path.is_dir() and not path.name.startswith(".")
        )
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")
    if not packages:
        parser.exit(1, f"{str(directory)!r}: no skill packages found\n")

    errors = []
    for package in packages:
        try:
            check_skill(package)
        except (OSError, ValueError) as error:
            errors.append(f"{str(package)!r}: {error}")
    if errors:
        parser.exit(1, "\n".join(errors) + "\n")
    print(f"Validated required metadata and instructions in {len(packages)} skill packages.")


if __name__ == "__main__":
    main()
