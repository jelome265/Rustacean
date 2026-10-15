# Releasing Rustacean

Nobody edits version numbers or tags by hand. Releases are produced from
Conventional Commits by [release-please](https://github.com/googleapis/release-please-action),
and published by the `publish-npm` workflow. This document describes the flow and what
enforces each step. If this document and the automation disagree, fix both in the same
pull request.

## Day-to-day: write Conventional Commits

Every commit subject on a pull request must follow Conventional Commits. The `validate-skills`
job checks this (`tools/check_commits.py`), and release-please depends on it:

| Subject | Effect on the next release (pre-1.0) |
|---|---|
| `fix: ...`, `fix(scope): ...` | patch bump |
| `feat: ...`, `feat(scope): ...` | minor bump |
| `feat!: ...` or a `BREAKING CHANGE:` footer | minor bump (pre-1.0, breaking changes bump minor) |
| `docs:`, `ci:`, `test:`, `chore:`, `build:`, `refactor:`, `style:` | no release by themselves |
| `security(scope): ...` | recorded in the changelog; no release on its own |

Merges of pull requests do not need to be squashed, but every commit that lands must
conform. A non-conforming subject fails the pull request.

## The release

1. Merge pull requests into `main` as usual.
2. release-please keeps one open pull request titled `chore: release X.Y.Z`. It bumps the version in
   `Cargo.toml`, `package.json`, `.claude-plugin/plugin.json`, and `.release-please-manifest.json`,
   and adds a section to `CHANGELOG.md` generated from the commits.
3. A maintainer reviews that pull request and merges it. The merge is the release decision.
4. release-please creates the tag `vX.Y.Z` on the merge commit and a GitHub release.
5. `publish-npm` starts. It waits for approval in the `npm-publish` environment, then publishes
   to npm with provenance.

No step asks anyone to type a version number or create a tag.

## What enforces what

Pull requests (`validate-skills` job):
- Conventional Commit subjects on every non-merge commit (`tools/check_commits.py`).
- Version sources agree and are valid SemVer; `CHANGELOG.md` is well formed (`tools/check_release.py`).

Release pull request and publish (`publish-npm` job, after approval):
- The tag's commit is an ancestor of `main`, and it is the commit being built.
- The tag equals `v<version>`, and the changelog has a dated section for that version.
- The version is strictly newer than every earlier release in the changelog.
- The version is strictly newer than the version on npm. The npm lookup fails closed: a
  registry error stops the release. Only a clean "not found" counts as unpublished.
- The `npm-publish` environment: a required reviewer approves each publish.
- Tooling advisories are checked against the time-limited allow-list.

Repository rulesets:
- `Main`: required status checks, one approving review, and code-owner review.
- `Release tags` (tags matching `v*`): creation, update, deletion, and non-fast-forward changes are
  limited to repository admins. release-please's tag creation runs as an admin token, so it passes.

## Version rules

Rustacean is pre-1.0 (`0.x`). Under the table above, breaking changes and new features
bump the minor version, and fixes bump the patch version. Once the public surface is stable,
the project moves to 1.0.0 by a deliberate pull request that changes the release configuration.

Public surface, for deciding what a change means:
- Installer: command-line flags, exit codes, agent IDs in `tools/agent_skill_targets.json`, and the
  install verification guarantees.
- Skill packages: skill folder names, `name` fields in `SKILL.md`, and rule IDs (`BP-*`).
- Plugin and npm package: plugin and marketplace names, and the `rustacean-skills` `bin` entry.

Any change to that surface that breaks a user must use `feat!:` or a `BREAKING CHANGE:` footer.

## One-time setup (already needed before the first release)

1. **`RELEASE_TOKEN` repository secret.** A fine-grained personal access token owned by a repository
   admin, with repository access to `jelome265/Rustacean` and these permissions: Contents (read and
   write), Pull requests (read and write), and Metadata (read). Pull requests opened with the default
   `GITHUB_TOKEN` do not trigger required checks, so this token is required. Tokens expire; set a
   reminder to rotate. A GitHub App token is the longer-term replacement.
2. **`npm-publish` environment** with a required reviewer (already configured).
3. **`NPM_TOKEN` in the `npm-publish` environment** (already configured).

## What is still manual, and why

- Approving and merging the release pull request. This is deliberate: it is the human decision to ship.
- Approving the npm publish in the `npm-publish` environment. This is deliberate too.
- Rotating `RELEASE_TOKEN` and `NPM_TOKEN`.

## Recovery

- If a publish fails before npm accepts the version, fix the cause and re-run the failed job
  from the Actions tab. The version stays the same.
- If npm has accepted a version, it cannot be reused. Ship a new release.
- `publish-npm` can also be run manually from `main` (workflow dispatch). It goes through the same checks
  and approval, so it cannot publish a version that the release pull request did not produce.
