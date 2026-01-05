# Claude Commands Configuration

This folder contains command definitions for Claude Code CLI.

## Available Commands

- **specify** - Create feature specification (WHAT)
- **plan** - Generate technical plan (HOW)
- **tasks** - Break down into tasks (BREAKDOWN)
- **implement** - Execute task implementation (CODE)
- **review** - Review implementation against specs

## Usage

These commands are used through Claude Code CLI:

```bash
# Specification phase
claude specify phase1-console-app

# Planning phase
claude plan phase1-console-app

# Task breakdown phase
claude tasks phase1-console-app

# Implementation phase
claude implement T-001
claude implement T-002
# ... and so on

# Review phase
claude review phase1-console-app
```

## Workflow

```
specify → plan → tasks → implement → review
```

## Integration with MCP

When MCP server is configured, these commands become available as prompts that can be invoked from any Claude-compatible IDE or interface.

## Command Structure

Each command file contains:
1. Description
2. Usage instructions
3. Prerequisites
4. What it does
5. Example
6. Prompts it asks
7. Output it generates
8. Next steps

## Customization

You can customize these commands by editing the respective `.md` files in this directory.

## Documentation

For more details on the Spec-Driven Development workflow, see:
- `AGENTS.md` - Agent behavior and workflow
- `constitution.md` - Project principles
- `README.md` - Project documentation
