"""Durable writes and recovery for a locked feature record."""

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from _local_files import read_text

DEFINITION = "DEFINITION.toml"
WORKLOG = "WORKLOG.yaml"
PENDING = ".status-pending.json"


@dataclass(frozen=True)
class StatusUpdate:
    definition: str
    worklog: str
    definition_before: str
    worklog_before: str


def digest(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def sync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def write_text(path: Path, content: str) -> None:
    with NamedTemporaryFile(
        mode="w", dir=path.parent, prefix=".write-", encoding="utf-8", delete=False
    ) as output:
        temporary = Path(output.name)
        try:
            _ = output.write(content)
            output.flush()
            os.fsync(output.fileno())
            output.close()
            _ = temporary.replace(path)
            sync_directory(path.parent)
        finally:
            temporary.unlink(missing_ok=True)


def finish_status(feature: Path, change: StatusUpdate) -> None:
    targets = (
        (feature / DEFINITION, change.definition, change.definition_before),
        (feature / WORKLOG, change.worklog, change.worklog_before),
    )
    replacements: list[tuple[Path, str]] = []
    for path, text, previous in targets:
        current = read_text(path)
        if current == text:
            continue
        if digest(current) != previous:
            raise ValueError(f"Pending status update conflicts with {path.name}. Preserve the records before resolving it")
        replacements.append((path, text))
    for path, text in replacements:
        write_text(path, text)
    (feature / PENDING).unlink()
    sync_directory(feature)


def commit_status(feature: Path, definition: str, worklog: str) -> None:
    change = StatusUpdate(
        definition, worklog, digest(read_text(feature / DEFINITION)), digest(read_text(feature / WORKLOG)),
    )
    write_text(feature / PENDING, json.dumps(asdict(change)))
    finish_status(feature, change)


def pending_status(feature: Path) -> StatusUpdate | None:
    path = feature / PENDING
    try:
        content = read_text(path)
    except FileNotFoundError:
        return None
    change: object = json.loads(content)
    match change:
        case {
            "definition": str(definition), "worklog": str(worklog),
            "definition_before": str(definition_before), "worklog_before": str(worklog_before),
        }:
            return StatusUpdate(definition, worklog, definition_before, worklog_before)
        case _:
            raise ValueError("Invalid pending feature status update")
