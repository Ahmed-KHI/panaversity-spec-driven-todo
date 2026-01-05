"""
Data models for Todo application.

This module contains the Task entity and TaskStorage class for in-memory storage.

[Task]: T-001, T-002
[From]: phase1-console-app.plan.md §3.1, §3.2
"""

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


class TaskStorage:
    """
    In-memory storage for tasks using dictionary.
    
    [Task]: T-002
    [From]: phase1-console-app.specify.md §3.2, phase1-console-app.plan.md §3.2
    """
    
    def __init__(self):
        """Initialize empty task storage."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1
    
    def add(self, title: str, description: Optional[str] = None) -> Task:
        """
        Add a new task and return it.
        
        Args:
            title: Task title (already validated)
            description: Optional task description
            
        Returns:
            The newly created Task
        """
        task = Task(
            id=self._next_id,
            title=title,
            description=description,
            completed=False,
            created_at=datetime.now()
        )
        
        self._tasks[self._next_id] = task
        self._next_id += 1
        
        return task
    
    def get(self, task_id: int) -> Optional[Task]:
        """
        Get task by ID or None if not found.
        
        Args:
            task_id: The ID of the task to retrieve
            
        Returns:
            Task if found, None otherwise
        """
        return self._tasks.get(task_id)
    
    def get_all(self) -> list[Task]:
        """
        Get all tasks ordered by creation time (oldest first).
        
        Returns:
            List of all tasks sorted by created_at
        """
        return sorted(self._tasks.values(), key=lambda t: t.created_at)
    
    def update(self, task_id: int, title: Optional[str] = None, 
               description: Optional[str] = None) -> bool:
        """
        Update task title and/or description.
        
        Args:
            task_id: The ID of the task to update
            title: New title (None to keep current)
            description: New description (None to keep current)
            
        Returns:
            True if successful, False if task not found
        """
        task = self._tasks.get(task_id)
        if not task:
            return False
        
        if title is not None:
            task.title = title
        
        if description is not None:
            task.description = description
        
        return True
    
    def delete(self, task_id: int) -> bool:
        """
        Delete task by ID.
        
        Args:
            task_id: The ID of the task to delete
            
        Returns:
            True if successful, False if task not found
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False
    
    def toggle_complete(self, task_id: int) -> bool:
        """
        Toggle task completion status.
        
        Args:
            task_id: The ID of the task to toggle
            
        Returns:
            True if successful, False if task not found
        """
        task = self._tasks.get(task_id)
        if not task:
            return False
        
        task.completed = not task.completed
        return True
    
    def count(self) -> tuple[int, int, int]:
        """
        Return task counts.
        
        Returns:
            Tuple of (total, completed, pending) counts
        """
        total = len(self._tasks)
        completed = sum(1 for task in self._tasks.values() if task.completed)
        pending = total - completed
        
        return (total, completed, pending)
