# Design: Feature Memory

## Scope and decisions

The user's feature-memory requirements are the source of the storage and lifecycle
contract. The authoritative schema and usage documentation live in
`.agents/skills/build-harness/references/feature-memory.md`, relative to the project
root. Feature records are local state; instructions and automation are shareable.
There is no remote storage, version-control history of records, or concurrency
coordinator in this feature.

Blocking preserves the requirement's prior TODO or WIP state in `blocked_from`.
Resuming that exact state prevents a blocked TODO from bypassing WIP. Requirement
DONE is terminal under the specified graph; newly discovered work gets a new TODO
requirement. A feature can return from DONE to an earlier phase, but must traverse
each forward phase again. These choices are documented rather than implicit.

## F-1: Isolated three-file storage

`create_feature.py` validates the supplied initial TOML before creating a directory.
`feature_path` accepts a single lowercase kebab-case name and rejects path escape
and symlink destinations. Exclusive directory creation refuses duplicate names.
Creation writes the supplied definition, a design outline keyed by requirement id,
and a chronological initial worklog entry. Failed initialization removes only the
newly created directory; an existing record is never overwritten.

## F-2: Definition schema

Use top-level description, documentation, status, and requirements fields.
Requirement tables contain stable ids, functional/non-functional kind, detailed
description, definition_of_done, status, and conditional blocking metadata.
`_feature_memory.py` validates field presence, nonempty text, lists, unique ids,
enums, and blocking consistency. It uses TOMLKit to preserve unknown metadata and
formatting when updating a status. Requirement quality, documentation relevance,
and the depth of a description remain agent and reviewer judgments.

## F-3: Design and worklog

The design must explain an implementable and verifiable approach for every
requirement; a generated outline alone does not satisfy this requirement.
Progress is a YAML list of mappings with ISO 8601 UTC timestamp, feature phase,
summary, and details. `append_worklog.py` rejects empty and exact duplicate manual
entries. Status commands append transition reasons as substantive progress.
PyYAML safely loads and serializes the history, preserving prior entry data while
allowing presentation to normalize. Corrections are new entries rather than edits
that erase history. TOML values are converted to ordinary strings at the YAML
boundary, avoiding representation errors for TOMLKit string wrappers.

## F-4: Feature lifecycle

`set_feature_status.py` reads the current phase from disk. A forward target must
have index current+1 in RESEARCH, DESIGN, IMPLEMENT, TEST, DONE. Any lower index
is valid; the current index is a rejected no-op. The shared validator rejects a
DONE definition unless all requirements are DONE. No previous high-water mark is
stored, so regression always requires ordered forward progress again.

## F-5: Requirement lifecycle

`set_requirement_status.py` selects a stable requirement id. Its normal edges are
TODO to WIP and WIP to DONE. TODO and WIP may enter BLOCKED with a detailed reason;
BLOCKED records its origin, may update its reason, and may resume only its origin.
Unblocking clears both blocking fields. DONE has no outgoing edge. Blank reasons,
unknown ids, unchanged blocking reasons, and invalid transitions fail before any
record mutation. Phase changes leave requirement states unchanged.

## F-6: Discovery and instructions

The skill entry point links to the memory contract only for memory-related harness
work. Root AGENTS.md routes feature starts/resumes to the concise contextual file
in `.harness/agents/`, which instructs the agent to load the selected record,
maintain definition/design/history, and use the status commands. It links to the
single authoritative contract rather than embedding the schema. All `##` headings
in active instruction files express lifecycle events.

## NF-1: Locality and version control

The initial root `.gitignore` ignored `/.harness/features/` and Python bytecode. The [feature completion policy](../../../docs/TECHNICAL.md#feature-completion-and-merge-checks) now versions the records. It leaves the
skill, `.harness/agents/`, scripts, and tests trackable. Since this workspace is not
currently a Git repository, verify ignore semantics in an isolated temporary Git
repository using the actual ignore file. Do not initialize Git in the live project
merely to test the rule.

## NF-2: Runtime, writes, and failure handling

Each command handles one task. Shared parsing, validation, worklog construction,
and atomic single-file writes live in `_feature_memory.py`. Runtime dependencies
are Python 3.11+, TOMLKit, and PyYAML, declared in requirements.txt. Test execution
uses an isolated temporary dependency cache; no project virtual environment is
required or committed.

Commands accept a feature name and optional `--root`; transitions require a reason.
They validate the loaded definition, nonempty design, worklog shape, transition,
and resulting definition before status writes. Errors print diagnostics and exit
nonzero. Each file is replaced atomically, but a definition and worklog update are
not one transaction. Use one writer per feature. If an I/O failure interrupts a
multi-file update, reconcile the definition against the log and append a recovery
entry before continuing; a future need for concurrent writers would justify a
different storage design.

## Verification strategy

Use unittest with CLI subprocesses operating only in temporary projects. Read
resulting definitions with the independent standard-library TOML parser and
worklogs with the YAML parser. Cover every feature-phase pair, normal requirement
edges and rejected edges, both BLOCKED origins, completion gates, ordered progress
after regression, malformed input, duplicate names, and preserved history and
unrelated metadata. Validate the skill and resolve local Markdown links. Check
actual Git ignore semantics separately from the script lifecycle tests. No test
asserts private function names, source structure, or incidental message wording.
