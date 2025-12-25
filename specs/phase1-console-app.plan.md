# Phase I: Todo Console App - PLAN

## Document Information

**Phase:** Phase I - In-Memory Python Console Application  
**Status:** Active  
**Version:** 1.0  
**Last Updated:** December 25, 2025  
**Based On:** phase1-console-app.specify.md v1.0

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────┐
│         User (Command Line)                 │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│         CLI Interface (main.py)             │
│  - Parse commands                           │
│  - Display output                           │
│  - Handle user input                        │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│      Service Layer (services.py)            │
│  - Business logic                           │
│  - Validation                               │
│  - Task operations                          │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│      Data Layer (models.py)                 │
│  - Task data structure                      │
│  - In-memory storage                        │
│  - Data access                              │
└─────────────────────────────────────────────┘
```

### 1.2 Design Principles

1. **Separation of Concerns:** UI, business logic, and data are separate
2. **Single Responsibility:** Each module has one clear purpose
3. **Type Safety:** Use type hints throughout
4. **Validation First:** Validate input before processing
5. **User Feedback:** Clear messages for all operations
6. **Error Handling:** Graceful error handling at all layers

## 2. Component Design

### 2.1 Component Breakdown

| Component | File | Responsibility |
|-----------|------|----------------|
| CLI Interface | main.py | User interaction, command routing |
| Service Layer | services.py | Business logic, validation |
| Data Models | models.py | Task entity, storage |
| Utilities | utils.py | Helper functions, formatting |

### 2.2 Component Diagram

```
main.py
  ├─> services.py
  │     ├─> models.py
  │     └─> utils.py
  └─> utils.py
```

## 3. Data Model Design

### 3.1 Task Entity

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
    
    def to_dict(self) -> dict:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat()
        }
    
    def __str__(self) -> str:
        """String representation for display."""
        status = "✓" if self.completed else "✗"
        return f"[{self.id}] [{status}] {self.title}"
```

### 3.2 Storage Design

**In-Memory Storage:**

```python
class TaskStorage:
    """
    In-memory storage for tasks.
    
    [Task]: T-002
    [From]: phase1-console-app.specify.md §3.2
    """
    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1
    
    def add(self, title: str, description: Optional[str] = None) -> Task:
        """Add a new task and return it."""
        pass
    
    def get(self, task_id: int) -> Optional[Task]:
        """Get task by ID or None if not found."""
        pass
    
    def get_all(self) -> list[Task]:
        """Get all tasks ordered by creation time."""
        pass
    
    def update(self, task_id: int, title: Optional[str] = None, 
               description: Optional[str] = None) -> bool:
        """Update task. Returns True if successful."""
        pass
    
    def delete(self, task_id: int) -> bool:
        """Delete task. Returns True if successful."""
        pass
    
    def toggle_complete(self, task_id: int) -> bool:
        """Toggle task completion status. Returns True if successful."""
        pass
    
    def count(self) -> tuple[int, int, int]:
        """Return (total, completed, pending) counts."""
        pass
```

**Design Rationale:**
- Use dictionary for O(1) lookup by ID
- Maintain auto-incrementing ID counter
- Return copies to prevent external mutation
- Simple, straightforward implementation

## 4. Service Layer Design

### 4.1 TaskService

