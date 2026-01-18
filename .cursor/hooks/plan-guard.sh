#!/bin/bash
# plan-guard.sh - Guard IMPLEMENTATION_PLAN.md edits to prevent modifying assigned stories

# Read JSON input from stdin
input=$(cat)

# Get file path
file_path=$(echo "$input" | jq -r '.file_path // ""')

# Only check IMPLEMENTATION_PLAN.md
if [[ "$file_path" != *"IMPLEMENTATION_PLAN.md" ]]; then
    echo '{"permission": "allow"}'
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

# Get the new content (what agent is trying to write)
new_content=$(echo "$input" | jq -r '.new_content // ""')

# If no new_content provided, allow (might be a read or hook doesn't provide it)
if [[ -z "$new_content" ]]; then
    echo '{"permission": "allow"}'
    exit 0
fi

# Find all assigned/in-progress stories in the NEW content
# Pattern: | story-name | ... | assigned | or | story-name | ... | in-progress |
assigned_stories=$(echo "$new_content" | grep -oE '\|\s*[^|]+\s*\|[^|]*\|\s*(assigned|in-progress)\s*\|' | sed 's/|//g' | awk '{print $1}' | sort -u)

# Check if any assigned story is NOT my context
for story in $assigned_stories; do
    if [[ "$story" != "$my_context" && "$my_context" != "root" ]]; then
        # I'm in a story context but touching another assigned story
        cat << EOF
{
  "permission": "deny",
  "user_message": "Cannot modify story '$story' — it's assigned to another agent. You are working on '$my_context'."
}
EOF
        exit 0
    fi
    
    if [[ "$my_context" == "root" && -n "$story" ]]; then
        # I'm in root context trying to modify an assigned story — ask permission
        cat << EOF
{
  "permission": "ask",
  "user_message": "Story '$story' is assigned/in-progress. Are you sure you want to modify it from root context?"
}
EOF
        exit 0
    fi
done

echo '{"permission": "allow"}'
