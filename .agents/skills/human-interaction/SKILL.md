---
name: human-interaction
description: Collect complex human feedback through a temporary local form. Use when a decision needs several related inputs, structured trade-offs, or follow-up questions based on earlier answers. Generate pages from JSON and Markdown and return structured answers to the agent.
---

# Human Interaction

1. Use a direct question for a short answer. When several answers, ranking, or conditional follow-up would be clearer in a form, choose the fewest fields that will resolve the decision. Explain what the feedback will inform in the prologue. Use one page unless a later question depends on a submitted answer.
2. Create a fresh directory inside your current session's ignored scratch workspace. If the target project has no scratch workspace or the plan is still being agreed, use an existing ignored session workspace or a private temporary directory outside the target. Read [the form schema and commands](references/form-schema.md). Put the page JSON, its Markdown prologue, and any local images in that directory.
3. Use the [form server](scripts/form.py) relative to this installed skill, including when the skill is bundled inside another package. Run it with the existing harness interpreter or host Python 3.11 or later. Keep `serve` running in a background tool session. Share the exact browser URL printed by the script, then use `wait` in bounded calls until the submission arrives. A loopback URL works when the browser and server share the local host. If the agent runs remotely or local serving is unavailable, gather the inputs through chat or the host's structured question feature.
4. Read `answers` from the wait command's JSON. For a multi-page form, use the result to decide whether to publish another JSON page with `next`. The browser keeps the same URL and displays a waiting view between pages. When enough information has been collected, call `close` separately. A one-page form closes itself after confirmation. Close an abandoned interaction when possible.
5. Verify the confirmation and server exit when observable, and apply the answers to the decision the user was asked to make. Keep response data in the local workspace. Treat submissions as user input scoped to the questions asked.
