# Specify Command

This command initiates the specification phase for a new feature.

## Usage

```
/specify <feature-name>
```

## What it does

1. Prompts for feature requirements
2. Asks about user stories
3. Collects acceptance criteria
4. Documents constraints
5. Creates `specs/<feature-name>.specify.md`

## Example

```
/specify phase1-console-app
```

## Prompts

The command will ask:

1. **What is the purpose of this feature?**
   - Describe the main goal

2. **Who are the users?**
   - Define user personas

3. **What are the user stories?**
   - As a [user], I want to [action], so that [benefit]

4. **What are the acceptance criteria?**
   - Clear, testable criteria for each story

5. **What are the constraints?**
   - Technical, business, or resource constraints

6. **What is out of scope?**
   - Features explicitly not included

## Output

Creates: `specs/<feature-name>.specify.md`

## Next Steps

After specification is complete:
- Review and validate the specification
- Run `/plan <feature-name>` to create technical plan
