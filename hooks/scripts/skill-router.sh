#!/usr/bin/env bash
# Skill auto-router (UserPromptSubmit).
# The user never types "/<skill>". This injects a short instruction on every prompt so
# Claude matches intent to the "Skill Auto-Routing" table in ~/.claude/CLAUDE.md and
# loads the skill(s) before answering. stdout of a UserPromptSubmit hook becomes context.
set -uo pipefail

INPUT="$(cat)"
PROMPT="$(jq -r '.prompt // empty' <<<"$INPUT" 2>/dev/null)"

# User already invoked a skill or command explicitly — nothing to add.
if [[ "$PROMPT" =~ ^[[:space:]]*/ ]]; then
  exit 0
fi

cat <<'EOF'
[skill-router] The user never types "/". Before answering, match this request to the
"Skill Auto-Routing" table in ~/.claude/CLAUDE.md (and the skill list) and load every
fitting skill with the Skill tool first — no need to ask or announce it. Skip only for
pure chit-chat or one-line factual answers.
EOF
exit 0
