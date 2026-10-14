# Installing the Rustacean skill suite

Rustacean is a suite of five cooperating Agent Skills, not one monolithic skill. The implementation, hardening, audit, and framework skills depend on shared rules and peer resources. Install the complete suite together to preserve those dependencies.

## Claude Code project-level installation

From your target project root, obtain this repository and copy these five directories into the target project's .claude/skills/ directory, preserving their names and contents:

- rust-enterprise-best-practices
- rust-enterprise-implement
- rust-enterprise-harden
- rust-enterprise-audit
- rust-enterprise-frameworks

Each installed directory must include its SKILL.md and any references/ and scripts/ folders. All five skills should be siblings under .claude/skills/.

For a user-level installation, place all five directories side by side under ~/.claude/skills/ instead. User-level installation makes them available to multiple projects; project-level installation keeps them scoped to one repository.

## Other agent platforms

Do not assume every agent discovers skills from the same directory. Consult the selected platform's current documentation for accepted Agent Skills format, discovery path, package/upload requirements, tool access, and execution capabilities. Valid SKILL.md metadata does not guarantee the host discovers the file or can execute its scripts.

Review the skill source and scripts before installing. Instructions and executable helpers influence agent behaviour and must remain within your project trust boundary.

## Validate after installation

1. Confirm all five SKILL.md files exist, with YAML frontmatter names matching their directory names.
2. Confirm all peer-skill links and local reference files resolve.
3. Run the repository validator and tests for the exact commit being installed.
4. Ask the target agent to name the skills it discovered and the tools it can actually use. Run a small controlled task and inspect its evidence.
5. Do not equate skill discovery with policy compliance. Skills guide behavior; compiler/lint/test/CI/platform controls enforce only the specific properties they actually check.

Official references:
- Agent Skills format and discovery: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Agent Skills authoring best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
