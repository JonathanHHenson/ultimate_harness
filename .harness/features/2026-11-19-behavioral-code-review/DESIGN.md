# Behavioral code review

## Coverage and full-suite gate (CV-1)

Keep the existing session-end trigger and review order. Add a test review stage that uses the automated test design skill and examines public outcomes, boundaries, failure and state invariants, fidelity, and known regressions. Require the complete configured unit suite on final code and re-run it after any code or test changes. Report unsuccessful and unavailable checks separately. Reuse a recorded full-suite run against the same final state when other validation triggered it.

## Larger paired workload (CV-2)

Use two isolated, synthetic Python projects. The stock reservation workload adds a persistent lifecycle, atomic batch operations, a leaseable outbox, and CLI entry points. The manifest workload adds layered parsing, graph planning, and safe plan application on a durable state file. Both have passing legacy tests, deliberately unimplemented feature boundaries, separate acceptance suites, and no external service. Measure correctness, maintainability, and the ability of authored tests to catch selected realistic faults. Compare the existing code review against the strengthened rule so other harness guidance remains matched. Keep all benchmark artifacts in scratch.
