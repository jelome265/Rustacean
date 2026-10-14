# Rustacean Enterprise Skills and Enforcement Audit

**Audit date:** 2026-10-14  
**Repository:** https://github.com/jelome265/Rustacean  
**Audited baseline:** main at commit 41e7fae1e0b0a5ea440cf6e1cec061ee69c1feb6 (2026-10-13)  
**Scope:** skill packages, implementation/audit/security instructions, Rust topic coverage, CI/security workflows, CodeQL, Dependabot, issue/PR templates, Git governance documentation, installation, and enforcement evidence.

**Evidence boundary:** A local Git clone was attempted but DNS could not resolve github.com. Source/configuration was inspected via the connected GitHub repository interface. No local builds, tests, shell scans, dynamic integration tests, or CI runs were executed as part of this audit. Branch protection/rulesets could not be retrieved because the GitHub API returned HTTP 403. This report does not claim those checks passed or those settings are enforced.

## Executive verdict

**The repository is a strong starting point, but it is not a universal enforcement engine and should not be described as fully production-enforcing.** The rulebooks contain significant breadth: toolchain and lint policy, implementation workflow, threat modelling, OAuth/OIDC/JWT/RBAC, TLS/secrets, resilience, observability, dependency controls, CI, and a topic coverage matrix. The conformance crate and Python validator provide executable checks.

The critical distinction is between a rule written in a skill, a check implemented in a script, a workflow that actually runs that script, a repository ruleset that blocks merges, and a test result that has actually been observed. These are separate evidence levels.

## Direct answers

| Question | Verdict | Explanation |
|---|---|---|
| Is the requirement set valid? | Mostly yes, with corrections. | Security, correctness, resilience, compatibility, supply-chain, observability and review are sound enterprise concerns. Controls should be conditional on actual requirements and risk; forcing OAuth, a broker, a circuit breaker, or microservices into every program is bad architecture. |
| Can an agent use the entire skill set? | Partially; host-dependent. | The procedures are detailed, but usefulness depends on discovery, cross-skill files, repository/tool access, ability to execute tests, fresh authoritative sources and task context. Instructions cannot guarantee agent compliance. |
| Is it installable? | Yes as a complete suite, not automatically in every host. | Five packages contain SKILL.md frontmatter with names matching directory names. Repository storage under skills/ is not Claude Code's automatic .claude/skills/ discovery location. Peer dependencies mean a single folder install may omit critical rulebooks. This PR adds an installation guide and cross-skill path validation. |
| Must all Rust topics be utilised? | No; all relevant topics must be considered. | The topic matrix maps topics to rules and mechanisms. It should require an applicability disposition, not indiscriminate feature use. Rust async is Future + async/await + an executor/runtime, not JavaScript Promise. |
| Are enterprise best practices enforced? | Partially. | Strict workspace lints, conformance tests, a validator, pinned actions and multiple workflows exist. But rule text is not equivalent to CI enforcement, and not all human/consumer-project controls are enforced in this repository. CodeQL's prior Rust exclusion was a gap; this PR adds Rust analysis and a Cargo advisory job, pending CI. |
| Was the fake/mock boundary strong enough? | Not sufficiently explicit before this PR. | Existing implementation guidance requires discovery, invariants and test-first development, but needed a direct prohibition on fake production paths and on using mock-only tests as integration/E2E evidence. This PR adds a binding execution contract and links it from the implementation skill. |

## Positive findings

### F-01 — Structured five-skill suite
**Severity:** Informational — strength

The repository separates normative Rust rules, implementation, hardening, audit and framework-specific controls. The framework guidance also distinguishes verified source/test claims from structural stub checks and unverified APIs, which is good evidence discipline.

Files: https://github.com/jelome265/Rustacean/tree/main/skills

### F-02 — Executable controls exist
**Severity:** Informational — strength

