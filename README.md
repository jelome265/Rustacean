# Rustacean

Enterprise engineering skills for Rust, with the enforcement that backs them.

This repository contains:

| Path | What it is |
|---|---|
| `skills/rust-enterprise-best-practices/` | Normative rulebook (BP rules), workspace lint policy, banned-pattern gate script, topic coverage matrix |
| `skills/rust-enterprise-implement/` | Build procedure for new Rust code, with templates |
| `skills/rust-enterprise-harden/` | Security, resilience, observability, operations, build and container controls |
| `skills/rust-enterprise-audit/` | Read-only security and logic audit procedure and report template |
| `skills/rust-enterprise-frameworks/` | Approved framework stack, hard bans, artefact gate, inventory patterns |
| `crates/rustacean-conformance/` | Executable form of the inventory validators, tested under the strict lint policy |
| `tools/validate_skills.py` | Validates skill frontmatter, referenced files, and rule-ID resolution |
| `tests/python/` | Unit tests for the framework gate and the skill validator |
| `.github/workflows/` | CI, security, CodeQL, and OpenSSF Scorecard workflows |

## Pinned toolchain

Rust `1.98.1`, from `rust-toolchain.toml`. Version `1.98.0` is excluded because of a
miscompilation in vtable generation that 1.98.1 fixes.

## Running the checks locally

```bash
python3 -m pip install -r requirements-ci.txt
python3 tools/validate_skills.py skills
python3 -m unittest discover -s tests/python -v
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --locked -- -D warnings
cargo test --workspace --locked
```

## Governance

- `main` is protected. Changes arrive by pull request.
- Automation never merges, approves, or pushes to `main`. A code owner merges.
- Every third-party action is pinned to a full commit SHA. Dependabot proposes updates.
- Security reports go through private vulnerability reporting (see `SECURITY.md`).

## Status and limits

The skill documents state exactly what was verified and what was not. See each skill's
verification table. Read those before relying on any claim.

## License

Apache License 2.0. See `LICENSE`.

## Installing the skill suite

The five skills are a cooperating suite. Follow [skills/INSTALLATION.md](skills/INSTALLATION.md) to install all packages into a supported agent's skill-discovery directory and validate cross-skill references. Successful discovery is not a substitute for running code and CI gates.
