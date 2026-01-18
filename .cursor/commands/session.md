# Start Session with Context

Start or continue a session with the specified context.

**Usage:** `/session <story-name>` or `/session root`

## Input
- `$ARGUMENTS` — Either a story name or "root"

## Instructions

1. **Set active context:**
   - If `$ARGUMENTS` is "root": set `logs/.active` to `logs/`
   - Otherwise: set `logs/.active` to `logs/$ARGUMENTS/`
   - Create the directory if it doesn't exist

2. **Read context:**
   - Read recent log files from the active directory (last 50 lines of most recent)
   - Read IMPLEMENTATION_PLAN.md for current tasks

3. **If story context (not root):**
   - Check story status in IMPLEMENTATION_PLAN.md
   - If `planned`: Mark as `assigned` and follow Story Planning instructions below
   - If `assigned` or `in-progress`: Show current tasks and continue work

4. **Output session summary** with:
   - Active context directory
   - Recent log summary
   - Current tasks from IMPLEMENTATION_PLAN.md
   - Next steps

## Story Planning (for newly assigned stories)

If the story status was `planned` (now `assigned`), complete these planning steps before implementation:

1. **Design** — Add to IMPLEMENTATION_PLAN.md under this story:
   - Problem summary
   - Inputs and outputs
   - Components/modules involved
   - Dependencies or risks

2. **Define Tests** — Add test criteria to IMPLEMENTATION_PLAN.md:
   - Integration tests (acceptance criteria)
   - Unit test coverage areas

3. **Break into Tasks** — Add atomic tasks under this story:
   - Each task completable without context switching
   - Mark story as `in-progress` once tasks are defined

Your thinking is automatically captured to logs via hooks — just think through the problem normally.
Only start implementation after tasks are in IMPLEMENTATION_PLAN.md.
