# claude-config

My Claude Code setup: global `CLAUDE.md` (with skill auto-routing), skills, agents, commands and rules.

## Install

```bash
git clone <this-repo> ~/claude-config && cd ~/claude-config
for d in agents commands contexts hooks rules skills scripts templates examples mcp-configs tests; do
  mkdir -p ~/.claude/$d && cp -R $d/. ~/.claude/$d/
done
cp -n CLAUDE.md AGENTS.md ~/.claude/        # -n: never overwrite your own
```

`settings.example.json` has the working hook wiring (merge its `hooks` block into `~/.claude/settings.json`; needs `jq`).

## Third-party skills (MIT, see upstream licenses)

- [mattpocock/skills](https://github.com/mattpocock/skills) — `mp-tdd` / `mp-code-review` are renamed copies
- [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) — installed as `cf-security-audit`
- [dietrichgebert/ponytail](https://github.com/dietrichgebert/ponytail)
