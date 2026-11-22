"""Host a local form and exchange page definitions and responses with the agent."""

import argparse
from http.client import HTTPConnection, HTTPException
import json
from pathlib import Path
from queue import Empty, Queue
import re
import subprocess
import sys
from threading import Thread
from time import monotonic, sleep
from typing import cast
from urllib.parse import urlsplit

from form_page import load_page
from form_schema import MAX_REQUEST, Record, record
from form_server import CLARIFICATION, RUNTIME, serve


def read_json(path: Path) -> Record:
    return record(json.loads(path.read_text(encoding="utf-8")), "Session data")


def pending_clarification(runtime: Path, page: int) -> Record | None:
    try:
        pending = read_json(runtime / CLARIFICATION)
    except FileNotFoundError:
        return None
    return pending if pending.get("page") == page else None


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
        pending = pending_clarification(runtime, page)
        if pending is not None:
            print(json.dumps(pending))
            return 0
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


def startup_result(process: subprocess.Popen[str]) -> Record:
    output = process.stdout
    assert output is not None
    startup: Queue[str] = Queue()

    def read_startup() -> None:
        startup.put(output.readline())

    Thread(target=read_startup, daemon=True).start()
    try:
        line = startup.get(timeout=5).strip()
    except Empty as error:
        raise ValueError("The local form did not start within five seconds.") from error
    if not line.startswith("{"):
        raise ValueError(line.removeprefix("Form error: ") or "The local form exited before publishing a URL.")
    return record(json.loads(line), "Form startup")


def launch_form(workspace: Path, args: argparse.Namespace, idle_timeout: int, lifetime: int | None) -> None:
    command = [
        sys.executable, str(Path(__file__).resolve()), "serve", "--workspace", str(workspace),
        "--page", str(args.page), "--idle-timeout", str(idle_timeout),
    ]
    if args.multi:
        command.append("--multi")
    if lifetime is not None:
        command.extend(("--lifetime", str(lifetime)))
    process = subprocess.Popen(
        command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        start_new_session=True, creationflags=getattr(subprocess, "DETACHED_PROCESS", 0), text=True,
    )
    try:
        result = startup_result(process)
    except (OSError, ValueError, KeyboardInterrupt):
        process.kill()
        _ = process.wait()
        raise
    finally:
        assert process.stdout is not None
        process.stdout.close()
    print(json.dumps(result))


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="Validate a page without starting a session.")
    start = commands.add_parser("serve", help="Start a form and print its browser URL.")
    launch = commands.add_parser("launch", help="Start a local form and return its URL without holding the terminal.")
    next_page = commands.add_parser("next", help="Show the next page after a multi-page submission.")
    revise = commands.add_parser("revise", help="Explain the current page again after a clarification request.")
    wait = commands.add_parser("wait", help="Print a submission or clarification request. Exit 2 if still waiting.")
    close = commands.add_parser("close", help="Show the final confirmation and end the session.")
    for command in (check, start, launch, next_page, revise, wait, close):
        _ = command.add_argument("--workspace", type=Path, required=True, help="Local interaction directory.")
    for command in (check, start, launch, next_page, revise):
        _ = command.add_argument("--page", type=Path, required=True, help="Page JSON path within the workspace.")
    for command in (start, launch):
        _ = command.add_argument("--multi", action="store_true", help="Wait for the agent after each submission.")
        _ = command.add_argument("--idle-timeout", type=int, default=3600, help="Seconds allowed between pages or submissions.")
        _ = command.add_argument("--lifetime", type=int, help="Optional hard limit in seconds, including active sessions.")
    _ = revise.add_argument("--request", type=int, required=True, help="Clarification request number from wait.")
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
    if args.command == "launch":
        launch_form(workspace, args, idle_timeout, lifetime)
        return
    page = load_page(workspace, cast(Path, args.page))
    serve(workspace, page, cast(bool, args.multi), idle_timeout, lifetime)


def control_payload(action: str, workspace: Path, args: argparse.Namespace) -> Record:
    if action == "close":
        return {}
    page = load_page(workspace, cast(Path, args.page))
    if action == "revise":
        return {"request": cast(int, args.request), "form": page}
    return page


def main() -> int:
    args = arguments()
    try:
        workspace = cast(Path, args.workspace).resolve(strict=True)
        if not workspace.is_dir():
            raise ValueError("The workspace must be a directory.")
        action = cast(str, args.command)
        runtime = workspace / RUNTIME
        if action == "check":
            _ = load_page(workspace, cast(Path, args.page))
            print("Page is valid.")
            return 0
        if action in {"serve", "launch"}:
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
        print(json.dumps(control(runtime, action, control_payload(action, workspace, args))))
        return 0
    except (OSError, HTTPException, ValueError, RecursionError) as error:
        print(f"Form error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
