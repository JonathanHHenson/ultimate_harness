---
name: shell-development
description: Write, lint, format, and test shell scripts and embedded shell steps. Use for POSIX shell, Bash, or other shell code in scripts and automation.
---

# Shell Development

- Determine the actual interpreter from the shebang, runner, or configured workflow shell. Keep POSIX scripts portable and use Bash features only where Bash is the declared runtime. Quote argument expansions and keep data separate from command text.
- Check syntax with the declared shell, such as `sh -n FILE` or `bash -n FILE`. Use the configured ShellCheck rule set and let shfmt check formatting with `shfmt -d FILES` when configured. For embedded workflow steps, validate the workflow syntax and apply the declared shell’s checks to the script body. [ShellCheck](https://www.shellcheck.net/) · [shfmt](https://github.com/mvdan/sh)
- Exercise the script through its normal entry point in a disposable directory. Check exit status, output, and file changes for success, invalid input, unusual filenames, and partial failure where applicable. Use the project’s shell test runner if one is configured.
