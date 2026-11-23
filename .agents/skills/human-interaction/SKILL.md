---
name: human-interaction
description: Collect complex human feedback through a temporary local form. Use when a decision needs several related inputs, structured trade-offs, or follow-up questions based on earlier answers. Generate pages from JSON and Markdown and return structured answers to the agent.
---

# Human Interaction

1. Use a direct question for a short answer. When several answers, ranking, or conditional follow-up would be clearer in a form, choose the fewest fields that will resolve the decision. Explain the purpose in the prologue. Set an editable `default` when you have a supported recommendation. Treat answers as decisions only after submission. Use a single submission for independent questions. The browser paginates long question sets automatically.
2. Create a fresh directory inside your current agent session's ignored scratch workspace. If the target project has no scratch workspace or the plan is still being agreed, use an existing ignored scratch workspace or a private temporary directory outside the target. Read [the form schema and commands](references/form-schema.md). Put the page JSON, its Markdown prologue, and any local images in that directory.
3. Use the [form CLI](scripts/form.py) relative to this installed skill, including when bundled. Run it with the harness interpreter or host Python 3.11 or later. Run `check`, resolve errors, then run `launch` from an ordinary terminal call and verify the URL using the [readiness request](references/form-schema.md#commands). If the runner can manage a foreground server in the background, it may use `serve` instead. A loopback URL works when the browser and server share the local host.
4. Share the verified form link in a progress message and run [`listen`](references/form-schema.md#listening-for-feedback) for the current round. Let the command keep running for its full 30-minute wait window unless an event arrives, the user cancels, or the form ends. If your tool returns a running command, check that same command instead of starting over. When the runner cannot keep listening, share the link and let the form tell the human when to send a chat message. Follow [the expiry procedure](#when-a-form-expires) for unanswered questions. Use [the delivery fallback](#when-the-form-cannot-be-delivered) for delivery failures. Close a form you abandon.
5. When the listener reports `kind: clarification`, explicitly invoke [Wait What](../wait-what/SKILL.md). Use the scope, feedback, and any `visible_questions` to revise the requested area. If the human asks for additional choices or questions, append them to the same form. Check the JSON and publish it with `revise` for the returned request number. For a change to an open form without a pending clarification, use [`update`](references/form-schema.md#updating-a-live-form). Listen again after publishing a revision.
6. Read submitted answers from the listener. In adaptive mode, check and publish a follow-up round with `next` if needed and listen for that round. Use the same URL throughout. When enough information has been collected, call `close` separately to end an adaptive form session. A single-submission form session ends after confirmation.
7. Verify the confirmation and server exit when observable, then summarize or apply the answers within the scope the user authorized. Keep response data in the local workspace.

## When the form cannot be delivered

- Try `launch` and verify readiness whenever terminal access allows it. A missing background tool still allows the ordinary terminal launch. If permissions, startup, or browser access prevent delivery, explain the specific blocker and ask whether to retry the form or collect the same inputs in chat. Use chat or host questions when the human chooses that format.

## When a form expires

- If questions remain unanswered, tell the human the form expired and ask them to let you know when they are ready. Send only the brief expiry notice and invitation to reopen. Keep the pending questions and any submitted answers in the local workspace.
- When the human says they are ready, follow [the reopen procedure](references/form-schema.md#when-reopening-after-expiry) to launch the pending page at a new URL. Carry forward earlier submissions and continue with the remaining questions.
