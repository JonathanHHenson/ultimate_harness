"""Exercise the feedback tool through its CLI and loopback HTTP interface."""

from functools import cached_property
from http.client import HTTPConnection
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic, sleep, time
from typing import cast
import unittest
from urllib.parse import urlsplit

SCRIPT = Path(__file__).resolve().parents[3] / ".agents/skills/human-interaction/scripts/form.py"


class HumanInteractionTests(unittest.TestCase):
    @cached_property
    def workspace(self) -> Path:
        return Path(self.enterContext(TemporaryDirectory()))

    def arguments(self, action: str, *args: str) -> list[str]:
        return [sys.executable, str(SCRIPT), action, "--workspace", str(self.workspace), *args]

    def cli(self, action: str, *args: str, expect: int = 0) -> dict[str, object]:
        result = subprocess.run(self.arguments(action, *args), text=True, capture_output=True, timeout=8)
        self.assertEqual(result.returncode, expect, result.stderr)
        return cast(dict[str, object], json.loads(result.stdout)) if result.stdout else {}

    def page(self, name: str, question: str, *, prologue: str | None = None) -> None:
        payload: dict[str, object] = {
            "title": "Project choices",
            "fields": [
                {"id": question, "type": "text", "label": "Your choice", "required": True},
                {"id": "rating", "type": "range", "label": "Rating", "min": 1, "max": 5, "default": 3},
                {"id": "ok", "type": "checkbox", "label": "Confirm"},
            ],
        }
        if prologue:
            payload["prologue"] = prologue
        _ = (self.workspace / name).write_text(json.dumps(payload))

    def start(self, *args: str) -> tuple[subprocess.Popen[str], str]:
        process = subprocess.Popen(
            self.arguments("serve", "--page", "page.json", *args),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )

        def cleanup() -> None:
            if process.poll() is None:
                process.terminate()
            _ = process.communicate(timeout=5)

        self.addCleanup(cleanup)
        assert process.stdout is not None
        cutoff = monotonic() + 5
        while not (self.workspace / ".form-session/session.json").exists():
            if process.poll() is not None:
                self.fail(process.communicate()[1])
            self.assertLess(monotonic(), cutoff, "Form did not start")
            sleep(0.04)
        published = cast(dict[str, str], json.loads(process.stdout.readline()))
        return process, published["url"]

    def request(
        self, url: str, route: str,
        payload: dict[str, object] | None = None, *, origin: str | None = None, host: str | None = None,
    ) -> tuple[int, dict[str, object]]:
        endpoint = urlsplit(url)
        address = f"http://{endpoint.netloc}"
        headers = {"Host": host or endpoint.netloc}
        if payload is not None:
            headers.update({"Origin": origin or address, "Content-Type": "application/json"})
        connection = HTTPConnection(endpoint.hostname or "", endpoint.port, timeout=3)
        try:
            target = route if route.startswith("/") else endpoint.path + route
            connection.request("POST" if payload is not None else "GET", target,
                               json.dumps(payload) if payload is not None else None, headers)
            response = connection.getresponse()
            return response.status, cast(dict[str, object], json.loads(response.read()))
        finally:
            connection.close()

    def submit(self, url: str, page: int, field: str, value: str, rating: int = 3) -> tuple[int, dict[str, object]]:
        return self.request(url, "submit", {"page": page, "answers": {field: value, "rating": rating, "ok": False}})

    def test_single_submission_confirms_and_saved_response_outlives_the_server(self) -> None:
        _ = (self.workspace / "intro.md").write_text("## Context\n\nRead this before answering.")
        self.page("page.json", "choice", prologue="intro.md")
        process, url = self.start()
        self.assertEqual(urlsplit(url).hostname, "127.0.0.1")
        self.cli("wait", "--timeout", "0", expect=2)
        status, state = self.request(url, "page")
        self.assertEqual(status, 200)
        self.assertIn("## Context", cast(dict[str, str], state["form"])["markdown"])
        self.assertEqual(self.submit(url, 1, "choice", "Design", 9)[0], 400)
        self.assertEqual(self.submit(url, 1, "choice", "Design")[1]["view"], "complete")
        self.assertEqual(self.submit(url, 1, "choice", "Different")[0], 409)
        self.assertEqual(self.request(url, "ack", {})[0], 200)
        self.assertEqual(process.wait(timeout=4), 0)
        self.assertEqual(self.cli("wait")["answers"], {"choice": "Design", "rating": 3, "ok": False})

    def test_terminal_launch_returns_while_the_form_can_still_receive_answers(self) -> None:
        self.page("page.json", "choice")
        launch = self.cli("launch", "--page", "page.json", "--lifetime", "10")
        url = cast(str, launch["url"])
        self.assertEqual(urlsplit(url).hostname, "127.0.0.1")
        self.assertEqual(self.request(url, "page")[1]["view"], "form")
        self.cli("launch", "--page", "page.json", "--lifetime", "10", expect=1)
        self.assertEqual(self.submit(url, 1, "choice", "Design")[1]["view"], "complete")
        self.assertEqual(self.request(url, "ack", {})[0], 200)
        self.assertEqual(self.cli("wait")["answers"], {"choice": "Design", "rating": 3, "ok": False})

    def test_terminal_launch_reports_an_invalid_page_without_starting_a_form(self) -> None:
        _ = (self.workspace / "invalid.json").write_text("{}")
        result = subprocess.run(self.arguments("launch", "--page", "invalid.json", "--lifetime", "10"),
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("title", result.stderr.lower())
        self.assertEqual({path.name for path in self.workspace.iterdir()}, {"invalid.json"})

    def test_multi_page_uses_waiting_state_and_explicit_close(self) -> None:
        self.page("page.json", "topic")
        self.page("next.json", "followup")
        process, url = self.start("--multi")
        self.cli("next", "--page", "next.json", expect=1)
        self.assertEqual(self.submit(url, 1, "topic", "Performance")[1]["view"], "waiting")
        self.assertEqual(cast(dict[str, str], self.cli("wait")["answers"])["topic"], "Performance")
        self.assertEqual(self.cli("next", "--page", "next.json")["page"], 2)
        self.assertEqual(self.submit(url, 1, "topic", "Stale tab")[0], 409)
        self.assertEqual(self.submit(url, 2, "followup", "Cache the results")[1]["view"], "waiting")
        self.assertIsNone(process.poll())
        self.assertEqual(self.cli("close")["view"], "complete")
        self.assertEqual(self.request(url, "state")[1]["submitted"], 2)
        self.assertEqual(self.request(url, "ack", {})[0], 200)
        self.assertEqual(process.wait(timeout=4), 0)
        self.assertEqual(cast(dict[str, str], self.cli("wait", "--page", "2")["answers"])["followup"], "Cache the results")

    def test_blank_clarification_revises_single_page_before_submission(self) -> None:
        self.page("page.json", "choice")
        _ = (self.workspace / "clear.md").write_text("Start with a concrete example.")
        self.page("clear.json", "choice", prologue="clear.md")
        process, url = self.start()
        old_revision = self.request(url, "page")[1]["revision"]
        status, state = self.request(url, "clarify", {"page": 1, "revision": old_revision, "feedback": ""})
        self.assertEqual(status, 200)
        self.assertEqual((state["view"], state["submitted"]), ("clarifying", 0))
        self.assertEqual(self.submit(url, 1, "choice", "Too early")[0], 409)
        event = self.cli("wait")
        self.assertEqual((event["kind"], event["page"], event["feedback"]), ("clarification", 1, ""))
        result = self.cli("revise", "--request", str(event["request"]), "--page", "clear.json")
        self.assertEqual((result["page"], result["submitted"]), (1, 0))
        updated = cast(dict[str, str], self.request(url, "page")[1]["form"])
        self.assertEqual(updated["markdown"], "Start with a concrete example.")
        _ = self.cli("wait", "--timeout", "0", expect=2)
        self.assertEqual(self.request(url, "clarify", {"page": 1, "revision": old_revision})[0], 409)
        stale_answer = {"page": 1, "revision": old_revision, "answers": {"choice": "Stale", "rating": 3, "ok": False}}
        self.assertEqual(self.request(url, "submit", stale_answer)[0], 409)
        status, complete = self.submit(url, 1, "choice", "Answered")
        self.assertEqual((status, complete["view"]), (200, "complete"))
        self.assertEqual(self.request(url, "ack", {})[0], 200)
        self.assertEqual(process.wait(timeout=4), 0)

    def test_clarification_keeps_multistep_decisions_and_checks_authority(self) -> None:
        self.page("page.json", "topic")
        self.page("next.json", "followup")
        process, url = self.start("--multi")
        self.assertEqual(self.submit(url, 1, "topic", "Shared storage")[0], 200)
        _ = self.cli("next", "--page", "next.json")
        payload = {"page": 2, "revision": self.request(url, "page")[1]["revision"], "feedback": "What is retained?"}
        self.assertEqual(self.request(url, "clarify", payload, origin="https://other.test")[0], 403)
        oversize = {**payload, "feedback": "x" * 2001}
        self.assertEqual(self.request(url, "clarify", oversize)[0], 400)
        self.assertEqual(self.request(url, "clarify", payload)[0], 200)
        self.assertEqual(self.request(url, "clarify", payload)[0], 409)
        event = self.cli("wait", "--page", "2")
        self.assertEqual(event["feedback"], "What is retained?")
        self.assertEqual(self.request(url, "/control/revise", {})[0], 403)
        _ = self.cli("revise", "--request", "0", "--page", "next.json", expect=1)
        _ = self.cli("revise", "--request", str(event["request"]), "--page", "page.json", expect=1)
        self.assertEqual(self.request(url, "state")[1]["view"], "clarifying")
        _ = self.cli("revise", "--request", str(event["request"]), "--page", "next.json")
        self.assertEqual(self.submit(url, 2, "followup", "Keep last week")[0], 200)
        self.assertEqual(self.request(url, "state")[1]["submitted"], 2)
        self.assertEqual(self.cli("close")["view"], "complete")
        self.assertEqual(self.request(url, "ack", {})[0], 200)
        self.assertEqual(process.wait(timeout=4), 0)

    def test_hard_lifetime_expires_while_clarification_is_pending(self) -> None:
        self.page("page.json", "choice")
        process, url = self.start("--lifetime", "1")
        self.assertEqual(self.request(url, "clarify", {"page": 1})[0], 200)
        deadline = monotonic() + 4
        while self.request(url, "state")[1]["view"] != "expired":
            self.assertLess(monotonic(), deadline, "The clarification outlived the hard timeout")
            sleep(0.05)
        self.assertEqual(self.request(url, "ack", {})[0], 200)
        self.assertEqual(process.wait(timeout=4), 0)
        _ = self.cli("wait", expect=1)

    def test_public_url_cannot_control_session_or_read_scratch_files(self) -> None:
        self.page("page.json", "choice")
        process, url = self.start()
        self.assertEqual(self.request(url, "state", host="wrong.test")[0], 421)
        self.assertEqual(self.request(url, "submit", {}, origin="https://other.test")[0], 403)
        self.assertEqual(self.request(url, "/control/close", {})[0], 403)
        self.assertEqual(self.request(url, "/state")[0], 404)
        self.assertEqual(self.request(url, ".form-session/session.json")[0], 404)
        self.assertEqual(self.cli("close")["view"], "complete")
        self.assertEqual(self.request(url, "state")[1]["submitted"], 0)
        self.assertEqual(self.request(url, "ack", {})[0], 200)
        self.assertEqual(process.wait(timeout=4), 0)
        self.cli("wait", expect=1)

    def test_linked_prologue_cannot_read_outside_workspace(self) -> None:
        with TemporaryDirectory() as directory:
            external = Path(directory) / "external.md"
            _ = external.write_text("Outside the interaction.")
            (self.workspace / "intro.md").symlink_to(external)
            self.page("page.json", "choice", prologue="intro.md")
            self.cli("serve", "--page", "page.json", expect=1)
            self.assertFalse((self.workspace / ".form-session").exists())

    def test_check_validates_page_without_starting_a_session(self) -> None:
        self.page("valid.json", "choice")
        valid = subprocess.run(self.arguments("check", "--page", "valid.json"),
                               capture_output=True, text=True, timeout=5)
        self.assertEqual(valid.returncode, 0, valid.stderr)
        _ = (self.workspace / "invalid.json").write_text(json.dumps({
            "title": "Invalid form",
            "fields": [{"id": "choice", "type": "text", "label": "x" * 121}],
        }))
        invalid = subprocess.run(self.arguments("check", "--page", "invalid.json"),
                                 capture_output=True, text=True, timeout=5)
        self.assertEqual(invalid.returncode, 1)
        self.assertIn("Field label", invalid.stderr)
        self.assertEqual({path.name for path in self.workspace.iterdir()}, {"valid.json", "invalid.json"})

    def test_abandoned_form_expires_without_saving_a_response(self) -> None:
        self.page("page.json", "choice")
        process, url = self.start("--idle-timeout", "1")
        deadline = monotonic() + 4
        while self.request(url, "state")[1]["view"] != "expired":
            self.assertLess(monotonic(), deadline, "Form did not expire")
            sleep(0.05)
        self.assertEqual(self.submit(url, 1, "choice", "Late")[0], 409)
        self.assertEqual(self.request(url, "ack", {})[0], 200)
        self.assertEqual(process.wait(timeout=4), 0)
        self.cli("wait", expect=1)

    def test_polling_preserves_the_hour_deadline_and_progress_refreshes_it(self) -> None:
        self.page("page.json", "choice")
        self.page("next.json", "followup")
        process, url = self.start("--multi")
        first = cast(int, self.request(url, "state")[1]["expires_at_ms"])
        self.assertAlmostEqual(first / 1000 - time(), 3600, delta=5)
        sleep(0.1)
        self.assertAlmostEqual(cast(int, self.request(url, "state")[1]["expires_at_ms"]), first, delta=5)
        status, waiting = self.submit(url, 1, "choice", "Proceed")
        self.assertEqual(status, 200)
        submitted = cast(int, waiting["expires_at_ms"])
        self.assertGreater(submitted, first + 50)
        sleep(0.1)
        self.assertGreater(cast(int, self.cli("next", "--page", "next.json")["expires_at_ms"]), submitted + 50)
        self.cli("close")
        self.assertEqual(self.request(url, "ack", {})[0], 200)
        self.assertEqual(process.wait(timeout=4), 0)

    def test_optional_hard_limit_caps_the_inactivity_extension(self) -> None:
        self.page("page.json", "choice")
        process, url = self.start("--multi", "--idle-timeout", "8", "--lifetime", "2")
        first = cast(int, self.request(url, "state")[1]["expires_at_ms"])
        self.assertAlmostEqual(first / 1000 - time(), 2, delta=1)
        status, waiting = self.submit(url, 1, "choice", "Proceed")
        self.assertEqual(status, 200)
        self.assertAlmostEqual(cast(int, waiting["expires_at_ms"]), first, delta=5)
        cutoff = monotonic() + 5
        while self.request(url, "state")[1]["view"] != "expired":
            self.assertLess(monotonic(), cutoff, "The hard limit did not expire an active session")
            sleep(0.05)
        self.assertEqual(self.request(url, "ack", {})[0], 200)
        self.assertEqual(process.wait(timeout=4), 0)
        self.assertEqual(cast(dict[str, str], self.cli("wait")["answers"])["choice"], "Proceed")

    def test_typed_fields_reject_invalid_answers_without_saving(self) -> None:
        fields = [
            {"id": "day", "type": "date", "label": "Day", "required": True},
            {"id": "time", "type": "time", "label": "Local time"},
            {"id": "link", "type": "url", "label": "Link"},
            {"id": "email", "type": "email", "label": "Email"},
            {"id": "color", "type": "color", "label": "Colour"},
            {"id": "count", "type": "number", "label": "Count", "min": 0},
            {
                "id": "options", "type": "multiselect", "label": "Options", "required": True,
                "options": [{"value": "a", "label": "A"}, {"value": "b", "label": "B"}],
            },
        ]
        _ = (self.workspace / "page.json").write_text(json.dumps({"title": "Details", "fields": fields}))
        process, url = self.start()
        valid: dict[str, object] = {
            "day": "2028-02-29", "time": "09:30", "link": "https://example.com",
            "email": "", "color": "#005500", "count": None, "options": ["a", "b"],
        }
        for name, invalid in (
            ("day", "2026-02-29"), ("time", "09:30+01:00"), ("link", "mailto:test@example.com"),
            ("email", "wrong-address"), ("color", "#abc"), ("count", True),
            ("options", ["a", "a"]), ("options", ["c"]), ("options", []),
        ):
            with self.subTest(field=name, value=invalid):
                response, _ = self.request(url, "submit", {"page": 1, "answers": {**valid, name: invalid}})
                self.assertEqual(response, 400)
        self.cli("wait", "--timeout", "0", expect=2)
        self.assertEqual(self.request(url, "state")[1]["view"], "form")
        self.assertEqual(self.request(url, "submit", {"page": 1, "answers": valid})[0], 200)
        self.assertEqual(self.request(url, "ack", {})[0], 200)
        self.assertEqual(process.wait(timeout=4), 0)
        self.assertEqual(self.cli("wait")["answers"], valid)

    def test_prologue_resolves_supported_images_relative_to_markdown(self) -> None:
        media = self.workspace / "material"
        media.mkdir()
        _ = (media / "photo.png").write_bytes(b"fixture")
        markdown = "![One](photo.png) ![Again](photo.png)\n![Remote](https://example.com/remote.png)\n![Vector](vector.svg)"
        _ = (media / "intro.md").write_text(markdown)
        self.page("page.json", "choice", prologue="material/intro.md")
        process, url = self.start()
        status, state = self.request(url, "page")
        self.assertEqual(status, 200)
        form = cast(dict[str, object], state["form"])
        self.assertEqual(form["markdown"], markdown)
        self.assertEqual(form["images"], {"photo.png": "data:image/png;base64,Zml4dHVyZQ=="})
        self.cli("close")
        self.assertEqual(self.request(url, "ack", {})[0], 200)
        self.assertEqual(process.wait(timeout=4), 0)
