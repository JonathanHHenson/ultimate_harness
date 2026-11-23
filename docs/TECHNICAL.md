# Ultimate Harness technical design

Ultimate Harness supplies repository-specific instructions and local tools to a coding agent. The agent interprets the current task, decides which rules apply, and invokes checks through its own tools and permissions. The Python scripts implement operations with concrete contracts, such as creating a workspace, advancing a feature phase, or checking a link. This division lets the harness guide judgment while enforcing the invariants it can check directly.

## How the concepts fit together

The [project glossary](../GLOSSARY.md) defines the vocabulary shared by the agent instructions, feature records, and adoption skills.

| Situation | How the concepts relate |
| --- | --- |
| A new requirement is discovered after a feature was completed | The feature returns to an earlier phase and adds the new requirement with status `TODO`. The prior requirements retain their statuses and the worklog retains its history. |
| An agent hands off with verification pending | The handoff reports the current phase, evidence, and open work. Feature closeout follows when the requirements and applicable validation are complete. |
| A change updates only a dependency manifest | The validation index selects security review for the configuration change. The review can call for targeted checks of dependency resolution or other affected controls. |
| A human asks for clearer wording on a follow-up page | The agent answers the clarification request by revising the current page within the same form session. It continues waiting for an answer to that page. |
| A team adopts the portable browser form | The export catalog describes the form's portable component, its files, and its dependencies. The install or evolve portable package carries those files. The target project decides where the form workflow applies. |

## Repository structure

| Location | Responsibility |
| --- | --- |
| [`AGENTS.md`](../AGENTS.md) | Agent entry point. Routes agent session events and kinds of work to the required instructions. |
| [`.harness/agents/`](../.harness/agents/) | Contextual instructions for environment setup, scratch space, and feature memory. |
| [`.harness/references/`](../.harness/references/) | Reusable harness contracts that a target project can install independently. |
| [`.harness/VALIDATE.md`](../.harness/VALIDATE.md) | Validation index for shared checks and situation-specific rulesets. |
| [`.harness/validation/`](../.harness/validation/) | Rulesets for guidance, scripts, scratch space, code review, and security review. |
| [`.agents/skills/`](../.agents/skills/) | Reusable procedures for harness maintenance, research, skill authoring, software design, and test design. |
| [`.harness/scripts/`](../.harness/scripts/) | Focused Python commands, their dependency manifest, and behavioral tests. |
| `.harness/features/` | Versioned feature definitions, designs, and worklogs. |
| [`scripts/`](../scripts/) | Standalone commands for CI to run in a pull request checkout. |
| [`skills_src/`](../skills_src/) | Conversational installation and evolution skills, with the export catalog that selects their reusable assets. |
| `docs/` and [`docs/agents/`](agents/) | Project documentation and durable feature decisions and verification evidence for agents. |
| `.scratch/` | Local notes and experiments. Agents create a scratch workspace per agent session under `.scratch/agent_sessions/`. |

The project shares instructions, skill sources, scripts, feature records, and documentation through Git. Feature records carry work across sessions and checkouts. Scratch, temporary feature locks and writes, the virtual environment, its setup lock, the default uv cache, and generated skill assets are ignored. [Repository ignore rules](../.gitignore)

## How a session runs

```mermaid
flowchart TD
    Start(["Session starts"]) --> Entry["AGENTS.md<br>Route by event and task"]
    Entry --> Setup["Set up harness Python<br>Create or reuse the scratch workspace"]
    Setup --> Work["Carry out the task"]
    Work -. Apply relevant guidance .-> Skills["Skills<br>Research, design, and testing"]
    Work -. Read and update for feature work .-> Memory[("Feature memory<br>Definition, design, and worklog")]
    Work --> Validate[".harness/VALIDATE.md<br>Select checks for the session's changes"]
    Validate -->|Code changed| Both["Code and security reviews"]
    Validate -->|Configuration only| Security["Security review"]
    Validate -->|Neither code nor configuration| Artifacts["Applicable checks for changed artifacts"]
    Both --> Ready{"Feature ready to close?"}
    Security --> Ready
    Artifacts --> Ready
    Ready -->|Yes| Close["Record decisions and evidence in docs/<br>Then set the feature to DONE"]
    Ready -->|Other handoff| Handoff(["Handoff<br>Report results, findings, and gaps"])
    Close --> Handoff
```

