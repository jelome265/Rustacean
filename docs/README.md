# Documentation index

This file maps each document to its authority and intended use. When two documents conflict,
use the authority and evidence model below instead of guessing.

## Start here

- [Project overview and local checks](../README.md) — repository purpose, toolchain, quick verification commands.
- [Skill installation guide](../skills/INSTALLATION.md) — dry-run, install, verify discovery, upgrade and removal.
- [Agent skill discovery research](agent-skill-install-matrix.md) — vendor sources, documented paths, conflicts and runtime verification gaps.
- [Enterprise enforcement audit](../AUDIT_REPORT.md) — audit baseline, findings, owner actions and dated reassessments.
- [Contributor and merge policy](../CONTRIBUTING.md) — branch model, exact required check names and local workflow.
- [Security reporting policy](../SECURITY.md) — private vulnerability reporting.
- [Pull request checklist](../.github/pull_request_template.md) — evidence and review checklist.

## Normative engineering guidance

| Document | Authority and scope |
|---|---|
| [Rust enterprise best practices](../skills/rust-enterprise-best-practices/SKILL.md) | Normative Rust rulebook and rule IDs (\`BP-*\`). |
| [Topic coverage matrix](../skills/rust-enterprise-best-practices/references/topic-coverage.md) | Topics that must receive an applicability disposition; not a requirement to use every language feature. |
| [Workspace lint policy](../skills/rust-enterprise-best-practices/references/lints-workspace.toml) | Lint levels intended for consuming workspaces; inspect actual CI to know what is enforced here. |
| [Implementation procedure](../skills/rust-enterprise-implement/SKILL.md) | Requirements-first engineering workflow and definition of done. |
| [Hardcore execution contract](../skills/rust-enterprise-implement/references/hardcore-agent-execution-contract.md) | Binding agent workflow: inspect, research, plan, implement, test, verify and report. |
| [Reusable templates](../skills/rust-enterprise-implement/references/templates.md) | Starting templates; validate versions and policy for the target application before copying. |
| [Security and operations hardening](../skills/rust-enterprise-harden/SKILL.md) | Threat modelling, trust boundaries, resilience, observability, operations and build controls. |
| [Read-only security and logic audit](../skills/rust-enterprise-audit/SKILL.md) | Audit workflow and finding/evidence discipline; does not authorize unrequested writes. |
| [Framework policy and gate](../skills/rust-enterprise-frameworks/SKILL.md) | Approved stack, banned patterns and framework inventory policy. |
| [Machine-readable framework policy](../skills/rust-enterprise-frameworks/references/frameworks-policy.toml) | Framework versions and bans consumed by the framework gate. |

## Executable checks and evidence

- \`tools/validate_skills.py\` checks skill frontmatter, internal references and rule-ID resolution.
- \`tools/install_skills.py\` installs the entire sibling-dependent skill suite; it defaults to dry-run and verifies copied content and peer paths.
- \`tools/agent_skill_targets.json\` is the installer's path registry. The first path listed per scope is the default; alternatives are documented, not auto-detected.
- \`tests/python/\` tests validator, framework gate and installer behavior.
- \`.github/workflows/\` defines checks that run. The active GitHub ruleset defines which statuses and reviews block merges; see [CONTRIBUTING.md](../CONTRIBUTING.md) and the latest [audit report](../AUDIT_REPORT.md).

A rule appearing in prose is not, by itself, automated enforcement. Before making an enforcement
claim, identify the exact command or platform setting and its current evidence. Use these labels
in reviews and reports:

- **VERIFIED** — the stated check ran against the identified commit and passed.
- **FAILED** — it ran and did not pass.
- **NOT RUN** — it was not attempted.
- **BLOCKED** — it could not run because a named prerequisite was unavailable.
- **UNVERIFIED** — evidence is insufficient to make a claim.

## Keeping documentation correct

Update documentation in the same change as behavior, policy, agent compatibility or check-name
changes. Revalidate relative links, skill references, rule IDs, installer target paths, commands,
and CI job names. Do not copy a prior green result onto a newer commit; record the SHA and the
checks actually observed. Document unresolved sources as conflicts instead of silently choosing
one, and recheck upstream documentation when an agent or dependency is upgraded.
