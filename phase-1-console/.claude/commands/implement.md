# Implement Command

This command implements a specific task from the task breakdown.

## Usage

```
/implement <task-id>
```

## Prerequisites

- Tasks file must exist: `specs/<feature-name>.tasks.md`
- Task must be defined with clear acceptance criteria

## What it does

1. Reads the task specification
2. Reviews referenced spec and plan sections
3. Generates code according to task requirements
4. Adds task reference comments
5. Creates or modifies specified files
6. Validates against acceptance criteria

## Example

```
/implement T-001
/implement T-002 T-003 T-004
```

## Implementation Rules

1. **Never generate code without a task reference**
2. **Follow the plan exactly**
3. **Add comments linking to specs**
   ```python
   # [Task]: T-001
   # [From]: phase1-console-app.specify.md §3.2
   ```
4. **Use type hints and docstrings**
5. **Handle errors as specified**

## Output

Creates/modifies files as specified in the task

## Validation

After implementation:
- Check all acceptance criteria met
- Run tests if specified
- Verify code references task ID
- Update task status to complete

## Next Steps

After implementing:
- Test the implementation
- Run `/implement <next-task-id>` for next task
- Update documentation if needed
