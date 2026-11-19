# Harness workflow reliability

## Session Python setup (H-1)

Default the uv cache for harness subprocesses to an ignored directory in the workspace and honor an explicit UV_CACHE_DIR. Keep the separate harness interpreter and the existing non-uv setup. Verify the plain startup command and isolate the unavailable-default-cache case with real uv and an empty dependency list.

## Project-owned skill verification (H-2)

Add a focused check for the required metadata and instruction body of each immediate project skill package. Reuse the available YAML dependency. Validate the required fields against the Agent Skills specification and accept additional runtime metadata. Keep the existing link check for local file paths and require a destination review on guidance moves. Project validation uses repo-owned commands, with the runtime validator still available for authoring. Add a short maintainer entry point with the existing workflow and validation commands.

## Feature-memory consistency (H-3)

Serialize each feature's CLI operations across processes using an advisory lock in the ignored features tree. Acquire the lock before reading or mutating the feature, including creation. Use a separate lock per feature and keep the three user files and schema intact. Support normal process-exit recovery of the lock. Commands continue to replace individual files atomically. Coordinate direct edits and keep cross-file crash consistency outside this revision.

## End-to-end verification (H-4)

Run a red-to-green concurrent append regression, exercise startup and invalid skill checks, and run the full suite. Walk through a disposable project with local setup, unique scratch space, new feature transitions, and guidance validation. Keep artifacts in the current scratch workspace.
