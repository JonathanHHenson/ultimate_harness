---
name: software-design
description: Design, implement, fix, or refactor software, or review a software design. Choose programming paradigms, apply SOLID and KISS, and use design patterns where they simplify required behavior. Apply to changes of any size, from local fixes to architecture.
---

# Software Design

## Establish the contract

- Read the relevant code, callers, tests, and project conventions. Identify the requested behavior, existing guarantees, and applicable non-functional requirements. Preserve existing behavior unless the change calls for a different contract.
- For a localized change, make a quick design pass and proceed. For changes to public interfaces, persisted state, or several components, use the project's existing design workflow to record boundaries, tradeoffs, failure behavior, and how to verify them.

## Choose the design

- Use the simplest paradigm that fits the work and the surrounding code. Start with functions for deterministic transformations, straightforward control flow for ordered effects, encapsulated state for objects with a lifecycle, or declarative rules where the runtime already interprets them. Combine paradigms at natural boundaries. When the choice has meaningful consequences, consult [Paradigm selection](references/paradigm-selection.md).
- Apply **KISS**. Prefer a direct path through existing functions, modules, and data structures. Keep the rules, invariants, and error handling the requirements call for. Defer speculative options, hooks, and infrastructure.
- Apply **SOLID** where it clarifies a boundary. Group decisions that change together (single responsibility). Isolate actual variation (open/closed). Keep replacements faithful to the caller's contract (Liskov substitution). Expose only what each caller needs (interface segregation). Keep policy independent of volatile implementation details when that boundary matters (dependency inversion).
- Consider a pattern when a concrete problem remains. Compare it with the simplest direct implementation. Use the pattern only if its benefit justifies its extra indirection, and fit it to the language and repository. Consult [Principles and patterns](references/principles-and-patterns.md) when choosing between designs or introducing a new abstraction.

## Verify the change

- Trace a normal path and relevant edge or failure paths through the public entry point. Check ordering, retries, partial updates, and concurrent changes where they can affect the contract.
- Check that a maintainer can locate each rule, see who owns mutable state, and follow the effects. Prefer domain names and straightforward control flow. Remove new structure that cannot be traced to a requirement or an established project constraint.
- Run the project's relevant checks. Where a behavior test is needed, assert the public contract or an invariant. For interchangeable implementations, check that each satisfies the same contract.
