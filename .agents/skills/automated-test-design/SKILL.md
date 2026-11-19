---
name: automated-test-design
description: Design, write, review, or improve automated software tests and decide how to verify a feature or bug fix. Use for behavior-focused unit, integration, regression, contract, or end-to-end coverage, including tests with difficult dependencies such as Spark.
---

# Automated Test Design

## Identify the behavior and risk

- Read the requirement, supported entry points, existing tests, and project validation rules. Name the behavior or failure to detect and how a caller can observe it. Derive expected results independently from the specification or a small worked example.
- Choose the smallest scope that can detect the failure with realistic semantics. Use existing test tools and fixtures when they fit. Add broad tests only where the narrower checks leave a meaningful gap.

| Goal | Strategy |
| --- | --- |
| Check a rule, invariant, or documented error in a focused scope | **Unit**. Exercise the module or component interface with minimal inputs and controlled dependencies. |
| Check an interaction whose semantics matter, such as transactions, migrations, serialization, or Spark evaluation | **Integration**. Exercise the real boundary or runtime with isolated data. |
| Check that independently released components agree on a schema, protocol, or error contract | **Contract**. Verify consumer expectations against the provider or its published contract. |
| Prove a critical user flow works across deployed parts | **End-to-end**. Cover essential journeys and assert the user-visible result. |
| Prevent a specific known failure from returning | **Regression**. Reproduce the trigger and assert the required result at the cheapest reliable level. |
| Check an invariant over many inputs or transitions | **Property-based**. Constrain generators to relevant inputs and retain a reproducible failing example. |
| Quickly verify a deployed build or environment is usable | **Smoke**. Check readiness and a small critical operation. |
| Verify a timing, throughput, or resource requirement | **Performance**. Measure that requirement under a representative, controlled workload. |

## Write behavioral assertions

- Assert returned values, documented errors, observable state, or externally meaningful side effects. Use configuration as an input when it changes a supported behavior. See [Behavioral unit tests](references/behavioral-unit-tests.md) when designing or reviewing unit assertions or replacing brittle tests.
- Reject unit tests that freeze source text, private helpers, incidental call order, or exact configuration values. A behavior-focused test should still pass after a refactor that preserves the contract. If a configuration artifact has its own required schema or policy, put that assertion in a configuration or deployment check. Exercise a public default or setting through the behavior it promises.
- Keep fixtures minimal and independent. Prefer explicit inputs, bounded waits, and controlled clocks or randomness when needed. Cover representative outcomes, important boundaries, and known failures. Give each test a clear purpose and a failure message that helps diagnose it.

## Choose dependency fidelity

- Unit-test logic independent of the service when a natural boundary exists. If the behavior requires a service, choose a maintained and trusted double only when it models the relevant contract. Otherwise use a real local runtime, a self-hosted service with Compose, or a short-lived deployment on the project's dev platform. Follow [Testing with complex dependencies](references/complex-dependencies.md) when making that choice.
- Keep resource requirements and verified scope visible. A focused test that needs a live dependency belongs in the service-backed or integration lane even if it exercises one component.

## Check that the test earns its place

- Verify the new test passes for the intended behavior. For a bug fix, observe the test fail on the unfixed code when feasible. Otherwise use a small controlled defect where it adds confidence, and check that failure comes from the intended assertion. Review whether an equivalent implementation could still pass.
- Run the focused tests and the relevant project suite. Report which behavior ran at which level and distinguish skipped or unavailable environments from passing runs.
