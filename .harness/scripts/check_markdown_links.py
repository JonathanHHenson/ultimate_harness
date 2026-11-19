"""Check local inline Markdown link targets, excluding fenced and inline examples."""

import argparse
from collections.abc import Iterator
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from _local_files import read_text

LINK = re.compile(r'\[[^\]\n]*\]\((?:<([^>\n]+)>|([^\s()]+))(?:\s+"[^"\n]*")?\)')
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
INLINE_CODE = re.compile(r"(`+).*?\1")


def prose_lines(text: str) -> Iterator[tuple[int, str]]:
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = FENCE.match(line)
        if marker:
            token, suffix = marker.groups()
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) and not suffix.strip():
                fence = None
            continue
        if fence is None:
            yield number, INLINE_CODE.sub("", line)


def check(document: Path) -> list[str]:
    errors: list[str] = []
    for number, line in prose_lines(read_text(document)):
        for match in LINK.finditer(line):
            target = match.group(1) or match.group(2)
            location = f"{str(document)!r}:{number}"
            try:
                url = urlsplit(target)
            except ValueError:
                errors.append(f"{location}: invalid link target")
                continue
            if url.scheme or url.netloc or not url.path:
                continue
            destination = document.parent / unquote(url.path)
            if not destination.exists():
                errors.append(f"{location}: missing local target {url.path!r}")
    return errors


def collect_documents(paths: list[Path]) -> set[Path]:
    documents: set[Path] = set()
    for path in paths:
        if path.is_symlink():
            raise ValueError(f"Expected a local Markdown file or directory at {str(path)!r}")
        if path.is_dir():
            documents.update(path.rglob("*.md"))
        elif path.is_file() and path.suffix.lower() == ".md":
            documents.add(path)
        else:
            raise ValueError(f"Expected a Markdown file or directory at {str(path)!r}")
    return documents


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.add_argument("paths", nargs="+", type=Path, help="Markdown files or directories to check")
    paths: list[Path] = parser.parse_args().paths
    try:
        documents = collect_documents(paths)
        errors = [error for document in sorted(documents) for error in check(document)]
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")
    if errors:
        parser.exit(1, "\n".join(errors) + "\n")
    print(f"Local inline links are valid in {len(documents)} Markdown files.")


if __name__ == "__main__":
    main()
