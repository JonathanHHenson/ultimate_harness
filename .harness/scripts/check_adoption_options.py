"""Flag generic answer labels in a schema-checked harness adoption page."""

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import NotRequired, TypedDict, cast


class Option(TypedDict):
    value: str
    label: str


class Field(TypedDict):
    id: str
    options: NotRequired[list[Option]]


GENERIC = re.compile(
    "|".join(
        (
            r"yes|no|adopt|add|include|keep|defer|omit|exclude|skip|accept|decline",
            r"include in the (?:planned harness|harness|plan)",
            r"(?:adopt|accept|keep) (?:the )?recommend(?:ation|ed option|ed approach)",
            r"keep (?:available|discoverable) without (?:activation|a(?:n active)? (?:live )?route)",
            r"(?:add|omit|exclude|skip|do not add) this (?:component|skill|check|validation|capability)",
            r"require this situational validation",
            r"add this project specific workflow",
            r"keep (?:the existing guidance only|an explicit manual acceptance checklist)",
            r"exclude resolve affected dependencies later",
            r"defer (?:leave this capability unavailable|retain the capability gap)",
        )
    )
)


def normalized_label(label: str) -> str:
    label = re.sub(r"\(recommended\)", "", label.casefold())
    words = re.sub(r"[^\w]+", " ", label).strip()
    return re.sub(r"^(?:yes|no|recommended) ", "", words)


def check_options(fields: list[Field]) -> list[str]:
    options = [
        (field["id"], option["value"], normalized_label(option["label"]))
        for field in fields
        for option in field.get("options", [])
    ]
    decisions_per_label = Counter(
        label for _, label in {(field, label) for field, _, label in options}
    )
    return [
        f"{field}/{value}: name the affected capability and the effect of choosing this option"
        for field, value, label in options
        if not label or GENERIC.fullmatch(label) or decisions_per_label[label] > 1
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.add_argument(
        "page", type=Path, help="page JSON already accepted by the form CLI"
    )
    page = cast(Path, parser.parse_args().page)
    fields = cast(list[Field], json.loads(page.read_text(encoding="utf-8"))["fields"])
    issues = check_options(fields)
    for issue in issues:
        print(issue)
    return int(bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