```python
class TaskService:
    """
    Business logic for task operations.
    
    [Task]: T-003
    [From]: phase1-console-app.specify.md §3.1
    """
    def __init__(self, storage: TaskStorage):
        self.storage = storage
    
    def create_task(self, title: str, description: Optional[str] = None) -> Task:
        """
        Create a new task with validation.
        Raises ValueError if validation fails.
        """
        # Validate title
        if not title or not title.strip():
            raise ValueError("Title is required")
        if len(title) > 200:
            raise ValueError("Title too long (max 200 characters)")
        
        # Validate description
        if description and len(description) > 1000:
            raise ValueError("Description too long (max 1000 characters)")
        
        return self.storage.add(title.strip(), description.strip() if description else None)
    
    def list_tasks(self) -> list[Task]:
        """Get all tasks."""
        return self.storage.get_all()
    
    def get_task(self, task_id: int) -> Task:
        """
        Get task by ID.
        Raises ValueError if task not found.
        """
        task = self.storage.get(task_id)
        if not task:
            raise ValueError(f"Task not found with ID {task_id}")
        return task
    
    def update_task(self, task_id: int, title: Optional[str] = None, 
                    description: Optional[str] = None) -> Task:
        """
        Update task with validation.
        Raises ValueError if validation fails or task not found.
        """
        # Validate task exists
        task = self.get_task(task_id)
        
        # Validate title if provided
        if title is not None:
            if not title.strip():
                raise ValueError("Title cannot be empty")
            if len(title) > 200:
                raise ValueError("Title too long (max 200 characters)")
        
        # Validate description if provided
        if description is not None and len(description) > 1000:
            raise ValueError("Description too long (max 1000 characters)")
        
        # Update
        self.storage.update(task_id, 
                          title.strip() if title else None, 
                          description.strip() if description else None)
        
        return self.get_task(task_id)
    
    def delete_task(self, task_id: int) -> Task:
        """
        Delete task.
        Raises ValueError if task not found.
        """
        task = self.get_task(task_id)  # Validate exists
        self.storage.delete(task_id)
        return task
    
    def mark_complete(self, task_id: int) -> Task:
        """
        Mark task as complete.
        Raises ValueError if task not found.
        """
        self.get_task(task_id)  # Validate exists
        self.storage.toggle_complete(task_id)
        return self.get_task(task_id)
    
    def mark_incomplete(self, task_id: int) -> Task:
        """
        Mark task as incomplete.
        Raises ValueError if task not found.
        """
        return self.mark_complete(task_id)  # Same implementation (toggle)
    
    def get_statistics(self) -> dict[str, int]:
        """Get task statistics."""
        total, completed, pending = self.storage.count()
        return {
            "total": total,
            "completed": completed,
            "pending": pending
        }
```

### 4.2 Validation Strategy

**Validation Rules:**

| Field | Rule | Error Message |
|-------|------|---------------|
| title | Not empty | "Title is required" |
| title | Length 1-200 | "Title too long (max 200 characters)" |
| description | Length 0-1000 | "Description too long (max 1000 characters)" |
| task_id | Exists in storage | "Task not found with ID {id}" |

**Validation Location:**
- All validation in TaskService (business logic layer)
- Storage layer assumes valid input
- CLI layer catches and displays validation errors

## 5. CLI Interface Design

### 5.1 Command Structure

```python
class TodoCLI:
    """
    Command-line interface for Todo app.
    
    [Task]: T-004
    [From]: phase1-console-app.specify.md §3.3, §3.4
    """
    def __init__(self, service: TaskService):
        self.service = service
        self.running = True
        
        # Command mapping
        self.commands = {
            "add": self.cmd_add,
            "a": self.cmd_add,
            "new": self.cmd_add,
            
            "list": self.cmd_list,
            "l": self.cmd_list,
            "ls": self.cmd_list,
            "show": self.cmd_list,
            
            "view": self.cmd_view,
            "v": self.cmd_view,
            "detail": self.cmd_view,
            
            "update": self.cmd_update,
            "u": self.cmd_update,
            "edit": self.cmd_update,
            
            "delete": self.cmd_delete,
            "d": self.cmd_delete,
            "remove": self.cmd_delete,
            "rm": self.cmd_delete,
            
            "complete": self.cmd_complete,
            "c": self.cmd_complete,
            "done": self.cmd_complete,
            
            "incomplete": self.cmd_incomplete,
            "ic": self.cmd_incomplete,
            "undone": self.cmd_incomplete,
            "pending": self.cmd_incomplete,
            
            "help": self.cmd_help,
            "h": self.cmd_help,
            "?": self.cmd_help,
            
            "exit": self.cmd_exit,
            "quit": self.cmd_exit,
            "q": self.cmd_exit,
        }
    
    def run(self):
        """Main application loop."""
        self.show_welcome()
        
        while self.running:
            try:
                command = input("\n> ").strip().lower()
                
                if not command:
                    continue
                
                if command in self.commands:
                    self.commands[command]()
                else:
                    print(f"❌ Unknown command: {command}")
                    print("   Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
    
    def show_welcome(self):
        """Display welcome message."""
        print("=" * 50)
        print("         Todo App - Phase I")
        print("         Spec-Driven Development")
        print("=" * 50)
        print("\nType 'help' for available commands")
    
    # Command implementations (see below)
    def cmd_add(self): pass
    def cmd_list(self): pass
    def cmd_view(self): pass
    def cmd_update(self): pass
    def cmd_delete(self): pass
    def cmd_complete(self): pass
    def cmd_incomplete(self): pass
    def cmd_help(self): pass
    def cmd_exit(self): pass
```

