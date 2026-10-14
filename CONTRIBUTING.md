# Contributing

## Branch and merge model

- `main` is protected. Nobody pushes to it directly.
- Work happens on a branch, and changes arrive as a pull request.
- A code owner reviews and merges. Automation never merges, approves, or force-pushes.
- Commits follow Conventional Commits (for example `feat(frameworks): ...`, `ci: ...`).

## Required checks for merge

GitHub reports each job by its bare job name. Rulesets match required checks by that exact
name, so the names below are the ones to require. Verified against the check runs on a
pull request head (`GET /repos/{owner}/{repo}/commits/{sha}/check-runs`).

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

**Status of enforcement:** these names are documented here, but the `Main` ruleset does not
yet require them. Until the owner adds them to the ruleset, a pull request can merge
without passing these checks. See `AUDIT_REPORT.md`, finding F-11.

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
