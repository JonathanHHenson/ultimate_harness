"""Validate page definitions and submitted answers without filesystem access."""

from datetime import date, datetime, time
import math
import re
from typing import cast
from urllib.parse import urlsplit

Record = dict[str, object]
TEXT = frozenset({"text", "textarea", "email", "url", "tel", "date", "time", "datetime-local", "color"})
NUMBER = frozenset({"number", "range"})
CHOICE = frozenset({"select", "radio", "multiselect", "checkbox-group"})
MULTIPLE = frozenset({"multiselect", "checkbox-group"})
KINDS = TEXT | NUMBER | CHOICE | {"section", "checkbox"}
MAX_REQUEST = 2_000_000
TEXT_PATTERNS = {
    "date": re.compile(r"\d{4}-\d{2}-\d{2}"),
    "email": re.compile(r"[^@\s]+@[^@\s]+"),
    "color": re.compile(r"#[0-9a-fA-F]{6}"),
}
TEMPORAL_PARSERS = {"date": date.fromisoformat, "time": time.fromisoformat, "datetime-local": datetime.fromisoformat}
TEMPORAL_SEPARATORS = {"time": ":", "datetime-local": "T"}
FIELD_PROPERTIES = {
    "id", "type", "label", "help", "placeholder", "required", "wide",
    "options", "default", "min", "max", "step", "min_length", "max_length", "rows",
}


def record(value: object, label: str) -> Record:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object.")
    return cast(Record, value)


def items(value: object, label: str, limit: int) -> list[object]:
    if not isinstance(value, list) or len(cast(list[object], value)) > limit:
        raise ValueError(f"{label} must be a list of at most {limit} items.")
    return cast(list[object], value)


def text(value: object, label: str, limit: int = 500, *, empty: bool = False) -> str:
    if not isinstance(value, str) or len(value) > limit or (not empty and not value.strip()):
        raise ValueError(f"{label} must be text of at most {limit} characters.")
    return value


def finite(value: object) -> bool:
    return type(value) in (int, float) and abs(cast(float, value)) <= 1e100


def choice_values(field: Record) -> list[str]:
    return [cast(str, option["value"]) for option in cast(list[Record], field["options"])]


def valid_date_or_time(kind: str, value: str) -> bool:
    separator = TEMPORAL_SEPARATORS.get(kind)
    if separator is not None and separator not in value:
        return False
    try:
        parsed = TEMPORAL_PARSERS[kind](value)
    except ValueError:
        return False
    return not isinstance(parsed, (datetime, time)) or parsed.tzinfo is None


def valid_http_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.hostname) and not any(c.isspace() for c in value)
    except ValueError:
        return False


def valid_text(kind: str, value: str) -> bool:
    pattern = TEXT_PATTERNS.get(kind)
    if pattern is not None and pattern.fullmatch(value) is None:
        return False
    if kind in TEMPORAL_PARSERS:
        return valid_date_or_time(kind, value)
    return kind != "url" or valid_http_url(value)


def bounds(field: Record) -> tuple[float, float]:
    slider = field["type"] == "range"
    return cast(float, field.get("min", 0 if slider else -math.inf)), cast(
        float, field.get("max", 100 if slider else math.inf)
    )


def valid_text_answer(field: Record, value: object, required: bool) -> bool:
    label = cast(str, field["label"])
    answer = text(value, label, cast(int, field.get("max_length", 8_000)), empty=True)
    if answer == "":
        return not required
    return (
        bool(answer.strip())
        and len(answer) >= cast(int, field.get("min_length", 0))
        and valid_text(cast(str, field["type"]), answer)
    )


def valid_number_answer(field: Record, value: object, required: bool) -> bool:
    if value is None:
        return not required and field["type"] != "range"
    low, high = bounds(field)
    return finite(value) and low <= cast(float, value) <= high


def valid_choice_answer(field: Record, value: object, required: bool) -> bool:
    options = choice_values(field)
    if field["type"] not in MULTIPLE:
        return (value == "" and not required) or value in options
    selected = items(value, cast(str, field["label"]), len(options))
    if not all(isinstance(item, str) and item in options for item in selected):
        return False
    return len(selected) == len(set(selected)) and (bool(selected) or not required)


