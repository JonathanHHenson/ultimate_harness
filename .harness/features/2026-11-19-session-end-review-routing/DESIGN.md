# Session-end review routing

## SELECT

At handoff or session end, use the root instructions to reach one decision in the project validation index. Determine which staged, unstaged, and untracked changes belong to the session or requested patch. Classify by purpose so a configuration file written in a programming language can still select the configuration route. Select the first matching row before opening review instructions. The row for any code change selects code and security review. The configuration-only row selects security review. The remaining row skips both. Evaluate other validation triggers independently. Leave the code and security review procedures in their existing files.

The prior Codex reports correctly recognized the pending file types but opened adjacent review rules anyway. Merely tightening the separate headings leaves that ambiguity intact. A single exclusive selection keeps scope visible and avoids adding a file-extension classifier that cannot distinguish settings from executable behavior or establish session ownership.

The first replay showed that agents could select the right rules and still run unrelated checks due to the general release handoff prompt. The same table now governs both actions. The configuration row limits checks to changed settings and affected controls. The final row ends the handoff after validating the changed artifacts where relevant.

## RETEST

Rebuild fresh synthetic workspaces from the previously tested B snapshots. Replace only the two routing files and retain the prompt, code and configuration inputs, local check commands, model settings and expected scope. Run two attempts per scope. Verify actual rule reads and completed commands in each trace. Mixed sessions should run the six-test suite, type check and deployment check. Configuration-only sessions should run the deployment check and skip code review. Documentation-only sessions should skip both reviews and all their checks. If a probe exceeds scope, revise the shared decision and replay the affected scenarios.
