#!/bin/bash
# track-files.sh - Track active files being edited in .active

# Read JSON input from stdin
input=$(cat)

# Get file path
file_path=$(echo "$input" | jq -r '.file_path // ""')

# Get workspace root
workspace_root=$(echo "$input" | jq -r '.workspace_roots[0] // "."')
cd "$workspace_root" 2>/dev/null || cd "$(dirname "$0")/../.."

# Skip non-project files (don't track logs, .active itself, etc.)
if [[ "$file_path" =~ ^logs/ ]] || [[ "$file_path" =~ \.active$ ]]; then
    exit 0
fi

# Skip if .active doesn't exist
if [[ ! -f "logs/.active" ]]; then
    exit 0
fi

# Make path relative to workspace
rel_path="${file_path#$workspace_root/}"
rel_path="${rel_path#./}"

# Check if file is already tracked
if grep -q "^  - $rel_path$" logs/.active 2>/dev/null; then
    exit 0
fi

# Add file to active files list
echo "  - $rel_path" >> logs/.active

exit 0
