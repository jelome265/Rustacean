<!-- Rustacean project banner -->
<div align="center">
  <h1>Rustacean</h1>
  <p><strong>Enterprise engineering skills for Rust, backed by executable checks.</strong></p>
  <p>Requirements-first implementation · Security and reliability hardening · Read-only audits · Framework controls</p>
  <p>
    <a href="https://github.com/jelome265/Rustacean/actions/workflows/ci.yml"><img alt="CI status" src="https://img.shields.io/github/actions/workflow/status/jelome265/Rustacean/ci.yml?branch=main&label=CI"></a>
    <a href="https://github.com/jelome265/Rustacean/actions/workflows/codeql.yml"><img alt="CodeQL status" src="https://img.shields.io/github/actions/workflow/status/jelome265/Rustacean/codeql.yml?branch=main&label=CodeQL"></a>
    <a href="https://github.com/jelome265/Rustacean/actions/workflows/security.yml"><img alt="Security workflow status" src="https://img.shields.io/github/actions/workflow/status/jelome265/Rustacean/security.yml?branch=main&label=Security"></a>
    <a href="https://github.com/jelome265/Rustacean/actions/workflows/scorecard.yml"><img alt="OpenSSF Scorecard status" src="https://img.shields.io/github/actions/workflow/status/jelome265/Rustacean/scorecard.yml?branch=main&label=Scorecard"></a>
    <a href="https://github.com/jelome265/Rustacean/blob/main/LICENSE"><img alt="License: Apache 2.0" src="https://img.shields.io/github/license/jelome265/Rustacean"></a>
    <img alt="Rust toolchain 1.98.1" src="https://img.shields.io/badge/Rust-toolchain%201.98.1-orange">
  </p>
</div>

---

Rustacean is a cooperating suite of five coding-agent skills for building, hardening, and auditing production-oriented Rust systems. The suite combines written engineering requirements with validators and CI checks where automation is practical. It is designed to support engineering decisions, not replace developer review, tests, or runtime evidence.

