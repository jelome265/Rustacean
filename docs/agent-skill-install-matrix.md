# Agent skill installation matrix

Research date: 2026-10-14. This records where each coding agent discovers `SKILL.md`
skills, how strong the evidence is, where sources disagree, and what was not verified.
The machine-readable form is `tools/agent_skill_targets.json`, which the installer uses.

## How to read the evidence grades

| Grade | Meaning |
|---|---|
| official | Vendor product documentation, retrieved and read |
| codelab | Vendor tutorial (for example a Google Codelab), retrieved and read |
| third-party | Secondary source (blog, package README, aggregator). Confirm on the installed product |
| conflicting | Vendor sources disagree on the paths, usually across product versions |
| none | No documented skill directory was found |

Each path below was taken from the cited source. None of these agents was installed and run
in this research. The discovery paths are therefore unverified on a running product until
someone checks them. Run each agent's own listing command after installing (see the
installation guide).

## The shared location: `.agents/skills`

As of 2026-10-14, current official product documentation explicitly lists project-level
`.agents/skills` for Codex CLI, OpenCode, Gemini CLI, Zed, Cursor, VS Code Copilot,
Kimi Code CLI, and Antigravity. This makes it the installer default for those products where
that current path is documented. Freebuff and Muse also list it, but their discovery evidence
is weaker (see their individual entries).

The user-level path is not equally universal: use the paths listed for each agent below.
Antigravity, for example, documents product-specific global paths. A path appearing in a
vendor document is source evidence, not proof that a particular installed version discovered
these skills; runtime discovery remains unverified in this repository.

## Agent-by-agent findings

### Claude Code: official

- Project: `<repo>/.claude/skills/<name>/SKILL.md`
- User: `~/.claude/skills/<name>/SKILL.md`
- Source: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview

Other agents also read these `.claude/skills` paths (OpenCode and Codebuff/Freebuff), so this
location is the most widely shared alongside `.agents/skills`.

### OpenAI Codex CLI: official

- Repository: scans `.agents/skills` in each directory from the working directory up to the
  repository root.
- User: `$HOME/.agents/skills`. Admin: `/etc/codex/skills`. Built-in skills ship with Codex.
- Source: https://developers.openai.com/codex/skills (build-skills page, retrieved in English,
  French and Portuguese versions; the paths match)

**Important source discrepancy.** The current Codex skills overview documents
`.agents/skills` for repository discovery, `$HOME/.agents/skills` for user discovery,
and `/etc/codex/skills` for administrator discovery:
https://developers.openai.com/codex/skills

However, the official `openai/codex` skill-creator sample still recommends creating skills
under `$CODEX_HOME/skills`, defaulting to `~/.codex/skills` when that variable is unset:
https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/SKILL.md

These official sources disagree about the destination to use. This installer follows the
current skills overview's documented discovery locations, but we must not claim that
`~/.codex/skills` is universally unused. Verify discovery in the installed Codex version
after installing. `AGENTS.md` remains a separate repository-instruction file, not a skill.

### OpenCode: official

- Project: `.opencode/skills/<name>/SKILL.md`, and also `.claude/skills/` and
  `.agents/skills/`
- Global: `~/.config/opencode/skills/`, and also `~/.claude/skills/` and `~/.agents/skills/`
- Sources: https://opencode.ai/docs/skills and https://opencode.ai/v2/docs/skills/
- Notes: the directory name must match the skill name. The v2 docs add a `skills` array in
  `opencode.json` for extra source directories, and per-agent `skill` permissions.

### Gemini CLI: official

- Workspace: `.gemini/skills/` or `.agents/skills/`
- User: `~/.gemini/skills/` or `~/.agents/skills/`
- Commands: `gemini skills link <path>` (symlink), `gemini skills install <git-url-or-path>`,
  `gemini skills enable|disable`, `/skills reload`
- Sources: https://geminicli.com/docs/cli/skills/ and https://geminicli.com/docs/cli/creating-skills/

### Google Antigravity: official

- Project: `.agents/skills/<skill-folder>/`. The old `.agent/skills/` path is supported for
  backward compatibility.