### 5.2 Command Implementations

#### Add Command

```python
def cmd_add(self):
    """
    Add a new task.
    [Task]: T-005
    """
    print("\n--- Add New Task ---")
    
    title = input("Enter task title: ").strip()
    description = input("Enter task description (optional): ").strip()
    
    try:
        task = self.service.create_task(
            title, 
            description if description else None
        )
        
        print(f"\n✓ Task added successfully!")
        print(f"  ID: {task.id}")
        print(f"  Title: {task.title}")
        print(f"  Status: Pending")
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
```

#### List Command

```python
def cmd_list(self):
    """
    List all tasks.
    [Task]: T-006
    """
    tasks = self.service.list_tasks()
    
    if not tasks:
        print("\n📝 Your todo list is empty!")
        print("   Use 'add' to create your first task")
        return
    
    print("\n" + "=" * 50)
    print("         Your Todo List")
    print("=" * 50)
    
    for task in tasks:
        print(f"\n{task}")
    
    stats = self.service.get_statistics()
    print("\n" + "-" * 50)
    print(f"Total: {stats['total']} tasks "
          f"({stats['completed']} completed, {stats['pending']} pending)")
```

#### View Command

```python
def cmd_view(self):
    """
    View single task details.
    [Task]: T-007
    """
    try:
        task_id = int(input("\nEnter task ID: "))
        task = self.service.get_task(task_id)
        
        print("\n" + "=" * 50)
        print(f"Task #{task.id}")
        print("=" * 50)
        print(f"Title:       {task.title}")
        print(f"Description: {task.description or '(none)'}")
        print(f"Status:      {'✓ Completed' if task.completed else '✗ Pending'}")
        print(f"Created:     {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
    except Exception as e:
        print(f"\n❌ Invalid input: Please enter a number")
```

#### Update Command

```python
def cmd_update(self):
    """
    Update a task.
    [Task]: T-008
    """
    try:
        task_id = int(input("\nEnter task ID: "))
        task = self.service.get_task(task_id)
        
        print(f"\nCurrent title: {task.title}")
        new_title = input("Enter new title (or press Enter to keep current): ").strip()
        
        print(f"Current description: {task.description or '(none)'}")
        new_desc = input("Enter new description (or press Enter to keep current): ").strip()
        
        # Update only if new values provided
        updated_task = self.service.update_task(
            task_id,
            new_title if new_title else None,
            new_desc if new_desc else None
        )
        
        print(f"\n✓ Task updated successfully!")
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
    except Exception:
        print(f"\n❌ Invalid input: Please enter a number")
```

#### Delete Command

```python
def cmd_delete(self):
    """
    Delete a task.
    [Task]: T-009
    """
    try:
        task_id = int(input("\nEnter task ID: "))
        task = self.service.get_task(task_id)
        
        confirm = input(f'Are you sure you want to delete "{task.title}"? (y/n): ').lower()
        
        if confirm == 'y':
            self.service.delete_task(task_id)
            print(f"\n✓ Task deleted successfully!")
        else:
            print(f"\n❌ Deletion cancelled")
            
    except ValueError as e:
        print(f"\n❌ Error: {e}")
    except Exception:
        print(f"\n❌ Invalid input: Please enter a number")
```

