# claude-config

My Claude Code setup: global `CLAUDE.md` (with skill auto-routing), skills, agents, commands and rules.

## Install

```bash
git clone https://github.com/OktaySavdi/claude-skills.git ~/claude-skills
cd ~/claude-skills
for d in agents commands contexts hooks rules skills scripts templates examples mcp-configs tests; do
  mkdir -p ~/.claude/$d && cp -R $d/. ~/.claude/$d/
done
cp -n CLAUDE.md AGENTS.md ~/.claude/   # -n: never overwrite your own
```

Restart Claude Code afterwards.

### Hooks

Hooks only run when they are listed in `~/.claude/settings.json`. Merge the `hooks` block from
`settings.example.json` into your own settings (requires `jq`). Never commit your real `settings.json`.

### Update

```bash
cd ~/claude-skills && git pull
# then re-run the copy loop above
```

### Use

Skills load automatically. The "Skill Auto-Routing" table in `CLAUDE.md` maps what you ask to the right skill, so no `/` is needed.

## Third-party skills (MIT, see upstream licenses)

- [mattpocock/skills](https://github.com/mattpocock/skills) — `mp-tdd` / `mp-code-review` are renamed copies
- [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) — installed as `cf-security-audit`
- [dietrichgebert/ponytail](https://github.com/dietrichgebert/ponytail)
