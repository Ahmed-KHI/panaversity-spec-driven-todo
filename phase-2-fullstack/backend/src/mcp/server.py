"""
MCP server registration and tool definitions.
[Task]: T-005
[From]: specs/003-phase-iii-chatbot/spec.md §6, plan.md §2.1.2

Provides OpenAI function calling format tool definitions for the agent.
"""

from typing import List, Dict, Any


def get_mcp_tools() -> List[Dict[str, Any]]:
    """
    Return OpenAI function calling format tool definitions.
    
    Returns:
        List of tool definitions compatible with OpenAI Chat Completions API
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task for the user with title, description, priority, due date, and recurrence options",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title (1-200 characters)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional task description"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Task priority level (default: medium)"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date in ISO format (YYYY-MM-DDTHH:MM:SS), e.g., '2026-01-25T15:00:00'"
                        },
                        "is_recurring": {
                            "type": "boolean",
                            "description": "Whether the task repeats (default: false)"
                        },
                        "recurrence_frequency": {
                            "type": "string",
                            "enum": ["daily", "weekly", "monthly", "yearly"],
                            "description": "How often the task repeats (only used if is_recurring is true)"
                        }
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "Get all tasks for the user, optionally filtered by completion status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "description": "Filter tasks by completion status (default: all)"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a specific task as completed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to mark as complete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update task title and/or description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New task title (optional)"
                        },
                        "description": {
                            "type": "string",
                            "description": "New task description (optional)"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Permanently delete a task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to delete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        }
    ]
