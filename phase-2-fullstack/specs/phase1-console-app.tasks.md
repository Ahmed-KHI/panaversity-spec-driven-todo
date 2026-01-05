# Phase I: Todo Console App - TASKS

## Document Information

**Phase:** Phase I - In-Memory Python Console Application  
**Status:** Active  
**Version:** 1.0  
**Last Updated:** December 25, 2025  
**Based On:** 
- phase1-console-app.specify.md v1.0
- phase1-console-app.plan.md v1.0

## 1. Task Overview

This document breaks down the Phase I implementation into atomic, testable work units. Each task should be completable in under 2 hours.

**Total Tasks:** 12  
**Estimated Time:** 12-16 hours  

## 2. Task List

### T-001: Create Task Data Model

**Priority:** HIGH  
**Depends On:** None  
**Estimated Time:** 1 hour  

**Description:**  
Create the Task dataclass with all required fields and methods.

**Specification Reference:**
- phase1-console-app.specify.md §3.2 (Data Requirements)
- phase1-console-app.plan.md §3.1 (Task Entity)

**Acceptance Criteria:**
- [ ] Task dataclass created with all fields (id, title, description, completed, created_at)
- [ ] Type hints for all fields
- [ ] `to_dict()` method implemented
- [ ] `__str__()` method implemented for display
- [ ] Docstring with task reference comment

**Files to Create/Modify:**
- `src/models.py` (create)

**Implementation Notes:**
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    """
    Represents a single todo task.
    
    [Task]: T-001
    [From]: phase1-console-app.specify.md §3.2
    """
    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
