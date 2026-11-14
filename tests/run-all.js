#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const os = require('os');

const CLAUDE_DIR = path.join(os.homedir(), '.claude');
let passed = 0;
let failed = 0;

function check(description, condition, detail) {
  if (condition) { console.log(`  \u2705 ${description}`); passed++; }
  else { console.error(`  \u274c ${description}${detail ? ' \u2014 ' + detail : ''}`); failed++; }
}

const p = (rel) => path.join(CLAUDE_DIR, rel);
const exists = (rel) => fs.existsSync(p(rel));
const listDir = (rel) => exists(rel) ? fs.readdirSync(p(rel)) : [];

console.log('\nECC Structure Tests\n');

console.log('Core directories:');
['agents','commands','skills','rules/common','hooks','hooks/scripts',
 'examples','scripts','scripts/lib','scripts/hooks','tests','contexts',
 '.claude-plugin','mcp-configs'].forEach(d => check(`${d}/`, exists(d)));

console.log('\nKey files:');
['README.md','AGENTS.md','CLAUDE.md','settings.json','ecc_dashboard.py',
 'hooks/hooks.json','hooks/README.md','rules/README.md'].forEach(f => check(f, exists(f)));

console.log('\nRules (languages):');
['python','golang','typescript','swift','php'].forEach(lang =>
  check(`rules/${lang}/rules.md`, exists(`rules/${lang}/rules.md`)));
check('rules/common/security.md', exists('rules/common/security.md'));

console.log('\nPlugin & MCP:');
check('.claude-plugin/plugin.json', exists('.claude-plugin/plugin.json'));
check('.claude-plugin/marketplace.json', exists('.claude-plugin/marketplace.json'));
check('mcp-configs/mcp-servers.json', exists('mcp-configs/mcp-servers.json'));

console.log('\nFrontmatter (YAML):');
function countBad(dir, asDir) {
  let bad = 0;
  for (const item of listDir(dir)) {
    const mdPath = asDir ? path.join(dir, item, 'SKILL.md') : path.join(dir, item);
    if (!asDir && !item.endsWith('.md')) continue;
    if (!exists(mdPath)) continue;
    const first = fs.readFileSync(p(mdPath), 'utf8').split('\n')[0];
    if (first.trim() !== '---') bad++;
  }
  return bad;
}
check('agents/*.md frontmatter', countBad('agents', false) === 0);
check('skills/*/SKILL.md frontmatter', countBad('skills', true) === 0);
// Commands use markdown headers, not YAML frontmatter — by convention

console.log('\nHook scripts executable:');
for (const s of listDir('hooks/scripts')) {
  if (!s.endsWith('.sh')) continue;
  const stats = fs.statSync(p(`hooks/scripts/${s}`));
  check(`hooks/scripts/${s}`, (stats.mode & 0o111) !== 0);
}

console.log('\nCounts:');
const counts = {
  agents: listDir('agents').filter(f => f.endsWith('.md')).length,
  commands: listDir('commands').filter(f => f.endsWith('.md')).length,
  skills: listDir('skills').length,
  examples: listDir('examples').filter(f => f.endsWith('.md')).length,
};
for (const [k, v] of Object.entries(counts)) console.log(`  \u2139\ufe0f  ${k}: ${v}`);
check('>= 30 agents', counts.agents >= 30, `got ${counts.agents}`);
check('>= 40 commands', counts.commands >= 40, `got ${counts.commands}`);
check('>= 60 skills', counts.skills >= 60, `got ${counts.skills}`);

console.log(`\n${'='.repeat(40)}`);
console.log(`Results: ${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
