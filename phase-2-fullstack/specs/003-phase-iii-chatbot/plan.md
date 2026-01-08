# Phase III: AI-Powered Todo Chatbot - TECHNICAL PLAN

**Project:** Hackathon II - The Evolution of Todo  
**Phase:** III - AI Chatbot with MCP Integration  
**Document Type:** Technical Architecture & Implementation Plan  
**Version:** 1.0  
**Date:** January 8, 2026  
**References:** spec.md (Phase III Specification)

---

## 1. Architecture Overview

### 1.1 Component Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                                 │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  Dashboard (app/dashboard/page.tsx)                          │    │
│  │  - Existing task list view                                   │    │
│  │  - NEW: "Chat" button/link                                   │    │
│  └──────────────┬───────────────────────────────────────────────┘    │
│                 │                                                      │
│                 ▼                                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  Chat Page (app/chat/page.tsx) - NEW                        │    │
│  │  - ChatInterface component wrapper                           │    │
│  │  - Authentication check                                      │    │
│  │  - User ID extraction                                        │    │
│  └──────────────┬───────────────────────────────────────────────┘    │
│                 │                                                      │
│                 ▼                                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  ChatInterface (components/ChatInterface.tsx) - NEW          │    │
│  │  - OpenAI ChatKit component                                  │    │
│  │  - Domain key configuration                                  │    │
│  │  - JWT token injection                                       │    │
│  │  - API endpoint configuration                                │    │
│  └──────────────┬───────────────────────────────────────────────┘    │
│                 │                                                      │
└─────────────────┼──────────────────────────────────────────────────────┘
                  │ POST /api/{user_id}/chat
                  │ { conversation_id, message }
                  ▼
┌───────────────────────────────────────────────────────────────────────┐
│                         BACKEND LAYER                                  │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  Chat Router (routers/chat.py) - NEW                        │    │
│  │  POST /api/{user_id}/chat                                    │    │
│  │                                                              │    │
│  │  Responsibilities:                                           │    │
│  │  1. JWT authentication (get_current_user dependency)        │    │
│  │  2. User ID validation (path vs token)                      │    │
│  │  3. Conversation management (fetch/create)                  │    │
│  │  4. Message history retrieval                               │    │
│  │  5. User message persistence                                │    │
│  │  6. Agent runner invocation                                 │    │
│  │  7. Assistant message persistence                           │    │
│  │  8. Response formatting                                     │    │
│  └──────────────┬───────────────────────────────────────────────┘    │
│                 │                                                      │
│                 ▼                                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  Agent Runner (agent/runner.py) - NEW                       │    │
│  │                                                              │    │
│  │  Responsibilities:                                           │    │
│  │  1. Build messages array from conversation history          │    │
│  │  2. Configure OpenAI client                                 │    │
│  │  3. Define agent instructions/system prompt                 │    │
│  │  4. Register MCP tools with OpenAI                          │    │
│  │  5. Invoke OpenAI Chat Completions API                      │    │
│  │  6. Handle tool calls                                       │    │
│  │  7. Return final response + tool call metadata              │    │
│  └──────────────┬───────────────────────────────────────────────┘    │
│                 │                                                      │
│                 ▼                                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  MCP Server (mcp/server.py + mcp/tools.py) - NEW           │    │
│  │                                                              │    │
│  │  Tools (5 functions):                                        │    │
│  │  - add_task(user_id, title, description?)                   │    │
│  │  - list_tasks(user_id, status?)                             │    │
│  │  - complete_task(user_id, task_id)                          │    │
│  │  - update_task(user_id, task_id, title?, description?)      │    │
│  │  - delete_task(user_id, task_id)                            │    │
│  │                                                              │    │
│  │  Each tool:                                                  │    │
│  │  - Stateless (no global state)                              │    │
│  │  - Database-backed (SQLModel queries)                       │    │
│  │  - User-isolated (WHERE user_id = ...)                      │    │
│  │  - Returns structured JSON                                  │    │
│  └──────────────┬───────────────────────────────────────────────┘    │
│                 │                                                      │
└─────────────────┼──────────────────────────────────────────────────────┘
                  │
                  ▼
