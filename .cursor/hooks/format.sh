#!/bin/bash
# format.sh - Auto-format Python files after edits

# Read JSON input from stdin
input=$(cat)

# Get file path
file_path=$(echo "$input" | jq -r '.file_path // ""')

# Exit if not a Python file
if [[ ! "$file_path" =~ \.py$ ]]; then
    exit 0
fi

# Get workspace root
workspace_root=$(echo "$input" | jq -r '.workspace_roots[0] // "."')
cd "$workspace_root" 2>/dev/null || cd "$(dirname "$0")/../.."

# Run ruff format and check --fix
if command -v uv &> /dev/null; then
    uv run ruff format "$file_path" 2>/dev/null
    uv run ruff check --fix "$file_path" 2>/dev/null
fi

exit 0
