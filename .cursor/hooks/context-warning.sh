#!/bin/bash
# context-warning.sh - Pre-compaction handoff: save state and prompt for new session

# Read JSON input from stdin
input=$(cat)

# Get context usage
context_usage=$(echo "$input" | jq -r '.context_usage_percent // 0')

# Get workspace root
workspace_root=$(echo "$input" | jq -r '.workspace_roots[0] // "."')
cd "$workspace_root" 2>/dev/null || cd "$(dirname "$0")/../.."

# Read active context from .active file
context="root"
if [[ -f "logs/.active" ]]; then
    context=$(grep '^context:' logs/.active | sed 's/context: *//' | tr -d '\n')
fi

# Determine log directory
if [[ "$context" == "root" ]]; then
    log_dir="logs/"
    session_arg="root"
else
    log_dir="logs/${context}/"
    session_arg="$context"
fi

# Append handoff entry to current log
timestamp=$(date '+%Y-%m-%d %H:%M')
recent_log=$(ls -t "${log_dir}"*.md 2>/dev/null | head -1)

if [[ -n "$recent_log" && -f "$recent_log" ]]; then
    # Get active files from .active
    active_files=$(grep '^  - ' logs/.active 2>/dev/null | sed 's/^  - //' | tr '\n' ', ' | sed 's/, $//')
    
    cat >> "$recent_log" << EOF

## Session Handoff (context limit reached)
- Context usage: ${context_usage}%
- Active context: $context
- Active files: ${active_files:-none}
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
