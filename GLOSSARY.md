# Ultimate Harness

Ultimate Harness gives programming agents shared instructions, reusable procedures, and a way to carry project work across sessions. This glossary defines the terms used to describe that work and how teams adopt the harness.

## Language

### Agent work

**Harness**

The project instructions, reusable skills, records, and tools that guide an agent's work and define how that work is verified.

**Agent entry point**

The project's starting instructions for agents. It routes them to the guidance that applies to their current work.

**Trigger**

An event or condition that makes a project instruction or validation rule apply.

**Contextual instructions**

Project guidance for a particular event, kind of work, or area of the repository.

**Skill**

A reusable procedure for carrying out a task. It can include supporting references and tools.

**Language skill**

A skill for working in one project language, including its conventions, development tools, and verification practices.

**Agent session**

A period of agent work with a shared working context. A feature can span several agent sessions.

**Scratch workspace**

A local place for an agent's working notes, drafts, and experiment artifacts. Its contents stay with the checkout.

**Handoff**

The transfer of work context to a human or another agent, including results, evidence, and anything still open.

### Feature memory

**Feature**

A defined change or outcome tracked through the harness lifecycle. A feature can cover product work or maintenance of the harness itself.

**Feature memory**

The practice of keeping a feature's requirements, design, and progress available across agent sessions.

**Feature record**

The durable definition, design, and worklog for one feature.

**Feature store**

The collection of a project's feature records.

**Feature phase**

The current stage of a feature's lifecycle.

_Avoid_ “feature status” in prose.

**Requirement**

A behavior or constraint a feature must satisfy.

**Requirement status**

The progress or blocked state of an individual requirement.

**Definition of done**

The observable criterion that a requirement must meet to be marked done.

**Worklog**

The chronological account of a feature's substantive progress, decisions, evidence, and blockers.

**Feature closeout**

The completion step that verifies the feature's requirements and records its key decisions and verification evidence in project documentation.

### Validation

**Validation index**

The project's routing guide for choosing applicable validation rulesets and shared checks.

_Avoid_ “validation guide” when referring to the index.

**Validation ruleset**

A set of instructions for verifying work in a specific situation.

**Check**

A specific verification action with an observable result.

**Review**

A reasoned assessment of a change and its evidence. A review can call for several checks.

**Feature merge check**

The check that reports whether the feature store records every feature and requirement as done.

### Human decisions

**Design interview**

The process of examining a proposed project change against existing rules and decisions, then resolving open choices with the human.

**Form session**

One browser-based exchange within an agent session. It may include several pages and submissions.

**Clarification request**

A request for the agent to explain the current form page more clearly while keeping the underlying decisions open.

### Portable adoption

**Target project**

The project whose harness is being installed or evolved.

**Harness adoption**

Introducing harness practices into a target project through installation or evolution.

**Harness installation**

Adoption in a target project without an established harness.

**Harness evolution**

Adoption that integrates new practices into an established harness or replaces existing practices with the team's agreement.

**Portable component**

A unit of harness adoption in the export catalog. Each component groups reusable files for a capability and identifies the other components it needs.

**Export catalog**

The inventory of portable components, their files, and their dependencies.

**Portable package**

A distributable harness adoption skill together with the reusable harness files it needs.

**Skill lockfile**

The project's record of imported third-party skills and their exact source revisions and content hashes.