def field_value(field: Record, value: object, *, default: bool = False) -> object:
    kind = cast(str, field["type"])
    required = bool(field.get("required")) and not default
    if kind in TEXT:
        valid = valid_text_answer(field, value, required)
    elif kind in NUMBER:
        valid = valid_number_answer(field, value, required)
    elif kind == "checkbox":
        valid = isinstance(value, bool) and (value or not required)
    else:
        valid = valid_choice_answer(field, value, required)
    if not valid:
        raise ValueError(f"Check your answer for {field['label']}.")
    return value


def validate_display_properties(field: Record) -> None:
    for key in ("help", "placeholder"):
        if key in field:
            _ = text(field[key], key, empty=True)
    for key in ("required", "wide"):
        if key in field and not isinstance(field[key], bool):
            raise ValueError(f"{key} must be true or false.")


def validate_options(field: Record, kind: str, name: str) -> None:
    if kind not in CHOICE:
        if "options" in field:
            raise ValueError("Only choice fields accept options.")
        return
    options = items(field.get("options"), "Options", 80)
    if not options:
        raise ValueError(f"Add options to {name!r}.")
    values: set[str] = set()
    for option in options:
        item = record(option, "Option")
        if item.keys() != {"value", "label"}:
            raise ValueError("Each option needs a value and label.")
        key = text(item.get("value"), "Option value", 200)
        _ = text(item.get("label"), "Option label", 200)
        if key in values:
            raise ValueError(f"Duplicate option value in {name!r}.")
        values.add(key)


def validate_length_settings(field: Record) -> None:
    for key, floor, ceiling in (("min_length", 0, 8_000), ("max_length", 1, 8_000), ("rows", 2, 12)):
        if key in field and (type(field[key]) is not int or not floor <= cast(int, field[key]) <= ceiling):
            raise ValueError(f"{key} must be an integer from {floor} to {ceiling}.")
    if cast(int, field.get("min_length", 0)) > cast(int, field.get("max_length", 8_000)):
        raise ValueError("min_length must not exceed max_length.")


def validate_numeric_settings(field: Record, kind: str) -> None:
    keys = ("min", "max", "step")
    if kind not in NUMBER:
        if field.keys() & keys:
            raise ValueError("Numeric bounds and step apply to number and range fields.")
        return
    for key in keys:
        if key in field and not finite(field[key]):
            raise ValueError(f"{key} must be a finite number.")
    low, high = bounds(field)
    if low > high or cast(float, field.get("step", 1)) <= 0:
        raise ValueError("Use ordered numeric bounds and a positive step.")


def field_definition(value: object) -> Record:
    field = record(value, "Field")
    if field.keys() - FIELD_PROPERTIES:
        raise ValueError("Unrecognised field property.")
    kind = text(field.get("type"), "Field type", 30)
    _ = text(field.get("label"), "Field label", 120)
    if kind not in KINDS:
        raise ValueError(f"Unsupported field type {kind!r}.")
    validate_display_properties(field)
    if kind == "section":
        if field.keys() - {"type", "id", "label", "help", "wide"}:
            raise ValueError("Sections accept a label and help text.")
        return field
    name = text(field.get("id"), "Field ID", 64)
    if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_-]*", name):
        raise ValueError(f"Invalid field ID {name!r}.")
    validate_options(field, kind, name)
    validate_length_settings(field)
    validate_numeric_settings(field, kind)
    if "default" in field:
        _ = field_value(field, field["default"], default=True)
    return field


def page_fields(page: Record) -> list[Record]:
    return cast(list[Record], page["fields"])


def validate_page(value: object) -> Record:
    page = record(value, "Page")
    _ = text(page.get("title"), "Page title", 120)
    if "submit_label" in page:
        _ = text(page["submit_label"], "Submit label", 48)
    fields = [field_definition(field) for field in items(page.get("fields"), "Fields", 40)]
    identifiers = [field["id"] for field in fields if field["type"] != "section"]
    if not identifiers or len(identifiers) != len(set(cast(list[str], identifiers))):
        raise ValueError("Provide at least one answer field and a unique ID for each answer field.")
    _ = text(page.get("markdown", ""), "Prologue", 65_536, empty=True)
    _ = record(page.get("images", {}), "Images")
    return page


def answers(page: Record, value: object) -> Record:
    submitted = record(value, "Answers")
    fields = {cast(str, field["id"]): field for field in page_fields(page) if field["type"] != "section"}
    if submitted.keys() != fields.keys():
        raise ValueError("The submitted fields do not match this page.")
    return {name: field_value(field, submitted[name]) for name, field in fields.items()}
