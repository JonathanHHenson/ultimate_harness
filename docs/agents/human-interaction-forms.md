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

Expiry pauses the exchange if questions remain open. The agent sends a short notice asking the human to say when they are ready. It then opens the outstanding questions at a new URL and uses the saved submissions from the original workspace. The design interview and both adoption routes use the same procedure. [Expiry instructions](../../.agents/skills/human-interaction/SKILL.md#when-a-form-expires)

## Choosing chat and handing off a form

Announce the number of answerable questions and offer chat or a web form before starting either. Chat presents one question at a time and prefers the host's built-in question controls when available and suitable. Use short choice aliases in plain chat. Either path requires an explicit answer, including when the human accepts a default. Install Harness and design interviews use the same procedure.

Deliver the verified form link in the final reply and ask the human to reply once the form is open. Post the current URL again immediately before each listener call. The server continues across turns, and the existing event reader can collect submissions and clarification requests sent before listening starts. This addresses reports that the link could be missed while Copilot was waiting. [Format choice and form handoff](../../.agents/skills/human-interaction/SKILL.md)

Walked through the extracted package for installation in chat and evolution with a form, including clarification, a follow-up round, and expiry. The packaged form CLI returned an early clarification and an answer submitted before listening. Package, link, and builder checks passed. The walkthrough did not run an interactive Copilot session.

For the native chat preference, traced the rebuilt package with a tool that supports batches, a tool that cannot represent the current question, and a host without a question tool. The instructions present only the current question in each case. Package checks and the four builder tests passed. This was an instruction walkthrough.

Verified the procedure using the extracted portable package. An ordinary bounded wait left the first form active. After the first answer was submitted, the follow-up expired. Serving that follow-up from a fresh workspace collected the remaining answer at a distinct URL and preserved the first submission. Reviewed the agent instructions for the expiry notice and fallback. All 70 harness tests, package checks, and local links passed.

## Opening a form from a terminal call

An adoption transcript showed an agent passing both preflight checks and switching to chat because its terminal lacked a managed background tool. Both adoption routes now call `launch` after preflight and verify the link. This command starts the existing server and returns the URL from a short-lived process. If delivery fails, the agent reports the blocker and lets the human choose whether to retry or use chat. [Delivery instructions](../../.agents/skills/human-interaction/SKILL.md#when-the-form-cannot-be-delivered)

All 72 harness tests passed. The new integration checks show that launch returns while the server still accepts answers, rejects invalid pages and duplicate starts, and leaves an existing form usable. The extracted portable package accepted both pages across separate commands, then closed and retained both submissions. The direct terminal flow was verified locally. A new editor-agent run was outside this check.

Ruff, BasedPyright error checks, skill metadata, and local links passed. The launcher starts the existing interpreter and server without passing commands through a shell. It returns only the published form metadata. The server still binds to loopback and enforces its existing credentials, deadlines, and shutdown rules. Startup has a bounded wait and a failed launch stops its own child.

## Question navigation and recommended answers

Put separate clarification controls by the context and questions. The user can attach an optional note to either. Preserve the other area and the answer constraints when revising. Long forms show up to five questions per browser page with Back, Next, and progress. Each round collects one submission. Agents can use `default` to prefill supported recommendations that the human can edit. [Form contract](../../.agents/skills/human-interaction/references/form-schema.md)

Verified the extracted package in Chromium with 12 questions across three pages and a separate short form. The long form retained edited and prefilled values across navigation and both scoped clarifications, restored the current question page, blocked advancement on required fields, and sent all answers in the final submission. Checked 1200 px and 390 px layouts. The short form submitted its editable default directly.

All 73 harness tests passed, including a scoped revision test that verifies preservation of the other area. Ruff, BasedPyright error checks, JavaScript complexity, HTML, CSS, package metadata, and links passed. The scope value is validated within the existing local origin, revision, and agent-control checks. Scoped revisions retain the original answer schema and recommended defaults.

## Form layout

Place the context clarification button below the prologue and the questions clarification button below the visible questions, alongside navigation. Keep questions in one column at every viewport width. Paint the gradient on the root so it spans the space above the form.

Verified the 30-question demo in Chromium at 1200 px and 390 px. Both buttons followed their content, the questions aligned in one column, and the top margin shared the same background. Navigating to the next question page kept its clarification button below the questions. All 73 harness tests and the JavaScript, CSS, HTML, and package checks passed.

## Live form updates

Use authenticated `update` to revise an open form and `revise` to respond to clarification. Both can append options or questions. Preserve the existing controls, values and constraints, and reject stale revisions. New questions keep their defaults and can add browser pages. Use `next` to publish a follow-up round after submission. [Live update commands](../../.agents/skills/human-interaction/references/form-schema.md#updating-a-live-form)

Verified the extracted package in Chromium. An open form gained a language option and an extra question page while retaining a typed answer, unchecked choice, and current position. A clarification added another language option at the same URL. A follow-up round kept the first round's answer record. All 74 harness tests passed, including API checks for unauthorized, stale, and destructive updates. Ruff, BasedPyright error checks, JavaScript complexity, links, and package metadata passed.

## Listening and question context

The form CLI provides a 30-minute `listen` window and can return sooner when an event arrives or the form ends. A short-lived record in the private session workspace indicates that a timed command is waiting. A receipt records that the command read the current clarification or submission. The browser distinguishes a waiting command, delivery, and a saved event that needs a chat message. [Listener](../../.agents/skills/human-interaction/references/form-schema.md#listening-for-feedback)

The questions clarification includes the browser page and its visible question IDs and labels. The server validates the IDs against the active form and resolves the text there. The request contains neither draft answers nor questions from the other browser pages. [Clarification requests](../../.agents/skills/human-interaction/references/form-schema.md#clarification-requests)

All 76 harness tests passed. Integration tests exercised both event types, listener shutdown and recovery, and rejection of a shorter listen window. In Chromium, a clarification from browser page three delivered just the two visible questions and kept the draft. The extracted package showed listening, receipt, and the chat prompt in the corresponding states. Verification exercised short runs rather than a full 30-minute quiet period. Ruff, BasedPyright error checks, JavaScript complexity, package metadata, and local links passed. Listener records and receipts use the existing private workspace and the scoped form status exposes only the resulting status.

## Visual design

Use a pale lavender masthead with a compact serif title, a warm context surface and clarification buttons, a coloured progress bar, and a tinted selected-choice state. Use stronger violet for primary actions and a visible outline for keyboard focus. Give dialogs and completion views the same palette. Forms retain a single column and native controls. The visual treatment uses local CSS and system fonts.

Reviewed the extracted package at 1200 px and 390 px in Chromium. Verified the selected-choice treatment, keyboard focus, context button placement, pagination, the clarification dialog, and submission with a retained edit. All 76 harness tests and JavaScript, CSS, HTML, package, and link checks passed.

After feedback on the initial styling, reduced the title size and softened the header, progress gradient, and dialog accents. Rechecked the extracted form at the same widths, including keyboard focus, question clarification, draft retention, and submission. CSS lint, package validation, and all 76 harness tests passed.

## Schema validation refactor

Separate checks for display properties, choices, length settings, and numeric settings. Validate submitted values by field family and keep workspace reads in the page loader. The same local branch-count method measured `field_definition` at 30 before and 7 after, `field_value` at 28 before and 8 after, and `valid_text` at 14 before and 5 after. The largest remaining count across the two modules was 9. [Schema validation](../../.agents/skills/human-interaction/scripts/form_schema.py) · [Page loader](../../.agents/skills/human-interaction/scripts/form_page.py)

Compared 6,021 cases against the previous implementation across all input types, invalid definitions, submitted values, and local prologues. Every result and rejection message matched. All 60 harness tests passed, including new coverage for typed answers and relative image paths. Both workflow archives exercised their packaged form, and Python type and language-server diagnostics reported zero errors.