The dotted arrows show what the agent consults during the task. Other validation triggers apply whenever their conditions match.

1. **Initialize the environment.** The session-start rule calls `init_venv.py` with host Python 3.11 or later. The script serializes setup with `.harness/.venv.lock` and creates or reuses `.harness/.venv/`. It prefers uv when available. Without uv, it attempts the standard-library `venv` module and then `virtualenv` if that attempt fails. Setup checks that the interpreter belongs to the harness environment and that system site packages are disabled. It installs the manifest into that environment with implicit installer configuration disabled. uv uses the project-local cache by default and honors an explicit `UV_CACHE_DIR`. Subsequent harness commands use `.harness/.venv/bin/python`. [Environment instructions](../.harness/agents/python-environment.md) · [Bootstrap implementation](../.harness/scripts/init_venv.py) · [Dependency manifest](../.harness/scripts/requirements.txt)
2. **Open a scratch workspace.** At the start of an agent session, the agent calls `create_agent_session.py`. The script creates a private directory with a UTC timestamp prefix and a unique suffix, then prints its absolute path. A resumed session reuses its known directory. Scratch persists after handoff so the agent and the human can inspect local artifacts or continue an experiment. [Scratch instructions](../.harness/agents/scratch-space.md) · [Workspace implementation](../.harness/scripts/create_agent_session.py)
3. **Load the context for the work.** For feature work, the agent reads the relevant feature record and the validation index. When the task calls for harness maintenance, software design, or automated test design, the root instructions route the agent to the corresponding skill. Other skills can be selected for the task. [Agent entry point](../AGENTS.md) · [Feature memory instructions](../.harness/agents/feature-memory.md)
4. **Review every proposed change before editing.** The agent applies Grill With Docs to project changes, including routine edits, tool-driven changes, and changes to the harness itself. It resolves facts from the repository, carries forward the human's settled choices, and asks about open decisions through Human Interaction. New decisions or an expansion of scope reopen the interview. [Design interview instructions](../.harness/agents/design-interviews.md)
5. **Validate and hand off.** The agent selects checks based on the work and its lifecycle event, runs them with the appropriate environment, and reports what happened. When feature memory applies, the worklog carries forward the important decisions, evidence, and blockers. When the feature is ready to close, the agent records those decisions and evidence in tracked documentation before marking it done. [Validation index](../.harness/VALIDATE.md)

## Feature memory

Feature records preserve enough state for another session to understand the purpose of the work, the current design, and what remains. Each directory follows `YYYY-MM-DD-<slug>`, with the UTC creation date before a lowercase kebab-case slug. Sorting by name groups records by date and sorts slugs within each day. Each directory contains three authored files.

| File | Contract |
| --- | --- |
| `DEFINITION.toml` | Feature description, documentation references, current phase, and functional and non-functional requirements. Each requirement has a stable ID, description, definition of done, and status. |
| `DESIGN.md` | Design decisions and the technical approach, including how they address the requirements and how the behavior will be verified. |
| `WORKLOG.yaml` | Chronological entries with a UTC timestamp, phase, summary, and details. Entries capture substantive progress, decisions, evidence, and blockers. |

