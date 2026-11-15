#!/usr/bin/env python3
"""Keep third-party skills at their latest upstream version.

skills.lock.json maps every third-party skill to its upstream repo + path.
  skills-update.py              check only: list skills whose upstream changed
  skills-update.py --apply      also copy changes into skills/ and ~/.claude/skills
  skills-update.py --apply --only ponytail azure-kubernetes

Every changed skill is scanned with skill-security-auditor before it is applied;
a FAIL blocks it (override with --force after reading the diff).
"""
from __future__ import annotations

import argparse
import filecmp
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOCK = REPO / "skills.lock.json"
LOCAL_SKILLS = REPO / "skills"
INSTALLED = Path.home() / ".claude" / "skills"
REPORT = Path.home() / ".claude" / "cache" / "skill-updates.txt"
AUDITOR = LOCAL_SKILLS / "skill-security-auditor" / "scripts" / "skill_security_auditor.py"
# agents/ holds Codex-only metadata (openai.yaml) that Claude Code does not use
SKIP = [".git", ".DS_Store", "__pycache__", "agents"]
IGNORE = shutil.ignore_patterns(*SKIP)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def version(skill_dir: Path) -> str:
    md = skill_dir / "SKILL.md"
    m = re.search(r'^\s+version:\s*"?([^"\n]+)', md.read_text(errors="ignore"), re.M) if md.exists() else None
    return m.group(1) if m else "-"


def stage(up: Path, name: str, renames: dict[str, str], out: Path) -> Path:
    """Copy an upstream skill and re-apply our local patches, so it compares 1:1 with skills/<name>."""
    dest = out / name
    shutil.copytree(up, dest, ignore=IGNORE)
    local_md = LOCAL_SKILLS / name / "SKILL.md"
    manual_only = local_md.exists() and "disable-model-invocation: true" in local_md.read_text(errors="ignore")
    for md in dest.rglob("*.md"):
        text = md.read_text(errors="ignore")
        if not manual_only:  # we auto-route skills (no "/"); keep the local choice
            text = re.sub(r"^disable-model-invocation:\s*true\s*\n", "", text, flags=re.M)
        for old, new in renames.items():
            text = re.sub(rf"(?<![\w/.-])/{re.escape(old)}(?![\w-])", f"/{new}", text)
        if md == dest / "SKILL.md" and name in renames.values():
            text = re.sub(r"^name:.*$", f"name: {name}", text, count=1, flags=re.M)
        md.write_text(text)
    for lic in (LOCAL_SKILLS / name).glob("LICENSE*"):  # attribution we add locally
        if not (dest / lic.name).exists():
            shutil.copy2(lic, dest / lic.name)
    return dest


def differs(a: Path, b: Path) -> bool:
    cmp = filecmp.dircmp(a, b, ignore=SKIP)
    if cmp.left_only or cmp.right_only or cmp.funny_files:
        return True
    if any(not filecmp.cmp(a / f, b / f, shallow=False) for f in cmp.common_files):
        return True
    return any(differs(a / d, b / d) for d in cmp.common_dirs)


def audit(skill_dir: Path) -> int:
    """0 PASS, 1 FAIL, 2 WARN — skill-security-auditor exit codes."""
    if not AUDITOR.exists():
        return 2
    r = subprocess.run([sys.executable, "-I", str(AUDITOR), str(skill_dir)], capture_output=True, text=True)
    if r.returncode:
        print("\n".join("      " + l for l in r.stdout.splitlines()[-15:]))
    return r.returncode


def install(staged: Path, name: str) -> None:
    for dest in (LOCAL_SKILLS / name, INSTALLED / name):
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(staged, dest)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="install changed skills")
    ap.add_argument("--force", action="store_true", help="install even if the security audit FAILs")
    ap.add_argument("--only", nargs="*", default=[], help="limit to these skill names")
    a = ap.parse_args()

    lock = json.loads(LOCK.read_text())
    changes: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for repo, src in lock["sources"].items():
            wanted = {k: v for k, v in src["skills"].items() if not a.only or k in a.only}
            if not wanted:
                continue
            clone = Path(tmp) / repo.replace("/", "__")
            try:
                git("clone", "-q", "--depth", "1", f"https://github.com/{repo}.git", str(clone))
            except subprocess.CalledProcessError as e:
                print(f"!! {repo}: clone failed: {e.stderr.strip()}")
                continue
            head = git("-C", str(clone), "rev-parse", "HEAD")
            renames = {Path(p).name: k for k, p in src["skills"].items() if Path(p).name != k and p != "."}
            print(f"== {repo} {src['commit'][:7]} -> {head[:7]}")
            applied_all = True
            for name, path in wanted.items():
                up, mine = clone / path, LOCAL_SKILLS / name
                if not (up / "SKILL.md").exists():
                    print(f"   {name:34} REMOVED UPSTREAM ({path}) — check the repo, fix skills.lock.json")
                    applied_all = False
                    continue
                up = stage(up, name, renames, Path(tmp) / "staged")
                if mine.exists() and not differs(up, mine):
                    continue
                line = f"{name:34} {version(mine) if mine.exists() else 'new'} -> {version(up)}"
                changes.append(line)
                print(f"   {line}")
                if not a.apply:
                    continue
                verdict = audit(up)
                if verdict == 1 and not a.force:
                    print(f"   {name:34} BLOCKED by security audit (re-run with --force after review)")
                    applied_all = False
                    continue
                install(up, name)
                print(f"   {name:34} applied{' (audit WARN — review git diff)' if verdict == 2 else ''}")
            if a.apply and applied_all and not a.only:
                src["commit"] = head
    if a.apply:
        lock["checked"] = date.today().isoformat()
        LOCK.write_text(json.dumps(lock, indent=2) + "\n")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("" if a.apply else "\n".join(changes))
    print(f"\n{len(changes)} skill(s) {'updated' if a.apply else 'have upstream updates'}.")
    if changes and not a.apply:
        print("Apply: python3 scripts/skills-update.py --apply   (then review `git diff skills/`)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