┌───────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                     │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  SQLModel Models - NEW                                       │    │
│  │  - Conversation (id, user_id, created_at, updated_at)       │    │
│  │  - Message (id, conversation_id, user_id, role, content)    │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  Neon PostgreSQL Database                                    │    │
│  │  - Existing: users, tasks                                    │    │
│  │  - New: conversations, messages                              │    │
│  └──────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Specifications

### 2.1 Backend Components

#### 2.1.1 Database Models

**File**: `backend/src/models/conversation.py`

```python
"""
Conversation model for storing chat sessions.
[Task]: T-001 (Conversation Model)
[From]: spec.md §4.1
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID
from typing import Optional, List

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
```

**File**: `backend/src/models/message.py`

```python
"""
Message model for storing conversation messages.
[Task]: T-002 (Message Model)
[From]: spec.md §4.2
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID
from typing import Optional

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True, ondelete="CASCADE")
    user_id: UUID = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    role: str = Field(max_length=20)  # 'user' or 'assistant'
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

---

#### 2.1.2 MCP Server

**File**: `backend/src/mcp/tools.py`

```python
"""
MCP tool implementations for task operations.
[Task]: T-003 (MCP Tools)
[From]: spec.md §6
"""

from sqlmodel import Session, select
from src.models.task import Task
from uuid import UUID
from typing import Dict, Any, Optional, List

def add_task(
    session: Session,
    user_id: UUID,
    title: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Create new task."""
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        completed=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    
    return {
        "task_id": task.id,
        "status": "created",
        "title": task.title,
        "description": task.description
    }

def list_tasks(
    session: Session,
    user_id: UUID,
    status: str = "all"
) -> Dict[str, Any]:
    """List user's tasks."""
    query = select(Task).where(Task.user_id == user_id)
    
    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)
    
    tasks = session.exec(query.order_by(Task.created_at.desc())).all()
    
    return {
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat()
            }
            for task in tasks
        ],
        "count": len(tasks)
    }

def complete_task(
    session: Session,
    user_id: UUID,
    task_id: int
) -> Dict[str, Any]:
    """Mark task as complete."""
    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
    ).first()
    
    if not task:
        return {"error": "Task not found or access denied"}
    
    task.completed = True
    session.add(task)
    session.commit()
    session.refresh(task)
    
    return {
        "task_id": task.id,
        "status": "completed",
        "title": task.title
    }

def update_task(
    session: Session,
    user_id: UUID,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Update task details."""
    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
    ).first()
    
    if not task:
        return {"error": "Task not found or access denied"}
    
    if title:
        task.title = title
    if description is not None:
        task.description = description
    
    session.add(task)
    session.commit()
    session.refresh(task)
    
    return {
        "task_id": task.id,
        "status": "updated",
        "title": task.title
    }

def delete_task(
    session: Session,
    user_id: UUID,
    task_id: int
) -> Dict[str, Any]:
    """Delete task."""
    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
    ).first()
    
    if not task:
        return {"error": "Task not found or access denied"}
    
    title = task.title
    session.delete(task)
    session.commit()
    
    return {
        "task_id": task_id,
        "status": "deleted",
        "title": title
    }
```

**File**: `backend/src/mcp/server.py`

```python
"""
MCP server registration and tool definitions.
[Task]: T-004 (MCP Server)
[From]: spec.md §6
"""

from typing import List, Dict, Any

def get_mcp_tools() -> List[Dict[str, Any]]:
    """
    Return OpenAI function calling format tool definitions.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task for the user with title and optional description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User UUID from JWT token"
                        },
                        "title": {
                            "type": "string",
                            "description": "Task title (1-200 characters)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional task description"
                        }
                    },
                    "required": ["user_id", "title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "Get all tasks for the user, optionally filtered by status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User UUID from JWT token"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "description": "Filter tasks by completion status"
                        }
                    },
                    "required": ["user_id"]
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
                        "user_id": {
                            "type": "string",
                            "description": "User UUID from JWT token"
                        },
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to complete"
                        }
                    },
                    "required": ["user_id", "task_id"]
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
                        "user_id": {
                            "type": "string",
                            "description": "User UUID from JWT token"
                        },
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New task title"
                        },
                        "description": {
                            "type": "string",
                            "description": "New task description"
                        }
                    },
                    "required": ["user_id", "task_id"]
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
                        "user_id": {
                            "type": "string",
                            "description": "User UUID from JWT token"
                        },
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to delete"
                        }
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        }
    ]
