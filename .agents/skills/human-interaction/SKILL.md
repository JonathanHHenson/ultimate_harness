---
name: human-interaction
description: Collect complex human feedback through a temporary local form. Use when a decision needs several related inputs, structured trade-offs, or follow-up questions based on earlier answers. Generate pages from JSON and Markdown and return structured answers to the agent.
---

# Human Interaction

1. Use a direct question for a short answer. When several answers, ranking, or conditional follow-up would be clearer in a form, choose the fewest fields that will resolve the decision. Explain what the feedback will inform in the prologue. Use one page unless a later question depends on a submitted answer.
2. Create a fresh directory inside your current agent session's ignored scratch workspace. If the target project has no scratch workspace or the plan is still being agreed, use an existing ignored scratch workspace or a private temporary directory outside the target. Read [the form schema and commands](references/form-schema.md). Put the page JSON, its Markdown prologue, and any local images in that directory.
3. Use the [form server](scripts/form.py) relative to this installed skill, including when bundled. Run it with the harness interpreter or host Python 3.11 or later. Run `check` on the page and resolve errors. Start `serve` in a managed background tool session and confirm the exact URL answers the readiness request described in the schema reference. A loopback URL works when the browser and server share the local host.
4. In a live conversation, publish the verified URL in a progress message while you can still call tools. Keep the conversation and server active, and use `wait` in bounded calls until a submission arrives, the user cancels, or the form session expires. Follow [the expiry procedure](#when-a-form-expires) for unanswered questions. Use chat or host questions if the runner cannot deliver a usable form at the outset or the human requests that format. Close a form you abandon.
5. When `wait` reports `kind: clarification`, explicitly invoke [Wait What](../wait-what/SKILL.md). Use the optional feedback, current page, and project vocabulary to explain the same decisions in plain language. Check the rewritten JSON and publish it with `revise` for the returned request number. Then wait for the same page again. A clarification request leaves the decisions open until the human submits an answer.
6. Read `answers` from `wait`. For a multi-page form, check the next JSON page and publish it with `next` if needed. The browser keeps the same URL and displays a waiting view. When enough information has been collected, call `close` separately to end the multi-page form session. A one-page form session ends after confirmation.
7. Verify the confirmation and server exit when observable, then summarize or apply the answers within the scope the user authorized. Keep response data in the local workspace.

## When a form expires

- If questions remain unanswered, tell the human the form expired and ask them to let you know when they are ready. Send only the brief expiry notice and invitation to reopen. Keep the pending questions and any submitted answers in the local workspace.
- When the human says they are ready, follow [the reopen procedure](references/form-schema.md#when-reopening-after-expiry) to launch the pending page at a new URL. Carry forward earlier submissions and continue with the remaining questions.