The repository has a pinned Rust toolchain, edition-2024 workspace metadata, strict lint policy, Cargo.lock, conformance crate, a skill validator checking frontmatter/package references/rule IDs, unit tests for validator/gate logic, and a substantial reusable Rust gate. The reusable gate's existence alone does not make it part of host CI.

Files:
- https://github.com/jelome265/Rustacean/blob/main/Cargo.toml
- https://github.com/jelome265/Rustacean/blob/main/tools/validate_skills.py
- https://github.com/jelome265/Rustacean/blob/main/skills/rust-enterprise-best-practices/scripts/rust-gate.sh
- https://github.com/jelome265/Rustacean/blob/main/skills/rust-enterprise-frameworks/scripts/check_frameworks.py

### F-03 — Supply-chain/PR foundations exist
**Severity:** Informational — strength

Dependabot covers GitHub Actions, pip and Cargo weekly. Existing workflows use full-SHA action pins, job-specific permissions/timeouts and secret scanning. CODEOWNERS, PR template, SECURITY.md and workflow-security auditing are present.

Files:
- https://github.com/jelome265/Rustacean/blob/main/.github/dependabot.yml
- https://github.com/jelome265/Rustacean/blob/main/.github/workflows/ci.yml
- https://github.com/jelome265/Rustacean/blob/main/.github/workflows/security.yml
- https://github.com/jelome265/Rustacean/blob/main/.github/workflows/scorecard.yml
- https://github.com/jelome265/Rustacean/blob/main/SECURITY.md

## Findings requiring action

### F-04 — CodeQL excluded Rust
**Severity:** Major  
**Status:** Fixed in the PR changes; CI and branch-protection verification pending.

Baseline evidence: the CodeQL language matrix contained python and actions only, with a comment explicitly saying Rust was not analysed. GitHub's current documentation lists Rust as a supported CodeQL language: https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-code-scanning

**Remediation:** this PR adds Rust to the CodeQL language matrix and updates the documented check list. This report does not claim the new rust analysis succeeded; PR CI must establish that.

**Owner action:** after a successful run creates the check, confirm codeql / analyze (rust) is required by the intended branch protection/ruleset. The settings could not be inspected through the available integration (HTTP 403).

### F-05 — The strict reusable Rust gate is not invoked by host CI
**Severity:** Major  
**Status:** Reported; requires intentional profile design.

Baseline CI runs formatting, Clippy, workspace tests and rustdoc. The security workflow scans secrets, checks dependency-review and audits Python dependencies; it does not run cargo audit. The reusable rust-gate.sh has stronger preconditions: cargo-nextest, cargo-deny, cargo-audit, cargo-vet, deny.toml, a supply-chain directory, root clippy.toml and the adjacent framework skill policy. These are not all present as root configuration in this skills/conformance repository.

**Do not blindly wire the whole script into CI or add empty placeholder policy files.** First create a genuine conformance fixture/profile that satisfies those policy requirements, or clearly scope the reusable gate as a consumer-project bootstrap gate. In the meantime, this PR adds a real, pinned-version cargo-audit check for this repository's Cargo.lock. CI must run to show its actual result.

### F-06 — Standard issue templates are absent
**Severity:** Minor  
**Status:** Finding; not changed in this PR.

The root .github directory has CODEOWNERS, Dependabot, PR template and workflows but no ISSUE_TEMPLATE directory was found.

**Recommendation:** add bug report and feature request templates requiring reproduction steps, expected/actual behavior, toolchain/environment, acceptance criteria and relevant output. Direct vulnerabilities to SECURITY.md/private reporting rather than encouraging public disclosure of exploit details.

### F-07 — Installation and peer dependencies were ambiguous
**Severity:** Major for portability  
**Status:** Installation guide and peer-link validation added in this PR.

The five skill packages use SKILL.md metadata, but storage under skills/ does not cause automatic Claude Code discovery. Claude Code project-level discovery uses .claude/skills/<skill-name>/SKILL.md; other agent platforms may differ. Some skill references also used root-style peer paths instead of explicit sibling-relative links.

