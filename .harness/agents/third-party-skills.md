# Third-party skill instructions

## Before installing or changing a third-party skill

- Use Vercel’s `skills@1.9.0` from the project root with Node.js 22.20.0 or later and npm. Use the project’s selected agents and repository scope. Change the CLI pin through the project’s normal review process. [Pinned CLI reference](https://github.com/vercel-labs/skills/blob/v1.9.0/docs/commands.md)
- Confirm the approved skill, source, version, and target path. Pin Git imports to a full commit SHA. For an archive-only release, use a version-specific public download URL and retain the approved SHA-256 in tracked provenance. Verify the downloaded archive against that digest and compare the staged skill with the reviewed archive contents. Keep source URLs free of credentials. Review the skill instructions, bundled scripts, dependencies, and redistribution notices before adoption. Use a disposable checkout for inspection when needed.
- Check for an existing skill with the same name and for local modifications. Preserve project-authored and bundled harness skills. For a different source or changed local behavior, resolve the collision with the human before replacing a skill. Confirm the provenance of an existing import before adding it to the skill lockfile.

## When installing or repinning an approved skill

- Select the exact skill and supported agent targets. For example, from the repository root, replace the source, commit and name below with the approved values.

  ```sh
  npx --yes skills@1.9.0 add owner/repo@FULL_COMMIT_SHA --skill skill-name -a codex github-copilot --yes
  ```

- Update by running `add` with the new approved pin. Review the upstream and installed diffs before adopting the new version. Use `npx --yes skills@1.9.0 remove skill-name --yes` from the project root for an approved removal.
- Track the complete installed skill directory under `.agents/skills/`, any required repository-local discovery paths for other selected agents, and the generated root skill lockfile `skills-lock.json` in the same Git change. Retain required upstream notices. Keep separately recorded provenance and notices outside CLI-managed skill folders so their contents match the lock. Create the skill lockfile through the CLI when the project first adopts a third-party skill.

## Before handing off a third-party skill change

- Run `npx --yes skills@1.9.0 list --json` from the project root. Require each added or updated skill to report `tracked`. Verify its lock entry points to the reviewed source, pin and content hash. For removal, verify that the selected files, lock entry and any discovery links are gone. Review the Git diff and check that all managed files and lock changes can be tracked, and that unrelated skills and lock entries are preserved.
- A normal checkout uses the tracked files directly. To verify or recover a pinned skill in a disposable checkout with a populated lock, run `npx --yes skills@1.9.0 experimental_install --frozen-lockfile` and compare the restored files and lock to the committed versions. Investigate a hash mismatch or unavailable source before changing the pin. [Restore and integrity checks](https://github.com/vercel-labs/skills/blob/v1.9.0/docs/commands.md#restore-skills-from-the-project-lock-file)
