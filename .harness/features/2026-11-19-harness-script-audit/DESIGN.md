# Harness script audit

## FEATURE

Keep the existing CLI arguments and record formats. Validate the initial definition from a single read, publish new features only when all records exist, and serialize commands using the existing per-feature lock. Write a private pending update before replacing either status document. Recover it under the same lock before the next command. Readers that bypass the commands should wait for interrupted updates to recover. Reject symlinks and special files at mutable record paths.

## LOCAL

Share regular-file reads and lock acquisition across the scripts with those boundaries. Keep scratch session creation private and environment setup isolated from implicit tool configuration. Preserve explicit uv environment settings and the standard-library and virtualenv fallbacks. At untrusted TOML, YAML and Markdown parsing boundaries, report the path and reason without echoing malformed data.

## QUALITY

Separate storage and recovery from feature validation and keep the CLI entry points small. Run the full harness suite, scoped static analysis, and targeted behavior tests for recovery, setup and validation. Review the remaining trust assumptions for local files, subprocess launches and tools.
