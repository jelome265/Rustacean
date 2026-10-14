#!/usr/bin/env python3
"""Install the Rustacean skill suite into a coding agent's skill directory.

The five skills reference one another by relative path (../rust-enterprise-*/SKILL.md),
so they are always installed together, as siblings, and verified together.

Behaviour:
  * Dry-run by default. Nothing is written unless --apply is given.
  * The source suite is validated first (tools/validate_skills.py). A failure stops the run.
  * The complete plan is computed before any write. A conflict with a different existing
    copy stops the run unless --force is given, so no partial suite is left behind.
  * After writing, every installed skill is compared with the source by content hash,
    and every peer-skill link is checked to resolve inside the destination.
  * Targets come from tools/agent_skill_targets.json. A target whose evidence is 'none'
    is refused. A 'conflicting' target is refused unless --accept-conflicting is given.

Examples:
  python3 tools/install_skills.py --list
  python3 tools/install_skills.py --agent codex --scope project --project-root ~/src/my-app
  python3 tools/install_skills.py --agent codex --scope project --project-root ~/src/my-app --apply

Exit codes: 0 success or dry-run, 1 refused or verification failed, 2 usage error.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import sys

TOOLS_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent
DEFAULT_SOURCE = REPO_ROOT / "skills"
TARGETS_FILE = TOOLS_DIR / "agent_skill_targets.json"

SUITE = [
    "rust-enterprise-best-practices",
    "rust-enterprise-implement",
    "rust-enterprise-harden",
    "rust-enterprise-audit",
    "rust-enterprise-frameworks",
]
IGNORED_NAMES = {"__pycache__", ".DS_Store"}


def load_validator():
    """Load tools/validate_skills.py so the installer uses the same rules as CI."""
    spec = importlib.util.spec_from_file_location("validate_skills", TOOLS_DIR / "validate_skills.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_targets():
    with TARGETS_FILE.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return {target["agent"]: target for target in data["targets"]}


def tree_digest(root):
    """Stable SHA-256 over relative paths and file contents, ignoring cache files."""
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file() and not (set(p.parts) & IGNORED_NAMES)):
        digest.update(str(path.relative_to(root)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def check_source(source):
    """Return a list of problems with the source suite. Empty means the suite is valid."""
    problems = []
    for name in SUITE:
        if not (source / name / "SKILL.md").is_file():
            problems.append(f"source suite is missing {name}/SKILL.md")
    if problems:
        return problems
    validator = load_validator()
    import io
    import contextlib

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = validator.main(str(source))
    if code != 0:
        problems.append("source suite failed validate_skills.py:\n" + buffer.getvalue().strip())
    return problems


def resolve_destination(target, scope, project_root, home, dest_dir):
    if dest_dir:
        return pathlib.Path(dest_dir).expanduser().resolve()
    entries = target["scope"][scope]
    if not entries:
        raise ValueError(f"{target['label']} has no documented {scope} skill directory")
    base = project_root if scope == "project" else home
    return (base / entries[0]).resolve()


def plan(source, dest_root, mode, force):
    """Return (actions, problems). Each action is (name, operation)."""
    actions = []
    problems = []
    for name in SUITE:
        src = source / name
        dst = dest_root / name
        if not dst.exists() and not dst.is_symlink():
            actions.append((name, "create"))
            continue
        if dst.is_symlink():
            problems.append(f"{dst} already exists as a symlink; remove it or choose another destination")
            continue
        if tree_digest(src) == tree_digest(dst):
            actions.append((name, "unchanged"))
        elif force:
            actions.append((name, "replace"))
        else:
            problems.append(f"{dst} exists and differs from the source; re-run with --force to replace it")
    return actions, problems


def apply_plan(source, dest_root, actions, mode):
    dest_root.mkdir(parents=True, exist_ok=True)
    for name, operation in actions:
        if operation == "unchanged":
            continue
        src = source / name
        dst = dest_root / name
        if operation == "replace":
            shutil.rmtree(dst)
        if mode == "symlink":
            os.symlink(src, dst, target_is_directory=True)
        else:
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*IGNORED_NAMES))


def verify(source, dest_root, mode):
    """Return a list of verification failures. Empty means the installed suite is correct."""
    failures = []
    validator = load_validator()
    for name in SUITE:
        installed = dest_root / name
        if not (installed / "SKILL.md").is_file():
            failures.append(f"{name}/SKILL.md is missing after install")
            continue
        if tree_digest(installed) != tree_digest(source / name):
            failures.append(f"{name} content differs from the source after install")
        for match in validator.PEER_SKILL_RE.finditer((installed / "SKILL.md").read_text(encoding="utf-8")):
            peer = match.group(2)
            if not (dest_root / peer / "SKILL.md").is_file():
                failures.append(f"{name} links to {peer}, which is not installed beside it")
    return failures


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list", action="store_true", help="list supported agents and their evidence grades")
    parser.add_argument("--agent", help="agent name from agent_skill_targets.json")
    parser.add_argument("--scope", choices=["project", "user"], default="project")
    parser.add_argument("--project-root", default=".", help="project directory for project scope")
    parser.add_argument("--home", default=str(pathlib.Path.home()), help="home directory for user scope")
    parser.add_argument("--dest-dir", help="explicit skill directory (overrides the registry)")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE), help="directory containing the five skill folders")
    parser.add_argument("--mode", choices=["copy", "symlink"], default="copy")
    parser.add_argument("--apply", action="store_true", help="write files; without this the run is a dry run")
    parser.add_argument("--force", action="store_true", help="replace existing copies that differ from the source")
    parser.add_argument("--accept-conflicting", action="store_true",
                        help="allow a target whose vendor documentation conflicts; verify the path yourself")
    args = parser.parse_args(argv)

    targets = load_targets()
    if args.list:
        for name, target in sorted(targets.items()):
            print(f"{name:<14} {target['evidence']:<12} {target['label']}")
        return 0
    if not args.agent:
        print("install_skills: --agent is required (use --list to see choices)", file=sys.stderr)
        return 2
    if args.agent not in targets:
        print(f"install_skills: unknown agent '{args.agent}'", file=sys.stderr)
        return 2

    target = targets[args.agent]
    if target["evidence"] == "none":
        print(f"REFUSED: {target['label']} has no documented skill directory. {target['notes']}")
        return 1
    if target["evidence"] == "conflicting" and not args.accept_conflicting:
        print(f"REFUSED: {target['label']} vendor documentation conflicts on skill paths. "
              f"Verify on your installed version, then re-run with --accept-conflicting or --dest-dir.")
        return 1

    source = pathlib.Path(args.source).expanduser().resolve()
    problems = check_source(source)
    if problems:
        print("REFUSED: source suite is not valid:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    try:
        dest_root = resolve_destination(target, args.scope, pathlib.Path(args.project_root).expanduser().resolve(),
                                        pathlib.Path(args.home).expanduser().resolve(), args.dest_dir)
    except ValueError as exc:
        print(f"REFUSED: {exc}")
        return 1

    actions, problems = plan(source, dest_root, args.mode, args.force)
    print(f"agent: {target['label']} ({target['evidence']})")
    print(f"destination: {dest_root}")
    print(f"mode: {args.mode}")
    for name, operation in actions:
        print(f"  {operation:<10} {name}")
    if problems:
        print("REFUSED: nothing was written.")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    if not args.apply:
        print("DRY RUN: nothing written. Re-run with --apply to install.")
        return 0

    apply_plan(source, dest_root, actions, args.mode)
    failures = verify(source, dest_root, args.mode)
    if failures:
        print("VERIFICATION FAILED:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("INSTALLED AND VERIFIED: content hashes match the source and all peer links resolve.")
    print("Restart the agent, then confirm which skills it discovered (see skills/INSTALLATION.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
