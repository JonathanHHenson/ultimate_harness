# Ultimate Harness domain model

## Research and open questions

The agent entry point, feature memory contract, validation index, form contract, and export catalog describe one connected workflow. The scripts confirm separate state transitions for features and requirements, distinguish form answers from clarification requests, and build both portable packages from the same export catalog. A single glossary can cover these relationships without assigning separate meanings to the same terms.

## Requirement coverage and technical approach

### DOMAIN-LANGUAGE

Give each project-specific concept a short definition in the root glossary. Keep relationships, lifecycle examples, and implementation contracts in the technical documentation. Cover the boundaries between a task's handoff and a feature closeout, between a feature phase and a requirement status, between a check and a review, between an agent session and a form session, and between a portable component and a portable package.

### TERMINOLOGY-ROUTING

Link the glossary from the root instructions only where agents need to name or document a harness concept. Link it from the README and the technical documentation. Align the feature transition heading, the name of the validation index, and the adoption steps that refer to dated feature records and catalog entries. Preserve the existing interface terms wherever they are literal identifiers.

### TERMINOLOGY-AUDIT

Audit maintained first-party text across the skills and references, contextual instructions, validation index and rulesets, reviewer instructions, and project documentation. Resolve aliases by checking what they refer to. A capability is behavior, a portable component is the unit of adoption, and a portable package is the distributable skill. Specify the kind of session when agent work, form state, and a background tool appear together. Keep public identifiers, control flow, and historical results intact.

### GLOSSARY-VALIDATION

Route skill, instruction, and documentation changes from the validation index directly to a glossary check in the existing harness guidance ruleset. The glossary already supplies definitions and aliases. A prose review can check both the word and the intended meaning, including distinctions that a search for disallowed phrases would miss. It can also distinguish prose from literal interface names and pinned upstream text. Review affected references across maintained prose when a glossary definition changes. Check prose-only, code-only, and mixed changes, and exercise a correct example and representative terminology failures.

### GLOSSARY-MEANING

Run the meaning pass first so the agent examines each changed passage before focusing on visibly outdated wording. Ask what each term refers to, what it does, and which glossary definition supports that role. The first revision explained this distinction but reproduced the baseline detection rate. The final revision calls out skill metadata explicitly, has the agent record a short list of the passages and their meaning, and gives a worked comparison for the glossary entries confused in the baseline. Finish with a separate naming pass and report any correction the agent cannot apply. Repeat the six matched Codex cases and count contextual findings separately from aliases. Use a separate example involving a different glossary distinction to check whether the process transfers.

### GLOSSARY-SKILL-DESCRIPTIONS

Start a glossary review note in the existing scratch workspace before evaluating terminology. Give each new or changed skill description its own entry, including the terms exactly as written, their intended meanings, the matching glossary entries, and the verdict. Review the description apart from the skill procedure so a procedure finding cannot substitute for a meaning check. Finish only after reopening the saved note and confirming its coverage. Keep the glossary's context and literal wording exceptions. Compare the revised procedure with the preceding ruleset on fresh skill patches with both incorrect and valid descriptions and on a clean documentation patch. The first revision produced consistent notes but could paraphrase away an incorrect term. Require the term as written and compare that term's definition before deciding, then retest on a separate set.

## Interfaces, data, and failure handling

The glossary describes this repository's domain. Portable packages retain their shared procedures and use the target project's language. The existing export allowlist leaves the source glossary outside the packages. This update adds documentation and changes wording in instructions without changing command behavior or data formats.

## Verification strategy

Trace a feature reopened after completion, a configuration-only change, a clarification request that preserves the current question, and a portable component that consists of files and dependencies. Check the glossary and its incoming links, the contextual terminology trigger, both portable packages, and the feature merge check.
