# Contributing

## Branch and merge model

- `main` is protected. Nobody pushes to it directly.
- Work happens on a branch, and changes arrive as a pull request.
- A code owner reviews and merges. Automation never merges, approves, or force-pushes.
- Commits follow Conventional Commits (for example `feat(frameworks): ...`, `ci: ...`).

## Required checks for merge

These job names must pass before a merge is possible:

- `ci / workflow-security`
- `ci / validate-skills`
- `ci / python-tests`
- `ci / shell-lint`
- `ci / rust-conformance`
- `security / dependency-review`
- `security / secret-scan`
- `security / python-dependency-audit`
- `security / rust-dependency-audit`
- `codeql / analyze (python)`, `codeql / analyze (actions)`, and `codeql / analyze (rust)`

Branch protection that enforces these is configured in the repository settings. The
settings are part of the governance record; a change to them is announced to the owner.

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