#### Complete/Incomplete Commands

```python
def cmd_complete(self):
    """
    Mark task as complete.
    [Task]: T-010
    """
    try:
        task_id = int(input("\nEnter task ID: "))
        task = self.service.mark_complete(task_id)
        
        status = "completed" if task.completed else "pending"
        print(f"\n✓ Task marked as {status}!")
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
    except Exception:
        print(f"\n❌ Invalid input: Please enter a number")

def cmd_incomplete(self):
    """
    Mark task as incomplete.
    [Task]: T-010
    """
    try:
        task_id = int(input("\nEnter task ID: "))
        task = self.service.mark_incomplete(task_id)
        
        status = "completed" if task.completed else "pending"
        print(f"\n✓ Task marked as {status}!")
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
    except Exception:
        print(f"\n❌ Invalid input: Please enter a number")
```

#### Help Command

```python
def cmd_help(self):
    """
    Show help message.
    [Task]: T-011
    """
    print("\n" + "=" * 50)
    print("         Available Commands")
    print("=" * 50)
    print("\n  add       - Add a new task")
    print("  list      - View all tasks")
    print("  view      - View task details")
    print("  update    - Update a task")
    print("  delete    - Delete a task")
    print("  complete  - Mark task as complete")
    print("  incomplete- Mark task as incomplete")
    print("  help      - Show this help message")
    print("  exit      - Exit application")
    print("\n" + "-" * 50)
    print("  Aliases: add/a/new, list/l/ls, view/v,")
    print("           update/u/edit, delete/d/rm,")
    print("           complete/c/done, incomplete/ic")
```

#### Exit Command

```python
def cmd_exit(self):
    """
    Exit application.
    [Task]: T-012
    """
    print("\nGoodbye! 👋")
    self.running = False
```

## 6. File Structure

```
hackathon-todo/
├── .spec-kit/
│   └── config.yaml
├── specs/
│   ├── phase1-console-app.specify.md
│   ├── phase1-console-app.plan.md      ← This file
│   └── phase1-console-app.tasks.md     ← Next to create
├── src/
│   ├── __init__.py
│   ├── main.py           # Entry point, CLI interface
│   ├── models.py         # Task entity, TaskStorage
│   ├── services.py       # TaskService with business logic
│   └── utils.py          # Helper functions (if needed)
├── tests/               # Optional for Phase I
│   └── test_manual.md   # Manual test scenarios
├── constitution.md
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── pyproject.toml       # UV project configuration
└── .gitignore
```

## 7. Dependencies

### 7.1 Python Standard Library

All features can be implemented using standard library:

- `dataclasses` - For Task model
- `datetime` - For timestamps
- `typing` - For type hints

### 7.2 Optional Dependencies

For enhanced UX (optional, not required):

- `rich` - For colored output and tables
- `click` - For better CLI structure

**Recommendation:** Start with standard library only. Add optional dependencies only if time permits.

## 8. Error Handling Strategy

### 8.1 Error Hierarchy

```
User Input → CLI Layer → Service Layer → Storage Layer
              ↓              ↓              ↓
         Catch All      ValueError    Assumed Valid
         Exceptions    (Validation)
              ↓              ↓
        Display Error  Display Error
```

### 8.2 Error Response Format

```
❌ Error: <clear message>
   <helpful hint or suggestion>
```

**Examples:**
- `❌ Error: Title is required`
- `❌ Error: Task not found with ID 999`
- `❌ Error: Title too long (max 200 characters)`

## 9. Testing Strategy

### 9.1 Manual Testing Checklist

See acceptance test scenarios in `phase1-console-app.specify.md` §10.

### 9.2 Test Data

```python
# Example tasks for testing
test_tasks = [
    ("Buy groceries", "Milk, eggs, bread, butter"),
    ("Call dentist", "Schedule appointment for next week"),
    ("Finish project report", "Due Friday 5 PM"),
    ("Review code", "Focus on error handling"),
    ("Write documentation", "Phase I specification and plan"),
]
```