**Start here:** [Quick installation](#quick-installation) · [Supported agents](#supported-agents) · [What is included](#what-is-included) · [Documentation](#documentation)

## Quick installation

The installer supports project-level or user-level installation. It validates the full five-skill suite, previews the plan by default, and verifies file hashes and cross-skill links after an installation.

**Prerequisites:** Git and Python 3. Clone this repository first:

```bash
git clone https://github.com/jelome265/Rustacean.git
cd Rustacean
python3 tools/install_skills.py --list
```

Set <code>PROJECT</code> to the repository where you want your coding agent to use Rustacean. The following Codex example first previews changes without writing anything:

```bash
PROJECT="/absolute/path/to/your/project"

# Dry run: inspect the target and planned actions; writes nothing.
python3 tools/install_skills.py --agent codex --project-root "$PROJECT"

# Apply the same install plan, then verify the installed suite.
python3 tools/install_skills.py --agent codex --project-root "$PROJECT" --apply
```

Replace <code>codex</code> with the target agent ID from the table below. Replace the example path with an existing project directory. The installer does not automatically detect agent installations or prove that a running agent has discovered the skills.

To install for your user account rather than one project, use <code>--scope user</code> and omit <code>--project-root</code>:

```bash
python3 tools/install_skills.py --agent codex --scope user --apply
```

Use the user-level directory only if you intend these skills to be available across projects on that machine. Review project-level skill changes as you would review source code.

## Supported agents

These are the agent targets currently recorded in <code>tools/agent_skill_targets.json</code>. The paths shown are the installer's **default project destination**; several agents also support alternative or user-level locations. Evidence grades describe the quality of the available path documentation, not a runtime test of skill discovery.

| Agent / platform | Installer ID | Default project directory | Path evidence |
|---|---|---|---|
| Claude Code | <code>claude-code</code> | <code>.claude/skills/</code> | Official |
| OpenAI Codex CLI | <code>codex</code> | <code>.agents/skills/</code> | Official; official sources disagree on some user-scope paths |
| OpenCode | <code>opencode</code> | <code>.agents/skills/</code> | Official |
| Gemini CLI | <code>gemini-cli</code> | <code>.agents/skills/</code> | Official |
| Zed Agent | <code>zed</code> | <code>.agents/skills/</code> | Official |
| Google Antigravity | <code>antigravity</code> | <code>.agents/skills/</code> | Official; CLI user path differs from app/IDE |
| Cursor | <code>cursor</code> | <code>.agents/skills/</code> | Official |
| GitHub Copilot in VS Code | <code>copilot</code> | <code>.agents/skills/</code> | Official |
| Freebuff (Codebuff) | <code>freebuff</code> | <code>.agents/skills/</code> | Third-party / not runtime-verified |
| Meta Muse Code | <code>muse</code> | <code>.agents/skills/</code> | Third-party / not runtime-verified |
| Kimi Code CLI | <code>kimi</code> | <code>.agents/skills/</code> | Conflicting upstream path guidance |
| Z.AI ZCode | <code>zcode</code> | <code>.zcode/skills/</code> | Official |

### Install on a specific agent

Use the same two-step workflow for each supported agent: run the dry run first, inspect its destination and planned actions, then add <code>--apply</code> to write the files. For example, to target Cursor:

```bash
python3 tools/install_skills.py --agent cursor --project-root "$PROJECT"
python3 tools/install_skills.py --agent cursor --project-root "$PROJECT" --apply
```

Change <code>cursor</code> to any installer ID in the table to select another agent. The command installs all five skills together as siblings; do not copy a single skill out of the suite because its relative links depend on the others.

**Platform-specific notes**

- **Kimi Code CLI:** official documentation for different generations describes different skill locations. The installer refuses this target unless you explicitly pass <code>--accept-conflicting</code> or supply a verified <code>--dest-dir</code>. Check the installed version's documentation before bypassing that guard.
- **Google Antigravity:** the table shows the project path. For Antigravity CLI user scope, the documented destination is <code>~/.gemini/antigravity-cli/skills</code>; pass <code>--dest-dir ~/.gemini/antigravity-cli/skills</code> when selecting user scope.
- **Codex CLI:** the current skills overview documents <code>.agents/skills</code> for repository discovery and <code>$HOME/.agents/skills</code> for user discovery, while an official skill-creator sample still recommends <code>$CODEX_HOME/skills</code> (normally <code>~/.codex/skills</code>). Verify discovery with your installed version.
- **Muse and Freebuff:** path evidence is not fully confirmed against a running installation. Muse project skills may also require you to trust the workspace.

See the [agent discovery research](docs/agent-skill-install-matrix.md) for source links, alternative destinations, unresolved conflicts, and verification gaps.

### Installer safety and behavior

- **Dry run by default:** no files are written unless <code>--apply</code> is supplied.
- **All five skills together:** the installer rejects a missing or incomplete source suite.
- **Plan before writing:** a differing existing install stops the operation unless <code>--force</code> is supplied.
- **Post-install verification:** it compares installed content hashes and checks peer-skill links.
- **Explicit destination available:** <code>--dest-dir PATH</code> overrides the registered destination.
- **Symlink mode available:** <code>--mode symlink</code> points to this checkout rather than copying it.

Inspect all supported names and current installer options with:

```bash
python3 tools/install_skills.py --help
python3 tools/install_skills.py --list
```

An install that succeeds means the files were installed and validated. It does **not** prove that a specific agent version discovered them or follows their rules. Follow the target agent's own skill-listing or reload procedure to verify discovery.

## What is included

Rustacean contains five cooperating skills. Install them together into one discovery directory because they reference one another by relative paths.

| Skill | Purpose |
|---|---|
| [rust-enterprise-best-practices](skills/rust-enterprise-best-practices/SKILL.md) | Normative Rust rulebook, rule IDs, topic coverage, and lint policy |
| [rust-enterprise-implement](skills/rust-enterprise-implement/SKILL.md) | Requirements-first implementation procedure and reusable templates |
| [rust-enterprise-harden](skills/rust-enterprise-harden/SKILL.md) | Security, resilience, observability, operations, build, and container controls |
| [rust-enterprise-audit](skills/rust-enterprise-audit/SKILL.md) | Read-only security and logic audit workflow with evidence-focused findings |
| [rust-enterprise-frameworks](skills/rust-enterprise-frameworks/SKILL.md) | Approved framework stack, prohibited patterns, and framework inventory controls |

Supporting components:

- <code>crates/rustacean-conformance/</code> — executable conformance validators.
- <code>tools/validate_skills.py</code> — validates skill frontmatter, referenced files, and rule-ID resolution.
- <code>tools/install_skills.py</code> — installs and verifies the full skill suite.
- <code>tools/agent_skill_targets.json</code> — machine-readable agent path registry.
- <code>tests/python/</code> — tests for the Python validation, framework gate, and installer tools.
- <code>.github/workflows/</code> — CI, security, CodeQL, and OpenSSF Scorecard workflows.

## Pinned toolchain

The repository pins Rust **1.98.1** in <code>rust-toolchain.toml</code>. Rust 1.98.0 is excluded because of a vtable-generation miscompilation fixed in [Rust 1.98.1](https://blog.rust-lang.org/releases/1.98.1/).

## Local verification

From a checkout of this repository, run the core validation commands:

```bash
python3 -m pip install -r requirements-ci.txt
python3 tools/validate_skills.py skills
python3 -m unittest discover -s tests/python -v
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --locked -- -D warnings
cargo test --workspace --locked
RUSTDOCFLAGS='-D warnings' cargo doc --workspace --no-deps --locked
```

These are the core local checks, not a substitute for all hosted CI jobs. Hosted workflows additionally run workflow-security linting, shell lint, secret scanning, Rust and Python dependency audits, pull-request dependency review, CodeQL, and OpenSSF Scorecard. See <code>.github/workflows/</code> for the definitions and [contributor guide](CONTRIBUTING.md) for the required merge checks.

## Documentation

The [documentation index](docs/README.md) explains each document's authority, the distinction between written policy and automated enforcement, and how verification evidence should be recorded.

| Document | Use it for |
|---|---|
| [Skill installation guide](skills/INSTALLATION.md) | Install options, per-agent paths, discovery verification, upgrades, and removal |
| [Agent skill discovery matrix](docs/agent-skill-install-matrix.md) | Upstream source links, path evidence, source conflicts, and open verification items |
| [Audit report](AUDIT_REPORT.md) | Findings, enforcement limits, and dated reassessments |
| [Contributor guide](CONTRIBUTING.md) | Contribution workflow, branch protection, and required checks |
| [Security policy](SECURITY.md) | Private vulnerability reporting |

## Engineering and security principles

- **Requirements before implementation:** identify requirements, constraints, assumptions, and acceptance evidence before editing code.
- **Evidence over assertion:** distinguish automated checks from written guidance and runtime behavior.
- **Defense in depth:** prefer enforceable controls, explicit trust boundaries, least privilege, and observable failure modes.
- **Human review remains mandatory:** agent instructions are guidance; code, tests, CI, and reviewers establish whether a change is acceptable.

The skills document what is verified and what remains uncertain. Do not infer runtime compliance from the existence of a rule, a successful installation, or a passing unrelated check.

## Governance

- <code>main</code> is protected; changes arrive through pull requests.
- Automation does not merge, approve, or push directly to <code>main</code>.
- Third-party GitHub Actions are pinned to full commit SHAs; Dependabot proposes updates.
- Report vulnerabilities through private reporting described in [SECURITY.md](SECURITY.md).

## License

Apache License 2.0. See [LICENSE](LICENSE).