Feature phases advance in order through `RESEARCH → DESIGN → IMPLEMENT → TEST → DONE`. The feature may return to an earlier phase and then advances through the intervening phases again. Requirements advance separately through `TODO → WIP → DONE`. A requirement can become `BLOCKED` from `TODO` or `WIP`. The definition records the reason and the prior state, which is the state the requirement returns to on unblocking. `DONE` is terminal for a requirement. The phase command allows the feature to enter `DONE` from `TEST` once every requirement is `DONE`. The agent verifies the definitions of done and the applicable checks before requesting that transition. [Feature memory contract](../.harness/references/feature-memory.md)

`create_feature.py` takes a slug, adds the UTC date, validates the initial definition, and publishes the three files from a staging directory. It prints the path to the new record. Status and worklog commands take the full dated directory name so they can address the same feature on later days. The status commands record the transition reason in the worklog. `append_worklog.py` appends a substantive entry and rejects an exact duplicate. [Feature creation](../.harness/scripts/create_feature.py) · [Feature phase changes](../.harness/scripts/set_feature_status.py) · [Requirement status changes](../.harness/scripts/set_requirement_status.py) · [Worklog updates](../.harness/scripts/append_worklog.py)

The shared command code takes an exclusive lock under `.harness/features/.locks/` for the selected feature. A paired status update saves a pending record containing the new definition, new worklog, and digests of their previous contents. The storage helper uses atomic replacement for each file and clears the pending record after completing both writes. After an interruption, the next feature command validates the pending data and completes the update under the same lock. If a file differs from both its prior and intended contents, recovery reports a conflict and preserves that edit. People editing the files directly coordinate with other writers. [Command coordination](../.harness/scripts/_feature_memory.py) · [Storage and recovery](../.harness/scripts/_feature_store.py)

## How instructions are written

- **Use an event as the heading.** A heading such as `Before handing off or ending a session` gives the agent a condition it can evaluate. The instruction underneath names the action and links to the relevant procedure. The root file stays short because detailed rules load when their conditions apply. [Instruction authoring standard](../.agents/skills/build-harness/references/agents-md.md)
- **Keep each rule in its owning file.** Repository-specific policy belongs in the agent instructions or validation ruleset. A reusable method belongs in a skill. Design rationale and background belong in explanatory documentation. A skill's YAML `name` and `description` support discovery, and its body describes how to execute the workflow and when to open supporting references. [Harness maintenance guidance](../.agents/skills/build-harness/SKILL.md) · [Skill authoring guidance](../.agents/skills/learn-and-build-skills/references/authoring-and-evaluation.md)
- **State actions, inputs, and evidence directly.** A rule that calls a command identifies when to run it, its working directory or inputs when relevant, and what the result means. Scripts handle repeatable operations. The agent assesses architecture, coverage, and whether a check addresses the actual risk. Tests exercise observable outputs, exit status, and resulting state through the supported interface. [Validation authoring standard](../.agents/skills/build-harness/references/validation.md) · [Behavioral testing guidance](../.agents/skills/automated-test-design/SKILL.md)
- **Keep implementation proportional to the job.** A script has a focused responsibility, a clear entry point, and a visible result. Shared code earns its place by protecting a common contract, as the feature lock and storage helpers do. Software design guidance applies KISS and SOLID where they clarify the required behavior and keep the code readable. [Software design guidance](../.agents/skills/software-design/SKILL.md)

## How validation is selected

