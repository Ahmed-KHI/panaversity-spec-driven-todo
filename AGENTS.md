# AGENTS.md

## Purpose

This project uses **Spec-Driven Development (SDD)** — a workflow where **no agent is allowed to write code until the specification is complete and approved**.

All AI agents (Claude Code, GitHub Copilot, Gemini, local LLMs, etc.) must follow the **Spec-Kit lifecycle**:

> **Specify → Plan → Tasks → Implement**

This prevents "vibe coding," ensures alignment across agents, and guarantees that every implementation step maps back to an explicit requirement.

---

## How Agents Must Work

Every agent in this project MUST obey these rules:

1. **Never generate code without a referenced Task ID.**
2. **Never modify architecture without updating the `.plan` file.**
3. **Never propose features without updating the `.specify` file (WHAT).**
4. **Never change approach without updating `constitution.md` (Principles).**
5. **Every code file must contain a comment linking it to the Task and Spec sections.**

If an agent cannot find the required spec, it must **stop and request it**, not improvise.

---

## Spec-Kit Workflow (Source of Truth)

### 1. Constitution (WHY — Principles & Constraints)

**File:** `constitution.md`

Defines the project's non-negotiables:
- Architecture values
- Security rules
- Tech stack constraints
- Performance expectations
- Allowed patterns
- Coding standards

**Agent Rule:** Check this before proposing solutions.

---

### 2. Specify (WHAT — Requirements, Journeys & Acceptance Criteria)

**File:** `specs/<feature>.specify.md`

Contains:
- User journeys
- Requirements
- Acceptance criteria
- Domain rules
- Business constraints

**Agent Rule:** Do not infer missing requirements — request clarification or propose specification updates.

---

### 3. Plan (HOW — Architecture, Components, Interfaces)

**File:** `specs/<feature>.plan.md`

Includes:
- Component breakdown
- APIs & schema diagrams
- Service boundaries
- System responsibilities
- High-level sequencing
- Data structures

**Agent Rule:** All architectural output MUST be generated from the Specify file.

---

### 4. Tasks (BREAKDOWN — Atomic, Testable Work Units)

**File:** `specs/<feature>.tasks.md`

Each Task must contain:
- Task ID (e.g., T-001)
- Clear description
- Preconditions
- Expected outputs
- Artifacts to modify
- Links back to Specify + Plan sections

**Agent Rule:** Implement only what these tasks define.

---

### 5. Implement (CODE — Write Only What the Tasks Authorize)

Agents now write code, but must:
- Reference Task IDs in comments
- Follow the Plan exactly
- Not invent new features or flows
- Stop and request clarification if anything is underspecified

> **The golden rule:** No task = No code.

---

## Agent Behavior in This Project

### When generating code:

Agents must reference:

```python
# [Task]: T-001
# [From]: specs/phase1-console-app.specify.md §2.1, 
#         specs/phase1-console-app.plan.md §3.4
```

### When proposing architecture:

Agents must reference:

```
Update required in specs/<feature>.plan.md → add component X
```

### When proposing new behavior or a new feature:

Agents must reference:

```
Requires update in specs/<feature>.specify.md (WHAT)
```

### When changing principles:

Agents must reference:

```
Modify constitution.md → Principle #X
```

---

## Agent Failure Modes (What Agents MUST Avoid)

Agents are NOT allowed to:

- Freestyle code or architecture
- Generate missing requirements
- Create tasks on their own
- Alter stack choices without justification
- Add endpoints, fields, or flows that aren't in the spec
- Ignore acceptance criteria
- Produce "creative" implementations that violate the plan
- Write code manually (humans included!)

**Conflict Resolution Hierarchy:**

```
Constitution > Specify > Plan > Tasks
```

If specs conflict, the higher-level document takes precedence.

---

## Developer–Agent Alignment

Humans and agents collaborate, but the **spec is the single source of truth**.

Before every session, agents should re-read:

