"""Create a new feature's memory from a researched initial definition."""

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from _feature_memory import (
    FeatureArguments, append_entry, entry, parse_definition, parser, phase_of, require_text,
    requirements_of, run,
)
from _feature_store import DEFINITION, sync_directory, write_text
from _local_files import read_text


@dataclass(frozen=True)
class CreateArguments(FeatureArguments):
    definition: Path


def create(args: CreateArguments, path: Path) -> None:
    if path.exists():
        raise ValueError(f"Feature already exists: {args.feature}")
    content = read_text(args.definition)
    definition = parse_definition(content, args.definition)
    requirements = requirements_of(definition)
    if phase_of(definition) != "RESEARCH" or any(r["status"] != "TODO" for r in requirements):
        raise ValueError("New features start in RESEARCH with all requirements TODO")

    with TemporaryDirectory(prefix="create-", dir=path.parent / ".locks") as staging:
        draft = Path(staging)
        write_text(draft / DEFINITION, content)
        sections = "".join(f"### {r['id']}\n\nDesign pending.\n\n" for r in requirements)
        write_text(
            draft / "DESIGN.md",
            f"# Design: {args.feature}\n\n"
            "## Research and open questions\n\n"
            "Design is pending research.\n\n"
            "## Requirement coverage and technical approach\n\n"
            + sections
            + "## Interfaces, data, and failure handling\n\n"
            "## Verification strategy\n",
        )
        append_entry(draft, [], entry(
            "RESEARCH", "Feature research opened", require_text(definition.get("description"), "Feature description")
        ))
        _ = draft.rename(path)
        sync_directory(path.parent)
    print(path)


if __name__ == "__main__":
    arguments = parser(__doc__, creating=True)
    _ = arguments.add_argument("--definition", type=Path, required=True, help="Initial DEFINITION.toml source")
    run(create, arguments, CreateArguments)
