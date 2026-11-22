# Release Ultimate Harness

Attach `install-harness.tar.gz` from the tagged commit's Actions build to each release of the combined skill. The release asset remains available after the build artifact expires. [GitHub releases](https://github.com/JonathanHHenson/ultimate_harness/releases) · [Packaging workflow](../.github/workflows/build-harness-skills.yml)

## Before creating the release

1. Use the [validation index](../.harness/VALIDATE.md) to run the applicable checks and reviews. Run the [feature merge check](../scripts/check_features_done.py). Push the release commit to `main`.
2. Find a successful **Build harness skills** run for that exact commit. Create and push an annotated `vMAJOR.MINOR.PATCH` tag on the commit.
3. From the repository root, set `tag` to that version, `run_id` to that run's numeric ID, and `release_dir` to an absolute path in a fresh local scratch workspace. Compare the run's `headSha` with the commit resolved by the tag. Continue when the hashes match and the run reports `success`. [GitHub CLI run view](https://cli.github.com/manual/gh_run_view)

```sh
git rev-parse "$tag^{commit}"
gh run view "$run_id" --json headSha,conclusion,url
gh run download "$run_id" --name harness-skills --dir "$release_dir/ci"
```

## Prepare and publish the asset

1. Check the archive contains the `install-harness/` folder, its `SKILL.md`, and the built `assets/harness/` payload. The license at the root of that folder must match `git show "$tag:LICENSE"`. If the CI archive omits it, extract the archive into a staging directory, add that file as `LICENSE` inside the skill folder, and recreate the archive from the staging directory. Verify the remaining files and executable permissions still match the CI archive. Place the final archive under `$release_dir/packages/`. [Repository license](../LICENSE)
2. Save release notes to `$release_dir/release-notes.md`. Point readers to the release's **Assets** section for `install-harness.tar.gz`. Create a draft with the archive attached. For an existing release missing the asset, upload it with `gh release upload`. Check an existing asset against the prepared file before continuing. [Create a release](https://cli.github.com/manual/gh_release_create) · [Upload release assets](https://cli.github.com/manual/gh_release_upload)

```sh
gh release create "$tag" --verify-tag --draft --notes-file "$release_dir/release-notes.md" \
  "$release_dir/packages/install-harness.tar.gz"
```

3. Verify that GitHub lists the asset on the intended tag, then publish the draft. Download the archive from its public release link and compare it byte for byte with the prepared file. Check that the release notes direct readers to the asset. [Edit a release](https://cli.github.com/manual/gh_release_edit) · [View a release](https://cli.github.com/manual/gh_release_view)

```sh
gh release view "$tag" --json tagName,isDraft,assets
gh release edit "$tag" --draft=false
```
