#!/bin/bash
# thought-capture.sh - Capture agent thinking and write to log files

# Read JSON input from stdin
input=$(cat)

# Get workspace root
workspace_root=$(echo "$input" | jq -r '.workspace_roots[0] // "."')
cd "$workspace_root" 2>/dev/null || cd "$(dirname "$0")/../.."

# Get thinking text
thinking_text=$(echo "$input" | jq -r '.text // ""')

# Exit if no thinking text
if [[ -z "$thinking_text" ]]; then
    exit 0
fi

# Read active context
active_context="logs/"
if [[ -f "logs/.active" ]]; then
    active_context=$(cat "logs/.active" | tr -d '\n')
fi

# Ensure directory exists
mkdir -p "$active_context"

# Find or create today's log file
timestamp=$(date '+%Y-%m-%d_%H-%M')
time_only=$(date '+%H:%M:%S')

# Find most recent log file in context
if [[ "$active_context" == "logs/" ]]; then
    recent_log=$(ls -t logs/*.md 2>/dev/null | grep -v '.active' | head -1)
else
    recent_log=$(ls -t "${active_context}"*.md 2>/dev/null | head -1)
fi

# Check if we need a new file (none exists or current > 4000 chars)
create_new=false
if [[ -z "$recent_log" ]]; then
    create_new=true
elif [[ $(wc -c < "$recent_log") -gt 4000 ]]; then
    create_new=true
fi

if [[ "$create_new" == "true" ]]; then
    log_file="${active_context}${timestamp}.md"
    echo "# Session Log: $(date '+%Y-%m-%d')" > "$log_file"
    echo "**Context:** $active_context" >> "$log_file"
    echo "" >> "$log_file"
else
    log_file="$recent_log"
fi

# Append thinking with timestamp
cat >> "$log_file" << EOF

## [$time_only] Agent Thinking
$thinking_text

---
EOF

exit 0
