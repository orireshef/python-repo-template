#!/bin/bash
# git-guard.sh - Guard dangerous git operations

# Read JSON input from stdin
input=$(cat)

# Get command
command=$(echo "$input" | jq -r '.command // ""')

# Default: allow
response='{"continue": true, "permission": "allow"}'

# Check if it's a git command
if [[ "$command" =~ ^git[[:space:]] ]] || [[ "$command" == "git" ]]; then
    
    # Block: git push --force
    if [[ "$command" =~ git[[:space:]]push.*--force ]] || [[ "$command" =~ git[[:space:]]push.*-f ]]; then
        response='{"continue": true, "permission": "deny", "user_message": "Force push blocked by workflow rules.", "agent_message": "Force push is blocked. This is a dangerous operation that can destroy history."}'
    
    # Block: git reset --hard
    elif [[ "$command" =~ git[[:space:]]reset.*--hard ]]; then
        response='{"continue": true, "permission": "deny", "user_message": "Hard reset blocked by workflow rules.", "agent_message": "Hard reset is blocked. This can cause data loss."}'
    
    # Ask: git push (to main/master)
    elif [[ "$command" =~ git[[:space:]]push ]] && [[ "$command" =~ (main|master) ]]; then
        response='{"continue": true, "permission": "ask", "user_message": "Pushing to main/master requires approval."}'
    
    # Ask: git commit --amend
    elif [[ "$command" =~ git[[:space:]]commit.*--amend ]]; then
        response='{"continue": true, "permission": "ask", "user_message": "Amending commits requires approval."}'
    
    # Allow: read-only git commands
    elif [[ "$command" =~ git[[:space:]](status|log|diff|branch|show|remote|fetch) ]]; then
        response='{"continue": true, "permission": "allow"}'
    
    # Allow: other git commands
    else
        response='{"continue": true, "permission": "allow"}'
    fi
fi

echo "$response"
