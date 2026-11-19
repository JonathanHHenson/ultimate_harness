# Ultimate Harness

Ultimate Harness helps coding agents work consistently in a repository. It gives an agent project instructions, a local record of decisions and progress it can pick up in a later session, and checks that match the files it changed. That gives you a place to see what the agent did and what it verified.

## Get started

1. Clone this repository and open it in a coding agent that reads `AGENTS.md`, such as Codex. [Agent entry point](AGENTS.md)
2. Give the agent a task. For a quick tour, try “Show me what the harness checks before handing off a configuration change.”
3. For work that spans sessions, ask the agent to keep a feature record. You can read its requirements, design, and work log under `.harness/features/`. Ask the agent to resume the same feature when you return.

For manual setup on macOS or Linux, run this from the repository root with Python 3.11 or later.

```sh
python3 .harness/scripts/init_venv.py
```

The setup command installs the harness dependencies in `.harness/.venv/`. Use `.harness/.venv/bin/python` for the harness commands below. Feature records and scratch files are local to the checkout and ignored by Git. [Python setup](.harness/agents/python-environment.md)

## Make changes

| If you want to change… | Edit |
| --- | --- |
| What agents do during a session | The triggers in [AGENTS.md](AGENTS.md) or the detailed instructions under [.harness/agents/](.harness/agents/) |
| Which checks run and when | The [validation guide](.harness/VALIDATE.md) or a specific review under [.harness/validation/](.harness/validation/) |
| A reusable agent workflow | The corresponding `SKILL.md` under [.agents/skills/](.agents/skills/) |
| A harness command | The script in [.harness/scripts/](.harness/scripts/) and its behavior tests in [.harness/scripts/tests/](.harness/scripts/tests/) |

Keep changes focused and run the checks that apply. For script changes, run the harness suite from the repository root.

```sh
.harness/.venv/bin/python -m unittest discover -s .harness/scripts/tests -v
```

For guidance or skill changes, use the documented link and package checks. [Validation commands](.harness/validation/harness-guidance.md)

For the architecture and the reasoning behind the harness, see the [technical design](TECHNICAL.md).
