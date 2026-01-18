#!/bin/bash
# context-inject.sh - Attempt to inject .active context via beforeSubmitPrompt
# NOTE: This hook can only block/allow, cannot inject context directly
# But we can use it to warn if .active is missing or stale

# Read JSON input from stdin
input=$(cat)

# Get workspace root
workspace_root=$(echo "$input" | jq -r '.workspace_roots[0] // "."')
cd "$workspace_root" 2>/dev/null || cd "$(dirname "$0")/../.."

# Check if .active exists
if [[ ! -f "logs/.active" ]]; then
    cat << 'EOF'
{
  "continue": false,
  "user_message": "No active context set. Please run /session <story-name> or /session root first."
}
EOF
    exit 0
fi

# Check if context is set
context=$(grep '^context:' logs/.active | sed 's/context: *//' | tr -d '\n')
if [[ -z "$context" ]]; then
    cat << 'EOF'
{
  "continue": false,
  "user_message": "Active context is empty. Please run /session <story-name> or /session root first."
}
EOF
    exit 0
fi

# Context exists - allow prompt
echo '{"continue": true}'
