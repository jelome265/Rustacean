# Contributing

## Branch and merge model

- `main` is protected. Nobody pushes to it directly.
- Work happens on a branch, and changes arrive as a pull request.
- A code owner reviews and merges. Automation never merges, approves, or force-pushes.
- Commits follow Conventional Commits (for example `feat(frameworks): ...`, `ci: ...`).

## CI check names and merge requirements

GitHub reports each job by its bare job name. The active `Main` ruleset now requires the
checks listed below by these exact names. This was verified by reading the repository's
active ruleset on 2026-10-14; re-check this list whenever workflow job names or rulesets change.

- `workflow-security`
- `validate-skills`
- `python-tests`
- `shell-lint`
- `rust-conformance`
- `dependency-review` (pull requests only)
- `secret-scan`
- `python-dependency-audit`
- `rust-dependency-audit`
- `analyze (python)`, `analyze (actions)`, `analyze (rust)`

**Current enforcement:** the active `Main` ruleset requires all 11 named status checks,
requires one approving review, and requires code-owner review. Required-check state is
repository configuration, not a property of this Markdown file. The historical audit finding
F-11 documents the earlier state and has a dated reassessment in `AUDIT_REPORT.md`.

## Local checks

```bash
python3 -m pip install -r requirements-ci.txt
python3 tools/validate_skills.py skills
python3 -m unittest discover -s tests/python -v
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --locked -- -D warnings
cargo test --workspace --locked
```

## Changing a pinned action

Pins are full commit SHAs with the release tag in a comment. To update one, resolve the new
tag to its commit, read that revision's `action.yml` to confirm every input you use still
exists, and change the SHA and comment together in one commit.
