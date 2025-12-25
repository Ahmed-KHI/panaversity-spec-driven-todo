# Spec-Driven Development Process

This document shows the actual workflow used to build Phase I using Claude Code and Spec-Kit.

## Phase I Development Journey

### Step 1: Project Initialization
```bash
# Initialize project structure
uv init hackathon-todo
cd hackathon-todo

# Initialize Spec-Kit
uv add spec-kit-plus
spec-kit init
```

**Output:** Created `.spec-kit/config.yaml` and project structure

---

### Step 2: Specification Phase
```bash
# Create specification
claude specify phase1-console-app
```

**Prompts and Responses:**

**Q: What is the purpose of this feature?**  
A: Build a command-line todo application that stores tasks in memory with 5 basic features: Add, Delete, Update, View, and Mark Complete.

**Q: Who are the users?**  
A: Individual users managing personal tasks via command line.

**Q: What are the user stories?**  
A: See [phase1-console-app.specify.md](phase1-console-app.specify.md) §2 (5 user stories documented)

**Q: What are the acceptance criteria?**  
A: See each user story in specification - detailed acceptance criteria for all features

**Q: What are the constraints?**  
A:
- Python 3.13+
- In-memory storage only
- No external dependencies preferred
- Must use UV package manager

**Q: What is out of scope?**  
A:
- Database persistence (Phase II)
- Web interface (Phase II)
- User authentication (Phase II)
- Advanced features (Phase V)

**Output:** Created `specs/phase1-console-app.specify.md`

---

### Step 3: Planning Phase
```bash
# Generate technical plan
claude plan phase1-console-app
```

**Process:**
1. Read specification
2. Designed 3-layer architecture
3. Created data model (Task entity)
4. Planned storage strategy
5. Designed service layer with validation
6. Designed CLI with command routing

**Key Decisions:**
- Dictionary-based storage (O(1) lookups)
- Dataclass for Task entity
- Service layer for validation
- Command pattern for CLI

**Output:** Created `specs/phase1-console-app.plan.md`

---

### Step 4: Task Breakdown
```bash
# Break into tasks
claude tasks phase1-console-app
```

**Process:**
1. Analyzed plan
2. Identified 12 atomic tasks
3. Determined dependencies
4. Assigned IDs (T-001 to T-012)
5. Created acceptance criteria per task

**Task List:**
- T-001: Create Task Model
- T-002: Implement TaskStorage
- T-003: Implement TaskService
- T-004: Create CLI Structure
- T-005 to T-012: Implement Commands

**Output:** Created `specs/phase1-console-app.tasks.md`

---

### Step 5: Implementation Phase
```bash
# Implement tasks in order
claude implement T-001  # Task Model
claude implement T-002  # Storage
claude implement T-003  # Service
claude implement T-004  # CLI Structure
claude implement T-005  # Add Command
claude implement T-006  # List Command
claude implement T-007  # View Command
claude implement T-008  # Update Command
claude implement T-009  # Delete Command
claude implement T-010  # Complete/Incomplete
claude implement T-011  # Help Command
claude implement T-012  # Exit & Entry Point
```

**For each task:**
1. Read task specification
2. Review referenced spec and plan sections
3. Generate code with task references
4. Add type hints and docstrings
5. Verify acceptance criteria

**Output:** 
- `src/models.py` (T-001, T-002)
- `src/services.py` (T-003)
- `src/main.py` (T-004 to T-012)

---

### Step 6: Testing
```bash
# Run the application
python src/main.py
```

**Manual Testing:**
- ✅ Happy path test passed
- ✅ Error handling test passed
- ✅ Edge cases test passed

---

### Step 7: Review
```bash
# Review implementation
claude review phase1-console-app
```

**Review Results:**
- ✅ All 12 tasks implemented
- ✅ Task references present in code
- ✅ Type hints on all functions
- ✅ Docstrings present
- ✅ Error handling implemented
- ✅ All acceptance criteria met

---

## Workflow Diagram

```
                    SPEC-DRIVEN DEVELOPMENT WORKFLOW
                                                                    
┌─────────────────────────────────────────────────────────────────┐
│                     1. SPECIFY (WHAT)                           │
│  claude specify phase1-console-app                              │
│  → 5 user stories documented                                    │
│  → Acceptance criteria defined                                  │
│  → Output: specs/phase1-console-app.specify.md                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     2. PLAN (HOW)                               │
│  claude plan phase1-console-app                                 │
│  → Architecture designed                                        │
│  → Components defined                                           │
│  → Output: specs/phase1-console-app.plan.md                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     3. TASKS (BREAKDOWN)                        │
│  claude tasks phase1-console-app                                │
│  → 12 atomic tasks created                                      │
│  → Dependencies mapped                                          │
│  → Output: specs/phase1-console-app.tasks.md                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     4. IMPLEMENT (CODE)                         │
│  claude implement T-001                                         │
│  claude implement T-002                                         │
│  ... (T-003 to T-012)                                           │
│  → Code generated with task references                          │
│  → Output: src/models.py, src/services.py, src/main.py         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     5. REVIEW & TEST                            │
│  claude review phase1-console-app                               │
│  python src/main.py (manual testing)                            │
│  → All tasks verified                                           │
│  → All tests passed                                             │
└─────────────────────────────────────────────────────────────────┘
```

## Time Tracking

| Phase | Command | Time Spent |
|-------|---------|------------|
| Specify | `claude specify phase1-console-app` | 2 hours |
| Plan | `claude plan phase1-console-app` | 2 hours |
| Tasks | `claude tasks phase1-console-app` | 1 hour |
| Implement | `claude implement T-001 to T-012` | 10 hours |
| Review | `claude review phase1-console-app` | 1 hour |
| **Total** | | **16 hours** |

## Key Benefits of This Workflow

1. **No Code Before Specs** - Every line of code justified by specification
2. **Full Traceability** - Code references link back to requirements
3. **Incremental Progress** - Small, testable tasks
4. **Quality Gates** - Review at each phase
5. **Reproducible** - Process can be repeated for Phase II-V

## Lessons Learned

1. **Detailed Specs Save Time** - Clear specs made implementation straightforward
2. **Task Breakdown Critical** - Atomic tasks easy to estimate and complete
3. **Type Hints Helpful** - Caught issues early in development
4. **Iterative Review** - Regular review prevents scope creep

## Next Phase

Use same workflow for Phase II (Web Application):

```bash
claude specify phase2-web-app
claude plan phase2-web-app
claude tasks phase2-web-app
claude implement <task-ids>
```

---

**This document demonstrates the actual Spec-Driven Development process used to build Phase I.**
