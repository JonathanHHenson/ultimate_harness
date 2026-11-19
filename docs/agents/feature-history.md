# Completed harness features

These notes summarize the decisions and verification recorded when the original harness features closed. Each feature's definition, design, and dated worklog are in the [feature records](../../.harness/features/). Test counts reflect the suite at the time of each change.

## Feature lifecycle and local tooling

| Feature | Decision and verification |
| --- | --- |
| Feature memory | Use a feature definition, design, and worklog with explicit feature and requirement transitions. The original closeout recorded 16 behavioral tests, parsed examples, and Git ignore checks. It was reconstructed after implementation. The [current completion policy](../TECHNICAL.md#feature-completion-and-merge-checks) supersedes its original ignore rule. |
| Dynamic validation | Keep trigger selection in a short index and place checks in contextual rulesets. The link checker, trigger walkthroughs, and all 21 harness tests passed. |
| Local scratch | Preserve a shared, ignored workspace and create a unique directory for each agent session. Isolated Git and filesystem checks verified path handling and preservation of existing files. All 27 harness tests passed. |
| Harness Python environment | Bootstrap an isolated environment with uv, the standard library, or virtualenv as available. The closeout recorded coverage of all three creation paths and verified environment reuse and Git ignore behavior. All 28 harness tests passed. |
| Harness workflow improvements | Keep concurrent feature updates recoverable and make cold startup work when the default uv cache is unavailable. All 33 tests passed. A disposable project exercised setup, scratch creation, feature transitions, and guidance checks. |
| Harness script audit | Consolidate filesystem safety checks where the scripts share a trust boundary. Code and security reviews covered local reads and writes, setup isolation, and user-facing diagnostics. All 41 tests passed. The type checker and language server reported zero errors across 16 files. |

## Skill design

| Feature | Decision and verification |
| --- | --- |
| Software design | Route software changes through paradigm selection, SOLID, KISS, and patterns that fit the task. The package and links validated. Two independent tasks passed four public-behavior checks. |
| Automated test design | Prefer public-behavior tests and select the environment according to the dependency behavior under test. Independent service plans and an isolated Compose walkthrough met the design criteria. |
| Standalone topic learning | Make inquiry, source assessment, and transfer available to workflows beyond skill authoring. Package and routing checks passed, and an independent validation drafting task reproduced the expected outcomes. |
| Build harness skill revision | Preserve the existing contracts and route by the kind of change. A matched relocation task scored 6 of 6 with both skill versions. That comparison established parity on one task. |

## Session-end reviews

| Feature | Decision and verification |
| --- | --- |
| Code review | Start with available diagnostics, then review design, branching, file cohesion, and module placement. Walkthroughs exercised review routing and gave concrete cases for each cleanup signal. |
| Behavioral code review | Require a review of public-behavior coverage and passing full-suite tests. In a focused example the selected test passed while full discovery found a regression. Both passed after repair. Two paired benchmark task designs passed preflight. |
| Security review | Scope STRIDE and OWASP review to the affected controls. In three matched runs per arm on a synthetic application, both arms found all six predefined issues. All three runs with the security rules showed concrete STRIDE and OWASP evidence checks. The code-review-only arm documented zero such applications. The detection results reached the benchmark's ceiling in both arms. |
| Review routing | Scope review selection and check execution together. The first replay opened the expected rule files but ran unrelated checks. With the revised routing, two fresh Codex runs for each scope confirmed that configuration-only ran security checks, documentation-only skipped both reviews, and mixed changes ran both. All 33 harness tests passed. |