At handoff, the agent identifies the changes attributable to the session or requested patch, including staged, unstaged, and untracked changes. It classifies changes by purpose. A settings file is configuration even when its syntax is a programming language. The first matching review row governs both which review rulesets to open and which checks to run. Other validation triggers, such as harness guidance or scratch-space checks, apply independently when their conditions match. [Session-end review table](../.harness/VALIDATE.md#before-choosing-session-end-reviews)

| Change scope | Selected handoff work |
| --- | --- |
| Code, including scripts and tests, with or without configuration | Code review and security review. |
| Configuration without code | Security review and checks specific to the changed settings and the controls they affect. |
| Prose-only or no code or configuration changes | Applicable checks for the changed artifacts. Both reviews are skipped. |

**Code review** combines available static diagnostics with a review of architecture, complexity, and module organization. The agent checks whether tests protect the changed behavior and runs the complete configured unit suite against the final code. **Security review** follows the effects of the change across trust boundaries, including effective configuration and relevant dependencies. It uses STRIDE to identify threats and uses OWASP guidance where web controls apply. The agent runs applicable project checks, verifies relevant controls, and records unresolved findings and missing evidence. [Code review](../.harness/validation/code-review.md) · [Security review](../.harness/validation/security-review.md)

The local validators cover specific contracts. The Markdown checker checks supported local inline file targets. The guidance review checks anchors and whether a trigger leads to the right instructions and actions. The skill checker verifies required skill metadata and instruction content. The harness test suite exercises the scripts in isolated workspaces. An agent-session evaluation checks which guidance the agent actually opens and which commands it runs. [Guidance validation](../.harness/validation/harness-guidance.md) · [Skill checker](../.harness/scripts/check_skill_packages.py) · [Script validation](../.harness/validation/harness-scripts.md)

The glossary check applies to new or updated skills, harness instructions, and project documentation. It verifies what each term refers to before checking names and aliases. The agent reviews each new or changed skill description separately and records its exact terms, intended meanings, and verdict in a scratch note. The agent verifies the saved note before passing the check. When a glossary definition changes, the agent also reviews affected uses in existing prose. [Glossary check](../.harness/validation/harness-guidance.md#after-adding-or-updating-skills-harness-instructions-or-project-documentation)

### Language skills and complexity validation

Code review requires complexity evidence for every changed executable language. Use the project's analyzer and limit where configured. Otherwise use a language helper or a documented manual decision count against the default limit of 10. Review the selected boundaries and coverage as well as the score. [Complexity validation](../.harness/validation/code-complexity.md)

Code review verifies that each project language has a dedicated, discoverable skill for tooling, documentation, and best practices. Learn and Build Skills owns the authoring method, and Build Harness routes language onboarding through it. Python prefers Ruff for linting and complexity, with a bundled standard-library fallback. JavaScript ships an ESLint complexity command. HTML and CSS have standalone validation helpers. Shell uses the declared interpreter’s syntax check and the project's configured lint and test tools. The existing packaging workflow runs the maintained source checks before exporting the skills. [Ruff configuration](../ruff.toml) · [Code review](../.harness/validation/code-review.md#before-running-code-review-diagnostics) · [Language routing](../.harness/agents/languages.md) · [Language skill authoring](../.agents/skills/learn-and-build-skills/SKILL.md#when-authoring-a-language-skill) · [Packaging workflow](../.github/workflows/build-harness-skills.yml)

The export catalog lists each language skill as its own portable component. When onboarding another executable language, add its skill and validation commands, and use the shared review policy for changes in that language. The Node-based checks run during development and packaging. The feedback form continues to use standard-library Python and browser APIs at runtime. [Export catalog](../skills_src/harness-files.toml)

## How feedback forms work

For complex feedback, the agent writes page JSON and a Markdown prologue in a private scratch workspace. A short-lived Python process binds to loopback and supplies the same browser URL throughout the form session. The browser shows up to five questions at a time in one column, with progress and Back and Next buttons. The agent can supply editable recommended defaults. Submit saves answers from all question pages in the round. In adaptive mode, the browser waits while the agent reads the answers and sends another round or closes the form. The final view prompts the human to return to the agent, and the server shuts down after the browser acknowledges the view or a short grace period elapses. The form uses local HTML, CSS and JavaScript. [Human interaction](../.agents/skills/human-interaction/SKILL.md) · [Form contract](../.agents/skills/human-interaction/references/form-schema.md)

Install Harness uses the bundled form on both adoption routes to collect open decisions before editing the target. It resolves the script relative to the portable package and keeps the form session's files outside the target project. This lets an agent finish research and agree on changes before creating project files or a harness environment.

The form CLI checks generated pages before starting a server or advancing to the next page. Its `launch` command returns the form URL from an ordinary terminal call while the server continues running on loopback. The agent verifies readiness, shares the link, and runs `listen` to await an event for up to 30 minutes by default. The browser shows when the agent is listening or has received an event, and asks the human to send a chat message when the agent is away. If terminal permissions, startup, or browser access prevents delivery, the agent explains the blocker and lets the human choose how to continue. [Form commands](../.agents/skills/human-interaction/references/form-schema.md#commands) · [Listener](../.agents/skills/human-interaction/references/form-schema.md#listening-for-feedback)

The context and each visible group of questions end with a **Wait.. What?** button. Either button lets the human add an optional note. The questions button includes the visible browser page number and the IDs and labels of its questions. The agent can clarify wording and append requested choices or questions. The server preserves the other area and the existing answer constraints. The browser resumes at the same question page with the draft answers intact. [Clarification workflow](../.agents/skills/human-interaction/references/form-schema.md#clarification-requests)

An agent can also publish changes to an open form with the authenticated `update` command. The browser polls for revisions and updates at the same URL. Appended questions can create additional browser pages with editable defaults. After the human submits a round, `next` can publish a new set of questions at that URL. [Live updates](../.agents/skills/human-interaction/references/form-schema.md#updating-a-live-form)

The form expires after an hour without a successful submission or a new page. The browser polls for state without extending the deadline. It can show the expiry notice from the last reported deadline if it cannot reach the server after the grace period.

If an expired form still has unanswered questions, the agent asks the human to say when they are ready. It then opens the pending questions at a fresh URL and carries forward any answers already submitted. [Expiry procedure](../.agents/skills/human-interaction/SKILL.md#when-a-form-expires)

## Feature completion and merge checks

Before setting a feature to `DONE`, update project docs under `docs/` for any changed shared behavior, interfaces, or architecture. Put the enduring decisions, their rationale, and verification evidence for agents under `docs/agents/`. Record which checks ran and what they established, including any scope left unverified. The definition links readers to those documents. Include the records and docs in the same change. [Feature closeout rule](../.harness/agents/feature-memory.md#before-marking-a-feature-done)

From the checkout, a pull request job can run this command with Python 3.11 or later using only the standard library.

```sh
python3 scripts/check_features_done.py
```

The feature merge check locates the checkout relative to the script and reads each feature's `DEFINITION.toml`. It exits zero when every feature and requirement is `DONE`, including a new checkout with an empty feature store. It exits one with diagnostics for unfinished statuses, unreadable or invalid status records, and pending status updates. It checks the recorded completion state. The agent's closeout review supplies the decisions and evaluates the evidence. Each adopting project configures its own CI job to call the command. [Merge check implementation](../scripts/check_features_done.py)

## How the harness evolves

The harness uses the same feature and validation workflow for changes to itself. An improvement starts with an observed problem and a concrete description of the desired behavior. The maintenance workflow traces the problem to its owning instruction, skill, or script and makes a scoped change. Research, prototypes, and raw evaluation results live in scratch. A verified change becomes tracked guidance or code, and the feature record links to the durable decisions and evidence. [Harness maintenance workflow](../.agents/skills/build-harness/SKILL.md)

For unfamiliar tasks, the research workflow starts from the question and checks whether sources actually support their claims. Socratic questioning exposes assumptions, tests alternatives and counterexamples, and checks whether the conclusion transfers to a fresh case. The skill-authoring workflow turns the supported procedure into short instructions with references or scripts where they help. [Research workflow](../.agents/skills/learn-a-topic/SKILL.md) · [Skill authoring workflow](../.agents/skills/learn-and-build-skills/SKILL.md)

Evaluation distinguishes **discovery**, **execution**, and **outcomes**. A rule can point to the correct file while the agent still runs an unrelated check. When evaluating a change, use fresh sessions, keep inputs and runtime comparable, and define success before inspecting the results. Check a matching case, an unrelated case, and an overlap. For a claim of improvement, compare matched runs with the relevant baseline and score what the agent did and what it found. Keep scoring criteria outside the worker's instructions. [Evaluation procedure](../.agents/skills/learn-and-build-skills/references/authoring-and-evaluation.md#evaluate-independently-of-the-draft)

## How portable skills are built

Install Harness has one portable package. Each portable component in the export catalog lists its repository-relative files and dependencies. The builder copies those files into `skills_src/install-harness/assets/harness/`, preserving paths and replacing old generated content. Edit portable content at its source. When adding an export, check the file's commands and links and update the catalog for any new dependencies. [Export catalog](../skills_src/harness-files.toml) · [Build command](../scripts/build_harness_skills.py)

The adopting project supplies its own entry point, validation index, ignore rules, documentation, and CI configuration. The catalog excludes this repository's versions of those files, its feature records, scratch, and runtime state. It includes a standalone feature merge check that can be wired into the target's CI by agreement.

The third-party skill component exports the management instructions. Imports live in the adopting project's Git history with their generated `skills-lock.json`. That lock records the source pin and installed content so teams can review an update and restore an exact skill. The project uses the installed files on a normal checkout. The tool version is pinned in the shared procedure, and the export catalog controls which files this repository distributes. [Third-party skill instructions](../.harness/agents/third-party-skills.md) · [Export catalog](../skills_src/harness-files.toml)

The skill researches the bundled export catalog and the target project's technical and team context before choosing between first installation and evolution. Both routes start with every portable component. Evolution compares existing behavior before recommending additions, merges, or targeted replacements. The feedback form separates material changes and each proposed project-specific skill or validation ruleset into individual decisions. Changes to the plan can prompt follow-up questions before the target is edited. [Install Harness](../skills_src/install-harness/SKILL.md) · [Shared adoption guide](../.agents/skills/build-harness/references/adoption.md)

Adoption forms open with the decision scope, agreed boundaries, and a concrete project task. The choices describe what the team will gain, keep, or defer. Catalog IDs support coverage checks while question labels use project terminology. The first submission includes known conditional preferences as separate choices. The agent applies them only when the human approves their prerequisites. A follow-up round is for a material decision revealed by the answers whose options could not be offered up front. The detailed catalog assessment stays in the research notes. [Decision-page instructions](../.agents/skills/build-harness/references/adoption.md#before-showing-a-design-decision-page)

Both adoption workflows invoke the bundled Grill With Docs skill before drafting the plan, including when the human requests planning only. An agent whose skill tool cannot load the bundled copies opens Grill With Docs, Grilling, and Domain Modeling directly. The target stays read-only during planning. When the target adopts the interview workflow, its active agent instructions route every future project change through the same pre-change step. The upstream interview and clarification skills ship with their MIT notice. [Install Harness](../skills_src/install-harness/SKILL.md#before-drafting-either-adoption-plan) · [Design interview instructions](../.harness/agents/design-interviews.md) · [Upstream notice](licenses/matt-pocock.txt)

GitHub Actions builds and validates the skill from the checkout and publishes `install-harness.tar.gz` in the `harness-skills` artifact. The archive preserves hidden harness directories and file permissions. This workflow belongs to the source repository. [Packaging workflow](../.github/workflows/build-harness-skills.yml) · [GitHub Actions artifact docs](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts)

The release maintainer attaches the archive from the tagged commit's successful build as a release asset and verifies the upload. The download remains available after the workflow artifact expires. [Release process](RELEASING.md)

The optional `copilot-review` component gives Copilot PR reviews an entry point into the shared review rulesets. It uses the validation index to select checks and grounds findings in evidence for the reviewed commit. [Reviewer instructions](../.github/instructions/harness-review.instructions.md)
