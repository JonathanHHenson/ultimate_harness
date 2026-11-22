# Feature Memory Contract

Use this contract when building or maintaining feature memory in a programming harness. The schemas and lifecycle rules below apply to each feature. Project paths and commands are relative to the project root.

## Storage and discovery

Create the feature store at `.harness/features/` and track its feature records. Ignore the `.locks/` child directory and each feature's pending status and temporary write files. Keep raw working artifacts in the scratch workspace where the project provides one.

Give each feature a directory in `YYYY-MM-DD-<slug>` format, such as `2026-11-19-incremental-build-cache`. The date is the UTC day of creation and the lowercase kebab-case slug matches `[a-z0-9]+(?:-[a-z0-9]+)*`. Reuse the full dated name when resuming a feature. Choose a descriptive slug for distinct work and never overwrite an existing directory.

Each directory contains:

```text
.harness/features/2026-11-19-incremental-build-cache/
├── DEFINITION.toml
├── DESIGN.md
└── WORKLOG.yaml
```

Route starting and resuming feature work from a contextual `AGENTS.md` trigger to `.harness/agents/feature-memory.md`. Require reading the selected feature's three files before continuing. Find the relevant feature without loading unrelated feature histories. If several records could match and context cannot resolve them, ask which feature to resume.

These records carry context across sessions and Git checkouts. Use durable repository paths and material that is suitable for version control.

## DEFINITION.toml

Use these fields:

- `description`: a detailed account of the feature's purpose, behavior, boundaries, and relevant context.
- `documentation`: a list of relevant documentation URLs or project-relative paths; state where a path is relative if it is not the project root. Gather relevant links during research; an empty list is valid when none have been identified yet.
- `status`: one of `RESEARCH`, `DESIGN`, `IMPLEMENT`, `TEST`, `DONE`.
- `requirements`: a list of requirement tables. Include functional behavior and applicable non-functional constraints; assess both explicitly rather than inventing irrelevant requirements.

Each requirement has a stable unique `id`, a `kind` of `functional` or `non-functional`, a detailed `description`, an observable `definition_of_done`, and a `status` of `TODO`, `WIP`, `BLOCKED`, or `DONE`.

For BLOCKED requirements, `blocked_reason` must explain the concrete obstacle and what is needed to resolve it. `blocked_from` records the prior `TODO` or `WIP` state so unblocking resumes the correct step. Both blocking fields must be empty or absent when not blocked.

Example initial definition:

```toml
description = """
Reuse compiled artifacts when source content and compiler options are unchanged.
Cache lookup must preserve existing compiler diagnostics and rebuild safely when
an artifact is corrupt. Remote cache distribution is outside this feature.
"""
documentation = ["docs/build-pipeline.md", "docs/artifact-format.md"]
status = "RESEARCH"

[[requirements]]
id = "F-1"
kind = "functional"
description = """
Compute a cache key from source content and compiler options. Reuse the artifact
only when both match; changed inputs must invoke the compiler and refresh it.
"""
definition_of_done = """
An unchanged-input build reuses the artifact without invoking the compiler;
changing either a source file or a compiler option invokes compilation.
"""
status = "TODO"
blocked_reason = ""

[[requirements]]
id = "NF-1"
kind = "non-functional"
description = """
Detect corrupt cached artifacts, emit a useful diagnostic, and rebuild without
failing a build that would succeed without the cache.
"""
definition_of_done = """
A test with a deliberately corrupt entry reports the rejected entry and
produces the same successful artifact as a cache-free build.
"""
status = "TODO"
blocked_reason = ""
```

Replace example content and documentation paths with real feature information. Keep requirements and links current as research changes the scope. Add new requirements in TODO; do not silently rewrite an already completed requirement's acceptance criteria as though new work were complete.

## DESIGN.md

Maintain a detailed technical design covering every requirement by its stable ID. Explain the architecture, interfaces, data and control flow, affected components, alternatives and tradeoffs, non-functional constraints, error handling, and verification strategy where relevant to this feature.

During RESEARCH, record findings, assumptions, and open questions. During DESIGN, resolve enough detail to implement and verify every requirement. Revise the design when new evidence changes the approach; return to an earlier feature phase when that work is needed. A scaffold is a starting point, not a completed design.

## WORKLOG.yaml

Use a chronological YAML list. Each entry has a quoted ISO 8601 UTC `timestamp`, the feature `phase` at that time, a concrete `summary`, and informative `details`:

```yaml
- timestamp: "2026-11-07T15:30:00+00:00"
  phase: DESIGN
  summary: Cache keys exclude checkout location
  details: >-
    Compared equivalent source trees in two checkout directories and confirmed
    that absolute paths would prevent reuse. The key will use relative source
    paths and content digests. Next, verify which compiler flags affect output.
```

