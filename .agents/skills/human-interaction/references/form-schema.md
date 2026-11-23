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
      "options": [{"value": "speed", "label": "Early feedback"}, {"value": "coverage", "label": "Broader coverage"}],
      "default": "coverage"
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

Field labels allow up to 120 characters and option labels allow up to 200. Put longer context in the field's `help` or the Markdown prologue. Set `default` to prefill a recommended answer the human can review and edit. For a radio or select field, use an option's value. For multi-select and checkbox groups, use an array of option values. Leave choices open where the evidence supports asking the human first. Defaults become answers only when the human submits.

The browser displays up to five questions at a time. Section headings accompany their questions. Back and Next preserve edits, and the progress bar shows the current question page. All browser pages in a round share one submission. Use another agent-driven round only when earlier answers determine which questions to ask next.

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
"$python" "$form" launch --workspace "$workspace" --page page-1.json
```

Run `check` before serving or publishing each page. It validates the page and workspace assets, returns 0 for a valid page, and never starts a form session. Fix diagnostics before proceeding.

Run `launch` in a regular terminal call. It starts the loopback server and returns JSON with a URL ending in `/`. Use `serve` when the tool manages the long-running process. Either command starts the same server. An HTTP GET to the exact URL with `page` appended should return JSON with `view` set to `form` and the current page number. Confirm readiness before sharing the browser URL. Add `--multi` for an adaptive sequence. The server expires after one hour without a successful submission or a new page. Browser polling leaves that deadline in place. Use `--idle-timeout SECONDS` to change the idle interval or `--lifetime SECONDS` to set an additional hard limit on total runtime. Each option accepts 1–7200 seconds.

An open tab polls for the form session state and explains when it expires. If it misses the final response and cannot reach the server past the last reported deadline, it shows the expiry message using that deadline. The server stops after the browser acknowledges expiry or a short grace period passes.

```sh
"$python" "$form" wait --workspace "$workspace" --page 1 --timeout 20
"$python" "$form" next --workspace "$workspace" --page page-2.json
"$python" "$form" wait --workspace "$workspace" --page 2 --timeout 20
"$python" "$form" close --workspace "$workspace"
```

`wait` exits 0 when an answer or clarification request is available, 2 when the wait timed out, and 1 for an error. An answer has the page number, timestamp and `answers`. Saved answers can be read again after shutdown. `next` accepts a page after the current multi-page submission. Use a separate `close` call to send the final confirmation in multi-page mode. The browser acknowledges the final view and the server exits. If the tab disconnects, the server exits after a short grace period. Use a fresh directory for each form session.

## Listening for feedback

```sh
"$python" "$form" listen --workspace "$workspace" --page 1
```

`listen` waits 30 minutes by default. Set `--timeout` to 1800–7200 seconds for a longer window. It returns as soon as an answer or clarification request is available, with the same output and exit codes as `wait`. A closed or expired form ends the wait. Keep the command running in a tool session that can survive while you wait. Use a new call for the same round after a clarification, or for the next round after `next`.

The browser distinguishes an active waiter, an event read by the agent's command, and an event saved while the agent is away. A stopped command's listening status clears within a few seconds. When the form asks the human to message the agent in chat, read the queued event with `wait --timeout 0` and continue. Keep the form lifetime long enough for the intended wait.

## Updating a live form

To update an open round before submission, save an updated JSON file in the same workspace. You can edit wording, append options to an existing question, or append questions. Keep existing question IDs, order, option values, defaults, and validation constraints. Read the current `revision` from the form's `state` endpoint. Run:

```sh
"$python" "$form" check --workspace "$workspace" --page updated.json
"$python" "$form" update --workspace "$workspace" --revision "$revision" --page updated.json
```

The command uses the authenticated `/control/update` endpoint. If the revision changed before publication, read the latest state and reconcile the update. The browser picks up the change at the same URL, maintains the draft and position, and applies defaults for newly added questions. Appending enough questions creates another browser page automatically. Use `next` after a submission to send a new adaptive round.

## When reopening after expiry

When a bounded `wait` ends without a submission, check the live page state or, after shutdown, read `.form-session/finished.json`. A `view` of `expired` confirms expiry. Exit code 2 by itself means to keep waiting.

Keep the latest page JSON, its prologue and assets, and earlier answer records in the original workspace. After the human signals readiness, copy the current unanswered page and its assets, or prepare the next page from the saved answers, in a fresh workspace with the same relative asset paths. Run `check` and `launch`, verify readiness, and share the new URL. The new form session starts at page 1. Continue from the earlier submissions and collect only the outstanding answers.

## Clarification requests

Every live form has a **Wait.. What?** button below the context and another below the visible questions. The user can include a short note or leave the field blank. The browser pauses the form and shows a waiting view. `wait` returns a distinct object, for example `{"kind":"clarification","page":1,"request":1,"scope":"questions","feedback":""}`.

For the questions button, `question_page` identifies the browser page the human was viewing, and `visible_questions` lists its question IDs and labels. For example, the second browser page of the first round reports `page: 1` and `question_page: 2`. Use the listed questions and any note to target the explanation. The context button reports its scope without question details.

Use [Wait What](../../wait-what/SKILL.md) to explain the requested area. For `context`, revise the title or prologue and its images. For `questions`, revise question wording and help or append requested options or questions while preserving the context. Legacy requests with scope `page` allow both. Apply the same rules for preserving earlier answers as for [live updates](#updating-a-live-form). Save the revised JSON and any prologue in the same workspace. Run the following commands using the request number returned by `wait`.

```sh
"$python" "$form" check --workspace "$workspace" --page clarified.json
"$python" "$form" revise --workspace "$workspace" --request 1 --page clarified.json
"$python" "$form" wait --workspace "$workspace" --page 1 --timeout 20
```

The same URL resumes at the current question page with the browser's in-progress answers. `revise` accepts the pending request and keeps the round number and submission count. The agent can handle more clarification requests or advance after a submission. Clarification activity refreshes the idle deadline and stays subject to the form session's hard lifetime.
