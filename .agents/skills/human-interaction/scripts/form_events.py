"""Exchange form events and listener status through the private session directory."""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import monotonic, sleep
from uuid import uuid4

from form_schema import Record, record

CLARIFICATION = "clarification.json"
LISTEN_SECONDS = 30 * 60
HEARTBEAT_INTERVAL = 1
HEARTBEAT_LIFETIME = 4


def read_json(path: Path) -> Record:
    return record(json.loads(path.read_text(encoding="utf-8")), "Session data")


def write_json(path: Path, value: Record) -> None:
    with NamedTemporaryFile(mode="w", dir=path.parent, encoding="utf-8", delete=False) as stream:
        temporary = Path(stream.name)
        try:
            json.dump(value, stream, ensure_ascii=True, allow_nan=False)
            stream.close()
            _ = temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


def response_event(runtime: Path, page: int) -> Record | None:
    target = runtime / f"answers-{page}.json"
    if target.is_file():
        return read_json(target)
    if (runtime / "finished.json").is_file():
        # The answer may have been saved just before the end marker.
        if target.is_file():
            return read_json(target)
        raise ValueError("The form ended before this page was submitted.")
    try:
        pending = read_json(runtime / CLARIFICATION)
    except FileNotFoundError:
        return None
    return pending if pending.get("page") == page else None


def receipt_path(runtime: Path, page: int, clarification: int | None = None) -> Path:
    if clarification is not None:
        return runtime / f"received-clarification-{clarification}"
    return runtime / f"received-answers-{page}"


def deliver_event(runtime: Path, page: int, event: Record) -> None:
    request = event.get("request")
    clarification = request if event.get("kind") == "clarification" and isinstance(request, int) else None
    print(json.dumps(event), flush=True)
    receipt_path(runtime, page, clarification).touch(mode=0o600)


def listener_active(path: Path, now: float) -> bool:
    try:
        expires = read_json(path).get("expires")
    except (OSError, ValueError):
        return False
    return isinstance(expires, (int, float)) and now < expires


def agent_status(runtime: Path, page: int, view: str, revision: int) -> str:
    if view in {"waiting", "clarifying", "complete"}:
        receipt = receipt_path(runtime, page, revision if view == "clarifying" else None)
        if receipt.is_file():
            return "received"
    now = monotonic()
    return "listening" if any(listener_active(path, now) for path in runtime.glob(f"listener-{page}-*.json")) else "away"


def wait_for_response(runtime: Path, page: int, timeout: int) -> bool:
    listener = runtime / f"listener-{page}-{uuid4().hex}.json"
    deadline = monotonic() + timeout
    next_heartbeat = 0.0
    try:
        while True:
            event = response_event(runtime, page)
            if event is not None:
                deliver_event(runtime, page, event)
                return True
            now = monotonic()
            if now >= deadline:
                return False
            if now >= next_heartbeat:
                write_json(listener, {"expires": now + HEARTBEAT_LIFETIME})
                next_heartbeat = now + HEARTBEAT_INTERVAL
            sleep(min(0.2, deadline - now))
    finally:
        listener.unlink(missing_ok=True)
