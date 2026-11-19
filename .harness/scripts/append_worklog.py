"""Append an informative progress entry without replacing existing history."""

from dataclasses import dataclass
from pathlib import Path

from _feature_memory import FeatureArguments, append_entry, entry, load_feature, parser, phase_of, run


@dataclass(frozen=True)
class AppendArguments(FeatureArguments):
    summary: str
    details: str


def append(args: AppendArguments, path: Path) -> None:
    definition, entries = load_feature(path)
    if any(item["summary"] == args.summary and item["details"] == args.details for item in entries):
        raise ValueError("An identical worklog entry already exists")
    append_entry(path, entries, entry(phase_of(definition), args.summary, args.details))
    print(f"Added progress entry to {args.feature}")


if __name__ == "__main__":
    arguments = parser(__doc__)
    _ = arguments.add_argument("--summary", required=True, help="Concrete outcome or decision")
    _ = arguments.add_argument("--details", required=True, help="Evidence, implications, blockers, or next action")
    run(append, arguments, AppendArguments)