```

**Testing:**
- Create a Task instance manually
- Verify all fields set correctly
- Test `to_dict()` returns correct dictionary
- Test `__str__()` returns formatted string

---

### T-002: Implement TaskStorage Class

**Priority:** HIGH  
**Depends On:** T-001  
**Estimated Time:** 1.5 hours  

**Description:**  
Implement in-memory storage for tasks using dictionary.

**Specification Reference:**
- phase1-console-app.specify.md §3.2 (Data Requirements)
- phase1-console-app.plan.md §3.2 (Storage Design)

**Acceptance Criteria:**
- [ ] TaskStorage class created
- [ ] Dictionary-based storage (`_tasks: dict[int, Task]`)
- [ ] Auto-incrementing ID (`_next_id: int`)
- [ ] `add()` method implemented
- [ ] `get()` method implemented
- [ ] `get_all()` method implemented (sorted by created_at)
- [ ] `update()` method implemented
- [ ] `delete()` method implemented
- [ ] `toggle_complete()` method implemented
- [ ] `count()` method implemented (returns total, completed, pending)
- [ ] Type hints and docstrings

**Files to Create/Modify:**
- `src/models.py` (modify)

**Implementation Notes:**
- Use dictionary for O(1) lookups
- Return copies to prevent external mutation
- `get_all()` should return sorted list (oldest first)

**Testing:**
- Add 3 tasks, verify IDs are 1, 2, 3
- Get task by ID
- Update task title and description
- Delete task, verify it's gone
- Toggle complete status multiple times
- Test count with mix of completed/pending tasks

---

### T-003: Implement TaskService Class

**Priority:** HIGH  
**Depends On:** T-002  
**Estimated Time:** 2 hours  

**Description:**  
Implement business logic layer with validation.

**Specification Reference:**
- phase1-console-app.specify.md §3.1 (Functional Requirements)
- phase1-console-app.plan.md §4.1 (TaskService)

**Acceptance Criteria:**
- [ ] TaskService class created with TaskStorage dependency
- [ ] `create_task()` with validation (title required, length checks)
- [ ] `list_tasks()` returns all tasks
- [ ] `get_task()` with existence check
- [ ] `update_task()` with validation
- [ ] `delete_task()` with existence check
- [ ] `mark_complete()` with existence check
- [ ] `mark_incomplete()` with existence check
- [ ] `get_statistics()` returns dict with total/completed/pending
- [ ] All methods raise ValueError with clear messages on failure
- [ ] Type hints and docstrings

**Files to Create/Modify:**
- `src/services.py` (create)

**Validation Rules to Implement:**
- Title: not empty, 1-200 characters
- Description: 0-1000 characters
- Task ID: must exist in storage

**Testing:**
- Create task with valid data
- Create task with empty title (should fail)
- Create task with title > 200 chars (should fail)
- Update non-existent task (should fail)
- Delete non-existent task (should fail)
- Complete non-existent task (should fail)

---

### T-004: Create CLI Application Structure

**Priority:** HIGH  
**Depends On:** T-003  
**Estimated Time:** 1 hour  

**Description:**  
Create TodoCLI class with command routing and main loop.

**Specification Reference:**
- phase1-console-app.specify.md §3.3, §3.4 (Commands, UI)
- phase1-console-app.plan.md §5.1 (Command Structure)

**Acceptance Criteria:**
- [ ] TodoCLI class created with TaskService dependency
- [ ] Command dictionary mapping commands to methods
- [ ] All command aliases mapped
- [ ] `run()` method with main loop
- [ ] `show_welcome()` method
- [ ] Keyboard interrupt handling (Ctrl+C)
- [ ] Unknown command handling
- [ ] Stub methods for all commands (add, list, view, update, delete, complete, incomplete, help, exit)

**Files to Create/Modify:**
- `src/main.py` (create)

**Commands to Map:**
- add/a/new → cmd_add
- list/l/ls/show → cmd_list
- view/v/detail → cmd_view
- update/u/edit → cmd_update
- delete/d/remove/rm → cmd_delete
- complete/c/done → cmd_complete
- incomplete/ic/undone/pending → cmd_incomplete
- help/h/? → cmd_help
- exit/quit/q → cmd_exit

**Testing:**
- Run application
- Test unknown command handling
- Test Ctrl+C handling
- Verify all command aliases recognized

---

### T-005: Implement Add Command

**Priority:** HIGH  
**Depends On:** T-004  
**Estimated Time:** 1 hour  

**Description:**  
Implement the add task command with user prompts and error handling.

**Specification Reference:**
- phase1-console-app.specify.md §2.1 (Add Task user story)
- phase1-console-app.plan.md §5.2 (Command Implementations)

**Acceptance Criteria:**
- [ ] `cmd_add()` method implemented
- [ ] Prompts for title and description
- [ ] Calls `service.create_task()`
- [ ] Success message with task ID and title
- [ ] Error handling for validation failures
- [ ] Clear error messages displayed

**Files to Create/Modify:**
- `src/main.py` (modify)

**Output Format:**
```
✓ Task added successfully!
  ID: 1
  Title: Buy groceries
  Status: Pending
```

**Testing:**
- Add task with title only
- Add task with title and description
- Try adding task with empty title
- Try adding task with very long title (>200 chars)

---

### T-006: Implement List Command

**Priority:** HIGH  
**Depends On:** T-004  
**Estimated Time:** 1 hour  

**Description:**  
Implement the list tasks command with formatted output and statistics.

**Specification Reference:**
- phase1-console-app.specify.md §2.2 (View Task List user story)
- phase1-console-app.plan.md §5.2 (Command Implementations)

**Acceptance Criteria:**
- [ ] `cmd_list()` method implemented
- [ ] Handles empty list case with helpful message
- [ ] Displays all tasks with ID, status icon, and title
- [ ] Shows statistics at bottom (total, completed, pending)
- [ ] Clear formatting with borders

**Files to Create/Modify:**
- `src/main.py` (modify)

**Output Format:**
```
==================================================
         Your Todo List
==================================================

[1] [✗] Buy groceries
[2] [✓] Call dentist
[3] [✗] Finish project report

