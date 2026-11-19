"""Change a feature phase without skipping forward lifecycle steps."""

from dataclasses import dataclass
from pathlib import Path

from _feature_memory import PHASES, FeatureArguments, entry, load_feature, parser, phase_of, run, save_status


@dataclass(frozen=True)
class StatusArguments(FeatureArguments):
    status: str
    reason: str


def change(args: StatusArguments, path: Path) -> None:
    definition, entries = load_feature(path)
    previous = phase_of(definition)
    if previous == args.status:
        raise ValueError("Feature is already in that phase. Use append_worklog.py for progress")
    if PHASES.index(args.status) > PHASES.index(previous) + 1:
        raise ValueError("Forward phase changes must advance exactly one step")
    definition["status"] = args.status
    save_status(path, definition, entries, entry(
        args.status, f"Feature phase: {previous} → {args.status}", args.reason
    ))
    print(f"{args.feature}: {previous} → {args.status}")


if __name__ == "__main__":
    arguments = parser(__doc__)
    _ = arguments.add_argument("status", choices=PHASES)
    _ = arguments.add_argument("--reason", required=True, help="Evidence or decision supporting this transition")
    run(change, arguments, StatusArguments)
