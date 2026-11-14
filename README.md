# claude-skills

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

Skills load automatically. The `skill-router.sh` hook (UserPromptSubmit) reminds Claude on every prompt to check the routing table, so this works without typing `/`. The "Skill Auto-Routing" table in `CLAUDE.md` maps what you ask to the right skill, so no `/` is needed.

## Third-party skills

All are MIT or Apache-2.0 licensed; each upstream license applies. Only non-duplicate skills that fit an
infrastructure / DevOps / security workflow were taken. Names that clashed with existing ones were renamed.

| Source | License | Added |
|---|---|---|
| [mattpocock/skills](https://github.com/mattpocock/skills) | MIT | engineering + productivity set (`mp-tdd`, `mp-code-review` are renamed copies) |
| [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | MIT | `cf-security-audit` |
| [dietrichgebert/ponytail](https://github.com/dietrichgebert/ponytail) | MIT | `ponytail`, `-audit`, `-review`, `-debt`, `-gain`, `-help` |
| [microsoft/azure-skills](https://github.com/microsoft/azure-skills) | MIT | `aks-cost-optimization`, `aks-known-issues`, `aks-network-capture`, `aks-troubleshooting`, `appinsights-instrumentation`, `azure-advisor`, `azure-cloud-migrate`, `azure-compliance`, `azure-compute`, `azure-deploy`, `azure-diagnostics`, `azure-enterprise-infra-planner`, `azure-kubernetes`, `azure-kusto`, `azure-local`, `azure-local-multi-rack`, `azure-prepare`, `azure-quotas`, `azure-reliability`, `azure-resource-lookup`, `azure-resource-visualizer`, `azure-storage`, `azure-upgrade`, `azure-validate`, `cost-analysis`, `cost-governance`, `cost-optimization`, `entra-app-registration` |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | MIT | `context-engineering`, `deprecation-and-migration`, `doubt-driven-development`, `git-workflow-and-versioning`, `incremental-implementation`, `performance-optimization`, `planning-and-task-breakdown`, `shipping-and-launch`, `spec-driven-development` |
| [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | MIT | `aws-solution-architect`, `chaos-engineering`, `commit-craft`, `dependency-auditor`, `incident-commander`, `iso27001-audit-prep`, `migration-architect`, `performance-profiler`, `runbook-generator`, `skill-security-auditor`, `slo-architect`, `soc2-audit-prep`, `tech-debt-tracker` |
| [anthropics/skills](https://github.com/anthropics/skills) | Apache-2.0 | `doc-coauthoring`, `mcp-builder` |
| [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | MIT | already installed as `karpathy-guidelines` (same content, nothing added) |

### Reviewed and skipped

- **anthropics/skills** `docx`, `pdf`, `pptx`, `xlsx`, `skill-creator`, `claude-api`: already provided by the built-in Anthropic skills. Design/brand skills are not relevant here.
- **addyosmani/agent-skills**: TDD, API design, code review, CI/CD, security, observability and docs skills overlap what is already installed. `using-agent-skills` conflicts with the routing in `CLAUDE.md`. Frontend and browser-testing skills skipped.
- **microsoft/azure-skills**: Foundry / AI gateway / GPU inference / Kusto-graph / app-onboarding skills skipped (not an infrastructure focus).
- **alirezarezvani/claude-skills** (483 skills): marketing, product, C-level, finance, regulatory and ML skills skipped. Also skipped where an existing skill already covers it: `terraform-patterns`, `senior-devops`, `senior-secops`, `ci-cd-pipeline-builder`, `docker-development`.

Every skill adds its description to the model's context, so the set is kept deliberately small.
