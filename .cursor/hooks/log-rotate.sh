#!/bin/bash
# log-rotate.sh - Auto-rotate log files when they exceed size limit

# Read JSON input from stdin
input=$(cat)

# Get file path
file_path=$(echo "$input" | jq -r '.file_path // ""')

# Only check log files (not .active)
if [[ ! "$file_path" =~ logs/.*\.md$ ]] || [[ "$file_path" =~ logs/\.active$ ]]; then
    exit 0
fi

# Get workspace root
workspace_root=$(echo "$input" | jq -r '.workspace_roots[0] // "."')
cd "$workspace_root" 2>/dev/null || cd "$(dirname "$0")/../.."

# Check file size (4000 chars ≈ 1000 tokens)
MAX_CHARS=4000

if [[ -f "$file_path" ]]; then
    char_count=$(wc -c < "$file_path" | tr -d ' ')
    
    if [[ "$char_count" -gt "$MAX_CHARS" ]]; then
        # Get context from .active
        context="root"
        if [[ -f "logs/.active" ]]; then
            context=$(grep '^context:' logs/.active | sed 's/context: *//' | tr -d '\n')
        fi
        
        # Determine log directory
        if [[ "$context" == "root" ]]; then
            log_dir="logs"
        else
            log_dir="logs/${context}"
            mkdir -p "$log_dir"
        fi
        
        # Create new log filename
        new_filename="${log_dir}/$(date '+%Y-%m-%d_%H-%M').md"
        
        # Don't create if it's the same file (avoid infinite loop)
        if [[ "$new_filename" == "$file_path" ]]; then
            # Add a second to differentiate
            sleep 1
            new_filename="${log_dir}/$(date '+%Y-%m-%d_%H-%M').md"
        fi
        
        # Mark old log as rotated
        cat >> "$file_path" << EOF

---
## Log Rotated
Continued in: \`$new_filename\`
---
EOF
        
        # Create new log file with header
        cat > "$new_filename" << EOF
# Session Log: $(date '+%Y-%m-%d %H:%M')
**Context:** $context
**Continued from:** \`$(basename "$file_path")\`

---

EOF
        
        # Update .active with current log file
        # First, preserve existing content but update/add log_file field
        if grep -q '^log_file:' logs/.active 2>/dev/null; then
            # Update existing log_file line
            sed -i '' "s|^log_file:.*|log_file: $new_filename|" logs/.active
        else
            # Add log_file field after context line
            sed -i '' "/^context:/a\\
log_file: $new_filename
" logs/.active
        fi
        
        # Log rotation event
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Rotated $file_path -> $new_filename" >> logs/hooks-debug.log
    fi
fi

exit 0
