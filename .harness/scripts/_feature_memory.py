"""Shared parsing and invariants for the feature-memory commands."""

import argparse
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
import re
from typing import TypeVar, cast

import tomlkit
from tomlkit.exceptions import ParseError
from tomlkit.toml_document import TOMLDocument
import yaml

from _feature_store import DEFINITION, WORKLOG, commit_status, finish_status, pending_status, write_text
from _local_files import exclusive_lock, read_text

PHASES = ("RESEARCH", "DESIGN", "IMPLEMENT", "TEST", "DONE")
REQUIREMENT_STATES = ("TODO", "WIP", "BLOCKED", "DONE")
Worklog = list[dict[str, object]]


def require_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must contain meaningful text")
    return str(value)


def feature_path(root: Path, name: str) -> Path:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError("Feature names must be lowercase kebab-case")
    base = root.resolve(strict=True) / ".harness" / "features"
    path = base / name
    if path.is_symlink() or base.resolve() != base:
        raise ValueError("Feature memory must remain inside .harness/features/")
    return path


def validate_requirement(requirement: Mapping[str, object]) -> str:
    identifier = require_text(requirement.get("id"), "Requirement id")
    if requirement.get("kind") not in ("functional", "non-functional"):
        raise ValueError(f"{identifier}: kind must be functional or non-functional")
    for field in ("description", "definition_of_done"):
        _ = require_text(requirement.get(field), f"{identifier}.{field}")
    status = requirement.get("status")
    if status not in REQUIREMENT_STATES:
        raise ValueError(f"{identifier}: invalid requirement status")
    reason = requirement.get("blocked_reason", "")
    previous = requirement.get("blocked_from", "")
    if status == "BLOCKED":
        _ = require_text(reason, f"{identifier}.blocked_reason")
        if previous not in ("TODO", "WIP"):
            raise ValueError(f"{identifier}: blocked_from must be TODO or WIP")
    elif reason or previous:
        raise ValueError(f"{identifier}: clear blocked_reason and blocked_from when unblocked")
    return identifier


def validate_definition(definition: Mapping[str, object]) -> None:
    _ = require_text(definition.get("description"), "Feature description")
    if definition.get("status") not in PHASES:
        raise ValueError(f"Feature status must be one of {PHASES}")
    links = definition.get("documentation")
    if not isinstance(links, list):
        raise ValueError("documentation must be a list of links or project paths")
    for link in cast(list[object], links):
        _ = require_text(link, "Documentation link")
    requirements = definition.get("requirements")
    if not isinstance(requirements, list):
        raise ValueError("requirements must be a list")

    ids: set[str] = set()
    for item in cast(list[object], requirements):
        if not isinstance(item, dict):
            raise ValueError("Each requirement must be a table")
        requirement = cast(dict[str, object], item)
        identifier = validate_requirement(requirement)
        if identifier in ids:
            raise ValueError(f"Duplicate requirement id: {identifier!r}")
        ids.add(identifier)
        if definition["status"] == "DONE" and requirement["status"] != "DONE":
            raise ValueError("A feature can be DONE only when every requirement is DONE")


def phase_of(definition: TOMLDocument) -> str:
    return require_text(definition.get("status"), "Feature status")


def requirements_of(definition: TOMLDocument) -> list[dict[str, str]]:
    return cast(list[dict[str, str]], definition["requirements"])


def parse_definition(content: str, source: Path) -> TOMLDocument:
    try:
        definition = tomlkit.parse(content)
    except (ParseError, RecursionError):
        raise ValueError(f"Invalid TOML in {str(source)!r}") from None
    validate_definition(cast(Mapping[str, object], definition))
    return definition


def parse_worklog(content: str, source: Path) -> Worklog:
    try:
        entries: object = yaml.safe_load(content)
    except (yaml.YAMLError, RecursionError):
        raise ValueError(f"Invalid YAML in {str(source)!r}") from None
    if not isinstance(entries, list):
        raise ValueError("WORKLOG.yaml must contain a YAML list")
    for item in cast(list[object], entries):
        if not isinstance(item, dict):
            raise ValueError("Every worklog entry must be a mapping")
        record = cast(dict[str, object], item)
        for field in ("timestamp", "summary", "details"):
            _ = require_text(record.get(field), f"Worklog {field}")
        if record.get("phase") not in PHASES:
            raise ValueError("Every worklog entry must identify its feature phase")
    return cast(Worklog, entries)


def load_feature(path: Path) -> tuple[TOMLDocument, Worklog]:
    definition = parse_definition(read_text(path / DEFINITION), path / DEFINITION)
    _ = require_text(read_text(path / "DESIGN.md"), "DESIGN.md")
    return definition, parse_worklog(read_text(path / WORKLOG), path / WORKLOG)


def entry(phase: str, summary: str, details: str) -> dict[str, object]:
    return {
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": phase,
        "summary": require_text(summary, "Worklog summary"),
        "details": require_text(details, "Worklog details"),
    }


def format_worklog(entries: Worklog) -> str:
    try:
        return yaml.safe_dump(entries, sort_keys=False, allow_unicode=True)
    except (yaml.YAMLError, RecursionError):
        raise ValueError("Could not serialize the feature worklog") from None


def append_entry(path: Path, entries: Worklog, item: dict[str, object]) -> None:
    write_text(path / WORKLOG, format_worklog([*entries, item]))


def save_status(path: Path, definition: TOMLDocument, entries: Worklog, item: dict[str, object]) -> None:
    validate_definition(cast(Mapping[str, object], definition))
    commit_status(path, tomlkit.dumps(definition), format_worklog([*entries, item]))


def recover_status(path: Path) -> None:
    change = pending_status(path)
    if change is not None:
        _ = parse_definition(change.definition, path / DEFINITION)
        _ = parse_worklog(change.worklog, path / WORKLOG)
        finish_status(path, change)


@dataclass(frozen=True)
class FeatureArguments:
    feature: str
    root: Path


Arguments = TypeVar("Arguments", bound=FeatureArguments)


def parser(description: str | None) -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=description)
    _ = result.add_argument("feature", help="Unique kebab-case feature directory name")
    _ = result.add_argument(
        "--root", type=Path, default=Path.cwd(), help="Project root (default: current directory)"
    )
    return result


def run(
    command: Callable[[Arguments, Path], None],
    arguments: argparse.ArgumentParser,
    schema: type[Arguments],
) -> None:
    args = schema(**vars(arguments.parse_args()))
    try:
        feature = feature_path(args.root, args.feature)
        locks = feature.parent / ".locks"
        if locks.is_symlink():
            raise ValueError("Feature locks must remain inside .harness/features/.locks/")
        locks.mkdir(mode=0o700, parents=True, exist_ok=True)
        with exclusive_lock(locks / f"{feature.name}.lock"):
            recover_status(feature)
            command(args, feature)
    except (ValueError, OSError) as error:
        arguments.exit(1, f"Error: {error}\n")
