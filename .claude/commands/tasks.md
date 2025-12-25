# Tasks Command

This command breaks down a plan into atomic, actionable tasks.

## Usage

```
/tasks <feature-name>
```

## Prerequisites

- Specification file must exist: `specs/<feature-name>.specify.md`
- Plan file must exist: `specs/<feature-name>.plan.md`

## What it does

1. Reads the plan
2. Identifies atomic work units
3. Determines dependencies
4. Assigns task IDs
5. Creates acceptance criteria per task
6. Creates `specs/<feature-name>.tasks.md`

## Example

```
/tasks phase1-console-app
```

## Task Format

Each task includes:
- **Task ID** (e.g., T-001)
- **Description** - Clear, specific goal
- **Depends On** - Prerequisites
- **Estimated Time** - Time to complete
- **Acceptance Criteria** - How to verify completion
- **Files to Modify** - Which files to create/edit
- **References** - Links to spec and plan sections

## Output

Creates: `specs/<feature-name>.tasks.md`

## Next Steps

After tasks are complete:
- Review task breakdown
- Run `/implement <task-id>` to execute tasks