- Antigravity app and IDE user scope: `~/.gemini/config/skills/<skill-folder>/`
- Antigravity CLI user scope: `~/.gemini/antigravity-cli/skills/<skill-folder>/`
- Source: https://www.antigravity.google/docs/skills
- CLI migration/source details: https://www.antigravity.google/docs/cli/gcli-migration
- The registry defaults to the shared project path and the app/IDE user path. For CLI user
  scope, explicitly pass `--dest-dir ~/.gemini/antigravity-cli/skills`. The installer does
  not guess which Antigravity surface you run.

### Zed (Zed Agent): official

- Global: `~/.agents/skills/`. Project: `.agents/skills/`.
- Skills apply to the Zed Agent only. External agents (Claude Code, Codex) configure their own.
- Project skills load only from trusted worktrees.
- Each skill must be a direct child of the skills root. The folder name must equal `name`.
- Source: https://zed.dev/docs/ai/skills

### Cursor: official

- Project: `.agents/skills/` and `.cursor/skills/`; Cursor also searches nested `SKILL.md`
  files under supported skill roots.
- User: `~/.agents/skills/` and `~/.cursor/skills/`
- Source: https://cursor.com/docs/skills
- The current official docs explicitly document `.agents/skills`; the registry now defaults
  to that shared path. Cross-skill references are file paths, so the installer keeps all five
  skills as siblings. Cursor discovery in an installed runtime is still unverified here.

### GitHub Copilot (VS Code agent): official

- Project: `.github/skills/`, `.claude/skills/`, and `.agents/skills/`.
- User: `~/.copilot/skills/`, `~/.claude/skills/`, and `~/.agents/skills/`.
- Official VS Code source: https://github.com/microsoft/vscode-docs/blob/main/docs/agent-customization/agent-skills.md
- The installer defaults to the shared `.agents/skills` path; the native Copilot paths remain
  available as alternatives.
- GitHub CLI also provides host-aware `gh skill install` with `--agent` and `--scope`:
  https://cli.github.com/manual/gh_skill_install. This installer does not depend on it.
- The `gh skill publish --dry-run` validator has not been run against this suite.
- Not verified: whether `gh skill install OWNER/REPO <skill>` installs from a monorepo
  subdirectory such as `skills/rust-enterprise-harden`.

### Freebuff (Codebuff): third-party (paths from Codebuff's official docs)

- Project: `.agents/skills/`, and also `.claude/skills/`
- User: `~/.agents/skills/`, and also `~/.claude/skills/`
- Project skills take priority over global skills with the same name.
- Freebuff also reads `AGENTS.md` natively. A repository's `AGENTS.md` is an instruction
  file and is not a skill.
- Sources: https://www.codebuff.com/docs/tips/skills (Codebuff skills page, official). The
  claim that Freebuff's CLI lists skills from `.agents/skills` comes from the upstream
  CodebuffAI/freebuff documentation index (docsearch.algolia.com). It is not on the skills page
  itself, so it is unconfirmed on the installed Freebuff version. A third-party repository,
  leo-gravity/codebuff, reproduces the README. It is not the upstream project and is not cited
  as evidence.

### Meta Muse Code: third-party

- User: `~/.agents/skills/` and `~/.config/muse/skills/<name>/SKILL.md`
- Project: `.agents/skills/` or `.claude/skills/` at the workspace root
- **Security note.** Project skills are skipped unless the workspace is trusted. Muse reports
  `project-skills-untrusted` and needs `muse skills list --source project --trust-workspace`.
  Trust is a decision for the user, and the installer does not grant it.
- Import: `muse skills import --from claude --dry-run` can import existing Claude skills.
- Sources: https://www.withone.ai/blog/muse-code-skills-not-mcp/md (command output shown) and
  the agentic-workstation v1.4.0 release notes.
- Not verified: the official reference at https://dev.meta.ai/docs/muse-code was not
  retrieved. Treat these paths as unconfirmed until `muse skills list` shows the suite.

### Kimi Code CLI (Moonshot): conflicting

