# Installing the Rustacean skill suite

The Rustacean suite is five skills that refer to one another. Install all five together,
as siblings, into the same skills directory. Installing one of them alone breaks its
references to the others, and the installer refuses to install a partial suite.

| Skill | Purpose |
|---|---|
| rust-enterprise-best-practices | Normative rulebook; the other four cite its rule IDs |
| rust-enterprise-implement | Build procedure for new Rust code |
| rust-enterprise-harden | Security, resilience, observability and operations controls |
| rust-enterprise-audit | Read-only security and logic audit procedure |
| rust-enterprise-frameworks | Approved framework stack and its enforcement |

## Quick start

From a clone of this repository:

```bash
# See the supported agents and how well each path is documented
python3 tools/install_skills.py --list

# Dry run: shows the plan and writes nothing
python3 tools/install_skills.py --agent codex --project-root /path/to/your/project

# Install and verify
python3 tools/install_skills.py --agent codex --project-root /path/to/your/project --apply
```

The installer validates the source suite, plans the whole install, and then copies the five
skills. Afterwards it compares each installed skill with the source by content hash, and it
checks that every peer link resolves. Any failure is reported and exits non-zero.

### Options

| Option | Effect |
|---|---|
| `--scope project` (default) | Install into the project. Use `--project-root` to set the project |
| `--scope user` | Install for every project on this machine. Use `--home` to change the home directory |
| `--dest-dir PATH` | Install to an explicit directory, overriding the registry |
| `--mode symlink` | Link to this checkout instead of copying. Changes to the checkout take effect immediately |
| `--force` | Replace an existing copy that differs from the source. Without it, a differing copy stops the install |
| `--accept-conflicting` | Allow an agent whose documentation disagrees about paths. Verify the path first |

An install that finds an existing identical copy leaves it unchanged. A differing copy stops
the run before anything is written, so a partial suite is never left behind.

## Which agent reads which directory

The installer's registry is `tools/agent_skill_targets.json`. The table below gives the
default target for each agent. The research behind each entry, with sources and the open
questions, is in `docs/agent-skill-install-matrix.md`.

| Agent | `--agent` | Default project directory | Default user directory | Evidence |
|---|---|---|---|---|
| Claude Code | `claude-code` | `.claude/skills` | `~/.claude/skills` | official |
| OpenAI Codex CLI | `codex` | `.agents/skills` | `~/.agents/skills` | official |
| OpenCode | `opencode` | `.opencode/skills` | `~/.config/opencode/skills` | official |
| Gemini CLI | `gemini-cli` | `.gemini/skills` | `~/.gemini/skills` | official |
| Zed (Zed Agent) | `zed` | `.agents/skills` | `~/.agents/skills` | official |
| Google Antigravity | `antigravity` | `.agent/skills` | `~/.gemini/antigravity/skills` | codelab |
| Cursor | `cursor` | `.cursor/skills` | `~/.cursor/skills` | official |
| GitHub Copilot | `copilot` | `.github/skills` | `~/.copilot/skills` | third-party |
| Freebuff | `freebuff` | `.agents/skills` | `~/.agents/skills` | third-party |
| Meta Muse Code | `muse` | `.agents/skills` | `~/.agents/skills` | third-party |
| Kimi Code CLI | `kimi` | conflicting | conflicting | conflicting |
| Z.AI ZCode | `zcode` | none documented | none documented | none |

Use `--dest-dir` for any agent whose path differs on your installed version. A target that
is refused (`zcode`) or marked conflicting (`kimi`) needs you to confirm the directory
yourself.

Many agents read `.agents/skills`, so a single install there covers several of them. Confirm
discovery in each agent you use, because the agents' documentation is not uniform.

**Codex-specific caveat:** the installer follows the current Codex skills overview: project
skills in `.agents/skills` and user skills in `~/.agents/skills`. The official
`openai/codex` skill-creator sample still suggests `$CODEX_HOME/skills` (default
`~/.codex/skills`) as a creation destination. These official sources conflict, so this is
not proof that the older path is universally unused. See
[the research matrix](../docs/agent-skill-install-matrix.md#openai-codex-cli-official) and
verify the skills list in the Codex version you actually run.

## Confirm discovery

Installing a skill does not prove that the agent discovered it. After each install:

1. Restart the agent, or start a new session. Some agents load skills only at startup.
2. Ask the agent to list the skills it can see. The five names above should all appear.
3. Use the agent's own listing command where one exists:
   - Gemini CLI: `/skills list`
   - Muse Code: `muse skills list --source project` (and `--trust-workspace` for project skills)
   - Zed: AI > Skills in the settings editor
   - Claude Code: type `/` to see skill entries
   - Codex: ask the agent which skills it can see; the Codex docs do not document a listing command
4. Run a small task that should trigger a skill, and check that the agent cites its rules.

If an agent does not list the skills, check the path against the table, then against that
agent's current documentation. Do not treat a valid `SKILL.md` as proof of discovery.

## Security before you install

- A skill is executable guidance. It shapes what the agent does, and some skills include
  scripts. Read the source before installing, and install from a commit you have reviewed.
- A project-scope install is committed to the repository and shared with everyone who clones
  it. Review it the same way you review code.
- A user-scope install applies to every project on the machine. Use it only for skills you
  trust in all of them.
- Muse Code skips project skills in an untrusted workspace. Trust a workspace deliberately, not
  by default.
- Installing these skills does not enforce them. Enforcement is in the compiler, lints, tests,
  CI and repository rulesets. Read `AUDIT_REPORT.md` for what is and is not enforced in this
  repository.

## Verify the installed copy

```bash
python3 tools/validate_skills.py skills                 # validates the source suite
python3 -m unittest discover -s tests/python -v        # tests the installer and the validator
```

The installer's own verification runs after every `--apply`. To check an install by hand,
compare the installed skills with the source:

```bash
python3 - <<'EOF'
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location("i", "tools/install_skills.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
dest = pathlib.Path("PATH/TO/INSTALLED/SKILLS")
for name in m.SUITE:
    print(name, m.tree_digest(dest / name) == m.tree_digest(pathlib.Path("skills") / name))
EOF
```

Replace `PATH/TO/INSTALLED/SKILLS` with the directory you installed into.

## Updating

Re-run the installer after pulling a new version. Use `--force` only when you have checked that
local edits are not needed. Symlink installs (`--mode symlink`) follow the checkout without
re-running.

## Removing

Delete the five directories, or remove the symlinks. The installer does not delete anything.
