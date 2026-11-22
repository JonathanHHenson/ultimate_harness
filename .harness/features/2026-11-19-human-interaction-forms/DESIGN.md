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