--------------------------------------------------
Total: 3 tasks (1 completed, 2 pending)
```

**Testing:**
- List when no tasks exist
- List with 1 task
- List with multiple tasks (some completed, some pending)

---

### T-007: Implement View Command

**Priority:** MEDIUM  
**Depends On:** T-004  
**Estimated Time:** 45 minutes  

**Description:**  
Implement the view task details command.

**Specification Reference:**
- phase1-console-app.specify.md §3.1 (F-006)
- phase1-console-app.plan.md §5.2 (Command Implementations)

**Acceptance Criteria:**
- [ ] `cmd_view()` method implemented
- [ ] Prompts for task ID
- [ ] Displays full task details (ID, title, description, status, created_at)
- [ ] Handles task not found error
- [ ] Handles invalid input (non-numeric)

**Files to Create/Modify:**
- `src/main.py` (modify)

**Output Format:**
```
==================================================
Task #1
==================================================
Title:       Buy groceries
Description: Milk, eggs, bread, butter
Status:      ✗ Pending
Created:     2025-12-25 14:30:00
```

**Testing:**
- View existing task
- Try viewing non-existent task ID
- Try entering non-numeric input

---

### T-008: Implement Update Command

**Priority:** HIGH  
**Depends On:** T-004  
**Estimated Time:** 1.5 hours  

**Description:**  
Implement the update task command with current value display.

**Specification Reference:**
- phase1-console-app.specify.md §2.3 (Update Task user story)
- phase1-console-app.plan.md §5.2 (Command Implementations)

**Acceptance Criteria:**
- [ ] `cmd_update()` method implemented
- [ ] Prompts for task ID
- [ ] Shows current title and prompts for new value
- [ ] Shows current description and prompts for new value
- [ ] Allows pressing Enter to keep current value
- [ ] Updates only fields with new values
- [ ] Success confirmation message
- [ ] Error handling for validation and not found

**Files to Create/Modify:**
- `src/main.py` (modify)

**Interaction Flow:**
```
Enter task ID: 1
Current title: Buy groceries
Enter new title (or press Enter to keep current): Buy groceries and fruits
Current description: Milk, eggs, bread, butter
Enter new description (or press Enter to keep current): [Enter]

✓ Task updated successfully!
```

**Testing:**
- Update title only
- Update description only
- Update both title and description
- Press Enter for both (no changes)
- Try updating non-existent task

---

### T-009: Implement Delete Command

**Priority:** HIGH  
**Depends On:** T-004  
**Estimated Time:** 1 hour  

**Description:**  
Implement the delete task command with confirmation.

**Specification Reference:**
- phase1-console-app.specify.md §2.4 (Delete Task user story)
- phase1-console-app.plan.md §5.2 (Command Implementations)

**Acceptance Criteria:**
- [ ] `cmd_delete()` method implemented
- [ ] Prompts for task ID
- [ ] Shows task title in confirmation prompt
- [ ] Asks for y/n confirmation
- [ ] Deletes only if user confirms with 'y'
- [ ] Shows cancellation message if 'n'
- [ ] Success confirmation message
- [ ] Error handling for not found and invalid input

**Files to Create/Modify:**
- `src/main.py` (modify)

**Interaction Flow:**
```
Enter task ID: 2
Are you sure you want to delete "Call dentist"? (y/n): y

✓ Task deleted successfully!
```

**Testing:**
- Delete task with confirmation
- Cancel deletion
- Try deleting non-existent task
- Try entering non-numeric input

---

### T-010: Implement Complete/Incomplete Commands

**Priority:** HIGH  
**Depends On:** T-004  
**Estimated Time:** 1 hour  

**Description:**  
Implement mark complete and mark incomplete commands.

**Specification Reference:**
- phase1-console-app.specify.md §2.5 (Mark as Complete user story)
- phase1-console-app.plan.md §5.2 (Command Implementations)

**Acceptance Criteria:**
- [ ] `cmd_complete()` method implemented
- [ ] `cmd_incomplete()` method implemented
- [ ] Both prompt for task ID
- [ ] Both call service methods
- [ ] Success confirmation shows current status
- [ ] Error handling for not found and invalid input

**Files to Create/Modify:**
- `src/main.py` (modify)

**Interaction Flow:**
```
> complete
Enter task ID: 1

