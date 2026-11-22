"""Serve one temporary interaction on the local machine."""

from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
from tempfile import NamedTemporaryFile
from threading import Lock
from time import monotonic, time
from typing import cast

from form_schema import MAX_REQUEST, Record, answers, decision_fields, record, text, validate_page

ASSETS = Path(__file__).resolve().parent.parent / "assets"
MEDIA = {
    "": ("index.html", "text/html; charset=utf-8"),
    "style.css": ("style.css", "text/css; charset=utf-8"),
    "app.js": ("app.js", "text/javascript; charset=utf-8"),
    "clarification.js": ("clarification.js", "text/javascript; charset=utf-8"),
    "markdown.js": ("markdown.js", "text/javascript; charset=utf-8"),
    "mermaid.js": ("mermaid.js", "text/javascript; charset=utf-8"),
}
RUNTIME = ".form-session"
CLARIFICATION = "clarification.json"
GRACE = 15


def write_json(path: Path, value: Record) -> None:
    with NamedTemporaryFile(mode="w", dir=path.parent, encoding="utf-8", delete=False) as stream:
        temporary = Path(stream.name)
        try:
            json.dump(value, stream, ensure_ascii=True, allow_nan=False)
            stream.close()
            _ = temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


class Conflict(ValueError):
    pass


class Interaction:
    def __init__(self, runtime: Path, page: Record, multi: bool, idle_timeout: int, lifetime: int | None) -> None:
        self.runtime = runtime
        self.page = page
        self.multi = multi
        self.number = 1
        self.count = 0
        self.revision: int = 0
        self.view = "form"
        started = monotonic()
        self.idle_timeout = idle_timeout
        self.idle_until = started + idle_timeout
        self.hard_limit = started + lifetime if lifetime is not None else float("inf")
        self.stop_at = float("inf")
        self.lock = Lock()

    @property
    def deadline(self) -> float:
        return min(self.idle_until, self.hard_limit)

    def expire_if_due(self) -> None:
        if monotonic() >= self.deadline:
            self.finish("expired")

    def state(self, *, include_form: bool = False) -> Record:
        state: Record = {"view": self.view, "page": self.number, "revision": self.revision,
                         "multi": self.multi, "submitted": self.count}
        if self.view in {"form", "waiting", "clarifying"}:
            remaining = max(0, self.deadline - monotonic())
            state["expires_at_ms"] = round((time() + remaining) * 1000)
        if self.view == "form" and include_form:
            state["form"] = self.page
        return state

    def show(self, view: str) -> None:
        self.view = view
        self.revision += 1

    def require_current_page(self, payload: Record) -> None:
        number = payload.get("page")
        revision = payload.get("revision", self.revision)
        if self.view != "form" or type(number) is not int or number != self.number:
            raise Conflict("This page has already moved on.")
        if type(revision) is not int or revision != self.revision:
            raise Conflict("This page has been updated. Review it and try again.")

    def submit(self, payload: Record) -> Record:
        self.require_current_page(payload)
        data = answers(self.page, payload.get("answers"))
        write_json(self.runtime / f"answers-{self.number}.json", {
            "page": self.number, "answers": data, "submitted_at": datetime.now(UTC).isoformat(),
        })
        self.count += 1
        if self.multi:
            self.show("waiting")
            self.idle_until = monotonic() + self.idle_timeout
        else:
            self.finish("complete")
        return self.state()

    def request_clarification(self, payload: Record) -> Record:
        self.require_current_page(payload)
        feedback = text(payload.get("feedback", ""), "Clarification feedback", 2000, empty=True).strip()
        write_json(self.runtime / CLARIFICATION, {
            "kind": "clarification", "page": self.number, "request": self.revision + 1, "feedback": feedback,
        })
        self.show("clarifying")
        self.idle_until = monotonic() + self.idle_timeout
        return self.state()

    def revise(self, payload: Record) -> Record:
        request = payload.get("request")
        if self.view != "clarifying" or type(request) is not int or request != self.revision:
            raise Conflict("This clarification request is no longer active.")
        page = validate_page(payload.get("form"))
        if decision_fields(page) != decision_fields(self.page):
            raise ValueError("Keep the same questions, choices, and answer constraints when clarifying a page.")
        (self.runtime / CLARIFICATION).unlink()
        self.page = page
        self.show("form")
        self.idle_until = monotonic() + self.idle_timeout
        return self.state()

    def next_page(self, payload: object) -> Record:
        if not self.multi or self.view != "waiting":
            raise Conflict("Wait for the current multi-page form submission before sending another page.")
        self.page = validate_page(payload)
        self.number += 1
        self.show("form")
        self.idle_until = monotonic() + self.idle_timeout
        return self.state()

    def finish(self, view: str) -> None:
        if self.view in {"complete", "expired"}:
            return
        (self.runtime / CLARIFICATION).unlink(missing_ok=True)
        self.show(view)
        self.stop_at = monotonic() + GRACE