```

---

#### 2.1.3 Agent Runner

**File**: `backend/src/agent/runner.py`

```python
"""
OpenAI Agent runner with MCP tool integration.
[Task]: T-005 (Agent Runner)
[From]: spec.md §7
"""

import openai
import json
from typing import List, Dict, Any
from sqlmodel import Session
from uuid import UUID
from src.mcp.server import get_mcp_tools
from src.mcp import tools as mcp_tools
from src.config import settings

def run_agent(
    session: Session,
    user_id: UUID,
    messages: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Run OpenAI agent with conversation history and MCP tools.
    
    Args:
        session: Database session
        user_id: User UUID for tool calls
        messages: Conversation history [{"role": "user/assistant", "content": "..."}]
    
    Returns:
        {
            "response": "Agent's text response",
            "tool_calls": [{"tool": "name", "arguments": {...}, "result": {...}}]
        }
    """
    
    # Configure OpenAI client
    openai.api_key = settings.OPENAI_API_KEY
    
    # System prompt
    system_message = {
        "role": "system",
        "content": """You are a helpful task management assistant. You help users manage their todo list through natural conversation.

Available actions:
- Create tasks when user mentions adding, creating, or remembering something
- List tasks when user asks to see, show, or list their tasks
- Mark tasks complete when user says they finished or completed something
- Update tasks when user wants to change or modify details
- Delete tasks when user wants to remove or cancel them

Always:
- Be concise and friendly
- Confirm actions with checkmarks (✅)
- Format task lists clearly
- Ask for clarification if ambiguous
- Handle errors gracefully"""
    }
    
    # Build full message history
    full_messages = [system_message] + messages
    
    # Get MCP tool definitions
    tools = get_mcp_tools()
    
    # Call OpenAI Chat Completions API
    response = openai.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=full_messages,
        tools=tools,
        tool_choice="auto"
    )
    
    # Extract response
    assistant_message = response.choices[0].message
    tool_calls_metadata = []
    
    # Handle tool calls if any
    if assistant_message.tool_calls:
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            # Inject user_id (never trust user input)
            tool_args["user_id"] = str(user_id)
            
            # Execute tool
            if tool_name == "add_task":
                result = mcp_tools.add_task(session, UUID(tool_args["user_id"]), **{k: v for k, v in tool_args.items() if k != "user_id"})
            elif tool_name == "list_tasks":
                result = mcp_tools.list_tasks(session, UUID(tool_args["user_id"]), tool_args.get("status", "all"))
            elif tool_name == "complete_task":
                result = mcp_tools.complete_task(session, UUID(tool_args["user_id"]), tool_args["task_id"])
            elif tool_name == "update_task":
                result = mcp_tools.update_task(session, UUID(tool_args["user_id"]), **{k: v for k, v in tool_args.items() if k != "user_id"})
            elif tool_name == "delete_task":
                result = mcp_tools.delete_task(session, UUID(tool_args["user_id"]), tool_args["task_id"])
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            
            # Record tool call
            tool_calls_metadata.append({
                "tool": tool_name,
                "arguments": tool_args,
                "result": result
            })
        
        # If tools were called, get final response
        # (OpenAI may generate text after tool calls)
        if assistant_message.content:
            response_text = assistant_message.content
        else:
            # Generate confirmation based on tool results
            response_text = _generate_confirmation(tool_calls_metadata)
    else:
        response_text = assistant_message.content
    
    return {
        "response": response_text,
        "tool_calls": tool_calls_metadata
    }

def _generate_confirmation(tool_calls: List[Dict]) -> str:
    """Generate friendly confirmation message from tool results."""
    if not tool_calls:
        return "I couldn't process that request. Could you try again?"
    
    last_call = tool_calls[-1]
    tool = last_call["tool"]
    result = last_call["result"]
    
    if "error" in result:
        return f"❌ {result['error']}"
    
    if tool == "add_task":
        return f"✅ Added '{result['title']}' to your task list."
    elif tool == "list_tasks":
        count = result["count"]
        if count == 0:
            return "You don't have any tasks yet."
        tasks_text = "\n".join([f"{i+1}. {t['title']} ({'completed' if t['completed'] else 'pending'})" for i, t in enumerate(result["tasks"])])
        return f"Here are your {count} task(s):\n{tasks_text}"
    elif tool == "complete_task":
        return f"✅ Marked '{result['title']}' as complete!"
    elif tool == "update_task":
        return f"✅ Updated '{result['title']}'"
    elif tool == "delete_task":
        return f"✅ Deleted '{result['title']}'"
    
    return "Done!"
```

---

#### 2.1.4 Chat Router

**File**: `backend/src/routers/chat.py`

```python
"""
Chat API endpoint for AI agent interaction.
[Task]: T-006 (Chat Endpoint)
[From]: spec.md §5.1
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List, Dict, Any
from src.database import get_session
from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message
from src.utils.deps import get_current_user
from src.agent.runner import run_agent

router = APIRouter(prefix="/api/{user_id}/chat", tags=["chat"])

# Request/Response schemas
class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List[Dict[str, Any]]

@router.post("", response_model=ChatResponse)
def chat(
    user_id: UUID,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Send message to AI agent and receive response.
    
    Stateless request cycle:
    1. Validate auth
    2. Fetch/create conversation
    3. Load message history
    4. Store user message
    5. Run agent
    6. Store assistant message
    7. Return response
    """
    
    # CRITICAL: Verify path user_id matches authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    # Validate message
    if not request.message or len(request.message) > 2000:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message must be between 1-2000 characters"
        )
    
    # Get or create conversation
    if request.conversation_id:
        conversation = session.exec(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id
            )
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        # Create new conversation
        conversation = Conversation(user_id=current_user.id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
    
    # Load conversation history
    messages_query = select(Message).where(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at.asc())
    
    message_history = session.exec(messages_query).all()
    
    # Build messages array for agent
    messages_array = [
        {"role": msg.role, "content": msg.content}
        for msg in message_history
    ]
    
    # Add current user message
    messages_array.append({"role": "user", "content": request.message})
    
    # Store user message
    user_message = Message(
        conversation_id=conversation.id,
        user_id=current_user.id,
        role="user",
        content=request.message
    )
    session.add(user_message)
    session.commit()
    
    # Run agent
    try:
        agent_result = run_agent(
            session=session,
            user_id=current_user.id,
            messages=messages_array
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )
    
    # Store assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        user_id=current_user.id,
        role="assistant",
        content=agent_result["response"]
    )
    session.add(assistant_message)
    session.commit()
    
    # Update conversation timestamp
    from datetime import datetime
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    session.commit()
    
    # Return response
    return ChatResponse(
        conversation_id=conversation.id,
        response=agent_result["response"],
        tool_calls=agent_result["tool_calls"]
    )
```

---

### 2.2 Frontend Components

#### 2.2.1 Chat Page

**File**: `frontend/app/chat/page.tsx`

```typescript
/**
 * Chat page for AI assistant interaction.
 * [Task]: T-007 (Chat Page)
 * [From]: spec.md §9
 */

import { redirect } from 'next/navigation';
import { auth } from '@/lib/auth';
import ChatInterface from '@/components/ChatInterface';

export default async function ChatPage() {
  const session = await auth();
  
  if (!session?.user) {
    redirect('/login');
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">
            AI Task Assistant
          </h1>
          <p className="text-gray-600 mt-2">
            Manage your tasks through natural conversation
          </p>
        </div>
        
        <ChatInterface
          userId={session.user.id}
          jwtToken={session.user.token}
        />
      </div>
    </div>
  );
}
```

---

#### 2.2.2 Chat Interface Component

**File**: `frontend/components/ChatInterface.tsx`

```typescript
/**
 * ChatKit integration component.
 * [Task]: T-008 (ChatInterface Component)
 * [From]: spec.md §9.2
 */

'use client';

import { ChatKit } from '@openai/chatkit';
import { useState } from 'react';

interface ChatInterfaceProps {
  userId: string;
  jwtToken: string;
}

export default function ChatInterface({ userId, jwtToken }: ChatInterfaceProps) {
  const [conversationId, setConversationId] = useState<number | null>(null);
  
  const apiUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/chat`;
  const domainKey = process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY;
  
  if (!domainKey) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold">Configuration Error</h3>
        <p className="text-red-700 mt-2">
          OpenAI domain key not configured. Please set NEXT_PUBLIC_OPENAI_DOMAIN_KEY.
        </p>
      </div>
    );
  }
  
  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      <ChatKit
        apiUrl={apiUrl}
        domainKey={domainKey}
        headers={{
          'Authorization': `Bearer ${jwtToken}`,
          'Content-Type': 'application/json'
        }}
        initialMessages={[
          {
            role: 'assistant',
            content: `👋 Hi! I'm your task management assistant. I can help you:

- **Add tasks**: "Add task to buy groceries"
- **List tasks**: "Show me my tasks"
- **Complete tasks**: "Mark task 1 as done"
- **Update tasks**: "Change task 2 to 'Call John'"
- **Delete tasks**: "Delete the grocery task"

What would you like to do?`
          }
        ]}
        onConversationStart={(id) => setConversationId(id)}
      />
    </div>
  );
}
```

---

#### 2.2.3 Dashboard Update

**File**: `frontend/app/dashboard/page.tsx` (UPDATED)

Add chat button/link to existing dashboard:

```typescript
// Add this button/link to the dashboard
<Link
  href="/chat"
  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
>
  💬 Chat with AI Assistant
</Link>
```

---

## 3. Data Flow Diagrams

### 3.1 Create Task via Chat

```
User types: "Add task to buy milk"
      ↓
Frontend (ChatKit)
- POST /api/{user_id}/chat
- Headers: Authorization: Bearer <jwt>
- Body: { conversation_id: null, message: "Add task to buy milk" }
      ↓
Backend (Chat Router)
1. Validate JWT → Extract user_id
2. Verify path user_id == token user_id
3. Create new conversation (since conversation_id is null)
4. No message history (new conversation)
5. Store user message to DB
      ↓
Agent Runner
1. Build messages: [system_prompt, {role: "user", content: "Add task to buy milk"}]
2. Call OpenAI API with messages + MCP tools
3. OpenAI analyzes intent → Decides to call add_task
4. Returns tool_call: add_task(user_id="...", title="Buy milk")
      ↓
MCP Tools
1. Execute: add_task(session, user_id, "Buy milk", None)
2. INSERT INTO tasks (user_id, title, completed) VALUES (...)
3. Return: {task_id: 42, status: "created", title: "Buy milk"}
      ↓
Agent Runner
1. Receive tool result
2. Generate response: "✅ Added 'Buy milk' to your task list."
3. Return to Chat Router
      ↓
Backend (Chat Router)
1. Store assistant message to DB
2. Update conversation.updated_at
3. Return JSON: {conversation_id: 1, response: "✅ Added...", tool_calls: [...]}
      ↓
Frontend (ChatKit)
1. Display assistant message in chat UI
2. Store conversation_id for next message
```

---

### 3.2 List Tasks via Chat

```
User types: "Show my tasks"
      ↓
Frontend → Backend (Chat Router)
POST /api/{user_id}/chat
{ conversation_id: 1, message: "Show my tasks" }
      ↓
Chat Router
1. Validate auth
2. Fetch conversation ID 1 (verify user_id)
3. Load message history from DB
4. Store user message
      ↓
Agent Runner
1. Build messages: [system, ...history, {role: "user", content: "Show my tasks"}]
2. Call OpenAI → Decides to call list_tasks
3. Tool call: list_tasks(user_id="...", status="all")
      ↓
MCP Tools
1. Execute: SELECT * FROM tasks WHERE user_id = '...' ORDER BY created_at DESC
2. Return: {tasks: [{id: 42, title: "Buy milk", completed: false}], count: 1}
      ↓
Agent Runner
1. Generate response: "Here are your tasks:\n1. Buy milk (pending)"
2. Return to Chat Router
      ↓
Chat Router
1. Store assistant message
2. Return response to frontend
      ↓
Frontend displays formatted task list
```

---

## 4. Security Architecture

### 4.1 Authentication Flow

```
1. User logs in (Phase II Better Auth)
   ↓
2. JWT token issued with payload: {user_id: "uuid", email: "...", exp: ...}
   ↓
3. Frontend stores JWT (httpOnly cookie or localStorage)
   ↓
4. Every chat request includes: Authorization: Bearer <jwt>
   ↓
5. Backend validates JWT:
   - Verify signature (BETTER_AUTH_SECRET)
   - Check expiration
   - Extract user_id
   ↓
6. Verify path {user_id} matches token user_id
   ↓
7. All MCP tools receive user_id from token (never from user input)
   ↓
8. All DB queries filter by user_id
```

### 4.2 User Isolation Enforcement

**Layer 1: JWT Validation**
```python
@router.post("")
def chat(
    user_id: UUID,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),  # ← JWT validation
    ...
):
```

**Layer 2: Path Verification**
```python
if str(current_user.id) != str(user_id):
    raise HTTPException(status_code=404, detail="Not found")
```

**Layer 3: Database Filtering**
```python
# Conversations
conversation = session.exec(
    select(Conversation).where(
        Conversation.user_id == current_user.id  # ← User isolation
    )
).first()

# Messages
messages = session.exec(
    select(Message).where(
        Message.conversation_id == conversation.id
    )
).all()

# Tasks (in MCP tools)
task = session.exec(
    select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id  # ← User isolation
    )
).first()
```

**Layer 4: MCP Tool Enforcement**
```python
# Always inject user_id from token
tool_args["user_id"] = str(current_user.id)  # Never trust user input

# Tools always require user_id
def add_task(session: Session, user_id: UUID, ...):
    task = Task(user_id=user_id, ...)  # Enforced at creation
```

---

## 5. Database Schema

### 5.1 ER Diagram

```
┌─────────────────┐
│     users       │
│─────────────────│
│ id (UUID) PK    │◀──┐
│ email           │   │
│ password_hash   │   │
│ created_at      │   │
└─────────────────┘   │
                      │
                      │ FK: user_id
                      │
┌─────────────────┐   │
│ conversations   │   │
│─────────────────│   │
│ id (INT) PK     │◀──┼───┐
│ user_id (UUID)  │───┘   │
│ created_at      │       │
│ updated_at      │       │
└─────────────────┘       │
                          │ FK: conversation_id
                          │
┌─────────────────┐       │
│    messages     │       │
│─────────────────│       │
│ id (INT) PK     │       │
│ conversation_id │───────┘
│ user_id (UUID)  │───────┐
│ role (VARCHAR)  │       │ FK: user_id
│ content (TEXT)  │       │
│ created_at      │       │
└─────────────────┘       │
                          │
┌─────────────────┐       │
│     tasks       │       │
│─────────────────│       │
│ id (INT) PK     │       │
│ user_id (UUID)  │◀──────┘
│ title (VARCHAR) │
│ description     │
│ completed (BOOL)│
│ created_at      │
│ updated_at      │
└─────────────────┘
```

### 5.2 Indexes

```sql
-- Conversations
CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- Messages
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Tasks (existing from Phase II)
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
```

---

## 6. Configuration

### 6.1 Environment Variables

**Backend (`backend/.env`):**
```env
# Existing Phase II variables
DATABASE_URL=postgresql://user:pass@neon-host/db?sslmode=require
BETTER_AUTH_SECRET=your-production-secret
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=7

# New Phase III variables
OPENAI_API_KEY=sk-proj-...
```

**Frontend (`frontend/.env.local`):**
```env
# Existing Phase II variables
NEXT_PUBLIC_API_URL=https://your-backend-api.com
BETTER_AUTH_SECRET=your-production-secret
DATABASE_URL=postgresql://...

# New Phase III variables
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=dk-...
```

### 6.2 Package Dependencies

**Backend (`backend/pyproject.toml`):**
```toml
[project]
dependencies = [
    # Existing Phase II dependencies
    "fastapi>=0.115.0",
    "sqlmodel>=0.0.22",
    "python-jose>=3.3.0",
    "bcrypt>=4.2.1",
    "psycopg2-binary>=2.9.9",
    
    # New Phase III dependencies
    "openai>=1.54.0",
    "mcp>=1.0.0"
]
```

**Frontend (`frontend/package.json`):**
```json
{
  "dependencies": {
    "next": "^16.1.1",
    "react": "^19.2.3",
    "@openai/chatkit": "^1.0.0"
  }
}
```

---

## 7. Deployment Architecture

### 7.1 Production Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                     PRODUCTION ENVIRONMENT                   │
│                                                              │
│  ┌────────────────────┐                                     │
│  │    Vercel          │                                     │
│  │    (Frontend)      │                                     │
│  │                    │                                     │
│  │  - Next.js 16      │                                     │
│  │  - ChatKit UI      │                                     │
│  │  - Domain Key      │                                     │
│  └─────────┬──────────┘                                     │
│            │ HTTPS                                           │
│            ▼                                                 │
│  ┌────────────────────┐                                     │
│  │ Hugging Face Spaces│                                     │
│  │    (Backend)       │                                     │
│  │                    │                                     │
│  │  - FastAPI         │                                     │
│  │  - MCP Server      │                                     │
│  │  - Agent Runner    │                                     │
│  └─────────┬──────────┘                                     │
│            │                                                 │
│            ├──────────────┐                                 │
│            │              │                                 │
│            ▼              ▼                                 │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Neon         │  │ OpenAI API   │                        │
│  │ PostgreSQL   │  │              │                        │
│  │              │  │ - GPT-4      │                        │
│  │ - Users      │  │ - Function   │                        │
│  │ - Tasks      │  │   Calling    │                        │
│  │ - Convers.   │  └──────────────┘                        │
│  │ - Messages   │                                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Deployment Steps

**Step 1: Backend Deployment (Hugging Face Spaces)**
1. Push changes to GitHub
2. Update `backend/Dockerfile` if needed
3. Deploy to HF Spaces
4. Set environment variable: `OPENAI_API_KEY`
5. Test API endpoint: `https://ahmedkhi-todo-api-phase2.hf.space/docs`

**Step 2: Frontend Deployment (Vercel)**
1. Configure OpenAI domain allowlist:
   - Go to: https://platform.openai.com/settings/organization/security/domain-allowlist
   - Add domain: `https://panaversity-spec-driven-todo.vercel.app`
   - Copy domain key
2. Set Vercel environment variable:
   - `NEXT_PUBLIC_OPENAI_DOMAIN_KEY=<key>`
3. Deploy to Vercel
4. Test chat functionality

**Step 3: Database Migration**
```bash
# Run locally first
cd backend
uv run alembic revision --autogenerate -m "Add conversations and messages tables"
uv run alembic upgrade head

# Then run on production
# (Connect to Neon DB and run migrations)
```

---

## 8. Testing Strategy

### 8.1 Unit Tests

**Test MCP Tools:**
```python
# tests/test_mcp_tools.py
def test_add_task():
    result = add_task(session, user_id, "Test task")
    assert result["status"] == "created"
    assert result["title"] == "Test task"

def test_list_tasks():
    result = list_tasks(session, user_id, "all")
    assert "tasks" in result
    assert "count" in result
```

**Test Agent Runner:**
```python
# tests/test_agent_runner.py
def test_agent_creates_task():
    messages = [{"role": "user", "content": "Add task to buy milk"}]
    result = run_agent(session, user_id, messages)
    assert "response" in result
    assert len(result["tool_calls"]) > 0
```

### 8.2 Integration Tests

**Test Chat Endpoint:**
```python
# tests/test_chat_endpoint.py
def test_chat_creates_conversation():
    response = client.post(
        f"/api/{user_id}/chat",
        json={"conversation_id": None, "message": "Hello"},
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.status_code == 200
    assert "conversation_id" in response.json()
```

### 8.3 End-to-End Tests

**Test Complete Flow:**
1. User logs in
2. Opens chat
3. Sends message: "Add task to buy milk"
4. Verifies task appears in database
5. Verifies bot confirms creation
6. Sends message: "Show my tasks"
7. Verifies task list is returned

---

## 9. Performance Considerations

### 9.1 Optimization Strategies

**Database Query Optimization:**
- Index on `messages.conversation_id` for fast history retrieval
- Index on `messages.created_at` for chronological ordering
- Limit message history to last 50 messages (configurable)

**OpenAI API Optimization:**
- Use `gpt-4-turbo-preview` (faster than gpt-4)
- Set `max_tokens` limit to prevent excessive responses
- Implement retry logic with exponential backoff

**Stateless Architecture Benefits:**
- No memory leaks
- Horizontal scaling without session affinity
- Simple load balancing

### 9.2 Caching Strategy (Future)

**Optional Enhancements:**
- Cache conversation history (Redis)
- Cache frequently asked questions
- Rate limit per user (prevent abuse)

---

## 10. Error Handling

### 10.1 Error Types & Responses

| Error Type | HTTP Code | Response | Action |
|------------|-----------|----------|--------|
| Invalid JWT | 401 | `{"detail": "Invalid token"}` | Redirect to login |
| User mismatch | 404 | `{"detail": "Not found"}` | Show error message |
| OpenAI API error | 500 | `{"detail": "Failed to process..."}` | Retry or show fallback |
| Database error | 500 | `{"detail": "Internal error"}` | Log and alert |
| Tool execution error | 200 | Bot says: "I had trouble..." | Graceful fallback |

### 10.2 Graceful Degradation

**If OpenAI API is down:**
- Return friendly error message
- Suggest using web UI instead
- Log error for monitoring

**If database is slow:**
- Set timeout on queries
- Return partial results if possible
- Show loading indicator

---

## 11. Monitoring & Logging

### 11.1 Logging Strategy

**Log Events:**
- Chat requests (user_id, conversation_id, timestamp)
- Tool calls (tool_name, arguments, result)
- OpenAI API calls (model, tokens used)
- Errors (stack trace, context)

**Log Format:**
```python
logger.info(
    "Chat request",
    extra={
        "user_id": str(user_id),
        "conversation_id": conversation_id,
        "message_length": len(message),
        "tool_calls": len(tool_calls)
    }
)
```

### 11.2 Metrics to Track

- Chat requests per minute
- Average response time
- Tool call success rate
- OpenAI API errors
- Database query time

---

## 12. File Structure Summary

```
phase-2-fullstack/
├── backend/
│   ├── src/
│   │   ├── models/
│   │   │   ├── conversation.py          # NEW
│   │   │   └── message.py               # NEW
│   │   ├── routers/
│   │   │   └── chat.py                  # NEW
│   │   ├── mcp/
│   │   │   ├── __init__.py             # NEW
│   │   │   ├── server.py               # NEW
│   │   │   └── tools.py                # NEW
│   │   ├── agent/
│   │   │   ├── __init__.py             # NEW
│   │   │   └── runner.py               # NEW
│   │   └── main.py                     # UPDATED
│   ├── pyproject.toml                   # UPDATED
│   └── .env.example                     # UPDATED
│
├── frontend/
│   ├── app/
│   │   ├── chat/
│   │   │   └── page.tsx                # NEW
│   │   └── dashboard/
│   │       └── page.tsx                # UPDATED
│   ├── components/
│   │   └── ChatInterface.tsx           # NEW
│   ├── package.json                     # UPDATED
│   └── .env.local.example              # UPDATED
│
├── specs/
│   └── 003-phase-iii-chatbot/
│       ├── spec.md                      # COMPLETE
│       ├── plan.md                      # THIS FILE
│       ├── tasks.md                     # TODO
│       └── contracts/                   # TODO
│
├── constitution.md                      # TODO (update)
└── README.md                            # TODO (update)
```

---

## 13. Next Steps

1. ✅ Specification complete (`spec.md`)
2. ✅ Technical plan complete (`plan.md`)
3. ⏭️ Task breakdown (`tasks.md`)
4. ⏭️ Update constitution
5. ⏭️ Implement database models
6. ⏭️ Implement MCP server
7. ⏭️ Implement agent runner
8. ⏭️ Implement chat endpoint
9. ⏭️ Implement frontend
10. ⏭️ Test end-to-end
11. ⏭️ Deploy
12. ⏭️ Demo video

---

**STATUS**: Ready for Task Breakdown  
**Next Document**: `tasks.md`  
**Created By**: Ahmed Khan  
**Date**: January 8, 2026

---

**END OF TECHNICAL PLAN**
