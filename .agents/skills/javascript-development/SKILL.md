---
name: javascript-development
description: Write, format, lint, test, and review JavaScript for browsers or Node.js. Use for JavaScript source, modules, tests, and JavaScript-specific development tasks.
---

# JavaScript Development

- Identify the browser or Node versions, module format, and commands in the target’s docs, scripts, and package configuration. Preserve the existing dependencies and runtime targets.
- Keep input handling, rendering, and state transitions distinct. Prefer built-in platform APIs where they cover the behavior. For browser code, use DOM text or attribute APIs for untrusted strings and keep network and storage failures observable.
- Use configured ESLint and formatter commands first. For standalone syntax checking, use `node --check FILE` for the project’s module format or `node --input-type=module --check < FILE` for an ES module in a plain asset directory. Where Prettier is configured, use its check mode on the changed paths. [ESLint CLI](https://eslint.org/docs/latest/use/command-line-interface) · [Prettier CLI](https://prettier.io/docs/cli)
- If the project has no JavaScript complexity diagnostic, run [the bundled ESLint check](scripts/check-complexity.sh) from the project root with Node 24 and npm. Pass explicit paths or quoted globs inside that project. It uses the pinned ESLint release and fails on ignored inputs or functions over 10. The package is used for linting.
- Run the project’s test scripts. Where the suite uses Node’s built-in runner, run `node --test` or select the changed behavior’s test file. Exercise browser-only behavior in the project’s browser tests, including asynchronous state, real interactions, and errors. [Node test runner](https://nodejs.org/api/test.html)
