#!/bin/bash
# plan-guard.sh - Warn if IMPLEMENTATION_PLAN.md edits touch other agents' stories
# NOTE: This runs AFTER edit (can't block), so it just logs warnings

# Read JSON input from stdin
input=$(cat)

# Get file path
file_path=$(echo "$input" | jq -r '.file_path // ""')

# Only check IMPLEMENTATION_PLAN.md
if [[ "$file_path" != *"IMPLEMENTATION_PLAN.md" ]]; then
    exit 0
fi

# Get workspace root
workspace_root=$(echo "$input" | jq -r '.workspace_roots[0] // "."')
cd "$workspace_root" 2>/dev/null || cd "$(dirname "$0")/../.."

# Read my context from .active
my_context="root"
if [[ -f "logs/.active" ]]; then
    my_context=$(grep '^context:' logs/.active | sed 's/context: *//' | tr -d '\n')
fi

# Log to debug file for visibility
timestamp=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$timestamp] IMPLEMENTATION_PLAN.md edited. Context: $my_context" >> logs/hooks-debug.log

# We can't block after the fact, so just log
# The workflow rules must guide the agent to only edit their story

exit 0
