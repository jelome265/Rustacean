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

Several agents read the same project and user directories: `.agents/skills` in the project
and `~/.agents/skills` for the user. This is the most portable install target. Confirmed in
official documentation for Codex, Gemini CLI, OpenCode, Zed, and Codebuff/Freebuff. The
installer's `codex` target uses it, and so do the Freebuff and Muse entries. Muse Code's
project scope skips skills in an untrusted workspace (see below).

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

### Google Antigravity: codelab

- Workspace: `<workspace>/.agent/skills/` (note: singular `.agent`)
- Global: `~/.gemini/antigravity/skills/`
- Source: Google's Antigravity skills codelab (`codelabs.developers.google.com/getting-started-with-antigravity-skills`),
  retrieved in several language versions with the same paths.
- Unverified claim: a third-party page says Antigravity CLI succeeds Gemini CLI, and that
  consumer Gemini CLI access ends in June 2026. Not verified. If true, the paths for the
  successor CLI may differ from the IDE paths above.

### Zed (Zed Agent): official

- Global: `~/.agents/skills/`. Project: `.agents/skills/`.
- Skills apply to the Zed Agent only. External agents (Claude Code, Codex) configure their own.
- Project skills load only from trusted worktrees.
- Each skill must be a direct child of the skills root. The folder name must equal `name`.
- Source: https://zed.dev/docs/ai/skills

### Cursor: official

- Project: `.cursor/skills/`, searched recursively for nested `SKILL.md` files
- User: `~/.cursor/skills/`
- Source: https://cursor.com/docs/skills
- Notes: Cursor's example layout uses `.agents/`, but the discovery of `.agents/skills` by
  Cursor was not confirmed here, so the installer does not target it for Cursor.
  Cursor documents no mechanism for one skill to load another. Cross-skill references are
  read as file paths, which is why the installer keeps the five skills together.

### GitHub Copilot (VS Code agent): third-party

- Project: `.github/skills/`. User: `~/.copilot/skills/`.
- Third-party summaries also say VS Code recognises `.claude/skills/` and `.agents/skills/`.
  This was not confirmed against VS Code's own documentation.
- Preferred install route: `gh skill` in GitHub CLI 2.90.0 (public preview, April 2026). It
  installs into the correct directory for the host, with `--agent` and `--scope` flags, and
  supports Copilot, Claude Code, Cursor, Codex, Gemini CLI and Antigravity. Source:
  https://github.blog/changelog/2026-04-16-manage-agent-skills-with-github-cli/
- `gh skill publish --dry-run` validates against the Agent Skills specification. That check
  has not been run against this suite.
- Not verified: whether `gh skill install OWNER/REPO <skill>` installs a skill from a
  monorepo subdirectory such as `skills/rust-enterprise-harden`. The installer does not
  depend on it.

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

- Newer Kimi Code docs: `~/.kimi-code/skills/` (moved with `KIMI_CODE_HOME`), `.kimi-code/skills/`
  in projects, and also `~/.agents/skills/` and `.agents/skills/`. Built-in skills have the
  lowest priority.
- Older kimi-cli docs: `~/.kimi/skills/` and `.kimi/skills/`. Also `kimi --skills-dir <path>`.
- Sources: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html (newer) and
  https://moonshotai.github.io/kimi-cli/en/customization/skills (older)
- Third-party aggregators say Kimi also reads `.claude/skills/`. Not confirmed.
- The installer refuses this target unless `--accept-conflicting` is given. Use `--dest-dir`
  with the directory your installed version reads.

### Z.AI ZCode: none

- Official Z.AI ZCode documentation (`docs.z.ai/devpack/tool/zcode.md`) covers installation
  and model configuration. No skill directory is documented.
- Third-party ZCode skill packages are installed by copying into an unnamed "agent skills
  directory". No path is given.
- The installer refuses this target.
- **Not the same product.** `simonyos/Z-CODE` is an unrelated open-source terminal agent. It
  reads `.zcode/skills/` and `~/.config/zcode/skills/`. Do not use those paths for ZCode.

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

- Run each agent's listing command after an install and record the result: Codex, Gemini
  CLI, OpenCode, Zed, Cursor, Claude Code, Freebuff, Muse, Antigravity, and Copilot.
- Confirm the Kimi path on a current release.
- Retrieve the official Muse Code and Antigravity CLI skill documentation.
- Check whether a ZCode skill directory exists in a current build.
