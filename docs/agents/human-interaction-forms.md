# Human interaction forms

## Decisions

- Generate the interface from JSON and a Markdown file in the interaction's scratch directory. The browser builds nodes and controls from text. Local raster images and basic Mermaid flowcharts and sequence diagrams render with the bundled code. Unsupported diagrams retain their source. [Form schema](../../.agents/skills/human-interaction/references/form-schema.md) · [Mermaid syntax](https://mermaid.js.org/syntax/flowchart.html)
- Keep the browser on one URL. Save one answer record per page before changing the view. Multi-page sessions wait for the agent to offer a new page or close the form. Single-page submissions and explicit multi-page close both lead to a confirmation, followed by server shutdown. [Lifecycle](../TECHNICAL.md#how-feedback-forms-work)
- Use loopback and separate browser and agent credentials. Restrict public mutations to the exact origin and interaction URL, and keep private runtime data and unselected workspace files outside the HTTP routes. Use a bounded lifetime and a short confirmation grace period. The runtime uses standard-library Python and local browser assets. [Server](../../.agents/skills/human-interaction/scripts/form_server.py) · [Python HTTP server documentation](https://docs.python.org/3/library/http.server.html)

## Verification

- All 56 harness tests passed, including loopback integration tests for one-page and multi-page flows, persisted responses, invalid and stale submissions, missing authorization, external prologue paths, and expiration. The type checker and language server reported zero errors over the four changed Python files. JavaScript syntax, skill metadata, local links, and both generated exports passed. [Integration tests](../../.harness/scripts/tests/test_human_interaction.py)
- Browser checks exercised a text entry, choices, a checklist, slider, textarea, radio button, and confirmation checkbox. A one-page submission showed the success message and exited. A two-page form showed the waiting prompt, then displayed a follow-up based on the first response. It confirmed and exited after an explicit close. The prologue link, local image, flowchart, and sequence diagram rendered. At 1200 px the form used two columns. At 390 px it used one column and kept wide diagram scrolling inside the form. The final mobile check launched the form from the generated install package.
- The server and browser require the same local host. Browser flows were verified in Chromium. The Mermaid renderer implements the documented subset and hosted build execution was outside this check.

## Portable harness adoption

Install Harness routes open choices through the bundled form. It can collect preferences on one page or use another page to confirm an updated plan. It can use host Python and a private scratch workspace outside the target project, so the form is available before changing project files or creating a harness environment. [Adoption workflow](../../skills_src/install-harness/SKILL.md#when-agreeing-on-either-plan)

The local archive step produced both packages. Smoke tests ran the installation package's one-page flow and the evolution package's adaptive flow from separate target fixtures. Both returned answers and exited, and both target fixtures retained their original files and contents. All 56 harness tests and the local package and link checks passed.

## Idle timeout

Use a one-hour inactivity timeout with an optional hard runtime limit. Successful submissions and new pages extend inactivity. Browser and agent polling leave the deadline in place. An open tab uses the server's expiry state when available and the last reported deadline if the server is unreachable. [Timeout options](../../.agents/skills/human-interaction/references/form-schema.md#commands)

All 58 harness tests passed. Integration tests verified the default deadline, renewal on progress, and enforcement of the hard limit. Chromium displayed the expiry message with ordinary polling and with a simulated lost connection. The server exited automatically in both cases, including after the grace period when the browser could not acknowledge expiry. Both portable packages rebuilt and static checks passed.

## Reopening an expired form

Expiry pauses the exchange if questions remain open. The agent sends a short notice asking the human to say when they are ready. It then opens the outstanding questions at a new URL and uses the saved submissions from the original workspace. The conversational fallback applies when the runner cannot deliver the initial form or the human requests chat. The design interview and both adoption routes use the same procedure. [Expiry instructions](../../.agents/skills/human-interaction/SKILL.md#when-a-form-expires)

Verified the procedure using the extracted portable package. An ordinary bounded wait left the first form active. After the first answer was submitted, the follow-up expired. Serving that follow-up from a fresh workspace collected the remaining answer at a distinct URL and preserved the first submission. Reviewed the agent instructions for the expiry notice and fallback. All 70 harness tests, package checks, and local links passed.

## Schema validation refactor

Separate checks for display properties, choices, length settings, and numeric settings. Validate submitted values by field family and keep workspace reads in the page loader. The same local branch-count method measured `field_definition` at 30 before and 7 after, `field_value` at 28 before and 8 after, and `valid_text` at 14 before and 5 after. The largest remaining count across the two modules was 9. [Schema validation](../../.agents/skills/human-interaction/scripts/form_schema.py) · [Page loader](../../.agents/skills/human-interaction/scripts/form_page.py)

Compared 6,021 cases against the previous implementation across all input types, invalid definitions, submitted values, and local prologues. Every result and rejection message matched. All 60 harness tests passed, including new coverage for typed answers and relative image paths. Both workflow archives exercised their packaged form, and Python type and language-server diagnostics reported zero errors.
