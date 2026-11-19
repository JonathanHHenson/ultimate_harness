# Session-End Code Review

## When starting the review

- Identify the code you added or changed this session, including tests, scripts, and new files. Use the diff and untracked-file list when Git is available. Otherwise use the session's changed paths. Read the changes in context and follow affected callers and interfaces as needed.
- Run the project's relevant lint and static type checks in diagnostic mode with its configured environment. Use available language-server diagnostics for the changed files. Prefer repository commands and configuration, then applicable installed tools when a repository command is missing. Check that the tools analyzed the intended files and report unavailable or excluded checks.

## After collecting tool diagnostics

- Use the [software-design skill](../../.agents/skills/software-design/SKILL.md) to review the code's architecture and behavior. Trace the change through its normal entry point and the relevant failure paths. Check interfaces, invariants, dependency direction, and whether the paradigm, abstractions, or patterns fit the actual requirements.

## When reviewing code cleanliness after the design pass

- **Cyclomatic complexity.** Inspect changed functions for new branches, deep nesting, compound conditions, and mixed error handling and business logic. Use configured complexity diagnostics and compare changes with the previous code when available. Make paths easier to follow with simple guards, named domain decisions, or a clear table for genuinely data-driven cases. Check that the change preserves edge cases and reduces the reasoning burden across helpers.
- **File size.** Use available size diagnostics or compare large or fast-growing files with their previous versions and nearby modules. Look for independent responsibilities that hide the main flow or force unrelated changes into one place. Extract a cohesive responsibility where it has a clear interface. Keep closely related behavior together when one file is easier to understand.
- **Module organization.** Look across the changed files and nearby modules. Put related code that changes together in the existing domain or feature module. Introduce a focused module or package when related files are scattered and have a clear shared purpose. Keep imports and public entry points usable and avoid cycles, generic dumping grounds, and moves based on filenames alone.
- Apply project-configured limits. For other findings, name the concrete path, responsibility, or dependency that makes the code hard to maintain. Flag any relevant dead code, duplication, or unclear naming that obscures behavior.

## When reviewing behavioral coverage

- Use the [automated test design skill](../../.agents/skills/automated-test-design/SKILL.md). Compare the changed behavior and affected existing guarantees with what the tests actually assert through supported entry points. Check meaningful success cases, boundaries, failures, and regressions. Check resulting state or side effects where they are part of the contract.
- Fix material coverage gaps with focused behavior tests at the appropriate level. Use integration tests where a unit test cannot exercise the relevant boundary. For bug fixes, verify that the regression test detects the original defect when feasible. Judge adequacy by the defects the tests can catch and the behavior they protect.

## Before reporting the review complete

- Fix actionable findings within the change's scope and rerun affected diagnostics and behavior checks. Confirm design, cleanliness, and behavioral coverage on the final code. Keep unrelated cleanup out of the change.
- Run the complete configured project unit-test suite after the last code or test change. Use the documented commands and environments, including each configured unit suite in a multi-package project. Reuse a passing full-suite run against the same final state. Require a successful run with the expected tests collected. Focused tests are useful while iterating. The full suite is the completion check.
- Resolve failing tests and rerun the full suite. If a suite is missing, skipped, or blocked, record the reason and the scope left unverified. Report skipped or excluded tests separately from passing tests.
- Record the tools and scope checked, any unavailable or unrun checks, and unresolved findings with a file location and impact. Use feature memory when applicable. Distinguish completed review from unresolved validation failures.
