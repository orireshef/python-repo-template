# Initialize context-engineering artifacts

Initialize the following context-engineering files and folders **if they do not exist**. Use minimal, sensible placeholders. **Do not overwrite** anything that already exists.

| Artifact | Location | Placeholder / Notes |
|----------|----------|---------------------|
| **DESIGN.md** | Project root | System goal and high-level design. Brief intro + placeholders for goals, KPIs, architecture. |
| **logs/** | Project root | Directory for session logs. |
| **logs/.active** | `logs/` | Session state file. Initialize with: `context: root`, `log_file: logs/<timestamp>.md`, `files:` |
| **logs/<timestamp>.md** | `logs/` | Initial root log file with header: `# Session Log: <date>`, `**Context:** root` |
| **IMPLEMENTATION_PLAN.md** | Project root | Planning doc. Short intro + placeholder for Epics / Stories / Tasks and their status (table or list). Include Status Legend: `planned`, `assigned`, `in-progress`, `blocked`, `done`. |
| **memories.md** | Project root | Personal preferences (style, local conventions). One-line note that this is for personal prefs; rest empty. |

## .active format
```yaml
context: root
log_file: logs/YYYY-MM-DD_HH-MM.md
files:
```

After running, list what was **created** and what **already existed**.