Update frequently when there is something useful to report: findings, decisions and their reasons, concrete changes, validation evidence, failures, blockers, or next actions that matter to a handoff. Name affected requirement IDs in the details when useful. A new agent should be able to understand the history and current next step, and a human should be able to audit what happened.

Avoid repeated plans, bland activity summaries, and duplicate status updates. Omit an entry if it adds no useful information. Preserve earlier entries; append a correction when earlier information proves wrong. Status commands append the supplied transition reason automatically, so do not repeat the same event manually. Scripts check that text is nonempty and reject exact duplicate manual entries; reviewing usefulness and detail remains the agent's responsibility.

## Lifecycle transitions

Features start in RESEARCH and advance exactly one phase at a time:

`RESEARCH → DESIGN → IMPLEMENT → TEST → DONE`

Any backward transition to an earlier phase is permitted, including from DONE. After going backward, advance through each phase again; the feature's previous high-water mark does not permit skipping steps. Moving TEST to DONE also requires every requirement to be DONE. A no-op status update adds no history and is rejected.

Requirements start in TODO and advance through:

`TODO → WIP → DONE`

TODO and WIP may enter BLOCKED. Record `blocked_reason` and `blocked_from`. BLOCKED may remain blocked with an updated reason, or resume exactly its recorded prior state; it cannot jump directly to DONE. Clear the blocking fields on resume and retain the blocking event in the worklog. DONE is terminal for an individual requirement under this graph; newly discovered work belongs in a new TODO requirement. Each requirement keeps its status when the feature changes phase.

Before marking a requirement DONE, verify its definition of done and put the evidence in the transition reason. Before marking a feature DONE, complete the applicable checks and reviews, assess the evidence, and follow the feature closeout instructions. Update project-facing docs under `docs/`, put decisions and verification evidence for agents under `docs/agents/`, and link those docs from the definition. The phase and requirement status commands enforce lifecycle and data invariants. Feature closeout assesses the adequacy of the evidence.

## Focused automation

Set up [the harness Python environment](../agents/python-environment.md) before running these commands. Use its interpreter for feature memory scripts and any installed harness tests.

- `create_feature.py`: take a lowercase kebab-case slug, prepend the current UTC date, and create the directory and its three files from an initial TOML definition. Print the new path. Refuse duplicates and invalid initial states.
- `set_feature_status.py`: enforce ordered forward phases, arbitrary backward phases, and the completion gate.
- `set_requirement_status.py`: enforce requirement transitions and blocking metadata.
- `append_worklog.py`: append substantive progress without changing definition or design.
- `_feature_memory.py`: shared parsing and validation used by the commands; it is not a separate task runner.

Examples, from the project root:

```sh
feature_path=$(.harness/.venv/bin/python .harness/scripts/create_feature.py incremental-build-cache --definition /tmp/cache-definition.toml)
feature_name=${feature_path##*/}
.harness/.venv/bin/python .harness/scripts/set_feature_status.py "$feature_name" DESIGN --reason "Research identified all compiler inputs; linked findings in the definition."
.harness/.venv/bin/python .harness/scripts/set_feature_status.py "$feature_name" IMPLEMENT --reason "The technical design covers every requirement and its verification strategy."
.harness/.venv/bin/python .harness/scripts/set_requirement_status.py "$feature_name" F-1 WIP --reason "Cache-key design is complete; implementing source and compiler-option hashing."
.harness/.venv/bin/python .harness/scripts/set_requirement_status.py "$feature_name" F-1 BLOCKED --reason "Integration testing requires artifact-store access." --blocked-reason "The platform team must grant the build account read access to the test artifact store."
.harness/.venv/bin/python .harness/scripts/set_requirement_status.py "$feature_name" F-1 WIP --reason "The platform team granted access; integration checks can resume."
.harness/.venv/bin/python .harness/scripts/append_worklog.py "$feature_name" --summary "Compiler option inventory reconciled" --details "F-1 now covers output-affecting options; diagnostic-only flags are excluded. Next, verify the cache key against the compiler fixtures."
```

The first command requires a real source definition, such as the example adapted to the feature. Commands default to the current project root and accept `--root PATH` when invoked elsewhere. They print useful errors and exit nonzero on invalid data or transitions. Resolve the problem through the command and keep direct edits to descriptions, links, requirements, and design valid.

The commands serialize operations for the same feature using a lock under `.harness/features/.locks/`. Commands for different features can run independently. Coordinate direct edits with other writers. Each file update is atomic, and a status update spans two files.

When changing the helpers or adopting equivalent commands, verify lifecycle transitions, blocked reasons, rejection without state changes, unique names, history preservation, and the conditions for entering DONE. Put new harness behavior tests under `.harness/scripts/tests/`. If the project adopts a feature merge check, place it in `scripts/` so its pull request workflow can invoke it.
