#!/bin/bash
# sync-plan.sh - Auto-commit IMPLEMENTATION_PLAN.md to master after edits

# Read JSON input from stdin
input=$(cat)

# Get file path
file_path=$(echo "$input" | jq -r '.file_path // ""')

# Exit if not IMPLEMENTATION_PLAN.md
if [[ ! "$file_path" =~ IMPLEMENTATION_PLAN\.md$ ]]; then
    exit 0
fi

# Get workspace root
workspace_root=$(echo "$input" | jq -r '.workspace_roots[0] // "."')
cd "$workspace_root" 2>/dev/null || cd "$(dirname "$0")/../.."

# Check if we're in a git repo
if [[ ! -d ".git" ]]; then
    exit 0
fi

# Stash other changes, commit IMPLEMENTATION_PLAN.md, push to master
{
    git stash --keep-index 2>/dev/null
    git add IMPLEMENTATION_PLAN.md
    git commit -m "sync: update IMPLEMENTATION_PLAN.md" 2>/dev/null
    git push origin HEAD:master 2>/dev/null
    git stash pop 2>/dev/null
} &>/dev/null

exit 0
