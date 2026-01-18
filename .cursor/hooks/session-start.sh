#!/bin/bash
# session-start.sh - Inject context and prompt for confirmation at session start

# Read JSON input from stdin
input=$(cat)

# Get workspace root from input
workspace_root=$(echo "$input" | jq -r '.workspace_roots[0] // "."')
cd "$workspace_root" 2>/dev/null || cd "$(dirname "$0")/../.."

# Read current active context from .active file
context="root"
active_files=""
if [[ -f "logs/.active" ]]; then
    context=$(grep '^context:' logs/.active | sed 's/context: *//' | tr -d '\n')
    active_files=$(grep '^  - ' logs/.active | sed 's/^  - //' | tr '\n' ', ' | sed 's/, $//')
fi

# Determine log directory
if [[ "$context" == "root" ]]; then
    log_dir="logs/"
else
    log_dir="logs/${context}/"
fi

# Read IMPLEMENTATION_PLAN.md to find first planned story
suggested_story=""
if [[ -f "IMPLEMENTATION_PLAN.md" ]]; then
    suggested_story=$(grep -E '\|\s*S[0-9]+\s*\|.*\|\s*planned\s*\|' IMPLEMENTATION_PLAN.md | head -1 | sed 's/.*|\s*\(S[0-9]*\)\s*|.*/\1/')
fi

# Build context summary
context_summary="## Session Context (auto-injected)\n\n"
context_summary+="### Active Context\n"
context_summary+="- **Context:** $context\n"
context_summary+="- **Log directory:** $log_dir\n"
if [[ -n "$active_files" ]]; then
    context_summary+="- **Active files from last session:** $active_files\n"
fi
context_summary+="\n"

if [[ -n "$suggested_story" && "$context" == "root" ]]; then
    context_summary+="### Available Story\n"
    context_summary+="Story $suggested_story is available (status: planned). Run \`/session $suggested_story\` to pick it up.\n\n"
fi

# Read recent log if exists
if [[ -d "$log_dir" ]]; then
    recent_log=$(ls -t "${log_dir}"*.md 2>/dev/null | head -1)
    if [[ -n "$recent_log" && -f "$recent_log" ]]; then
        context_summary+="### Recent Log ($recent_log)\n"
        context_summary+="\`\`\`\n"
        context_summary+="$(tail -30 "$recent_log" 2>/dev/null)\n"
        context_summary+="\`\`\`\n\n"
    fi
fi

# Read relevant IMPLEMENTATION_PLAN.md section
if [[ -f "IMPLEMENTATION_PLAN.md" ]]; then
    context_summary+="### IMPLEMENTATION_PLAN.md\n"
    if [[ "$context" != "root" ]]; then
        # For story context, show only that story's section
        context_summary+="*Showing tasks for story: $context*\n"
        context_summary+="\`\`\`\n"
        context_summary+="$(grep -A 20 "| $context |\\|$context" IMPLEMENTATION_PLAN.md | head -25)\n"
        context_summary+="\`\`\`\n"
    else
        context_summary+="\`\`\`\n"
        context_summary+="$(head -30 IMPLEMENTATION_PLAN.md)\n"
        context_summary+="\`\`\`\n"
    fi
fi

# Build user message
user_msg="Session context: $context"
if [[ "$context" == "root" ]]; then
    user_msg+="\nRun /session <story-name> to work on a story, or continue with ad-hoc work."
else
    user_msg+="\nContinuing work on story: $context"
fi

# Output JSON response
cat << EOF
{
  "additional_context": "$(echo -e "$context_summary" | sed 's/"/\\"/g' | tr '\n' ' ' | sed 's/  */ /g')",
  "continue": true,
  "user_message": "$(echo -e "$user_msg" | sed 's/"/\\"/g' | tr '\n' ' ')"
}
EOF
