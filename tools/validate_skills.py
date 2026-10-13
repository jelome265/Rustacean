#!/usr/bin/env python3
"""Validate skill packages for CI.

Checks for every skills/<name>/SKILL.md:
  1. Frontmatter exists, parses as YAML, and has name and description.
  2. name equals the folder name and matches ^[a-z0-9-]{1,64}$.
  3. description is 1..1024 characters and contains no unquoted ': ' that would break YAML.
  4. Every relative file reference in SKILL.md (`references/...`, `scripts/...`) exists.
  5. Every rule ID cited anywhere in the package resolves to a defined rule ID.

Exit codes: 0 pass, 1 violations, 2 usage or missing dependency.
Requires PyYAML (pip install pyyaml). A missing dependency is an error, never a skip.
"""
import pathlib
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    print("validate_skills: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

RULE_PREFIXES = "BP|SEC|RES|OBS|OPS|BLD|CTR|DB|CFG|IMP|AUD|HRD|FW"
DEF_RE = re.compile(rf"\*\*((?:{RULE_PREFIXES})-[A-Z]*-?\d+[A-Z]?(?:-\d+)?)")
CITE_RE = re.compile(rf"\b((?:{RULE_PREFIXES})-[A-Z]{{1,8}}(?:-[A-Z0-9]{{1,8}})?-?\d{{1,3}}[A-Z]?)\b")
REF_RE = re.compile(r"`((?:references|scripts)/[A-Za-z0-9_./-]+)`|\]\(((?:references|scripts)/[A-Za-z0-9_./-]+)\)")
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")


def main(root):
    skills_root = pathlib.Path(root)
    skill_files = sorted(skills_root.glob("*/SKILL.md"))
    if not skill_files:
        print(f"validate_skills: no */SKILL.md under {skills_root}", file=sys.stderr)
        return 2

    violations = []
    all_text = {}
    for path in sorted(skills_root.rglob("*")):
        if path.is_file() and path.suffix in {".md", ".toml", ".py", ".sh", ".rs"}:
            all_text[path] = path.read_text(encoding="utf-8", errors="replace")

    defined = set()
    for text in all_text.values():
        defined.update(DEF_RE.findall(text))

    for skill in skill_files:
        folder = skill.parent
        text = skill.read_text(encoding="utf-8")
        m = FM_RE.match(text)
        if not m:
            violations.append(f"{skill}: missing frontmatter")
            continue
        try:
            fm = yaml.safe_load(m.group(1))
        except yaml.YAMLError as exc:
            violations.append(f"{skill}: frontmatter does not parse: {exc}")
            continue
        if not isinstance(fm, dict) or "name" not in fm or "description" not in fm:
            violations.append(f"{skill}: frontmatter needs name and description")
            continue
        name = str(fm["name"])
        if name != folder.name:
            violations.append(f"{skill}: name '{name}' does not equal folder '{folder.name}'")
        if not NAME_RE.match(name):
            violations.append(f"{skill}: name '{name}' must match ^[a-z0-9-]{{1,64}}$")
        desc = str(fm["description"])
        if not (1 <= len(desc) <= 1024):
            violations.append(f"{skill}: description length {len(desc)} outside 1..1024")

        for ref_match in REF_RE.finditer(text):
            rel = ref_match.group(1) or ref_match.group(2)
            if not (folder / rel).exists():
                violations.append(f"{skill}: referenced file does not exist: {rel}")

    for path, text in all_text.items():
        for cited in set(CITE_RE.findall(text)):
            if cited not in defined:
                violations.append(f"{path}: rule ID '{cited}' is cited but never defined")

    print(f"validated {len(skill_files)} skill(s); {len(defined)} rule IDs defined")
    if violations:
        print(f"VALIDATION FAIL: {len(violations)} violation(s)")
        for v in violations:
            print(f"  - {v}")
        return 1
    print("VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    sys.exit(main(target))
