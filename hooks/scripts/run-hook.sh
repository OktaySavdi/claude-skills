#!/usr/bin/env bash
# Adapter: Claude Code passes hook input as JSON on stdin; the ECC scripts read env vars.
# Usage: run-hook.sh <script> [file-path-regex]   (regex = only run when edited file matches)
set -uo pipefail
readonly SCRIPT="${1:?script required}"
readonly PATH_RE="${2:-}"
INPUT="$(cat)"
CLAUDE_BASH_COMMAND="$(jq -r '.tool_input.command // empty' <<<"$INPUT" 2>/dev/null)"
CLAUDE_TOOL_INPUT_FILE_PATH="$(jq -r '.tool_input.file_path // empty' <<<"$INPUT" 2>/dev/null)"
export CLAUDE_BASH_COMMAND CLAUDE_TOOL_INPUT_FILE_PATH
export CLAUDE_TOOL_INPUT="$CLAUDE_BASH_COMMAND"
if [[ -n "$PATH_RE" && ! "$CLAUDE_TOOL_INPUT_FILE_PATH" =~ $PATH_RE ]]; then exit 0; fi
exec bash "$HOME/.claude/hooks/scripts/$SCRIPT"