**Remediation:** install all five directories side by side; add INSTALLATION.md, explicit sibling-relative cross-skill links, validator checks and regression tests. Do not claim universal plug-and-play installation for every agent host.

References:
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

### F-08 — No-fake implementation contract was underspecified
**Severity:** Major  
**Status:** New contract added and linked from implementation skill in this PR.

The implementation skill already bans invented requirements, weakened gates and test skipping. It needed explicit rules that a placeholder/stub/no-op/hard-coded success cannot stand in for requested production behavior and that mocks cannot be used as proof of real service integration.

**Remediation:** the contract prohibits fake production paths. Unit tests may use narrow doubles for pure domain logic; integration, contract and end-to-end tests must exercise the actual adapter and a real dependency or controlled official sandbox. If infrastructure is unavailable, report the test as BLOCKED/NOT RUN, not passed.

### F-09 — Skill validation is not proof of behavior enforcement
**Severity:** Major — architectural limitation

The validator checks metadata, package-local references and rule-ID resolution. It cannot prove that a referenced control has a working test, is included in CI, blocks merging, or has a green result. Nor can skill discovery prove that an agent followed its policy.

**Remediation:** maintain an enforcement/evidence matrix mapping every BLOCKER to its enforcement tier, exact command/check, most recent result and any owner-only action. Seeded-violation tests should prove the gates fail when bad inputs/configuration are introduced. Explicitly label human-only controls rather than imply automation.

### F-10 — Forcing every Rust language topic would be a design defect
**Severity:** Advisory

The coverage matrix is valuable as a scope map, not a command to use every language feature in every project. Using a feature without a requirement increases complexity and can add bugs/attack surface. Require a per-topic disposition such as REQUIRED, USED, NOT APPLICABLE or DEFERRED with justification.

Rust async uses Future, async/await and an executor/runtime; JavaScript Promise is not a Rust language primitive. This correction is included in the new execution contract.

Rust async reference: https://rust-lang.github.io/async-book/part-guide/async-await.html

### F-11 — Branch protection is not verified
**Severity:** Major for merge governance  
**Status:** Owner action.

CONTRIBUTING.md enumerates required status checks and says branch protection enforces them. The branch protection API returned 403, so this audit cannot independently confirm required checks are enabled.

**Recommendation:** owner confirms required checks (including Rust CodeQL and Cargo audit), dismiss-stale-review policy, code-owner approval, force-push/deletion restrictions and bypass permissions in GitHub settings.

## Changes included in this PR

1. Add a binding enterprise execution contract: investigate, research, plan, implement, verify and report; prohibit fake production behavior and mock-only integration/E2E evidence.
2. Link that contract from the implementation skill and its definition of done.
3. Add a suite installation guide for Claude Code and caveats for other hosts.
4. Make cross-skill paths explicit and extend the validator/unit tests to catch missing peer-skill files.
5. Enable Rust in CodeQL and update required-check documentation.
6. Add a pinned-version cargo-audit CI job for the root Cargo.lock and update required-check documentation.
7. Record findings and clearly state what remains unverified.

## Verification and limitations

- Remote source/config inspection: completed using the connected GitHub interface.
- Local git clone: attempted; failed because the environment could not resolve github.com.
- Local Python tests, Rust tests, formatting, Clippy, shell lint, CodeQL, cargo audit: NOT RUN during the audit.
- CI for the PR changes: pending until the actual PR head workflows complete.
- Branch protection/rulesets: UNVERIFIED because the API returned 403.
- Runtime integration: not applicable to this repository's skill/conformance scope; it is not a deployed service.

## Primary references

- GitHub CodeQL supported languages: https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-code-scanning
- Agent Skills format/discovery: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Agent Skills best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Rust async book: https://rust-lang.github.io/async-book/part-guide/async-await.html
- RustSec cargo-audit: https://github.com/rustsec/rustsec/tree/main/cargo-audit
