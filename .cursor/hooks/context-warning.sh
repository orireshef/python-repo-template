#!/bin/bash
# context-warning.sh - Pre-compaction handoff: save state and prompt for new session

# Read JSON input from stdin
input=$(cat)

# Get context usage
context_usage=$(echo "$input" | jq -r '.context_usage_percent // 0')

# Get workspace root
workspace_root=$(echo "$input" | jq -r '.workspace_roots[0] // "."')
cd "$workspace_root" 2>/dev/null || cd "$(dirname "$0")/../.."

# Read active context
active_context="logs/"
if [[ -f "logs/.active" ]]; then
    active_context=$(cat "logs/.active" | tr -d '\n')
fi

# Determine story name for /session command
session_arg="root"
if [[ "$active_context" != "logs/" ]]; then
    session_arg=$(echo "$active_context" | sed 's|logs/||' | sed 's|/$||')
fi

# Append handoff entry to current log
timestamp=$(date '+%Y-%m-%d %H:%M')
if [[ "$active_context" == "logs/" ]]; then
    recent_log=$(ls -t logs/*.md 2>/dev/null | grep -v '.active' | head -1)
else
    recent_log=$(ls -t "${active_context}"*.md 2>/dev/null | head -1)
fi

if [[ -n "$recent_log" ]]; then
    cat >> "$recent_log" << EOF

## Session Handoff (context limit reached)
- Context usage: ${context_usage}%
- Active context: $active_context
- Timestamp: $timestamp

Continue with: /session $session_arg

---
EOF
fi

# Return user message
cat << EOF
{
  "user_message": "Context is ${context_usage}% full. State saved to logs. Start a new agent and run: /session $session_arg"
}
EOF