- Current Kimi Code CLI docs support project `.agents/skills/` and `.kimi-code/skills/`,
  plus user `~/.agents/skills/` and `~/.kimi-code/skills/`. `KIMI_CODE_HOME` changes the
  Kimi-specific directory.
- Older kimi-cli docs describe `~/.kimi/skills/`, `.kimi/skills/`, and
  `kimi --skills-dir <path>`.
- Sources: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html (current)
  and https://moonshotai.github.io/kimi-cli/en/customization/skills (legacy)
- Because these official docs describe different generations and paths, the registry keeps
  this target at evidence grade `conflicting`. It defaults to the current shared
  `.agents/skills` path but refuses to write until `--accept-conflicting` is passed, or a
  `--dest-dir` is supplied after verifying the installed version.
- Third-party claims about `.claude/skills/` were not confirmed.

### Z.AI ZCode: conflicting

- Cited vendor pages: https://zcode.z.ai/en/docs/skill and https://zcode.z.ai/en/docs/qa.
  Neither could be retrieved during the 2026-10-14 check, so the paths they are cited for
  are unconfirmed. The registry does not grade this entry as official.
- Candidate project paths: `.zcode/skills/<name>/SKILL.md` (cited vendor page; also the path of
  the unrelated open-source project simonyos/Z-CODE) and `.claude/skills/<name>/SKILL.md`
  (third-party sources say ZCode reads the Claude plugin format and skill location).
- Candidate user paths: `~/.zcode/skills/<name>/SKILL.md` (a third-party Chinese-language guide)
  and `~/.claude/skills/` (third-party).
- Other third-party evidence: a `dev-skills` package ships a `.zcode-plugin/` manifest alongside
  `.claude-plugin/`. The `agent-config` project lists ZCode config at `.zcode/config.json` and
  `~/.zcode/cli/config.json`. These support a Claude-compatible plugin model, not a specific
  skill directory.
- The installer refuses this target unless `--accept-conflicting` is given. Confirm discovery on
  your installed version before relying on it. Ask ZCode to list its skills, or use `--dest-dir`.
- **Not the same product.** `simonyos/Z-CODE` is an unrelated open-source terminal agent. Do not use
  its paths for Z.AI ZCode without confirming them.

## Tools that generate guidance files rather than reading SKILL.md

Some tools generate rule files for many agents rather than installing SKILL.md packages.
These were seen only in the documentation of the `skillpack` generator (docs.rs,
retrieved 2026-10-14). They are listed so that nobody assumes skill discovery where there is
none. Each agent's own documentation was not checked.

| Agent | Rule file the generator writes |
|---|---|
| Windsurf | Rules and `AGENTS.md` |
| Aider | Conventions file |
| Cline | `.clinerules/` |
| Roo Code | Rules |
| Kilo Code | `.kilocode/rules/` |
| Goose | Hints file |
| GitHub Copilot | `.github/copilot-instructions.md` |

## Cross-cutting rules for this repository

1. Install all five skills together, as siblings, under one root. Their relative links
   (`../rust-enterprise-*/SKILL.md`) resolve only then. The installer enforces this.
2. The installed copy is a snapshot. Re-run the installer after pulling a new version.
   Symlink mode (`--mode symlink`) tracks the checkout instead.
3. Installing a skill does not prove the agent follows it. The guide's verification steps
   check discovery, not compliance.
4. A project-scope install is committed to the repository and shared with the team. Review it
   the way you review code. A user-scope install applies to every project on the machine.

## Open items

- Run each agent's discovery/listing command after an install and record the result. None of
  the supported agents has been installed and exercised as part of this repository change.
- Verify Kimi Code CLI's shared-path behavior against the exact installed version before
  bypassing the installer's conflict guard.
- Retrieve the official Muse Code skills reference; the paths remain third-party evidence.
- Verify Antigravity app/IDE and CLI user-level paths separately in running installations.
- Capture a ZCode import/discovery run and verify that its installed version reads the cited
  `.zcode/skills` locations, and that `.claude/skills` is or is not also read.
