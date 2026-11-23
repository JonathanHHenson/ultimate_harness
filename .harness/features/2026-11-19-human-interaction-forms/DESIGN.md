# Human interaction forms

## FLOW

The agent creates a page JSON and runs a foreground Python server in a background tool session. A random browser URL serves one interaction. The status route presents the current page, a waiting view after a multi-page submission, or a final confirmation. Each successful submission is saved atomically as a separate private JSON response, readable by the wait command even after the server exits. Next and close use a separate local control credential. Page numbers make duplicate or stale submissions fail without replacing responses. On completion, the browser acknowledges the rendered confirmation and the server shuts down. A short grace period and bounded lifetime cover a disconnected browser or an abandoned server.

## RENDER

The JSON declares fields, choices, defaults, validation, layout, and a relative Markdown path in the session workspace. Browser standards supply responsive, accessible HTML controls. A local text renderer supports the Markdown needed for prologues and renders documented Mermaid flowchart and sequence subsets. It builds DOM and SVG nodes from text. Unsupported diagram syntax remains visible as code. Local raster images are included from the prologue directory within the session workspace.

## LOCAL

Use standard-library Python and local HTML, CSS, and JavaScript. Listen on IPv4 loopback with an ephemeral port. Separate public form and agent control capabilities. Restrict public mutations to the form origin, verify Host, reject broad file access, avoid raw HTML injection, and keep response files out of Git under the chosen scratch workspace. Use two integration tests for the lifecycles and defensive boundaries, a real browser for mobile and desktop views, and validate the portable export.

## ADOPTION

Route open installation and evolution decisions to the existing form tool from each built package. Use a single submission when the proposal is concrete and subsequent pages when answers change the plan. Keep the payloads and responses outside the target if it has no suitable ignored workspace or changes have yet to be agreed. Run the bundled script with an existing interpreter so the feedback step is independent of the target installation. Preserve chat and native questions as a fallback for remote sessions or short answers.

## EXPIRY

Use a monotonic one-hour inactivity deadline with an optional absolute cap. Extend inactivity on accepted multi-page submissions and next pages only. Check deadlines under the same lock that governs transitions. Publish an estimated wall-clock deadline while active. The browser polls for state, refreshes when brought to the foreground, and uses the last deadline when it cannot reach the server after expiry. The server stays available briefly for the final status, then exits even without a browser acknowledgement.

## CLEANLINESS

Keep schema validation free of filesystem access. Split field definition checks by the properties they protect and submitted value checks by field family. Put page, prologue and local image reads behind the existing load operation in a dedicated module. Compare branch counts and behavior with the previous code, then verify the ordinary CLI, browser API, and portable packages.

## RESUME-AFTER-EXPIRY

Use the existing live expiry state and final state record to tell expiry apart from an ordinary bounded wait. Keep unanswered page inputs and saved responses in their original workspace. Ask the human to signal when they are ready. Then create a fresh form session for the pending questions with the regular page checks and readiness probe. Carry forward earlier submissions from the original workspace. Reserve the conversational fallback for initial delivery limits or a human request to use chat. This changes agent guidance and uses the existing server interface.

Exercise expiry on an unanswered follow-up page, serve that page from a new workspace, and confirm that a new URL can collect the remaining response while the original answer record stays available.

## TERMINAL-LAUNCH

The previous instructions required a managed background tool even when the editor could execute terminal commands. Add a short-lived launch command that starts the same form server as a child process with its own session and returns the server's published URL. Reuse page validation, workspace isolation, time limits, and access checks. Wait at most five seconds for the startup result and clean up the child on failure. Run a separate loopback readiness request before sharing the URL. Use the launch command on both adoption routes. If the form cannot be delivered, report the actual blocker and ask the human how to continue.

Exercise launch through a terminal call that exits before the form is opened. Check a duplicate start, an invalid page, and completion with saved answers. Run the same flow from the extracted portable package.

## FORM-NAVIGATION

Display a clarification button with the context and a second with the questions. The request carries its scope and the server preserves the other part of the form during revision. Keep the existing scope for older clients. Preserve answer IDs, values, defaults, and constraints during every clarification.

Split each round into browser pages of up to five questions. Keep the controls in one form so navigation retains their values and the final Submit action sends all answers together. Validate the current group before moving forward and locate any invalid control before submitting. Preserve the browser page and draft when a clarification returns. Reuse the JSON default field for recommended answers and tell the human that prefills are editable.

## FORM-LAYOUT

Put each clarification control after its content. The questions control follows the current group, alongside navigation. Use one question column at all widths. Paint the gradient on the root so the page has a continuous background through the top margin.

## LIVE-FORM-UPDATES

Add authenticated `update` for an open revision and let `revise` append choices or questions when the clarification scope permits it. Existing IDs, order, options, defaults, and constraints stay valid. Additions can create new browser question pages before the round is submitted. Keep `next` for a new round after submission. Reject stale revisions before publishing and keep completed answer records in place.

The browser renders the new revision at the same URL and carries forward the draft and visible page. Track which field names existed before the update so unchecked answers stay unchecked and new questions keep their defaults. Verify both update paths and a subsequent adaptive round.

## FORM-LISTENER

Add `listen` to the form CLI with a minimum wait of 30 minutes and reuse the saved-event reader. While a timed command waits, refresh a short-lived record in the private session directory. Expired records stop indicating presence even if the command is killed. Mark receipt when the command delivers an answer or a clarification. Tie receipt to the submitted round or the clarification's revision. The HTTP state exposes the status without exposing the records. The browser updates its message as status changes and gives a listening command time to read a single-page submission before acknowledging final shutdown. Keep form expiry independent of the listener.

## QUESTION-CONTEXT

Send the browser's current question-page number and the visible field IDs with a questions clarification. Resolve their labels against the server's current page and retain them in the event. The context button continues to send only its scope and optional feedback. The clarification's revision still identifies the correct page definition.

## FORM-VISUAL-DESIGN

Use a pale lavender masthead with a compact serif title, violet progress accents, warm surfaces for context and clarification, and tinted selected choices. Use stronger violet for primary actions and keyboard focus. Retain standard system fonts, native form controls, and the single-column layout. Use the existing stylesheet and a small amount of structural markup, with no runtime assets or dependencies. Check the form, clarification dialog, and confirmation at desktop and phone widths.
