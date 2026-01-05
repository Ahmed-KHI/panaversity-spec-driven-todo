# Phase I: Todo Console App - SPECIFICATION

## Document Information

**Phase:** Phase I - In-Memory Python Console Application  
**Status:** Active  
**Version:** 1.0  
**Last Updated:** December 25, 2025  

## 1. Overview

### 1.1 Purpose

Build a command-line todo application that stores tasks in memory using Python 3.13+, UV package manager, and spec-driven development with Claude Code and Spec-Kit Plus.

### 1.2 Scope

Implement all 5 Basic Level features:
1. Add Task
2. Delete Task
3. Update Task
4. View Task List
5. Mark as Complete

### 1.3 Out of Scope (For Phase I)

- Database persistence (Phase II)
- Web interface (Phase II)
- User authentication (Phase II)
- AI chatbot (Phase III)
- Advanced features (Priority, Tags, Due Dates) (Phase V)

## 2. User Stories

### 2.1 Add Task

**As a** user  
**I want to** add a new task to my todo list  
**So that** I can track things I need to do  

**Acceptance Criteria:**
- User can enter a task title (required)
- User can optionally enter a task description
- Task title must be 1-200 characters
- Task description can be up to 1000 characters
- Task is assigned a unique ID automatically
- Task is marked as "pending" by default
- System confirms task creation with ID and title
- Empty titles are rejected with clear error message

**Example Interaction:**
```
> add
Enter task title: Buy groceries
Enter task description (optional): Milk, eggs, bread, butter
✓ Task added successfully!
  ID: 1
  Title: Buy groceries
  Status: Pending
```

### 2.2 View Task List

**As a** user  
**I want to** view all my tasks  
**So that** I can see what needs to be done  

**Acceptance Criteria:**
- Display all tasks in a formatted list
- Show task ID, title, and status for each task
- Indicate completion status clearly (e.g., [✓] or [✗])
- Show message if no tasks exist
- Tasks displayed in order of creation (oldest first)
- Long titles are truncated with "..." if needed
- Description is not shown in list view (only in detail view)

**Example Output:**
```
=== Your Todo List ===

[1] [✗] Buy groceries
[2] [✓] Call dentist
[3] [✗] Finish project report

Total: 3 tasks (1 completed, 2 pending)
```

### 2.3 Update Task

**As a** user  
**I want to** update a task's title or description  
**So that** I can correct mistakes or add more details  

**Acceptance Criteria:**
- User can update task by ID
- User can change title, description, or both
- Title validation rules apply (1-200 chars)
- Description validation rules apply (max 1000 chars)
- User can leave fields blank to keep current value
- System shows current values before update
- Invalid task IDs show clear error message
- System confirms successful update

**Example Interaction:**
```
> update
Enter task ID: 1
Current title: Buy groceries
Enter new title (or press Enter to keep current): Buy groceries and fruits
Current description: Milk, eggs, bread, butter
Enter new description (or press Enter to keep current): [Enter]
✓ Task updated successfully!
```

### 2.4 Delete Task

**As a** user  
**I want to** delete a task from my list  
**So that** I can remove tasks I no longer need  

**Acceptance Criteria:**
- User can delete task by ID
- System asks for confirmation before deleting
- Confirmation can be skipped with a flag (e.g., --force)
- Invalid task IDs show clear error message
- System confirms successful deletion
- Deleted tasks cannot be recovered (in Phase I)

**Example Interaction:**
```
> delete
Enter task ID: 2
Are you sure you want to delete "Call dentist"? (y/n): y
✓ Task deleted successfully!
```

### 2.5 Mark as Complete

**As a** user  
**I want to** mark a task as complete or incomplete  
**So that** I can track my progress  

**Acceptance Criteria:**
- User can toggle task completion status by ID
- Marking complete changes status from "pending" to "completed"
- Marking incomplete changes status from "completed" to "pending"
- Invalid task IDs show clear error message
- System confirms status change
- Status change is reflected immediately in list view

**Example Interaction:**
```
> complete
Enter task ID: 1
✓ Task marked as completed!

> incomplete
Enter task ID: 1
✓ Task marked as pending!
```

