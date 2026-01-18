# Start Session with Context

Start or continue a session with the specified context.

**Usage:** `/session <story-name>` or `/session root`

## Input
- `$ARGUMENTS` — Either a story name (e.g., `add-auth`) or `root`

## Instructions

1. **Sync IMPLEMENTATION_PLAN.md from master:**
   ```bash
   git fetch origin master && git checkout origin/master -- IMPLEMENTATION_PLAN.md
   ```

2. **Update `logs/.active`:**
   ```yaml
   context: $ARGUMENTS
   files:
   ```
   - If `$ARGUMENTS` is a story name, create `logs/$ARGUMENTS/` directory if needed

3. **Read context:**
   - If story context: use `grep` to read only your story from IMPLEMENTATION_PLAN.md
   - Read recent log files from `logs/` (root) or `logs/$ARGUMENTS/` (story)

4. **If story context:**
   - Check story status in IMPLEMENTATION_PLAN.md
   - If `planned`: Mark as `assigned` and follow Story Planning instructions below
   - If `assigned` or `in-progress`: Show current tasks and continue work

5. **Output session summary**

## Reading IMPLEMENTATION_PLAN.md (Story Context)

When in a story context, only read/edit your story's section:

```bash
# Read your story's tasks
grep -A 20 "| S1 |" IMPLEMENTATION_PLAN.md

# Or find tasks for your story
grep "| your-story-name |" IMPLEMENTATION_PLAN.md
```

This prevents accidentally modifying other agents' work.

## Story Planning (for newly assigned stories)

If the story status was `planned` (now `assigned`), complete these planning steps:

1. **Design** — Add to IMPLEMENTATION_PLAN.md under this story:
   - Problem summary
   - Inputs and outputs
   - Components/modules involved
   - Dependencies or risks

2. **Define Tests** — Add test criteria:
   - Integration tests (acceptance criteria)
   - Unit test coverage areas

3. **Break into Tasks** — Add atomic tasks under this story:
   - Each task completable without context switching
   - Mark story as `in-progress` once tasks are defined

Only start implementation after tasks are in IMPLEMENTATION_PLAN.md.