## 10. Performance Considerations

### 10.1 Complexity Analysis

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Add task | O(1) | O(1) |
| Get task by ID | O(1) | O(1) |
| List all tasks | O(n) | O(n) |
| Update task | O(1) | O(1) |
| Delete task | O(1) | O(1) |
| Toggle complete | O(1) | O(1) |
| Get statistics | O(n) | O(1) |

Where n = number of tasks

### 10.2 Performance Targets

- Command execution < 100ms ✓ (all O(1) or O(n))
- Support 1000 tasks ✓ (dictionary scales well)
- Startup time < 500ms ✓ (no external dependencies)

## 11. Security Considerations

### 11.1 Phase I Security

- Input validation (length checks)
- No external network access
- No file system access
- Single user, single session

### 11.2 Future Security (Phase II+)

- SQL injection prevention (SQLModel handles this)
- Authentication and authorization
- Secrets management
- HTTPS for API

## 12. Deployment Plan

### 12.1 Setup Requirements

1. Python 3.13+ installed
2. UV package manager installed
3. Clone repository
4. Run `uv sync` (if using pyproject.toml)
5. Run `python src/main.py`

### 12.2 PyProject.toml

```toml
[project]
name = "hackathon-todo"
version = "0.1.0"
description = "Todo app - Spec-Driven Development"
requires-python = ">=3.13"
dependencies = []

[project.optional-dependencies]
dev = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## 13. Success Metrics

### 13.1 Functional Completeness

- [ ] All 5 Basic Level features implemented
- [ ] All commands working with aliases
- [ ] All validation rules enforced
- [ ] All error cases handled gracefully

### 13.2 Code Quality

- [ ] Type hints on all functions
- [ ] Docstrings on all public functions
- [ ] PEP 8 compliant
- [ ] Modular structure (separation of concerns)
- [ ] Task reference comments in all code

### 13.3 Documentation

- [ ] README with setup instructions
- [ ] CLAUDE.md with usage instructions
- [ ] All spec files complete
- [ ] Manual test scenarios documented

## 14. Known Limitations (Phase I)

1. **No Persistence:** Data lost on exit (by design)
2. **Single User:** No multi-user support
3. **No Search/Filter:** Coming in Phase V
4. **No Priorities/Tags:** Coming in Phase V
5. **No Due Dates:** Coming in Phase V
6. **No Undo:** Cannot recover deleted tasks

These are intentional Phase I limitations. They will be addressed in future phases.

## 15. Migration Path (Future Phases)

### 15.1 Phase I → Phase II

- Replace TaskStorage with SQLModel + Neon DB
- Keep same service layer interface
- Add authentication layer
- Build REST API around service layer
- Create Next.js frontend

### 15.2 Service Layer Stability

The service layer interface (`TaskService`) is designed to remain stable across phases:

```python
# Phase I: In-memory
storage = TaskStorage()
service = TaskService(storage)

# Phase II: Database
session = create_session()
storage = SQLModelTaskStorage(session)
service = TaskService(storage)  # Same interface!
```

## 16. Next Steps

1. **Review this plan** with specification (phase1-console-app.specify.md)
2. **Create tasks breakdown** (phase1-console-app.tasks.md)
3. **Implement via Claude Code** following tasks
4. **Manual testing** using acceptance scenarios
5. **Documentation** (README.md, CLAUDE.md)
6. **Demo video** (90 seconds max)

## 17. Approval

**Prepared By:** Architecture Team  
**Based On:** phase1-console-app.specify.md v1.0  
**Reviewed By:** Pending  
**Approved By:** Pending  

**Approval Date:** _____________

---

**References:**
- `phase1-console-app.specify.md` - Requirements specification
- `constitution.md` - Project principles
- `AGENTS.md` - Development workflow
- Python 3.13 Documentation
- PEP 8 Style Guide

**Next Document:** `phase1-console-app.tasks.md`
