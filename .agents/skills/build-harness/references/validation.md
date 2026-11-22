# Dynamic Validation Authoring Standard

Use this standard to establish or maintain context-sensitive project validation.
It defines how to organise validation instructions; actual project checks belong
in the project's validation files.

## Before adding or materially changing a rule

Use [learn-a-topic](../../learn-a-topic/SKILL.md) to establish what the rule must catch and what the available check actually verifies. Inspect existing checks and the contract for the behavior under test. When feasible, try the proposed check on a case that should pass and a case that should fail. Carry the pass criteria and any limits into the rule. Reuse research already done for this change.

## Validation index

Store the validation index in `.harness/VALIDATE.md`. Keep it minimal,
clear, and instructional, like `AGENTS.md`. Every `##` heading must describe a
concrete situation or lifecycle event that requires validation. Under each heading,
state which checks or review actions to perform and how to complete them, or
explicitly require following a linked situational ruleset.

Use triggers such as `## After changing the database schema` or
`## Before marking a feature DONE`. Avoid topic headings such as `## Database`
or `## Tests`. Tie triggers to real project situations and affected behavior,
not an expanding catalog of ad hoc tasks. Do not fill the index with long
commands, schemas, rationale, or unused scenarios.

## Situational validation rulesets

Put each situation-specific validation ruleset in a descriptively named
`.harness/validation/<situation>.md`. Add a matching `##` trigger to
`VALIDATE.md` that explicitly requires reading and following that file.
Keep specialised files minimal and instructional, with contextual `##` headings
and links to background documentation when needed. Do not load them unconditionally.

Each actionable ruleset must provide enough information to perform its checks:

- The prerequisites, working directory, inputs, and exact command or review actions.
- Observable pass criteria, including evidence needed for manual checks.
- What to fix or record on failure, and which affected checks to repeat after a fix.

State path bases where needed. Prefer file-relative Markdown links for navigable
document references, and explicitly state the working directory for commands.
Use focused scripts under `.harness/scripts/` for repeatable mechanical checks;
keep semantic review in instructions. Put appropriate behavioral tests under
`.harness/scripts/tests/`.

## Discovery and selection

Add a short contextual route from `AGENTS.md` to `.harness/VALIDATE.md`, so the
agent learns applicable validation obligations during relevant project work.
Keep procedural detail in its owning validation ruleset rather than duplicating
it in agent instructions, skills, or feature memory.

Match the change and current lifecycle event against the triggers. Apply every
matching ruleset; overlapping contexts may require multiple sets of checks.
Unrelated situations should not load their specialised rules merely because
the files exist. Shared checks may stay in a short shared trigger
section of `VALIDATE.md` when they truly apply to all matching work.

Before completing a feature, verify its requirements against their definitions of
done and follow the applicable validation rulesets. Record meaningful commands,
results, acceptance evidence, and unresolved blockers in the feature record. Distinguish passed, failed,
and unrun checks. A missing prerequisite is an unrun check, not a successful one.
Use the existing feature phases and follow the feature closeout instructions.

## Maintaining the rules

When a component, interface, dependency, test command, or acceptance criterion
changes, update the corresponding triggers and actions. Remove obsolete rules,
repair callers when moving rulesets, and keep one maintained source for each
procedure. Create specialised files only for actual project situations.

Check that every situation-specific ruleset is reachable from `VALIDATE.md`, references and
commands resolve, and all live `##` headings express contextual triggers.
Walk through a matching case, an unrelated case, and overlapping cases to verify
selection. Run relevant scripts and behavioral tests; do not infer semantic
correctness solely from a heading or link checker. After a fix, repeat affected
checks and broaden verification when new changes or failures warrant it.
