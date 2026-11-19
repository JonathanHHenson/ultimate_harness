"""Host a local form and exchange page definitions and responses with the agent."""

import argparse
from http.client import HTTPConnection, HTTPException
import json
from pathlib import Path
import re
import sys
from time import monotonic, sleep
from typing import cast
from urllib.parse import urlsplit

from form_page import load_page
from form_schema import MAX_REQUEST, Record, record
from form_server import RUNTIME, serve


def read_json(path: Path) -> Record:
    return record(json.loads(path.read_text(encoding="utf-8")), "Session data")


def wait_for_response(runtime: Path, page: int, timeout: int) -> int:
    target = runtime / f"answers-{page}.json"
    deadline = monotonic() + timeout
    while True:
        if target.is_file():
            print(json.dumps(read_json(target)))
            return 0
        if (runtime / "finished.json").is_file():
            # A response can be saved between the first read and the end marker.
            if target.is_file():
                continue
            raise ValueError("The form ended before this page was submitted.")
        if monotonic() >= deadline:
            print("No submission yet.", file=sys.stderr)
            return 2
        sleep(min(0.2, max(0, deadline - monotonic())))


def control(runtime: Path, action: str, payload: Record) -> Record:
    finished = runtime / "finished.json"
    if action == "close" and finished.is_file():
        return read_json(finished)
    session = read_json(runtime / "session.json")
    url = urlsplit(cast(str, session["url"]))
    token = session.get("control")
    if url.scheme != "http" or not re.fullmatch(r"127\.0\.0\.1:[0-9]{1,5}", url.netloc) or not isinstance(token, str):
        raise ValueError("Invalid local form session address.")
    body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode()
    if len(body) > MAX_REQUEST:
        raise ValueError("The page payload is too large.")
    connection = HTTPConnection("127.0.0.1", url.port, timeout=5)
    try:
        connection.request("POST", f"/control/{action}", body, {
            "Content-Type": "application/json", "Authorization": f"Bearer {token}",
        })
        response = connection.getresponse()
        result = record(json.loads(response.read(MAX_REQUEST)), "Control response")
        if response.status != 200:
            raise ValueError(str(result.get("error", "The form did not accept the command.")))
        return result
    finally:
        connection.close()


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("serve", help="Start a form and print its browser URL.")
    next_page = commands.add_parser("next", help="Show the next page after a multi-page submission.")
    wait = commands.add_parser("wait", help="Print a saved page response as JSON. Exit 2 if still waiting.")
    close = commands.add_parser("close", help="Show the final confirmation and end the session.")
    for command in (start, next_page, wait, close):
        _ = command.add_argument("--workspace", type=Path, required=True, help="Local interaction directory.")
    for command in (start, next_page):
        _ = command.add_argument("--page", type=Path, required=True, help="Page JSON path within the workspace.")
    _ = start.add_argument("--multi", action="store_true", help="Wait for the agent after each submission.")
    _ = start.add_argument("--idle-timeout", type=int, default=3600, help="Seconds allowed between pages or submissions.")
    _ = start.add_argument("--lifetime", type=int, help="Optional hard limit in seconds, including active sessions.")
    _ = wait.add_argument("--page", type=int, default=1, help="Page number to read.")
    _ = wait.add_argument("--timeout", type=int, default=20, help="Seconds to wait for the response (0–60).")
    return parser.parse_args()


def start_form(workspace: Path, args: argparse.Namespace) -> None:
    idle_timeout = cast(int, args.idle_timeout)
    lifetime = cast(int | None, args.lifetime)
    if not 1 <= idle_timeout <= 7200:
        raise ValueError("Use an idle timeout between 1 and 7200 seconds.")
    if lifetime is not None and not 1 <= lifetime <= 7200:
        raise ValueError("Use a lifetime between 1 and 7200 seconds.")
    page = load_page(workspace, cast(Path, args.page))
    serve(workspace, page, cast(bool, args.multi), idle_timeout, lifetime)


def main() -> int:
    args = arguments()
    try:
        workspace = cast(Path, args.workspace).resolve(strict=True)
        if not workspace.is_dir():
            raise ValueError("The workspace must be a directory.")
        action = cast(str, args.command)
        runtime = workspace / RUNTIME
        if action == "serve":
            start_form(workspace, args)
            return 0
        if not runtime.is_dir() or runtime.is_symlink():
            raise ValueError("No local form session found in this workspace.")
        if action == "wait":
            number = cast(int, args.page)
            timeout = cast(int, args.timeout)
            if number < 1 or not 0 <= timeout <= 60:
                raise ValueError("Use a positive page number and a timeout between 0 and 60 seconds.")
            return wait_for_response(runtime, number, timeout)
        payload = load_page(workspace, cast(Path, args.page)) if action == "next" else {}
        print(json.dumps(control(runtime, action, payload)))
        return 0
    except (OSError, HTTPException, ValueError, RecursionError) as error:
        print(f"Form error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