class FormServer(ThreadingHTTPServer):
    def __init__(self, state: Interaction) -> None:
        super().__init__(("127.0.0.1", 0), FormHandler)
        self.timeout = 0.2
        self.state = state
        self.host = f"127.0.0.1:{self.server_port}"
        self.origin = f"http://{self.host}"
        self.scope = f"/{secrets.token_urlsafe(24)}/"
        self.control = secrets.token_urlsafe(32)


class FormHandler(BaseHTTPRequestHandler):
    timeout = 5
    server_version = "LocalForm"
    sys_version = ""

    @property
    def form_server(self) -> FormServer:
        return cast(FormServer, self.server)

    def log_message(self, format: str, *args: object) -> None:
        # URLs and request data are private to the session.
        pass

    def reply(self, status: int, kind: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Content-Security-Policy", "default-src 'none'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; img-src data:; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"
        )
        self.end_headers()
        try:
            _ = self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def send_json(self, status: int, payload: Record) -> None:
        self.reply(status, "application/json; charset=utf-8", json.dumps(payload, allow_nan=False).encode())

    def body(self) -> Record:
        size = int(self.headers.get("Content-Length", "0"))
        if not 0 < size <= MAX_REQUEST or self.headers.get("Content-Type") != "application/json":
            raise ValueError("Expected a small JSON request.")
        try:
            return record(json.loads(self.rfile.read(size)), "Request")
        except (UnicodeError, RecursionError, ValueError) as error:
            raise ValueError("Invalid JSON request.") from error

    def correct_host(self) -> bool:
        if self.headers.get_all("Host") == [self.form_server.host]:
            return True
        self.send_json(421, {"error": "Use the exact local form URL."})
        return False

    def do_GET(self) -> None:
        server = self.form_server
        if not self.correct_host():
            return
        if not self.path.startswith(server.scope):
            self.send_json(404, {"error": "Form not found."})
            return
        route = self.path.removeprefix(server.scope)
        if route in MEDIA:
            filename, content_type = MEDIA[route]
            self.reply(200, content_type, (ASSETS / filename).read_bytes())
        elif route in {"state", "page"}:
            with server.state.lock:
                server.state.expire_if_due()
                state = server.state.state(include_form=route == "page")
            self.send_json(200, state)
        else:
            self.send_json(404, {"error": "Page not found."})

    def do_POST(self) -> None:
        server = self.form_server
        if not self.correct_host():
            return
        route = self.path.removeprefix(server.scope)
        if self.path.startswith(server.scope) and route in {"submit", "clarify", "ack"}:
            if self.headers.get("Origin") != server.origin:
                self.send_json(403, {"error": "Submit from the local form."})
                return
        elif self.path in {"/control/next", "/control/revise", "/control/close"}:
            if not secrets.compare_digest(
                self.headers.get("Authorization", "").encode(), f"Bearer {server.control}".encode()
            ):
                self.send_json(403, {"error": "Agent authorization required."})
                return
        else:
            self.send_json(404, {"error": "Page not found."})
            return
        try:
            payload = self.body()
            with server.state.lock:
                response = self.update(route, payload)
            self.send_json(200, response)
        except Conflict as error:
            self.send_json(409, {"error": str(error)})
        except (ValueError, TimeoutError) as error:
            self.send_json(400, {"error": str(error)})
        except OSError:
            self.send_json(500, {"error": "Could not save the response. Try again."})

    def update(self, route: str, payload: Record) -> Record:
        state = self.form_server.state
        state.expire_if_due()
        if route == "submit":
            return state.submit(payload)
        if route == "clarify":
            return state.request_clarification(payload)
        if route == "/control/next":
            return state.next_page(payload)
        if route == "/control/revise":
            return state.revise(payload)
        if route == "/control/close":
            state.finish("complete")
        elif state.view in {"complete", "expired"}:
            state.stop_at = monotonic()
        return {"view": state.view}


def serve(workspace: Path, page: Record, multi: bool, idle_timeout: int, lifetime: int | None) -> None:
    runtime = workspace / RUNTIME
    state = Interaction(runtime, page, multi, idle_timeout, lifetime)
    with FormServer(state) as server:
        runtime.mkdir(mode=0o700)
        url = f"{server.origin}{server.scope}"
        write_json(runtime / "session.json", {"url": url, "control": server.control})
        print(json.dumps({
            "url": url, "page": 1, "multi": multi, "idle_timeout": idle_timeout, "lifetime": lifetime,
        }), flush=True)
        try:
            while True:
                with state.lock:
                    state.expire_if_due()
                    if monotonic() >= state.stop_at:
                        break
                server.handle_request()
        finally:
            write_json(runtime / "finished.json", {"view": state.view, "submitted": state.count})