✓ Task marked as completed!

> incomplete
Enter task ID: 1

✓ Task marked as pending!
```

**Testing:**
- Mark task as complete
- Mark same task as incomplete
- Toggle multiple times
- Try with non-existent task
- Verify list command shows updated status

---

### T-011: Implement Help Command

**Priority:** MEDIUM  
**Depends On:** T-004  
**Estimated Time:** 30 minutes  

**Description:**  
Implement help command showing all available commands.

**Specification Reference:**
- phase1-console-app.specify.md §3.3 (Commands)
- phase1-console-app.plan.md §5.2 (Command Implementations)

**Acceptance Criteria:**
- [ ] `cmd_help()` method implemented
- [ ] Lists all commands with descriptions
- [ ] Shows command aliases
- [ ] Clear, readable formatting

**Files to Create/Modify:**
- `src/main.py` (modify)

**Output Format:**
```
==================================================
         Available Commands
==================================================

  add       - Add a new task
  list      - View all tasks
  view      - View task details
  update    - Update a task
  delete    - Delete a task
  complete  - Mark task as complete
  incomplete- Mark task as incomplete
  help      - Show this help message
  exit      - Exit application

--------------------------------------------------
  Aliases: add/a/new, list/l/ls, view/v,
           update/u/edit, delete/d/rm,
           complete/c/done, incomplete/ic
```

**Testing:**
- Run help command
- Verify all commands listed
- Verify aliases shown

---

### T-012: Implement Exit Command & Application Entry Point

**Priority:** HIGH  
**Depends On:** T-004  
**Estimated Time:** 30 minutes  

**Description:**  
Implement exit command and main entry point to run the application.

**Specification Reference:**
- phase1-console-app.specify.md §3.3 (Commands)
- phase1-console-app.plan.md §5.1 (CLI Interface Design)

**Acceptance Criteria:**
- [ ] `cmd_exit()` method implemented
- [ ] Sets `self.running = False` to exit loop
- [ ] Shows goodbye message
- [ ] `if __name__ == "__main__":` block created
- [ ] Initializes TaskStorage, TaskService, and TodoCLI
- [ ] Calls `cli.run()`

**Files to Create/Modify:**
- `src/main.py` (modify)

**Implementation:**
```python
def cmd_exit(self):
    """Exit application."""
    print("\nGoodbye! 👋")
    self.running = False

if __name__ == "__main__":
    # [Task]: T-012
    # [From]: phase1-console-app.plan.md §5.1
    
    storage = TaskStorage()
    service = TaskService(storage)
    cli = TodoCLI(service)
    
    cli.run()
```

**Testing:**
- Run `python src/main.py`
- Verify welcome message displays
- Add a few tasks
- Run exit command
- Verify application exits cleanly
- Restart and verify data is lost (in-memory)

---

## 3. Task Dependencies

```
T-001 (Task Model)
  ↓
T-002 (Storage)
  ↓
T-003 (Service)
  ↓
T-004 (CLI Structure)
  ↓
