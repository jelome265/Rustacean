# Changelog

All notable changes to Rustacean are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). The release process
is in [RELEASING.md](RELEASING.md).

## [Unreleased]

## [0.1.0] - 2026-10-15

### Added
- Five cooperating agent skills: `rust-enterprise-best-practices`, `rust-enterprise-implement`, `rust-enterprise-harden`, `rust-enterprise-audit`, `rust-enterprise-frameworks`.
- `rustacean-conformance` crate with executable inventory validators and the workspace lint policy.
- Skill installer (`tools/install_skills.py`): dry run by default, hash-verified after `--apply`, per-agent registry with evidence grades.
- Claude Code plugin and marketplace manifests (`.claude-plugin/`).
- `rustacean-skills` npx launcher, which forwards to the installer.
- Manual and tag-triggered npm publish workflow, gated by the `npm-publish` environment.
- Release policy checks (`tools/check_release.py`) and this changelog.

### Security
- CI workflows pinned to full commit SHAs, with empty default permissions and zizmor and actionlint checks.
- Publish tooling pinned to npm 12.2.0 through a lockfile. Four high-severity advisories in npm's bundled dependencies are recorded as time-limited exceptions in `tools/npm-publish/advisory-allowlist.json`, expiring 2026-12-31.

### Fixed
- Z.AI ZCode is graded `conflicting` rather than `official` for its skill path.
