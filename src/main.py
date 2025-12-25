"""
Command-line interface for Todo application.

This module contains the TodoCLI class with all commands and the application entry point.

[Task]: T-004 to T-012
[From]: phase1-console-app.plan.md §5.1, §5.2
"""

from models import TaskStorage
from services import TaskService


class TodoCLI:
    """
    Command-line interface for Todo app.
    
    [Task]: T-004
    [From]: phase1-console-app.specify.md §3.3, §3.4
    """
    
    def __init__(self, service: TaskService):
        """
        Initialize TodoCLI with service dependency.
        
        Args:
            service: TaskService instance for business logic
        """
        self.service = service
        self.running = True
        
        # Command mapping with aliases
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
        """
        Main application loop.
        
        [Task]: T-004
        """
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
        """
        Display welcome message.
        
        [Task]: T-004
        """
        print("=" * 50)
        print("         Todo App - Phase I")
        print("         Spec-Driven Development")
        print("=" * 50)
        print("\nType 'help' for available commands")
    
    def cmd_add(self):
        """
        Add a new task.
        
        [Task]: T-005
        [From]: phase1-console-app.specify.md §2.1
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
    
    def cmd_list(self):
        """
        List all tasks.
        
        [Task]: T-006
        [From]: phase1-console-app.specify.md §2.2
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
    
    def cmd_view(self):
        """
        View single task details.
        
        [Task]: T-007
        [From]: phase1-console-app.specify.md §3.1 (F-006)
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
        except Exception:
            print(f"\n❌ Invalid input: Please enter a number")
    
    def cmd_update(self):
        """
        Update a task.
        
        [Task]: T-008
        [From]: phase1-console-app.specify.md §2.3
        """
        try:
            task_id = int(input("\nEnter task ID: "))
            task = self.service.get_task(task_id)
            
            print(f"\nCurrent title: {task.title}")
            new_title = input("Enter new title (or press Enter to keep current): ").strip()
            
            print(f"Current description: {task.description or '(none)'}")
            new_desc = input("Enter new description (or press Enter to keep current): ").strip()
            
            # Update only if new values provided
            self.service.update_task(
                task_id,
                new_title if new_title else None,
                new_desc if new_desc else None
            )
            
            print(f"\n✓ Task updated successfully!")
            
        except ValueError as e:
            print(f"\n❌ Error: {e}")
        except Exception:
            print(f"\n❌ Invalid input: Please enter a number")
    
    def cmd_delete(self):
        """
        Delete a task.
        
        [Task]: T-009
        [From]: phase1-console-app.specify.md §2.4
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
    
    def cmd_complete(self):
        """
        Mark task as complete.
        
        [Task]: T-010
        [From]: phase1-console-app.specify.md §2.5
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
        [From]: phase1-console-app.specify.md §2.5
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
    
    def cmd_help(self):
        """
        Show help message.
        
        [Task]: T-011
        [From]: phase1-console-app.specify.md §3.3
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
    
    def cmd_exit(self):
        """
        Exit application.
        
        [Task]: T-012
        [From]: phase1-console-app.specify.md §3.3
        """
        print("\nGoodbye! 👋")
        self.running = False


if __name__ == "__main__":
    """
    Application entry point.
    
    [Task]: T-012
    [From]: phase1-console-app.plan.md §5.1
    """
    # Initialize storage, service, and CLI
    storage = TaskStorage()
    service = TaskService(storage)
    cli = TodoCLI(service)
    
    # Run the application
    cli.run()
