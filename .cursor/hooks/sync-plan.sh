#!/bin/bash
# sync-plan.sh - Sync IMPLEMENTATION_PLAN.md with master, detect conflicts

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

# Read my context from .active
my_context="root"
if [[ -f "logs/.active" ]]; then
    my_context=$(grep '^context:' logs/.active | sed 's/context: *//' | tr -d '\n')
fi

# Fetch latest from master
git fetch origin master 2>/dev/null

# Get the remote version
remote_plan=$(git show origin/master:IMPLEMENTATION_PLAN.md 2>/dev/null)

if [[ -z "$remote_plan" ]]; then
    # No remote version, just push
    git add IMPLEMENTATION_PLAN.md
    git commit -m "sync: update IMPLEMENTATION_PLAN.md" 2>/dev/null
    git push origin HEAD:master 2>/dev/null
    exit 0
fi

# Save current local version
local_plan=$(cat IMPLEMENTATION_PLAN.md)

# Check for stories that are assigned/in-progress in REMOTE but not ours
# These are lines with | story-name | ... | assigned/in-progress |
remote_assigned=$(echo "$remote_plan" | grep -oE '\|\s*[A-Za-z0-9_-]+\s*\|[^|]*\|\s*(assigned|in-progress)\s*\|' | sed 's/|//g' | awk '{print $1}' | sort -u)

# Check if our edit touched any of those stories (compare local vs remote for those sections)
conflict_detected=""
for story in $remote_assigned; do
    if [[ "$story" != "$my_context" && "$my_context" != "root" ]]; then
        # Check if this story's section differs between local and remote
        local_section=$(echo "$local_plan" | grep -A 20 "| $story |" | head -25)
        remote_section=$(echo "$remote_plan" | grep -A 20 "| $story |" | head -25)
        
        if [[ "$local_section" != "$remote_section" ]]; then
            conflict_detected="$story"
            break
        fi
    fi
done

timestamp=$(date '+%Y-%m-%d %H:%M:%S')

if [[ -n "$conflict_detected" ]]; then
    # CONFLICT: We modified another agent's story
    # Revert to remote version for that story's section
    echo "[$timestamp] CONFLICT: Attempted to modify story '$conflict_detected' (assigned to another agent). Reverting." >> logs/hooks-debug.log
    
    # Restore remote version
    echo "$remote_plan" > IMPLEMENTATION_PLAN.md
    
    # Log warning
    if [[ -f "logs/.active" ]]; then
        log_dir="logs/"
        if [[ "$my_context" != "root" ]]; then
            log_dir="logs/${my_context}/"
        fi
        recent_log=$(ls -t "${log_dir}"*.md 2>/dev/null | head -1)
        if [[ -n "$recent_log" ]]; then
            cat >> "$recent_log" << EOF

## ⚠️ HOOK WARNING: Edit Reverted
- Attempted to modify story: $conflict_detected
- This story is assigned to another agent
- Your edit was reverted to prevent conflicts
- Timestamp: $timestamp

EOF
        fi
    fi
    
    exit 0
fi

# No conflict - safe to push
# For root context editing assigned stories, we should have asked permission (workflow rule)
git add IMPLEMENTATION_PLAN.md
git commit -m "sync: update IMPLEMENTATION_PLAN.md" 2>/dev/null
git push origin HEAD:master 2>/dev/null

echo "[$timestamp] IMPLEMENTATION_PLAN.md synced to master. Context: $my_context" >> logs/hooks-debug.log

exit 0
