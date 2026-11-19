# Automated test design skill

## Discover and choose the test scope (TEST-1)

Install a project skill with a narrow instruction to use it before designing, writing, or reviewing automated tests. The entry point selects the smallest test that actually exercises the relevant risk. Strategy details distinguish the level of a test from its purpose, so bug regression coverage can live at any level.

## Assert behavior (TEST-2)

Use public results, documented errors, and visible effects for oracles. Start with minimal deterministic fixtures. Use refactor resistance and defect sensitivity as complementary checks. Document the exception for behavior required across a boundary and keep configuration-only validation in its own checks.

## Keep difficult tests faithful (TEST-3)

Load service guidance when a dependency cannot be isolated faithfully. Compare accepted fakes, local real runtimes, isolated Compose services, and temporary dev deployments based on the semantics being tested. Keep the test scope narrow and label its dependencies honestly. Cover isolation, version, readiness, and cleanup. Use Spark transformations and managed-platform behavior as contrasting examples.

## Verify

Check the package and link references, review trigger overlap with software design and project validation, and forward-test through independent work. Compare generated behavioral tests against a correct implementation, a behavior-preserving refactor, and realistic defects. Review the service choices separately and keep artifacts in scratch.
