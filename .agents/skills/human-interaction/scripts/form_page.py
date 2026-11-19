"""Load a form definition and its local prologue assets from the workspace."""

import base64
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from form_schema import Record, record, text, validate_page

IMAGE_TYPES = {".png": "png", ".jpg": "jpeg", ".jpeg": "jpeg", ".webp": "webp", ".gif": "gif", ".avif": "avif"}
IMAGE = re.compile(r"!\[[^\]\n]*\]\((?:<([^>\n]+)>|([^\s()]+))\)")


def workspace_file(workspace: Path, path: Path, limit: int) -> bytes:
    source = path.resolve(strict=True)
    if not source.is_relative_to(workspace) or not source.is_file():
        raise ValueError("Page files must be regular files inside the session workspace.")
    with source.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"{source.name!r} exceeds the page file size limit.")
    return data


def prologue_images(workspace: Path, directory: Path, markdown: str) -> dict[str, str]:
    images: dict[str, str] = {}
    remaining = 1_000_000
    for match in IMAGE.finditer(markdown):
        reference = match.group(1) or match.group(2)
        asset = Path(reference)
        subtype = IMAGE_TYPES.get(asset.suffix.lower())
        if asset.is_absolute() or urlsplit(reference).scheme or not subtype or reference in images:
            continue
        data = workspace_file(workspace, directory / asset, remaining)
        remaining -= len(data)
        images[reference] = f"data:image/{subtype};base64,{base64.b64encode(data).decode('ascii')}"
    return images


def load_page(workspace: Path, filename: Path) -> Record:
    path = workspace / filename
    page = record(json.loads(workspace_file(workspace, path, 128_000)), "Page")
    if page.keys() - {"title", "submit_label", "fields", "prologue"}:
        raise ValueError("Unrecognised page property.")
    if "prologue" in page:
        link = Path(text(page.pop("prologue"), "Prologue path"))
        if link.is_absolute() or link.suffix.lower() not in {".md", ".markdown"}:
            raise ValueError("Use a relative Markdown prologue path.")
        prologue = path.parent / link
        markdown = workspace_file(workspace, prologue, 65_536).decode("utf-8")
        page.update(markdown=markdown, images=prologue_images(workspace, prologue.parent, markdown))
    return validate_page(page)
