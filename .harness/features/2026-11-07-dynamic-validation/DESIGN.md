# Design: Dynamic Validation

## F-1: Main validation entry point

Create `.harness/VALIDATE.md` as a small instruction file. Every second-level
heading is a contextual event. A common selection trigger tells the agent to
apply every matching situation, followed by concrete guidance-change and
script-change triggers that route to separate rulesets. A feature-completion
trigger requires satisfied acceptance criteria and recorded validation evidence.
Use file-relative Markdown links and project-root-relative command paths so
links remain navigable without making command execution ambiguous.

## F-2: Situational rulesets

Use `.harness/validation/harness-guidance.md` for agent instructions, skill
documentation, and validation policy changes. It owns local-reference checking,
skill packaging validation when applicable, semantic trigger review, and a
matching/nonmatching walkthrough. Use `harness-scripts.md` for script, test, or
dependency changes. It owns the existing unittest command and the rule that
changed behavior needs suitable behavioral coverage. Both keep contextual
second-level headings, state success criteria, and explain failure handling.
Do not create placeholder rulesets for future products or tests.

## F-3: Discovery and skill guidance

Add a short route to VALIDATE.md under the existing start/resume feature trigger
in AGENTS.md. The feature-completion instruction also refers to VALIDATE.md.
Extend build-harness with a validation-authoring reference, an explicit placement
table row, and a conditional pointer. The reference explains the format,
selection of overlapping rules, executable actions and prerequisites, completion
criteria, evidence, and maintenance as project scenarios change. It contains
authoring guidance rather than a duplicate of this project's runnable checks.

## F-4: Focused local-reference checker

Add `.harness/scripts/check_markdown_links.py` using only the Python standard
library. Accept Markdown files or directories, recursively inspect Markdown
files in directories, and fail on nonexistent input paths or missing local
targets. Skip fenced examples and inline code; handle the inline file-link
syntax used by this harness, including percent-encoded spaces and angle-wrapped
destinations. Resolve targets relative to the document, remove query/fragment
suffixes, and ignore external URL schemes and anchor-only links. Report the
source location of broken references and exit nonzero. It checks file existence,
not heading anchors, network URLs, semantic triggers, or every Markdown dialect.
Test observable outcomes in temporary files through the command interface.

## NF-1: Dynamic selection, completion, and maintenance

Guidance-only changes select the guidance ruleset. Script-only changes select
the script ruleset. A change to both selects both; unrelated changes do not
select either situation merely because the files exist. Common feature
acceptance and evidence rules still apply at completion. After a fix, repeat
affected checks; expand coverage if new changes or failures warrant it. Record
passed, failed, and unrun checks accurately, including blockers, in feature
memory without redefining its schema or weakening its DONE gate.

The Markdown index is interpreted by the agent. Selection remains semantic:
there is no scheduler, filesystem monitor, or generated execution engine. Keep
commands in their owning rulesets and link to them instead of copying them
into AGENTS.md or the feature-memory instructions. Validation documents remain
trackable. The [feature completion policy](../../../docs/TECHNICAL.md#feature-completion-and-merge-checks) also versions feature records.

## Verification and risks

Run focused reference-checker behavior tests, then the existing harness suite
because a new script and tests are being added. Run the checker over live
instruction and skill Markdown and use skill-creator's validator on the updated
skill. Review every active instruction heading and manually exercise the four
selection scenarios above. A file-existence checker cannot establish semantic
quality or real acceptance evidence; keep those review steps explicit.
