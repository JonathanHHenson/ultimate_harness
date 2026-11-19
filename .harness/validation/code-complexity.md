# Code Complexity Validation

## Before selecting complexity checks for changed code

- Identify every executable language changed, including embedded scripts and test code. Review changed functions, methods, procedures, and equivalent units such as executable rules or queries. Apply the project's language skills and configured analyzer for each language. Record the command, measured scope, limit, and outcome for each language. A passing check for one language leaves the others open.
- Use the configured maximum when the project has one. Otherwise use 10 per unit. For tools with different counting rules, use the same tool and settings when comparing old and new code. Review the code’s boundaries as well as its score.

## When an analyzer is unavailable or misses changed units

- Count decision points by hand for those units. Start at one, then add the choices introduced by branches, loops, exception handlers, conditional expressions, short-circuit Boolean operators, and alternatives or guards in pattern matching. Apply the same method to the language's equivalent constructs, including conditional expressions inside a query or rule. Count nested independently callable functions separately.
- Record the unit and the count in the validation evidence. Review declarative changes with their language's syntax and behavior checks. When a declarative unit includes branching logic, apply the complexity check to that logic. Report any changed executable unit that remains unverified.

## Before marking code review complete

- Fix functions above their limit and rerun the affected checks. Use cohesive responsibilities and meaningful boundaries. Review nesting, file size, and module organization alongside the score. Keep a review open while a changed executable unit lacks complexity evidence.