## 3. Functional Requirements

### 3.1 Core Features

| Feature | Priority | Description |
|---------|----------|-------------|
| F-001 | MUST | Add task with title and optional description |
| F-002 | MUST | View all tasks in formatted list |
| F-003 | MUST | Update task title and/or description |
| F-004 | MUST | Delete task by ID |
| F-005 | MUST | Mark task as complete/incomplete |
| F-006 | MUST | Display task details (ID, title, description, status) |
| F-007 | MUST | Input validation for title and description |
| F-008 | SHOULD | Show helpful error messages |
| F-009 | SHOULD | Confirm destructive actions (delete) |
| F-010 | COULD | Show task statistics (total, completed, pending) |

### 3.2 Data Requirements

#### Task Entity

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| id | integer | Yes | Auto-generated, unique, starts at 1 |
| title | string | Yes | 1-200 characters |
| description | string | No | 0-1000 characters |
| completed | boolean | Yes | Default: False |
| created_at | datetime | Yes | Auto-generated on creation |

### 3.3 Commands

The application must support these commands:

| Command | Aliases | Description |
|---------|---------|-------------|
| add | a, new | Add a new task |
| list | l, ls, show | View all tasks |
| view | v, detail | View single task details |
| update | u, edit | Update task title/description |
| delete | d, remove, rm | Delete a task |
| complete | c, done | Mark task as complete |
| incomplete | ic, undone, pending | Mark task as incomplete |
| help | h, ? | Show help message |
| exit | quit, q | Exit the application |

### 3.4 User Interface

**Menu System:**
```
=== Todo App - Phase I ===

Commands:
  add       - Add a new task
  list      - View all tasks
  view      - View task details
  update    - Update a task
  delete    - Delete a task
  complete  - Mark task as complete
  incomplete- Mark task as incomplete
  help      - Show this help message
  exit      - Exit application

> _
```

**Input Prompts:**
- Clear, descriptive prompts for all inputs
- Show current values when updating
- Indicate optional fields
- Provide examples where helpful

**Output Formatting:**
- Use emojis or symbols for visual clarity (✓, ✗, ✏️, 🗑️)
- Box drawing characters for tables (optional)
- Color coding (optional, Phase I - basic version acceptable)
- Consistent spacing and alignment

## 4. Non-Functional Requirements

### 4.1 Performance

- Command execution < 100ms for all operations
- Support up to 1000 tasks without degradation
- Startup time < 500ms

### 4.2 Usability

- Clear, concise error messages
- Intuitive command structure
- Minimal keystrokes for common operations
- Consistent command patterns

### 4.3 Reliability

- No data loss during session
- Graceful error handling
- No crashes on invalid input

### 4.4 Maintainability

- Clean, modular code structure
- Type hints for all functions
- Docstrings for all public functions
- Follow PEP 8 style guide

## 5. Constraints

### 5.1 Technical Constraints

- **Language:** Python 3.13+
- **Package Manager:** UV
- **Storage:** In-memory only (Python data structures)
- **Dependencies:** Minimal (standard library preferred)
- **Platform:** Cross-platform (Windows, macOS, Linux)

### 5.2 Development Constraints

- **Method:** Spec-driven development only
- **Tool:** Claude Code for implementation
- **No Manual Coding:** All code must be generated via specs
- **Testing:** Manual testing via console (automated tests optional)

## 6. Assumptions

1. User has Python 3.13+ installed
2. User has basic command-line familiarity
3. User has UV package manager installed
4. Single user per session (no concurrent access)
5. Data persistence not required (in-memory is acceptable)
6. Session ends when user exits (data lost on exit)

## 7. Dependencies

### 7.1 External Dependencies

Preferred: Use Python standard library only

Optional (if needed):
- `rich` - For enhanced terminal output (optional)
- `click` - For command-line interface (optional)

### 7.2 Internal Dependencies

None (self-contained application)

## 8. Success Criteria

### 8.1 Phase I Completion Criteria

- [ ] All 5 Basic Level features working
- [ ] All user stories satisfied
- [ ] All acceptance criteria met
- [ ] Clean, modular code structure
- [ ] Type hints present
- [ ] Error handling implemented
- [ ] Help system functional
- [ ] Manual testing passed for all features