1. `constitution.md` (principles)
2. `specs/<feature>.specify.md` (requirements)
3. `specs/<feature>.plan.md` (architecture)
4. `specs/<feature>.tasks.md` (work units)

This ensures predictable, deterministic development.

---

## Spec-Kit Tools (For Claude Code with MCP)

When Spec-Kit Plus MCP server is configured, agents can use these tools:

### Initialization

```bash
# Initialize Spec-Kit structure (human runs this once)
uv specifyplus init hackathon-todo
```

### Specification Phase

```bash
# Create feature specification (WHAT)
speckit specify <feature-name>
```

**Agent Action:** Answer prompts about:
- User stories
- Requirements
- Acceptance criteria
- Constraints

**Output:** `specs/<feature>.specify.md`

### Planning Phase

```bash
# Generate technical plan (HOW)
speckit plan <feature-name>
```

**Agent Action:** Based on `.specify`, create:
- Component architecture
- Data models
- API contracts
- Sequence diagrams

**Output:** `specs/<feature>.plan.md`

### Task Breakdown Phase

```bash
# Break plan into tasks (BREAKDOWN)
speckit tasks <feature-name>
```

**Agent Action:** Decompose plan into:
- Atomic work units
- Each with Task ID
- Preconditions and outputs
- File paths to modify

**Output:** `specs/<feature>.tasks.md`

### Implementation Phase

```bash
# Execute tasks (CODE)
speckit implement <task-id>
```

**Agent Action:**
- Read task specification
- Generate code with task reference comments
- Follow patterns in constitution.md
- Create/modify only specified files

**Output:** Working code in `/src` or appropriate folder

---

## Hackathon-Specific Workflow

### Phase I: Console App

```
1. speckit specify phase1-console-app
   → Define 5 Basic Level features

2. speckit plan phase1-console-app
   → Design in-memory data structures
   → Define CLI interface

3. speckit tasks phase1-console-app
   → Break into 5-10 atomic tasks

4. speckit implement T-001, T-002, ... T-010
   → Generate Python code
```

### Phase II: Web Application

```
1. speckit specify phase2-web-app
   → Define frontend + backend + auth

2. speckit plan phase2-web-app
   → Design REST API
   → Define database schema
   → Plan authentication flow

3. speckit tasks phase2-web-app
   → Frontend tasks
   → Backend tasks
   → Database migration tasks

4. speckit implement <task-ids>
   → Generate Next.js + FastAPI code
```

### Phase III: AI Chatbot

```
1. speckit specify phase3-chatbot
   → Define natural language commands
   → Define MCP tools

2. speckit plan phase3-chatbot
   → Design agent architecture
   → Plan conversation persistence
   → Define MCP tool interfaces

3. speckit tasks phase3-chatbot
   → MCP server tasks
   → Agent integration tasks
   → Database schema tasks

4. speckit implement <task-ids>
   → Generate ChatKit + MCP code
```

### Phase IV: Kubernetes Deployment

```
1. speckit specify phase4-kubernetes
   → Define deployment requirements
   → Define container specs

2. speckit plan phase4-kubernetes
   → Design Kubernetes architecture
   → Plan Helm charts

3. speckit tasks phase4-kubernetes
   → Dockerfile tasks
   → Helm chart tasks
   → Minikube setup tasks

4. speckit implement <task-ids>
   → Generate Docker + Helm configs
```

### Phase V: Cloud Deployment

```
1. speckit specify phase5-cloud
   → Define advanced features
   → Define event-driven architecture
   → Define Dapr requirements

2. speckit plan phase5-cloud
   → Design Kafka topics
   → Plan Dapr integration
   → Define CI/CD pipeline

3. speckit tasks phase5-cloud
   → Kafka setup tasks
   → Dapr configuration tasks
   → Cloud deployment tasks

4. speckit implement <task-ids>
   → Generate event-driven code
```

---

## File Reference Patterns

### For Agents Using MCP

When spec files are available, agents reference them:

```
@specs/phase1-console-app.specify.md
@specs/phase1-console-app.plan.md
@specs/phase1-console-app.tasks.md
```

