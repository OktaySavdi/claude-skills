#!/usr/bin/env bash
# Skill auto-router (UserPromptSubmit). Scoring lives in skill-router.py; never block the prompt.
exec python3 "$(dirname "${BASH_SOURCE[0]}")/skill-router.py" 2>/dev/null || exit 0
