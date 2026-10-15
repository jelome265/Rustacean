# Releasing Rustacean

This is the policy. CI and the publish workflow enforce it through
`tools/check_release.py`. If this document and the checker disagree, fix the
checker and this document in the same pull request.

## Versioning

Rustacean follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

Public surface, for the purpose of deciding what a change means:
- Installer: command-line flags, exit codes, the agent IDs in `tools/agent_skill_targets.json`, and the install-verification guarantees.
- Skill packages: skill folder names, `name` fields in `SKILL.md`, and rule IDs (`BP-*`) that other skills and audits cite.
- Plugin and npm package: the plugin name, marketplace name, and the `rustacean-skills` `bin` entry.
- Conformance crate: public items, once it is published as a library.

Bump rules:
- **MAJOR**: a removed or renamed public item, a changed exit-code meaning, a removed rule ID, or a changed install layout.
- **MINOR**: a new skill, new agent, new flag, new rule ID, or a new validator.
- **PATCH**: fixes that change no public surface, including wording and grading corrections.

Before 1.0.0, MINOR bumps may include breaking changes, and each one must say so under a `### Changed` or `### Removed` heading in the changelog.

## Version sources

Four places must hold the same version. The checker fails if they differ.

| File | Field |
|---|---|
| `Cargo.toml` | `[workspace.package] version` |
| `package.json` | `version` |
| `.claude-plugin/plugin.json` | `version` |
| `CHANGELOG.md` | the `## [X.Y.Z] - YYYY-MM-DD` heading |

Plugin users receive updates only when `plugin.json` `version` changes, so a release that changes skill content must bump it.

## Changelog rules

- Every pull request that changes release-relevant paths adds a line under `## [Unreleased]` in the same pull request. Release-relevant paths are listed in `tools/check_release.py`: `bin/`, the installer and validator tools, `skills/`, `crates/`, `.claude-plugin/`, `package.json`, and `Cargo.toml`. CI enforces this on pull requests.
- Use the Keep a Changelog sections: Added, Changed, Deprecated, Removed, Fixed, Security.
- Do not edit a released section. Corrections go under a new version.

## Release procedure

1. Open a release pull request that:
   - sets the new version in all four places above;
   - renames `## [Unreleased]` entries into `## [X.Y.Z] - YYYY-MM-DD`, using the date of the merge, and leaves an empty `## [Unreleased]` above it;
   - passes `python3 tools/check_release.py --require-release` locally.
2. Get the pull request reviewed and merged under the `Main` ruleset.
3. Tag the merge commit on `main` as `vX.Y.Z` (for example `git tag v0.1.0 <sha> && git push origin v0.1.0`). Tags are not yet protected by a ruleset, so the tag must be created from `main` by a maintainer.
4. Run the `publish-npm` workflow on the tag. The workflow runs `tools/check_release.py --tag vX.Y.Z --require-release`, then publishes after `npm-publish` environment approval.
5. Confirm `npm view rustacean-skills version` shows the new version.

The publish workflow refuses to run if the version is already on npm, if the tag does not match, or if the changelog has no dated section for the version.

## What is enforced

Enforced on every pull request, by the `validate-skills` job:
- Cargo, npm, and plugin versions agree, and are valid SemVer.
- `CHANGELOG.md` is well formed: an `[Unreleased]` section, dated releases, no duplicate versions.
- A change to a release-relevant path also changes `CHANGELOG.md`.
- The version is never lower than the newest dated release.

Enforced when publishing, by the `publish-npm` workflow:
- The tag is exactly `v<version>`.
- `CHANGELOG.md` has a dated section for the version.
- The version is strictly greater than every earlier dated release in the changelog.
- The version is strictly greater than the version already on npm, if any.
- The version is not already on npm.
- The `npm-publish` environment approval and the npm advisory check.

Enforced by repository rulesets:
- The `Main` ruleset requires the 11 status checks, one approving review, and code-owner review.
- The `Release tags` ruleset (target: tags matching `v*`) blocks creation, update, deletion, and non-fast-forward changes for everyone except repository admins. Admins can create release tags, so the rule protects against accidental or unauthorised tags, not against an admin's own actions.

## Known gaps

- A tag ruleset cannot require that a tag points to a commit on `main`. The publish workflow runs on whatever commit the tag names. The maintainer step "tag the merge commit on `main`" is still manual.
- Version ordering uses SemVer core numbers and treats any pre-release as lower than its release. It does not implement the full SemVer precedence rules for pre-release identifiers. Publish plain `X.Y.Z` versions.
- Duplicate-version protection at publish depends on the npm registry lookup. If npm is unreachable, the lookup returns nothing and the check cannot see the published version. The publish step then depends on the registry's own rejection of duplicate versions.
