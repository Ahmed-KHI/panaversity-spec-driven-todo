# Plan Command

This command generates a technical plan from a specification.

## Usage

```
/plan <feature-name>
```

## Prerequisites

- Specification file must exist: `specs/<feature-name>.specify.md`

## What it does

1. Reads the specification
2. Designs the architecture
3. Breaks down components
4. Defines data models
5. Plans implementation approach
6. Creates `specs/<feature-name>.plan.md`

## Example

```
/plan phase1-console-app
```

## Prompts

The command will ask:

1. **What is the high-level architecture?**
   - System components and their relationships

2. **What are the data models?**
   - Entities, fields, relationships

3. **What are the APIs/interfaces?**
   - Function signatures, endpoints

4. **What are the dependencies?**
   - External libraries, services

5. **What is the implementation strategy?**
   - Step-by-step approach

## Output

Creates: `specs/<feature-name>.plan.md`

## Next Steps

After plan is complete:
- Review architecture decisions
- Run `/tasks <feature-name>` to break down into tasks
