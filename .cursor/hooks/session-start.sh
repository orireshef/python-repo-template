#!/bin/bash
# session-start.sh - Inject context and prompt for confirmation at session start

# Read JSON input from stdin
input=$(cat)

# Get workspace root from input
workspace_root=$(echo "$input" | jq -r '.workspace_roots[0] // "."')
cd "$workspace_root" 2>/dev/null || cd "$(dirname "$0")/../.."

# Read current active context
active_context=""
if [[ -f "logs/.active" ]]; then
    active_context=$(cat "logs/.active" | tr -d '\n')
fi

# Read IMPLEMENTATION_PLAN.md to find first planned story
suggested_story=""
suggested_context=""
if [[ -f "IMPLEMENTATION_PLAN.md" ]]; then
    # Find first story with status "planned"
    suggested_story=$(grep -E '\|\s*S[0-9]+\s*\|.*\|\s*planned\s*\|' IMPLEMENTATION_PLAN.md | head -1 | sed 's/.*|\s*\(S[0-9]*\)\s*|.*/\1/')
    if [[ -n "$suggested_story" ]]; then
        # Extract story name for directory
        story_name=$(grep -E "\|\s*$suggested_story\s*\|" IMPLEMENTATION_PLAN.md | sed 's/.*|\s*Story\s*|\s*\([^|]*\)\s*|.*/\1/' | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | head -1)
        suggested_context="logs/${story_name}/"
    fi
fi

# Build context summary
context_summary="## Session Context (auto-injected)\n\n"
context_summary+="### Current Active Context\n"
context_summary+="${active_context:-'(none set)'}\n\n"

if [[ -n "$suggested_story" ]]; then
    context_summary+="### Suggested Story\n"
    context_summary+="Story: $suggested_story\n"
    context_summary+="Directory: $suggested_context\n\n"
fi

# Read recent log if active context exists
if [[ -n "$active_context" && -d "$active_context" ]]; then
    recent_log=$(ls -t "$active_context"/*.md 2>/dev/null | head -1)
    if [[ -n "$recent_log" ]]; then
        context_summary+="### Recent Log ($recent_log)\n"
        context_summary+="\`\`\`\n"
        context_summary+="$(tail -30 "$recent_log" 2>/dev/null)\n"
        context_summary+="\`\`\`\n\n"
    fi
elif [[ "$active_context" == "logs/" ]]; then
    recent_log=$(ls -t logs/*.md 2>/dev/null | grep -v '.active' | head -1)
    if [[ -n "$recent_log" ]]; then
        context_summary+="### Recent Log ($recent_log)\n"
        context_summary+="\`\`\`\n"
        context_summary+="$(tail -30 "$recent_log" 2>/dev/null)\n"
        context_summary+="\`\`\`\n\n"
    fi
fi

# Read IMPLEMENTATION_PLAN.md summary
if [[ -f "IMPLEMENTATION_PLAN.md" ]]; then
    context_summary+="### IMPLEMENTATION_PLAN.md Summary\n"
    context_summary+="\`\`\`\n"
    context_summary+="$(head -30 IMPLEMENTATION_PLAN.md)\n"
    context_summary+="\`\`\`\n"
fi

# Build user message
user_msg="Please confirm your session context.\n\n"
if [[ -n "$suggested_story" ]]; then
    user_msg+="Suggested: '$suggested_context' (Story $suggested_story)\n"
fi
user_msg+="Current: '${active_context:-logs/}'\n\n"
user_msg+="Run: /session <story-name> or /session root"

# Output JSON response - always prompt for confirmation
cat << EOF
{
  "additional_context": "$(echo -e "$context_summary" | sed 's/"/\\"/g' | tr '\n' ' ' | sed 's/  */ /g')",
  "continue": true,
  "user_message": "$(echo -e "$user_msg" | sed 's/"/\\"/g' | tr '\n' ' ')"
}
EOF
