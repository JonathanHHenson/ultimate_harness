"""Change one requirement's status and maintain its blocking information."""

from dataclasses import dataclass
from pathlib import Path

from _feature_memory import (
    REQUIREMENT_STATES, FeatureArguments, entry, load_feature, parser, phase_of, require_text,
    requirements_of, run, save_status,
)


@dataclass(frozen=True)
class StatusArguments(FeatureArguments):
    requirement: str
    status: str
    reason: str
    blocked_reason: str | None


def block(requirement: dict[str, str], reason: str) -> None:
    previous = requirement["status"]
    if previous not in ("TODO", "WIP", "BLOCKED"):
        raise ValueError("Only unfinished requirements can be blocked")
    if previous != "BLOCKED":
        requirement["blocked_from"] = previous
    elif requirement["blocked_reason"] == reason:
        raise ValueError("Blocking reason is unchanged. Omit repetitive worklog updates")
    requirement["blocked_reason"] = reason


def advance(requirement: dict[str, str], status: str) -> None:
    previous = requirement["status"]
    target = {"TODO": "WIP", "WIP": "DONE", "BLOCKED": requirement.get("blocked_from")}.get(previous)
    if status != target:
        raise ValueError("Follow TODO → WIP → DONE and unblock to the recorded prior state")
    requirement["blocked_reason"] = ""
    requirement["blocked_from"] = ""


def change(args: StatusArguments, path: Path) -> None:
    details = require_text(args.reason, "Transition reason")
    definition, entries = load_feature(path)
    requirement = next((r for r in requirements_of(definition) if r["id"] == args.requirement), None)
    if requirement is None:
        raise ValueError(f"Unknown requirement: {args.requirement}")
    previous = requirement["status"]
    if args.status == "BLOCKED":
        reason = require_text(args.blocked_reason, "Blocking reason")
        block(requirement, reason)
        details += f"\nBlocking reason: {reason}"
    else:
        if args.blocked_reason:
            raise ValueError("--blocked-reason is only valid for BLOCKED")
        advance(requirement, args.status)
    requirement["status"] = args.status
    save_status(path, definition, entries, entry(
        phase_of(definition), f"{args.requirement}: {previous} → {args.status}", details
    ))
    print(f"{args.requirement}: {previous} → {args.status}")


if __name__ == "__main__":
    arguments = parser(__doc__)
    _ = arguments.add_argument("requirement", help="Stable requirement id from DEFINITION.toml")
    _ = arguments.add_argument("status", choices=REQUIREMENT_STATES)
    _ = arguments.add_argument("--reason", required=True, help="Progress, evidence, or decision behind the change")
    _ = arguments.add_argument("--blocked-reason", help="Detailed cause and what is needed to unblock")
    run(change, arguments, StatusArguments)
