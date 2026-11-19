# Choose a Programming Paradigm

Start with the project's idioms. Identify whether the hard part is transformation, ordering effects, protecting state, or declaring a result. Change the approach only where it makes the behavior easier to express and verify.

| What the code needs to do | Good starting point | Design check |
| --- | --- | --- |
| Perform a series of operations in order | Imperative or procedural functions with explicit control flow | Keep sequencing and failure handling visible. Extract named steps when they clarify the sequence or are reused. |
| Transform or combine data, evaluate rules, or calculate a result | Functional style with pure functions and explicit inputs | Keep I/O outside the calculation where useful. Prefer familiar operations and use readable names for intermediate values. |
| Preserve rules over the lifetime of an entity with identity | Object-oriented encapsulation or an explicit state value with transition functions | Give state one owner. Choose the representation that makes legal operations and transitions easiest to see. Prefer composition unless callers can rely on behavioral substitutability. |
| Describe what result or constraints the runtime should satisfy | Declarative mechanisms such as queries, schemas, and rule tables | Use an existing runtime. Define what happens when rules overlap or no rule matches. Consider how to observe failures. |

A single feature can use more than one approach. An import can validate and transform records with pure functions, then perform a transaction in a small imperative entry point. A workflow with explicit legal transitions can use a transition table. Model concurrent work only when the behavior or a performance constraint requires it, and make ownership, ordering, and cancellation explicit wherever they affect callers.

Compare viable approaches on how directly they express the domain, how much state and coupling they introduce, and how well they fit the project. For a consequential choice, record the deciding constraint and what would make you revisit it.

[Peter Van Roy, Programming Paradigms for Dummies](https://webperso.info.ucl.ac.be/~pvr/VanRoyChapter.pdf)