├─ T-005 (Add)
├─ T-006 (List)
├─ T-007 (View)
├─ T-008 (Update)
├─ T-009 (Delete)
├─ T-010 (Complete/Incomplete)
├─ T-011 (Help)
└─ T-012 (Exit & Entry Point)
```

**Implementation Order:**
1. T-001 → T-002 → T-003 (Data & Logic layers)
2. T-004 (CLI structure)
3. T-005 through T-012 (Commands, can be parallel)

---

## 4. Testing Checklist

After completing all tasks, perform these tests:

### 4.1 Happy Path Test
- [ ] Start application
- [ ] Add 3 tasks
- [ ] List tasks
- [ ] View task details
- [ ] Update a task
- [ ] Mark task complete
- [ ] Mark task incomplete
- [ ] Delete a task
- [ ] Run help command
- [ ] Exit application

### 4.2 Error Handling Test
- [ ] Try empty title
- [ ] Try title > 200 characters
- [ ] Try description > 1000 characters
- [ ] Try viewing non-existent task
- [ ] Try updating non-existent task
- [ ] Try deleting non-existent task
- [ ] Try completing non-existent task
- [ ] Try invalid task ID (non-numeric)
- [ ] Test unknown command
- [ ] Test Ctrl+C interrupt

### 4.3 Edge Cases Test
- [ ] Add task with max length title (200 chars)
- [ ] Add task with max length description (1000 chars)
- [ ] Add 10 tasks, verify sequential IDs
- [ ] Toggle task complete/incomplete multiple times
- [ ] Update task with same values
- [ ] Cancel task deletion
- [ ] List with 0 tasks
- [ ] List with 1 task
- [ ] List with 10+ tasks

---

## 5. File Checklist

After completing all tasks, these files should exist:

```
src/
├── __init__.py              # Empty or with __all__
├── main.py                  # T-004, T-005-T-012
├── models.py                # T-001, T-002
└── services.py              # T-003
```

**File Sizes (Approximate):**
- `main.py`: ~300-400 lines
- `models.py`: ~100-150 lines
- `services.py`: ~150-200 lines

---

## 6. Implementation Notes

### 6.1 Code Comments

Every function should include:
```python
"""
Brief description.

[Task]: T-XXX
[From]: phase1-console-app.specify.md §X.X, 
        phase1-console-app.plan.md §Y.Y
"""
```

### 6.2 Type Hints

Required for all:
- Function parameters
- Function return types
- Class attributes

### 6.3 Error Messages

Format:
```
❌ Error: <clear message>
```

Examples:
- `❌ Error: Title is required`
- `❌ Error: Task not found with ID 999`
- `❌ Error: Invalid input: Please enter a number`

### 6.4 Success Messages

Format:
```
✓ <action> successfully!
```

Examples:
- `✓ Task added successfully!`
- `✓ Task updated successfully!`
- `✓ Task deleted successfully!`
- `✓ Task marked as completed!`

---

## 7. Completion Criteria

Phase I is complete when:

- [ ] All 12 tasks implemented
- [ ] All acceptance criteria met
- [ ] Happy path test passes
- [ ] Error handling test passes
- [ ] Edge cases test passes
- [ ] All files have proper structure
- [ ] Type hints present on all functions
- [ ] Docstrings with task references present
- [ ] Manual testing successful

---

## 8. Next Steps After Task Completion

1. **Create pyproject.toml** for UV
2. **Write README.md** with:
   - Project overview
   - Setup instructions
   - Usage guide with examples
   - Technology stack
3. **Update CLAUDE.md** (if needed)
4. **Create demo video** (90 seconds max)
5. **Prepare GitHub repository**
6. **Submit Phase I**

---

## 9. Time Tracking

| Task | Estimated | Actual | Notes |
|------|-----------|--------|-------|
| T-001 | 1h | | |
| T-002 | 1.5h | | |
| T-003 | 2h | | |
| T-004 | 1h | | |
| T-005 | 1h | | |
| T-006 | 1h | | |
| T-007 | 0.75h | | |
| T-008 | 1.5h | | |
| T-009 | 1h | | |
| T-010 | 1h | | |
| T-011 | 0.5h | | |
| T-012 | 0.5h | | |
| **Total** | **12.75h** | | |

---

## 10. Approval

**Prepared By:** Development Team  
**Based On:** 
- phase1-console-app.specify.md v1.0
- phase1-console-app.plan.md v1.0  

**Reviewed By:** Pending  
**Approved By:** Pending  

**Approval Date:** _____________

---

**References:**
- `phase1-console-app.specify.md` - Requirements
- `phase1-console-app.plan.md` - Architecture
- `constitution.md` - Coding standards
- `AGENTS.md` - Development workflow

**Next Action:** Begin implementation starting with T-001
