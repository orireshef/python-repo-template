#!/bin/bash
# file-guard.sh - Ensure agent only interacts with files in active scope

# Read JSON input from stdin
input=$(cat)

# Get file path
file_path=$(echo "$input" | jq -r '.file_path // ""')

# Get workspace root
workspace_root=$(echo "$input" | jq -r '.workspace_roots[0] // "."')
cd "$workspace_root" 2>/dev/null || cd "$(dirname "$0")/../.."

# Default: allow
response='{"permission": "allow"}'

# Read active context
if [[ -f "logs/.active" ]]; then
    context=$(grep '^context:' logs/.active | sed 's/context: *//')
    
    # Check if file is a log file
    if [[ "$file_path" =~ logs/.*\.md$ ]]; then
        # If context is root, only allow logs/*.md (not subdirs)
        if [[ "$context" == "root" ]]; then
            if [[ "$file_path" =~ logs/[^/]+\.md$ ]]; then
                response='{"permission": "allow"}'
            else
                response='{"permission": "ask", "user_message": "This log file is outside root context. Switch context first?"}'
            fi
        else
            # Story context - only allow logs/<story>/*.md
            if [[ "$file_path" =~ logs/${context}/.*\.md$ ]]; then
                response='{"permission": "allow"}'
            else
                response='{"permission": "ask", "user_message": "This log file is outside your active story context ('"$context"'). Switch context first?"}'
            fi
        fi
    fi
    
    # Check IMPLEMENTATION_PLAN.md access (always allowed, but we track it)
    # The workflow rules guide agents to use grep for their story only
fi

echo "$response"
