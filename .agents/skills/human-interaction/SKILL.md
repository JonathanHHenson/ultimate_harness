---
name: human-interaction
description: Collect complex human feedback in chat or through a temporary local form. Use for several related questions, structured trade-offs, or follow-up questions based on earlier answers.
---

# Human Interaction

## Before asking for structured feedback

1. Prepare the smallest set of questions the human can answer now. Keep independent decisions separate and make supported recommendations editable defaults. Ask a routine short question directly.
2. Tell the human how many questions are ready now and offer **one question at a time in chat** or **a web form**. Count only answerable questions, excluding headings and unknown follow-ups. End the turn and wait for their choice before launching anything or asking the first question. If they already chose a format, state the count and use it.

## When the human chooses chat

- Ask one question at a time and wait for an answer before presenting the next. Give essential context briefly and show progress, such as “Question 1 of 4”.
- Prefer the host's built-in question tool when it is available in the current mode and supports the question. Send one question per call even if it supports batches. Mark any recommended default in the choices and require the human to submit an answer.
- If the tool is unavailable, cannot represent the question, or the human asks for plain chat, ask the single question in a message. Give choices numeric or alphabetic aliases and state whether multiple choices are allowed. Name any default and let the human reply “default” to accept it.
- Record only explicit answers. If the answer is ambiguous or the human asks for an explanation, resolve it on the current question. Keep the same aliases and proceed once the answer is clear. Preserve earlier answers and announce the count for any newly necessary follow-up questions.
- When the answers settle the decision, summarize or apply them within the authorized scope.

## When the human chooses a form

1. Create a fresh directory inside the current agent session's ignored scratch workspace. If the target project has no scratch workspace or the plan is still being agreed, use an existing ignored scratch workspace or a private temporary directory outside the target. Read [the form schema and commands](references/form-schema.md). Write the page JSON, its Markdown prologue, and any local images. Put independent questions in one submission. The browser paginates long question sets automatically.
2. Resolve the [form CLI](scripts/form.py) relative to this skill, including when bundled. Use the harness interpreter or host Python 3.11 or later. Run `check`, fix diagnostics, then run `launch` and verify the URL with the [readiness request](references/form-schema.md#commands). Use `serve` when the runner can manage a background process. A loopback URL works when the browser and server share the local host.
3. **End this turn with the verified form link in your final reply.** Ask the human to open it and reply “ready” in chat once it is open so you can start listening. Keep the server running across turns. If the runner cannot show a link before a tool call or sustain a listener, ask the human to message you after submitting or requesting clarification. Use the [delivery fallback](#when-the-form-cannot-be-delivered) if you cannot provide a working link.

## When the human returns after opening a form

1. If the human reports a submission or clarification for the current round, read the saved event with `wait --timeout 0`. Use the same command when the runner cannot show a link before a tool call or sustain a listener. Otherwise, post the current form URL in a user-visible message and make [`listen`](references/form-schema.md#listening-for-feedback) your next tool call. Repeat this sequence for every new listener, including after a revision or follow-up. Let the same command run for the full 30-minute window unless an event arrives, the user cancels, or the form ends. Poll it if the tool yields a session handle.
2. If the form expires, follow the [expiry procedure](#when-a-form-expires). If the current round is still open and waiting has ended without an event, ask the human to message you after submitting or requesting clarification. Close the form if the human cancels.
3. For `kind: clarification`, invoke [Wait What](../wait-what/SKILL.md). Use the scope, feedback, and any `visible_questions` to revise the requested area. Append requested options or questions to the same form. Check the JSON and publish with `revise` using the returned request number. For a change without a pending clarification, use [`update`](references/form-schema.md#updating-a-live-form).
4. Read submitted answers and in adaptive mode publish a checked follow-up round with `next` if needed. Keep the same URL for revisions and follow-ups. Call `close` separately when an adaptive form is complete or when abandoning a form. A single-submission form ends after confirmation. Verify confirmation and server exit when observable, then summarize or apply the answers within the authorized scope. Keep response data in the local workspace.

## When the form cannot be delivered

- Try `launch` and verify readiness whenever terminal access allows it. If permissions, startup, or browser access prevents delivery, explain the blocker and offer to retry or continue with the [same questions in chat](#when-the-human-chooses-chat).

## When a form expires

- If questions remain unanswered, send a brief expiry notice and ask the human to say when they are ready. Keep the pending questions and submitted answers in the local workspace.
- When the human says they are ready, follow the [reopen procedure](references/form-schema.md#when-reopening-after-expiry) and use the new verified URL for the [form handoff](#when-the-human-chooses-a-form). Carry forward earlier submissions and ask only the remaining questions.
