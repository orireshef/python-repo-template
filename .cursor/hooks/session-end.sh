#!/bin/bash
# session-end.sh - Save session state when agent stops

# Read JSON input from stdin
input=$(cat)

# Get workspace root
workspace_root=$(echo "$input" | jq -r '.workspace_roots[0] // "."')
cd "$workspace_root" 2>/dev/null || cd "$(dirname "$0")/../.."

# Get status
status=$(echo "$input" | jq -r '.status // "unknown"')

# Read active context from .active file
context="root"
if [[ -f "logs/.active" ]]; then
    context=$(grep '^context:' logs/.active | sed 's/context: *//' | tr -d '\n')
fi

# Determine log directory
if [[ "$context" == "root" ]]; then
    log_dir="logs/"
else
    log_dir="logs/${context}/"
fi

# Append session end entry to current log
timestamp=$(date '+%Y-%m-%d %H:%M')
recent_log=$(ls -t "${log_dir}"*.md 2>/dev/null | head -1)

if [[ -n "$recent_log" && -f "$recent_log" ]]; then
    active_files=$(grep '^  - ' logs/.active 2>/dev/null | sed 's/^  - //' | tr '\n' ', ' | sed 's/, $//')
    
    cat >> "$recent_log" << EOF

## Session End
- Status: $status
- Context: $context
- Files touched: ${active_files:-none}
- Timestamp: $timestamp

---
EOF
fi

# Output empty JSON (stop hook can return followup_message but we don't need it)
echo '{}'
