# Apply SOLID, KISS, and Patterns

These checks apply to functions, modules, interfaces, and objects. Start with the existing design and use only the distinctions that help this change.

| Principle | Ask | Apply it when it helps |
| --- | --- | --- |
| Single responsibility | Which decisions should change independently? | Keep related policy and invariants together. Separate unrelated decisions, such as a pricing rule and how quotes are stored, when coupling would make either harder to change. |
| Open/closed | Which variation does the contract already require? | Isolate the varying decision so adding an implementation leaves stable policy alone. Keep a short branch or table when alternatives are fixed and clear together. |
| Liskov substitution | Can a caller rely on the same guarantees for every implementation? | Check accepted inputs, outputs, errors, invariants, and relevant side effects. Implementations must accept the inputs the shared contract permits and honor its promises. |
| Interface segregation | What behavior does this caller actually use? | Expose a focused contract. Reuse a clear existing interface if it already fits. |
| Dependency inversion | Does stable policy need to know how a volatile detail works? | Let the caller or policy define the contract it needs and supply the concrete implementation at the boundary. A callable or plain argument can suffice. |

KISS includes keeping necessary recovery and validation straightforward. Defer capabilities without a current requirement. A useful abstraction makes it easier to locate a rule, preserve an invariant, or change an existing variation. Verify that it pays for the new names and extra hops.

## Choose a pattern by its problem

| Concrete problem | Try first | Consider the pattern when |
| --- | --- | --- |
| Several required ways to perform one operation share a caller contract | A conditional, lookup table, or callables | **Strategy** makes the alternatives independently implementable or selectable without changing shared policy. |
| A library or service represents an operation differently from callers | A small conversion function | **Adapter** gives callers one coherent contract and contains representation, error, or protocol translation. |
| The same operation behaves differently in different lifecycle states | An explicit state value and guarded transitions | **State** groups substantial state-specific behavior and makes transition rules easier to follow. |
| Construction varies across required contexts | Direct construction or a named constructor | A **factory** centralizes meaningful construction rules or selection shared by multiple callers. |
| Several callers repeat the same behavior around an operation | A shared function | A **Decorator** allows required behavior to compose while preserving the original contract. Make wrapper order visible where it matters. |

For a handling fee that now has one cap, put the rule beside the existing calculation. A pricing strategy interface would add an extension point with no current use. For two shipping services that represent money and failures differently, normalize each service response at its boundary and keep shared quote policy in one place. A conversion function per service may be enough.

[Robert C. Martin, Design Principles and Design Patterns](https://wnmurphy.com/assets/pdf/Robert_C._Martin_-_2000_-_Principles_and_Patterns.pdf) · [Liskov and Wing, A Behavioral Notion of Subtyping](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf) · [Gamma et al., Design Patterns](https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-9780321770462) · [Martin Fowler, Yagni](https://martinfowler.com/bliki/Yagni.html)
