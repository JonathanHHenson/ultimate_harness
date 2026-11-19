# Software design skill

## Project entry point (DES-1)

Add one contextual trigger to the root agent instructions and install the skill at `.agents/skills/software-design/`. Its discovery description covers designing and changing software, including localized fixes. Documentation-only changes do not match the trigger. The root instruction also enables direct loading when runtime discovery has not refreshed.

## Design workflow (DES-2)

Use the current code and callers to establish the contract. Choose paradigms by the problem and the repository's conventions, then apply SOLID and choose patterns only where they resolve an identified problem. Keep the core workflow short and load the two references conditionally. Treat simplicity as reducing the amount of code and reasoning needed to satisfy the contract, including genuine failure and operational requirements.

## Verification (DES-3)

Review trigger matches and reference routes, validate the package and local links, then independently apply the staged skill to a localized change and a small integration change. Check artifacts for observable behavior and review how much design structure each task required. Keep evidence in the local session directory. A successful forward test verifies use on those cases. Comparative effectiveness requires separate evaluation.
