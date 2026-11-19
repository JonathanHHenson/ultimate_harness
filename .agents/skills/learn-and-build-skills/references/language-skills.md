# Language Skill Authoring

## When scoping a language skill

- Inventory the language’s maintained source, tests, scripts, templates, and embedded uses. Read the project’s runtime and version policy, manifests, CI commands, and development documentation. Identify the commands the project already uses and the scope each one covers.
- Create or adapt one discoverable skill for the language. Make its description cover relevant tasks and file contexts, including embedded uses. Link it from the project’s language inventory so mixed-language work can load each applicable skill.

## When choosing content and helpers

- Document the actual entry points for linting, formatting, and testing, plus applicable type checking, complexity, build, or runtime checks. State the interpreter or tool version, working directory, inputs, and how to interpret results. Prefer check modes for review. Explain the fallback and how to report gaps when a configured tool is unavailable.
- Link to maintained project documentation and relevant authoritative language or tool references. Explain the project’s conventions and language-specific practices that matter for design, security, error handling, and testability. Use examples where they clarify a choice agents frequently get wrong.
- Keep reusable language-specific helpers inside the skill. Reuse configured tools and separate portable helpers from commands that depend on the adopting project’s layout or configuration.

## Before handing off a language skill

- Run representative configured commands or exercise the documented fallback. Verify that the intended files are analyzed and that a meaningful failure is detectable. Check discovery on a task in that language and on mixed-language work, including whether the right skill routes from the project’s instructions.
- Validate the package and its links. Record tested commands, scope, outcomes, and any prerequisites still needed. Update the language inventory and any release or export catalog that ships the skill.
