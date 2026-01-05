"""
Business logic layer for Todo application.

This module contains TaskService with validation and business logic.

[Task]: T-003
[From]: phase1-console-app.plan.md §4.1
"""

from typing import Optional
from models import Task, TaskStorage


class TaskService:
    """
    Business logic for task operations with validation.
    
    [Task]: T-003
    [From]: phase1-console-app.specify.md §3.1
    """
    
    def __init__(self, storage: TaskStorage):
        """
        Initialize TaskService with storage dependency.
        
        Args:
            storage: TaskStorage instance for data persistence
        """
        self.storage = storage
    
    def create_task(self, title: str, description: Optional[str] = None) -> Task:
        """
        Create a new task with validation.
        
        Args:
            title: Task title (required)
            description: Optional task description
            
        Returns:
            The newly created Task
            
        Raises:
            ValueError: If validation fails
        """
        # Validate title
        if not title or not title.strip():
            raise ValueError("Title is required")
        
        title = title.strip()
        if len(title) > 200:
            raise ValueError("Title too long (max 200 characters)")
        
        # Validate description
        if description:
            description = description.strip()
            if len(description) > 1000:
                raise ValueError("Description too long (max 1000 characters)")
        
        return self.storage.add(title, description if description else None)
    
    def list_tasks(self) -> list[Task]:
        """
        Get all tasks.
        
        Returns:
            List of all tasks
        """
        return self.storage.get_all()
    
    def get_task(self, task_id: int) -> Task:
        """
        Get task by ID.
        
        Args:
            task_id: The ID of the task to retrieve
            
        Returns:
            The requested Task
            
        Raises:
            ValueError: If task not found
        """
        task = self.storage.get(task_id)
        if not task:
            raise ValueError(f"Task not found with ID {task_id}")
        return task
    
    def update_task(self, task_id: int, title: Optional[str] = None, 
                    description: Optional[str] = None) -> Task:
        """
        Update task with validation.
        
        Args:
            task_id: The ID of the task to update
            title: New title (None to keep current)
            description: New description (None to keep current)
            
        Returns:
            The updated Task
            
        Raises:
            ValueError: If validation fails or task not found
        """
        # Validate task exists
        task = self.get_task(task_id)
        
        # Validate title if provided
        if title is not None:
            title = title.strip()
            if not title:
                raise ValueError("Title cannot be empty")
            if len(title) > 200:
                raise ValueError("Title too long (max 200 characters)")
        
        # Validate description if provided
        if description is not None:
            description = description.strip()
            if len(description) > 1000:
                raise ValueError("Description too long (max 1000 characters)")
        
        # Update
        self.storage.update(task_id, title, description if description else None)
        
        return self.get_task(task_id)
    
    def delete_task(self, task_id: int) -> Task:
        """
        Delete task.
        
        Args:
            task_id: The ID of the task to delete
            
        Returns:
            The deleted Task
            
        Raises:
            ValueError: If task not found
        """
        task = self.get_task(task_id)  # Validate exists
        self.storage.delete(task_id)
        return task
    
    def mark_complete(self, task_id: int) -> Task:
        """
        Mark task as complete (or toggle if already complete).
        
        Args:
            task_id: The ID of the task to mark complete
            
        Returns:
            The updated Task
            
        Raises:
            ValueError: If task not found
        """
        self.get_task(task_id)  # Validate exists
        self.storage.toggle_complete(task_id)
        return self.get_task(task_id)
    
    def mark_incomplete(self, task_id: int) -> Task:
        """
        Mark task as incomplete (same as mark_complete - toggles status).
        
        Args:
            task_id: The ID of the task to mark incomplete
            
        Returns:
            The updated Task
            
        Raises:
            ValueError: If task not found
        """
        return self.mark_complete(task_id)  # Same implementation (toggle)
    
    def get_statistics(self) -> dict[str, int]:
        """
        Get task statistics.
        
        Returns:
            Dictionary with 'total', 'completed', and 'pending' counts
        """
        total, completed, pending = self.storage.count()
        return {
            "total": total,
            "completed": completed,
            "pending": pending
        }
