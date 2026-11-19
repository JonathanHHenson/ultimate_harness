#!/usr/bin/env python3
"""Fail if any harness feature or requirement in this checkout is unfinished."""

from pathlib import Path
import sys
import tomllib
from typing import cast

FEATURE_PHASES = ("RESEARCH", "DESIGN", "IMPLEMENT", "TEST", "DONE")
REQUIREMENT_STATES = ("TODO", "WIP", "BLOCKED", "DONE")


def describe_status(status: object, known_states: tuple[str, ...]) -> str:
    if isinstance(status, str) and status in known_states:
        return status
    return "missing or invalid"


def requirement_problems(requirements: object) -> list[str]:
    if not isinstance(requirements, list):
        return ["requirements must be a list"]

    problems: list[str] = []
    for number, item in enumerate(cast(list[object], requirements), start=1):
        if not isinstance(item, dict):
            problems.append(f"requirement {number} must be a table")
            continue
        requirement = cast(dict[str, object], item)
        identifier = requirement.get("id")
        if not isinstance(identifier, str) or not identifier.strip():
            problems.append(f"requirement {number} is missing its ID")
            continue
        status = requirement.get("status")
        if status != "DONE":
            problems.append(
                f"requirement {identifier!r} status is {describe_status(status, REQUIREMENT_STATES)}. Expected DONE"
            )
    return problems


def feature_problems(feature: Path) -> list[str]:
    if feature.is_symlink():
        return ["expected a local feature directory"]
    pending = feature / ".status-pending.json"
    problems = []
    if pending.exists() or pending.is_symlink():
        problems.append("status update pending. Run a feature command to recover it")

    definition = feature / "DEFINITION.toml"
    if definition.is_symlink() or not definition.is_file():
        return [*problems, "expected a regular DEFINITION.toml"]
    try:
        data = tomllib.loads(definition.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError, RecursionError):
        return [*problems, "unable to read a valid DEFINITION.toml"]

    status: object = data.get("status")
    if status != "DONE":
        problems.append(f"feature status is {describe_status(status, FEATURE_PHASES)}. Expected DONE")
    problems.extend(requirement_problems(data.get("requirements")))
    return problems


def main() -> int:
    features = Path(__file__).resolve().parents[1] / ".harness/features"
    if features.is_symlink() or features.parent.is_symlink():
        print("Expected a local .harness/features directory.", file=sys.stderr)
        return 1
    try:
        records = sorted(
            path for path in features.iterdir()
            if not path.name.startswith(".") and (path.is_symlink() or path.is_dir())
        )
    except FileNotFoundError:
        records = []
    except OSError as error:
        print(f"Could not scan .harness/features: {error}", file=sys.stderr)
        return 1

    failed = False
    for feature in records:
        for problem in feature_problems(feature):
            print(f"{feature.name!r}: {problem}", file=sys.stderr)
            failed = True
    if failed:
        return 1
    print(f"All {len(records)} feature records are done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