### For Manual Agents (Without MCP)

Read the spec files directly:

```
Read: specs/phase1-console-app.specify.md
Read: specs/phase1-console-app.plan.md
Read: specs/phase1-console-app.tasks.md
Then: Implement according to tasks
```

---

## Quality Gates

Before moving to the next phase:

### Specification Quality Gate
- [ ] All user stories documented
- [ ] Acceptance criteria clear and testable
- [ ] No ambiguous requirements

### Planning Quality Gate
- [ ] Component diagram complete
- [ ] Data models defined
- [ ] API contracts specified
- [ ] Dependencies identified

### Task Quality Gate
- [ ] All tasks atomic (completable in < 2 hours)
- [ ] Each task has clear outputs
- [ ] Task order/dependencies documented
- [ ] File paths specified

### Implementation Quality Gate
- [ ] All tasks completed
- [ ] Code references task IDs
- [ ] Tests pass (if applicable)
- [ ] Documentation updated

---

## Error Recovery

### If Specification is Incomplete:

```
Agent: "STOP. Specification incomplete. 
        Missing: [specific requirement]
        Action: Update specs/phase1-console-app.specify.md"
```

### If Plan Conflicts with Constitution:

```
Agent: "STOP. Plan violates constitution.md §X.Y
        Conflict: [describe conflict]
        Action: Either update plan OR request constitution amendment"
```

### If Task is Ambiguous:

```
Agent: "STOP. Task T-005 is ambiguous.
        Unclear: [specific ambiguity]
        Action: Refine specs/phase1-console-app.tasks.md"
```

---

## Communication Protocol

### Status Updates

Agents should provide progress updates:

```
Phase: I - Console App
Status: Implementing T-003 (Update Task Function)
Progress: 3/10 tasks complete
Blockers: None
```

### Clarification Requests

```
Question: Should task titles be unique?
Context: specs/phase1-console-app.specify.md §2.1
Impact: Affects data model design
```

### Completion Confirmations

```
Completed: T-003 (Update Task Function)
Files Modified:
  - src/services.py (lines 45-67)
  - src/models.py (line 12)
Tests: Passed manual testing
References: specs/phase1-console-app.tasks.md §3
```

---

## Integration with Claude Code

### CLAUDE.md Shim

The `CLAUDE.md` file in the root directory contains:

```markdown
@AGENTS.md
```

This ensures Claude Code loads these instructions automatically.

### Context Loading

When Claude Code starts:

1. Reads `CLAUDE.md`
2. Follows pointer to `AGENTS.md`
3. Loads `constitution.md`
4. Reads relevant spec files from `specs/`
5. Understands the Spec-Kit lifecycle

---

## Summary: The Agentic Dev Stack

```
┌─────────────────────────────────────────────────┐
│              AGENTS.md (The Brain)              │
│   Defines how agents should behave             │
└──────────────────┬──────────────────────────────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
      ▼            ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│Constitution│Spec-Kit  │Claude Code│
│(Principles)│(Architect)│(Executor) │
└──────────┘ └──────────┘ └──────────┘
      │            │            │
      │     Specify→Plan→Tasks→Implement
      │            │            │
      ▼            ▼            ▼
┌─────────────────────────────────────┐
│        Working Software              │
│  (Spec-Driven, High-Quality)        │
└─────────────────────────────────────┘
```

**Key Benefits:**

1. **Predictability:** Every line of code maps to a spec
2. **Auditability:** Full traceability from requirement to implementation
3. **Quality:** Specs reviewed before implementation
4. **Collaboration:** Multiple agents can work from same specs
5. **Evolution:** Easy to add phases without breaking existing code

---

## Final Reminder

**No code without specs.**  
**No specs without requirements.**  
**No requirements without understanding the problem.**

This is not just a process — it's the **only** way to build software in this project.

---

**Version:** 1.0  
**Last Updated:** December 25, 2025  
**Authority:** Panaversity Hackathon II - Agentic Dev Stack
