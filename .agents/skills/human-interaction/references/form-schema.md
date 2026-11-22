# Local feedback form

## Page JSON

Write one UTF-8 JSON file per page. Set `title`, optional `submit_label`, optional `prologue`, and `fields`. The prologue is a Markdown file path relative to the JSON file. Put both files and any referenced images in the directory for the form session.

```json
{
  "title": "Plan the first release",
  "prologue": "context.md",
  "submit_label": "Send feedback",
  "fields": [
    {"type": "section", "label": "Scope"},
    {
      "id": "priority", "type": "radio", "label": "What should we prioritise?", "required": true,
      "options": [{"value": "speed", "label": "Early feedback"}, {"value": "coverage", "label": "Broader coverage"}]
    },
    {"id": "confidence", "type": "range", "label": "Confidence", "min": 1, "max": 5, "default": 3, "step": 1},
    {"id": "feedback", "type": "textarea", "label": "What would change your choice?", "max_length": 1200}
  ]
}
```

| Field types | Value returned |
| --- | --- |
| `text`, `textarea`, `email`, `url`, `tel`, `date`, `time`, `datetime-local`, `color` | String. A blank optional field returns an empty string. Use HTTP(S) links for URL answers and native date, time and hex colour formats. |
| `number`, `range` | Number. Blank optional numbers return `null`. A slider always returns a number. |
| `select`, `radio` | Choice value or an empty string. |
| `multiselect`, `checkbox-group` | Array of choice values. |
| `checkbox` | Boolean. Setting `required` requires a checked box. |
| `section` | A heading and optional help text. It adds no answer. |

Use a unique `id` per answer field. Start IDs with a letter and use letters, digits, hyphens and underscores. All fields have a `label`. Use `help`, `placeholder` where the control supports one, `required`, `default` in the return type, and `wide` for a full-width field. Set `min_length` and `max_length` for text, `rows` for textarea, and `min`, `max` and optional browser `step` for number and range. Options are objects with `value` and `label`, and choice values are unique within a field. Pages can have up to 40 fields.

Field labels allow up to 120 characters and option labels allow up to 200. Put longer context in the field's `help` or the Markdown prologue. Keep each required choice unanswered until the human selects it.

## Prologues

Markdown supports paragraphs, headings, lists, block quotes, emphasis, inline and fenced code, HTTP(S) and mail links, and local raster images. Image paths are relative to the Markdown and stay inside the workspace. Use PNG, JPEG, GIF, WebP or AVIF. Image data on one page is limited to 1 MB. Use angle brackets to wrap destinations with spaces.

A `mermaid` code fence renders basic flowcharts and sequence diagrams without network calls. Flowcharts use `flowchart` or `graph`, a direction such as `TD` or `LR`, named nodes, rectangle or rounded labels, decisions and simple arrows with optional `|labels|`. Sequence diagrams support declared or implicit participants and plain solid or dashed messages. Unsupported diagram syntax is shown as code. [Mermaid flowchart syntax](https://mermaid.js.org/syntax/flowchart.html) · [Mermaid sequence syntax](https://mermaid.js.org/syntax/sequenceDiagram.html)

```mermaid
flowchart LR
    A[Choose scope] --> B{More input?}
    B -->|Yes| C[Ask a follow-up]
    B -->|No| D[Confirm]
```

## Commands

Set `workspace` to a fresh directory beneath the agent session's ignored scratch workspace, or to a private temporary directory outside the project when setting up a harness. Resolve `form` from the human-interaction skill you opened. In the portable harness package, the script is under `assets/harness/.agents/skills/human-interaction/scripts/` relative to the package root. Use host Python 3.11 or later when a harness environment is unavailable. The examples use this project's paths.

```sh
python=.harness/.venv/bin/python
form=.agents/skills/human-interaction/scripts/form.py
"$python" "$form" check --workspace "$workspace" --page page-1.json
"$python" "$form" serve --workspace "$workspace" --page page-1.json
```

Run `check` before serving or publishing each page. It validates the page and workspace assets, returns 0 for a valid page, and never starts a form session. Fix diagnostics before proceeding.

Run `serve` in a background tool session. It prints JSON with a loopback URL ending in `/`. An HTTP GET to the exact URL with `page` appended should return JSON with `view` set to `form` and the current page number. Confirm readiness before sharing the browser URL. Add `--multi` for an adaptive sequence. The server expires after one hour without a successful submission or a new page. Browser polling leaves that deadline in place. Use `--idle-timeout SECONDS` to change the idle interval or `--lifetime SECONDS` to set an additional hard limit on total runtime. Each option accepts 1–7200 seconds.

An open tab polls for the form session state and explains when it expires. If it misses the final response and cannot reach the server past the last reported deadline, it shows the expiry message using that deadline. The server stops after the browser acknowledges expiry or a short grace period passes.

```sh
"$python" "$form" wait --workspace "$workspace" --page 1 --timeout 20
"$python" "$form" next --workspace "$workspace" --page page-2.json
"$python" "$form" wait --workspace "$workspace" --page 2 --timeout 20
"$python" "$form" close --workspace "$workspace"
```

`wait` exits 0 when an answer or clarification request is available, 2 when the wait timed out, and 1 for an error. An answer has the page number, timestamp and `answers`. Saved answers can be read again after shutdown. `next` accepts a page after the current multi-page submission. Use a separate `close` call to send the final confirmation in multi-page mode. The browser acknowledges the final view and the server exits. If the tab disconnects, the server exits after a short grace period. Use a fresh directory for each form session.

## When reopening after expiry

When a bounded `wait` ends without a submission, check the live page state or, after shutdown, read `.form-session/finished.json`. A `view` of `expired` confirms expiry. Exit code 2 by itself means to keep waiting.

Keep the latest page JSON, its prologue and assets, and earlier answer records in the original workspace. After the human signals readiness, copy the current unanswered page and its assets, or prepare the next page from the saved answers, in a fresh workspace with the same relative asset paths. Run `check` and `serve`, verify readiness, and share the new URL. The new form session starts at page 1. Continue from the earlier submissions and collect only the outstanding answers.

## Clarification requests

Every live form page has a **Wait.. What?** button. The user can include a short note or leave the field blank. The browser pauses the page and shows a waiting view. `wait` returns a distinct object, for example `{"kind":"clarification","page":1,"request":1,"feedback":""}`.

Use [Wait What](../../wait-what/SKILL.md) to write a clearer explanation of the page. Rewrite the prologue, headings, question and option labels, or help text. Keep answer fields in the same order with the same IDs, types, option values, and answer constraints. Save the revised JSON and prologue in the same workspace. Run the following commands using the request number returned by `wait`.

```sh
"$python" "$form" check --workspace "$workspace" --page clarified.json
"$python" "$form" revise --workspace "$workspace" --request 1 --page clarified.json
"$python" "$form" wait --workspace "$workspace" --page 1 --timeout 20
```

The same page and URL resume with the browser's in-progress answers. `revise` accepts the pending request and keeps the page number and submission count. The agent can handle more clarification requests or advance after a real submission. Clarification activity refreshes the idle deadline and stays subject to the form session's hard lifetime.
