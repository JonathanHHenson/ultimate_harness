# Ultimate Harness

Ultimate Harness helps coding agents work consistently in a repository. It gives an agent project instructions, a versioned record of decisions and progress it can pick up in a later session, and checks that match the files it changed. That gives you a place to see what the agent did and what it verified.

## Get started

1. Clone this repository and open it in a coding agent that reads `AGENTS.md`, such as Codex. [Agent entry point](AGENTS.md)
2. Give the agent a task. For a quick tour, try “Show me what the harness checks before handing off a configuration change.”
3. For work that spans sessions, ask the agent to keep a feature record. Its requirements, design, and work log live in a dated folder such as `.harness/features/2026-11-19-tracked-feature-completion/`. Use that name to resume the same feature when you return.

For manual setup on macOS or Linux, run this from the repository root with Python 3.11 or later.

```sh
python3 .harness/scripts/init_venv.py
```

The setup command installs the harness dependencies in `.harness/.venv/`. Use `.harness/.venv/bin/python` for the harness tests below. Feature records travel with the repository. Scratch files stay local to your checkout. [Python setup](.harness/agents/python-environment.md)

## Add these practices to another project

- Choose **Install a Harness** for a first setup. The agent will ask which capabilities fit your workflow and set up the selected ones. [Install skill source](skills_src/install-harness/SKILL.md)
- Choose **Evolve a Harness** when you already have agent instructions and want to adopt a practice at a time. The agent will review your existing workflow and agree on the next change with you. [Evolve skill source](skills_src/evolve-harness/SKILL.md)

Download `harness-skills` from a successful **Build harness skills** workflow run and extract the archive for the skill you want. Place the whole extracted skill folder, including `assets/`, in the skill location your coding agent uses. Open your target project and ask the agent to use that skill.

To build from your checkout, run the harness setup above, then run `.harness/.venv/bin/python scripts/build_harness_skills.py`. The two ready-to-use skill folders are written under `skills_src/`. [Build and export details](docs/TECHNICAL.md#how-portable-skills-are-built)

## Make changes

| If you want to change… | Edit |
| --- | --- |
| What agents do during a session | The triggers in [AGENTS.md](AGENTS.md) or the detailed instructions under [.harness/agents/](.harness/agents/) |
| Which checks run and when | The [validation guide](.harness/VALIDATE.md) or a specific review under [.harness/validation/](.harness/validation/) |
| A reusable agent workflow | The corresponding `SKILL.md` under [.agents/skills/](.agents/skills/) |
| A harness command | The script in [.harness/scripts/](.harness/scripts/) and its behavior tests in [.harness/scripts/tests/](.harness/scripts/tests/) |
| A command used by CI | The corresponding command under [scripts/](scripts/) |
| How another project installs or evolves a harness | The corresponding skill or the shared export catalog under [skills_src/](skills_src/) |
| Shared documentation | Project docs under [docs/](docs/) and feature decisions and verification under [docs/agents/](docs/agents/) |

Keep changes focused and run the checks that apply. For script changes, run the harness suite from the repository root.

```sh
.harness/.venv/bin/python -m unittest discover -s .harness/scripts/tests -v
```

For guidance or skill changes, use the documented link and package checks. [Validation commands](.harness/validation/harness-guidance.md)

Before merging a feature branch, run `python3 scripts/check_features_done.py` with Python 3.11 or later. Use that command in the pull request workflow for your project's CI system. [Merge check](docs/TECHNICAL.md#feature-completion-and-merge-checks)

For the architecture and the reasoning behind the harness, see the [technical design](docs/TECHNICAL.md).
