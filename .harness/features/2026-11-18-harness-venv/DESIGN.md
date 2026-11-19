# Design: Harness Python Environment

## F-1. Environment setup

Run the standard-library bootstrap with an available Python 3.11 or later.
Resolve the environment and requirements paths relative to the bootstrap file.
Prefer uv with an explicit target and interpreter. Without uv, try the
standard venv module, then use virtualenv if venv cannot complete. Reuse an
existing interpreter after checking its prefix and version. Install the
requirements from `.harness/scripts/requirements.txt` through uv or the
environment's pip. Bootstrap an environment's pip with ensurepip if uv is
no longer available and the existing environment has no pip.

## F-2. Session and script integration

Put environment setup ahead of session scratch creation in AGENTS.md.
Document the bootstrap exception and use the environment's interpreter
directly in scratch, feature memory, and validation commands, including
skill packaging validation. No shell activation is needed. Refresh the
harness environment when its manifest changes.

## NF-1. Isolation and repeatability

Ignore the local environment and bootstrap lock. Serialize bootstrap writes
with a POSIX file lock. Use explicit locations for environment creation and
dependency installation so a neighboring project environment is unaffected.
Report setup errors and let a later invocation retry. Describe the convention
in the build-harness skill. Verify a fresh setup, reuse, fallback selection,
Git ignore semantics, dependency separation, and the existing harness suite.
