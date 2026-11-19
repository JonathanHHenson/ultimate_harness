# Design Behavioral Unit Tests

## Pick the observation

- Start from a supported interface. State the scenario, input or prior state, and observable outcome. Include important negatives, such as rejection with no write, when specified. Exercise private logic through its caller. If it has a genuine independent contract, give it a focused interface when that improves the design.
- Arrange only the conditions that affect the outcome. Act through the entry point. Assert the relevant values, errors, state, or effects. Multiple assertions can describe one coherent outcome. Parameterize cases with the same rule and keep distinct scenarios readable.
- Use real deterministic collaborators or lightweight fakes where feasible. Use stubs to inject errors or conditions that are hard to arrange. Inspect a recorded interaction only when it represents a requirement across a boundary, such as a single externally billed request or a guarantee that rejected data is never published. Prefer observing the effect where you can.

| Brittle assertion | Behavior to exercise |
| --- | --- |
| The code contains a private helper or calls it twice | An invalid input produces the documented error and leaves state unchanged. |
| The fixture matches the current settings dictionary | Omitting the option applies the documented default, or changing it changes the result in the specified way. |
| The mock sees a particular chain of query builder methods | The query returns the right rows with realistic data in the target engine. |
| A full output dump matches a snapshot approved by the current code | Contract fields match independent expectations. Use a focused snapshot only for an intentionally stable artifact, such as a public serialization format, and review meaningful differences. |

A fixture or mock can reproduce a particular configuration to expose a bug. Assert the behavior that went wrong under that configuration. For configuration artifacts under their own contract, use a schema or policy check for declarative constraints and a runtime test for effects that depend on startup or deployment.

## Review for false confidence

- Ask what defect the test would catch and whether an equivalent implementation would still pass. Remove duplicated application logic from expected values. Inspect that the test runner collects the case and that the assertion observes the actual result.
- For regression coverage, reproduce the smallest useful failing example. Run the same test against unfixed and fixed code, or record why the original could not be run. A failure caused by broken fixture setup provides no evidence about the defect.
- Treat coverage as a map of exercised code. Assess whether assertions are sensitive to meaningful defects. For a critical rule, selectively try a small mutation in a disposable copy when this is safe and useful.

[Software Engineering at Google, Unit Testing](https://abseil.io/resources/swe-book/html/ch12.html) · [Software Engineering at Google, Test Doubles](https://abseil.io/resources/swe-book/html/ch13.html) · [Ham Vocke, The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