### 8.2 Demo Requirements

**90-second demo must show:**
1. Adding 2-3 tasks
2. Viewing task list
3. Updating a task
4. Marking a task complete
5. Deleting a task
6. Error handling (invalid ID)

### 8.3 Documentation Requirements

- [ ] README.md with setup instructions
- [ ] CLAUDE.md with Claude Code usage
- [ ] This specification document
- [ ] Plan document (phase1-console-app.plan.md)
- [ ] Tasks document (phase1-console-app.tasks.md)

## 9. Future Considerations (Not Phase I)

- Database persistence (Phase II)
- Multi-user support with authentication (Phase II)
- Web interface (Phase II)
- AI chatbot interface (Phase III)
- Advanced features: priorities, tags, due dates (Phase V)
- Search and filter (Phase V)
- Recurring tasks (Phase V)

## 10. Acceptance Test Scenarios

### Test Scenario 1: Happy Path - Complete Workflow

```
1. Start application
2. Run 'add' command
   - Enter: "Write hackathon documentation"
   - Enter: "Phase I specification and plan"
   - Verify: Task created with ID 1
3. Run 'add' command
   - Enter: "Review code"
   - Enter: "" (no description)
   - Verify: Task created with ID 2
4. Run 'list' command
   - Verify: Both tasks shown, both pending
5. Run 'complete' command
   - Enter: 1
   - Verify: Task 1 marked complete
6. Run 'list' command
   - Verify: Task 1 shows complete, Task 2 shows pending
7. Run 'update' command
   - Enter: 2
   - Enter: "Review and refactor code"
   - Enter: "Focus on error handling"
   - Verify: Task 2 updated
8. Run 'view' command
   - Enter: 2
   - Verify: Full details shown with new title and description
9. Run 'delete' command
   - Enter: 1
   - Enter: y (confirm)
   - Verify: Task 1 deleted
10. Run 'list' command
    - Verify: Only Task 2 shown
11. Run 'exit' command
    - Verify: Application exits cleanly
```

**Expected Result:** All operations succeed with appropriate confirmations

### Test Scenario 2: Error Handling

```
1. Start application
2. Run 'delete' command with no tasks
   - Verify: Error message "No tasks available"
3. Run 'add' command with empty title
   - Enter: "" (empty)
   - Verify: Error "Title is required"
4. Run 'add' command with very long title (>200 chars)
   - Verify: Error "Title too long (max 200 characters)"
5. Add a task (ID 1)
6. Run 'complete' command with invalid ID
   - Enter: 999
   - Verify: Error "Task not found with ID 999"
7. Run 'update' command with invalid ID
   - Enter: 999
   - Verify: Error "Task not found with ID 999"
8. Run 'delete' command and cancel
   - Enter: 1
   - Enter: n (cancel)
   - Verify: Task not deleted, confirmation message shown
```

**Expected Result:** All errors handled gracefully with clear messages

### Test Scenario 3: Edge Cases

```
1. Start application
2. Add task with maximum length title (200 chars)
   - Verify: Accepted
3. Add task with maximum length description (1000 chars)
   - Verify: Accepted
4. Add 10 tasks rapidly
   - Verify: All IDs unique and sequential
5. Mark task complete, then incomplete, then complete again
   - Verify: Status toggles correctly each time
6. Update task to have same title as before
   - Verify: Update succeeds (idempotent)
7. View task list with 10 tasks
   - Verify: All displayed correctly with formatting
```

**Expected Result:** All edge cases handled correctly

## 11. Open Questions

None at this time. All requirements for Phase I are clearly defined.

## 12. Approval

**Prepared By:** Spec-Driven Development Team  
**Reviewed By:** Pending  
**Approved By:** Pending  

**Approval Date:** _____________

---

**Next Steps:**
1. Create `phase1-console-app.plan.md` (architecture and design)
2. Create `phase1-console-app.tasks.md` (task breakdown)
3. Implement via Claude Code following tasks

**References:**
- `constitution.md` - Project principles and constraints
- `AGENTS.md` - Agent behavior and workflow
- Hackathon II Requirements Document
