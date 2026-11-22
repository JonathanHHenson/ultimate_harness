# Ultimate Harness

Ultimate Harness helps coding agents work consistently in a repository. It gives an agent project instructions, a versioned record of decisions and progress it can pick up in a later session, and checks that match the files it changed. That gives you a place to see what the agent did and what it verified.

## Get started

1. Clone this repository and open it in a coding agent that reads `AGENTS.md`, such as Codex. [Agent entry point](AGENTS.md)
2. Give the agent a task. For a quick tour, try “Show me what the harness checks before handing off a configuration change.”
3. For work that spans sessions, ask the agent to keep a feature record. Its requirements, design, and worklog live in a dated folder such as `.harness/features/2026-11-19-tracked-feature-completion/`. Use that name to resume the same feature when you return.

For manual setup on macOS or Linux, run this from the repository root with Python 3.11 or later.

```sh
python3 .harness/scripts/init_venv.py
```

The setup command installs the harness dependencies in `.harness/.venv/`. Use `.harness/.venv/bin/python` for the harness tests below. Feature records travel with the repository. Scratch files stay local to your checkout. [Python setup](.harness/agents/python-environment.md)

## Add these practices to another project

Use **Install Harness** for both a first setup and an upgrade. The agent researches the bundled harness and your project, proposes full component coverage, and asks about each meaningful customization in a local form. For an upgrade, it keeps compatible practices and asks how to resolve conflicts before changing existing behavior or records. [Install Harness skill](skills_src/install-harness/SKILL.md)

Download `install-harness.tar.gz` from a release that includes the combined skill. Extract the archive and place the whole `install-harness` folder, including `assets/`, in the skill location your coding agent uses. Open your target project and ask the agent to use `install-harness`. [GitHub releases](https://github.com/JonathanHHenson/ultimate_harness/releases)

To use the version in your checkout, run the harness setup above, then run `.harness/.venv/bin/python scripts/build_harness_skills.py`. Install the built folder from `skills_src/install-harness/`. [Build and export details](docs/TECHNICAL.md#how-portable-skills-are-built)

## Manage third-party skills

The harness uses Vercel’s Skills CLI at an exact version. Each import is pinned to a reviewed upstream revision. Commit the installed skill files with `skills-lock.json` so teammates get the same skills on checkout. Both adoption workflows can set up this policy, and evolution can plan a migration for existing imports. [Third-party skill instructions](.harness/agents/third-party-skills.md)

## Make changes

| If you want to change… | Edit |
| --- | --- |
| What agents do during a session | The triggers in [AGENTS.md](AGENTS.md) or the detailed instructions under [.harness/agents/](.harness/agents/) |
| Which checks run and when | The [validation index](.harness/VALIDATE.md) or a ruleset under [.harness/validation/](.harness/validation/) |
| A reusable agent workflow | The corresponding `SKILL.md` under [.agents/skills/](.agents/skills/) |
| Which tools agents use for a programming language | The corresponding skill in the [language guide](.harness/agents/languages.md) |
| A harness command | The script in [.harness/scripts/](.harness/scripts/) and its behavior tests in [.harness/scripts/tests/](.harness/scripts/tests/) |
| A command used by CI | The corresponding command under [scripts/](scripts/) |
| How another project installs or evolves a harness | [Install Harness](skills_src/install-harness/SKILL.md) or the [export catalog](skills_src/harness-files.toml) |
| Shared documentation | Project docs under [docs/](docs/) and feature decisions and verification under [docs/agents/](docs/agents/) |

Keep changes focused and run the checks that apply. For script changes, run the harness suite from the repository root.

```sh
.harness/.venv/bin/python -m unittest discover -s .harness/scripts/tests -v
```

For guidance or skill changes, use the documented link and package checks. [Validation commands](.harness/validation/harness-guidance.md)

Before merging a feature branch, run `python3 scripts/check_features_done.py` with Python 3.11 or later. Use that command in the pull request workflow for your project's CI system. [Feature merge check](docs/TECHNICAL.md#feature-completion-and-merge-checks)

The [project glossary](GLOSSARY.md) defines the terms used in the harness. The [technical design](docs/TECHNICAL.md) explains how the pieces work together.

To publish a new version, follow the [release process](docs/RELEASING.md).
