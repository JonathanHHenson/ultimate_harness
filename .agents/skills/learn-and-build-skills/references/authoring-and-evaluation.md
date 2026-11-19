# Authoring and Evaluation

## Package what should transfer

- Identify the gap the skill fills. Use rules for recurring decision points, examples for decisions best shown concretely, and scripts for stable operations where deterministic execution matters. Explain applicability and how to recover from likely failures. Keep version-specific facts conditional and verify them against the target environment.
- Use the target runtime's supported skill location and format. Write a concise `SKILL.md` with YAML `name` and `description`, a directory that matches the name, and guidance that changes execution. The description should identify the task and trigger in natural user language. Add an exclusion only when a plausible neighboring request could misroute.
- Keep the entry point focused on inputs, choices, required actions, and completion. Put long or conditional material in linked references that state when to read them. Bundle templates and scripts only for demonstrated needs. Review bundled and third-party material, including assumptions, dependencies, and side effects. Scope actions to what the original user authorized.

The specification defines package structure. Runtime documentation and installed validation establish platform-specific behavior. [Agent Skills specification](https://agentskills.io/specification), [Codex skill documentation](https://developers.openai.com/codex/skills)

## Evaluate independently of the draft

Before tuning on results, save test prompts, representative inputs, and observable pass criteria. A good set includes a normal run, a different input or prerequisite failure, and a related task that should not activate the skill. Keep fixture answers and scoring rules out of runtime instructions. Retain an untried variant for later transfer testing if a draft is revised against the first cases.

- **Structure.** Check frontmatter, local links, resource paths, and helper prerequisites using available runtime validators. This confirms that the package can be read.
- **Discovery.** A direct invocation tests that the package can be used. An implicit invocation and a near miss in fresh sessions test whether the metadata routes appropriately. If you can only review metadata by inspection, report that as a review.
- **Execution.** In an isolated workspace, run realistic prompts with fresh inputs. Verify output, relevant procedure constraints, and side effects. Prefer deterministic checks for objective outcomes. When independent execution is available and authorized, give the evaluator raw inputs and the actual user request without the desired answer or implementation hints.
- **Added value.** For a performance claim, run the same cases with the skill and with no skill or the previous version, holding the runtime and permissions constant. Count repairs and regressions and consider command count, time, or context when relevant. A successful smoke test alone does not establish improvement. Repeat when variance matters.
- **Iteration.** Diagnose whether misses are routing, missing knowledge, incompatible tools, or execution. Make the smallest relevant edit, rerun affected checks, and evaluate on a new case before broadening the claim. Report manual reviews, test runs, and checks that could not run separately.

Curated skills can help, and results depend on tasks and runtimes. Evidence-grounded generation and paired verification are promising strategies rather than guarantees for a new skill. [SkillsBench](https://arxiv.org/abs/2602.12670v4), [SkillLens](https://arxiv.org/abs/2605.23899), [SkillGen](https://arxiv.org/abs/2605.10999), [Agent Skills evaluation guide](https://agentskills.io/skill-creation/evaluating-skills)
