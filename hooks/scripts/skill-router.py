#!/usr/bin/env python3
"""UserPromptSubmit hook: pick the best skills for the prompt, so no "/" is needed.

Scores every ~/.claude/skills/*/SKILL.md (name + description) plus the trigger column
of the "Skill Auto-Routing" tables in ~/.claude/CLAUDE.md against the prompt (TF-IDF
style), and prints the top matches. Hook stdout is added to Claude's context.
Self-test: skill-router.py --test
"""
from __future__ import annotations

import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

CLAUDE = Path.home() / ".claude"
TOP_N = 3
MIN_SCORE = 4.0  # below this nothing is a confident match
RELATIVE_CUTOFF = 0.45  # keep runners-up scoring at least 45% of the best
STOP = set("""a an the and or of to for in on at by with from is are be it this that these those
i me my we you your can could would should will need want please help use using how what why
when where which into about make get do does just also some any all not no new set up like
skill skills claude user""".split())


def stem(w: str) -> str:
    for suf in ("ing", "ed", "es", "s"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def tokens(text: str) -> list[str]:
    return [stem(w) for w in re.findall(r"[a-z0-9][a-z0-9.+#]*", text.lower()) if w not in STOP and len(w) > 1]


def load_docs() -> dict[str, dict[str, float]]:
    """skill -> {token: weight}."""
    docs: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

    def add(skill: str, text: str, weight: float) -> None:
        for t in tokens(text):
            docs[skill][t] += weight

    for md in (CLAUDE / "skills").glob("*/SKILL.md"):
        head = md.read_text(errors="ignore")[:4000]
        fm = head.split("---", 2)[1] if head.startswith("---") else head[:800]
        name = md.parent.name
        desc = re.split(r"DO NOT USE|PREFER .* OVER", fm, flags=re.I)[0]  # negative clauses would mis-route
        desc = re.sub(r"^(name|license|argument-hint|author|version|category):.*$", "", desc, flags=re.M)
        add(name, name.replace("-", " "), 3.0)
        add(name, desc, 1.0)

    claude_md = CLAUDE / "CLAUDE.md"
    if claude_md.exists():
        for line in claude_md.read_text(errors="ignore").splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 2 or set(cells[0]) <= set("-: "):
                continue
            for skill in re.findall(r"`([a-z0-9:-]+)`", " ".join(cells[1:]) + " " + cells[0]):
                if skill in docs:
                    add(skill, re.sub(r"`[^`]*`", "", cells[0]), 2.5)
    return docs


def rank(prompt: str, docs: dict[str, dict[str, float]]) -> list[tuple[str, float]]:
    q = set(tokens(prompt))
    df: dict[str, int] = defaultdict(int)
    for d in docs.values():
        for t in d:
            df[t] += 1
    n = len(docs) or 1
    scores = {
        s: sum(math.log(1 + n / df[t]) * (1 + math.log(d[t])) for t in q if t in d)
        for s, d in docs.items()
    }
    best = sorted(((s, v) for s, v in scores.items() if v >= MIN_SCORE), key=lambda x: -x[1])
    return [(s, v) for s, v in best[:TOP_N] if v >= best[0][1] * RELATIVE_CUTOFF] if best else []


def main() -> int:
    try:
        prompt = json.load(sys.stdin).get("prompt", "")
    except (json.JSONDecodeError, AttributeError):
        return 0
    if prompt.lstrip().startswith("/") or len(tokens(prompt)) < 2:
        return 0  # explicit command or chit-chat
    picks = rank(prompt, load_docs())
    if picks:
        names = ", ".join(f"`{s}`" for s, _ in picks)
        print(f"[skill-router] Best-matching skills for this request: {names}. Load the ones that "
              "truly fit with the Skill tool before answering (also check the routing table in "
              "~/.claude/CLAUDE.md for combos); ignore any that do not fit. Do not ask or announce it.")
    else:
        print("[skill-router] No strong skill match. If the request is non-trivial, check the "
              "routing table in ~/.claude/CLAUDE.md and load fitting skills; otherwise just answer.")
    return 0


def self_test() -> None:
    docs = load_docs()
    cases = {
        "my aks pod is in CrashLoopBackOff and node NotReady": "aks-troubleshooting",
        "write a kyverno policy to block latest image tags": "kubernetes-expert",
        "review this pull request diff": "ponytail-review",
        "grill me on this migration plan": "grilling",
        "our azure bill spiked this month, why": "cost-analysis",
        "design SLOs and error budget burn rate alerts": "slo-architect",
    }
    for prompt, want in cases.items():
        got = [s for s, _ in rank(prompt, docs)]
        assert want in got, f"{prompt!r}: expected {want}, got {got}"
    print(f"ok: {len(cases)} cases, {len(docs)} skills indexed")


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        self_test()
    else:
        sys.exit(main())
