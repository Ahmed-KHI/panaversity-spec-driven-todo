# Phase III: AI-Powered Todo Chatbot with MCP - SPECIFICATION

**Project:** Hackathon II - The Evolution of Todo  
**Phase:** III - AI Chatbot with MCP Integration  
**Status:** Active  
**Version:** 1.0  
**Created:** January 8, 2026  
**Dependencies:** Phase II Complete (Full-Stack Web Application)

---

## 1. Executive Summary

### 1.1 Phase Objective

Add an AI-powered conversational interface to the Phase II web application, allowing users to manage tasks through natural language using:
- **Model Context Protocol (MCP)** for standardized AI-to-app communication
- **OpenAI Agents SDK** for conversation management and tool orchestration
- **OpenAI ChatKit** for pre-built conversational UI
- **Stateless architecture** with full conversation persistence to PostgreSQL

### 1.2 Deliverables

1. MCP Server with 5 standardized tools for task operations
2. OpenAI Agent with conversation state management
3. ChatKit-based conversational UI integrated with existing dashboard
4. Database schema extensions (conversations, messages tables)
5. Stateless chat API endpoint with JWT authentication
6. Complete documentation and 90-second demo video

### 1.3 Success Criteria

- User can manage all task operations via natural language
- Conversations persist across browser sessions
- Server remains stateless (horizontally scalable)
- User isolation maintained at all layers
- All Phase II features continue to work unchanged
- Production deployment on Vercel + Hugging Face Spaces

---

## 2. Architecture Overview

### 2.1 System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                      PHASE III ARCHITECTURE                          │
│                                                                       │
│  ┌────────────────────┐                                              │
│  │   ChatKit UI       │                                              │
│  │   (Frontend)       │                                              │
│  │                    │                                              │
│  │  - OpenAI ChatKit  │                                              │
│  │  - Domain Key      │                                              │
│  │  - JWT Auth        │                                              │
│  └────────┬───────────┘                                              │
│           │ HTTP POST /api/{user_id}/chat                            │
│           ▼                                                           │
│  ┌────────────────────────────────────────────────────────┐          │
│  │              FastAPI Backend                            │          │
│  │                                                          │          │
│  │  ┌────────────────────────────────────────────────┐    │          │
│  │  │  Chat Endpoint (/routers/chat.py)             │    │          │
│  │  │  - Validate JWT                                │    │          │
│  │  │  - Fetch/Create Conversation                   │    │          │
│  │  │  - Load Message History                        │    │          │
│  │  │  - Invoke Agent Runner                         │    │          │
│  │  │  - Persist Messages                            │    │          │
│  │  └───────────────┬────────────────────────────────┘    │          │
│  │                  │                                      │          │
│  │                  ▼                                      │          │
│  │  ┌────────────────────────────────────────────────┐    │          │
│  │  │  OpenAI Agent Runner (/agent/runner.py)       │    │          │
│  │  │  - Build message array from history           │    │          │
│  │  │  - Call OpenAI API with tools                 │    │          │
│  │  │  - Orchestrate tool execution                 │    │          │
│  │  │  - Generate natural language response         │    │          │
│  │  └───────────────┬────────────────────────────────┘    │          │
│  │                  │                                      │          │
│  │                  ▼                                      │          │
│  │  ┌────────────────────────────────────────────────┐    │          │
│  │  │  MCP Server (/mcp/server.py)                  │    │          │
│  │  │  - add_task()                                  │    │          │
│  │  │  - list_tasks()                                │    │          │
│  │  │  - complete_task()                             │    │          │
│  │  │  - update_task()                               │    │          │
│  │  │  - delete_task()                               │    │          │
│  │  └───────────────┬────────────────────────────────┘    │          │
│  │                  │                                      │          │
│  └──────────────────┼──────────────────────────────────────┘          │
│                     │                                                 │
│                     ▼                                                 │
│  ┌──────────────────────────────────────────────────────┐            │
│  │           Neon PostgreSQL Database                    │            │
│  │                                                        │            │
│  │  Existing Tables:                                     │            │
│  │  - users                                              │            │
│  │  - tasks                                              │            │
│  │                                                        │            │
│  │  New Tables (Phase III):                              │            │
│  │  - conversations                                      │            │
│  │  - messages                                           │            │
│  └──────────────────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.2 Request Flow (Stateless Cycle)

```
1. User types message in ChatKit UI
   ↓
2. Frontend: POST /api/{user_id}/chat
   {
     "conversation_id": 123 (or null for new),
     "message": "Add task to buy groceries"
   }
   ↓
3. Backend Chat Endpoint:
   a. Validate JWT token
   b. Verify path user_id matches token user_id
   c. Fetch or create conversation (from DB)
   d. Fetch message history (from DB)
   e. Store user message (to DB)
   ↓
4. Agent Runner:
   a. Build messages array: [history] + [new message]
   b. Call OpenAI API with agent config + MCP tools
   c. Agent analyzes intent and decides which tool(s) to call
   d. Execute tool(s) via MCP server
   ↓
5. MCP Server:
   a. Receive tool call (e.g., add_task with parameters)
   b. Execute database operation (INSERT task)
   c. Return tool result to agent
   ↓
6. Agent:
   a. Receive tool result
   b. Generate natural language response
   c. Return response to backend
   ↓
7. Backend:
   a. Store assistant message (to DB)
   b. Return JSON response to frontend
   ↓
8. Frontend:
   a. Display assistant message in ChatKit
   
9. Server forgets everything (stateless)
```

### 2.3 Stateless Architecture Principles

**Critical Design Decision**: Server holds ZERO state between requests

- ✅ Every request fetches state from database
- ✅ Every response persists state to database
- ✅ No in-memory sessions or caches
- ✅ Server can restart without data loss
- ✅ Load balancer can route to any server instance
- ✅ Horizontally scalable architecture

---

## 3. User Stories

### US-001: Start Conversation

**As a** logged-in user  
**I want to** access a chat interface from my dashboard  
**So that** I can manage tasks through natural language

**Acceptance Criteria:**
- Dashboard has "Chat" button or link
- Clicking opens ChatKit UI
- If no conversation exists, creates new one automatically
- If conversation exists, loads message history
- User isolation: only my conversations visible

---

### US-002: Create Task via Natural Language

**As a** user  
**I want to** create tasks by describing them naturally  
**So that** I avoid filling forms

**Acceptance Criteria:**
- Recognizes intent: "Add task...", "Create todo...", "Remember to..."
- Extracts title from message
- Optionally extracts description
- Calls `add_task` MCP tool
- Confirms with friendly message
- Task appears in web UI and database

**Examples:**
```
User: "Add a task to buy groceries"
Agent: "✅ Added 'Buy groceries' to your task list."

User: "Remember to call mom about her birthday tomorrow"
Agent: "✅ Task created: 'Call mom about her birthday tomorrow'"

User: "I need to finish the quarterly report with all charts"
Agent: "✅ Added task: 'Finish quarterly report with all charts'"
```

---

### US-003: List Tasks via Natural Language

**As a** user  
**I want to** see my tasks by asking  
**So that** I can quickly review what needs doing

**Acceptance Criteria:**
- Recognizes variations: "Show tasks", "What's pending?", "List my todos"
- Calls `list_tasks` MCP tool with optional status filter
- Formats results readably
- Shows empty state gracefully
- Supports filtering: all, pending, completed

**Examples:**
```
User: "Show me all my tasks"
Agent: "Here are your 3 tasks:
1. Buy groceries (pending)
2. Call mom (pending)
3. Finish report (pending)"

User: "What have I completed?"
Agent: "You've completed 2 tasks:
✅ Weekly review
✅ Email to client"

User: "What's pending?"
Agent: "You have 3 pending tasks:
- Buy groceries
- Call mom
- Finish report"
```

---

### US-004: Complete Task via Natural Language

**As a** user  
**I want to** mark tasks complete by telling the chatbot  
**So that** I update status conversationally

**Acceptance Criteria:**
- Recognizes: "Mark X as done", "Completed X", "Finished X"
- Identifies task by title or ID
- Calls `complete_task` MCP tool
- Confirms completion
- Asks for clarification if ambiguous

**Examples:**
```
User: "Mark buy groceries as complete"
Agent: "✅ Marked 'Buy groceries' as complete!"

User: "I finished calling mom"
Agent: "✅ 'Call mom' marked as complete. Great job!"

User: "Done with task 3"
Agent: "✅ 'Finish report' completed!"
```

---

### US-005: Update Task via Natural Language

**As a** user  
**I want to** modify tasks by describing changes  
**So that** I update details without forms

**Acceptance Criteria:**
- Recognizes: "Change X to Y", "Update X", "Rename X"
- Identifies task by title or ID
- Updates title and/or description
- Calls `update_task` MCP tool
- Shows before/after values

**Examples:**
```
User: "Change 'buy groceries' to 'buy groceries and fruits'"
Agent: "✅ Updated: 'Buy groceries' → 'Buy groceries and fruits'"

User: "Update task 2 to include meeting notes"
Agent: "✅ Updated 'Call mom' with additional details"
```

---

### US-006: Delete Task via Natural Language

**As a** user  
**I want to** remove tasks by asking  
**So that** I clean up my list conversationally

**Acceptance Criteria:**
- Recognizes: "Delete X", "Remove X", "Cancel X"
- Identifies task by title or ID
- Calls `delete_task` MCP tool
- Confirms deletion
- Asks for confirmation if ambiguous

**Examples:**
```
User: "Delete the grocery task"
Agent: "✅ Deleted 'Buy groceries and fruits'"

User: "Remove task 1"
Agent: "✅ Deleted task #1"

User: "Cancel all completed tasks"
Agent: "Are you sure you want to delete 2 completed tasks? (yes/no)"
```

---

### US-007: Conversation Persistence

**As a** user  
**I want to** see previous messages when I return  
**So that** I have context and history

**Acceptance Criteria:**
- Conversation ID stored in database
- All messages (user + assistant) persisted
- History loads on chat interface open
- Can start new conversation anytime
- Old conversations remain accessible
- User isolation enforced

---

### US-008: Error Handling

**As a** user  
**I want to** receive clear feedback when errors occur  
**So that** I know how to proceed

**Acceptance Criteria:**
- Task not found: "I couldn't find that task. Can you try again?"
- Ambiguous command: "Did you mean to add a task or complete one?"
- Tool failure: "I had trouble updating that. Please retry."
- Invalid input: "I need a task title to create one."
- Graceful fallback: Never crashes, always responds

---

## 4. Database Schema Extensions

### 4.1 New Table: conversations

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

**SQLModel Definition:**
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    
    id: int | None = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    messages: list["Message"] = Relationship(back_populates="conversation")
```

---

### 4.2 New Table: messages

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL,
    user_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_conversation FOREIGN KEY (conversation_id) 
        REFERENCES conversations(id) ON DELETE CASCADE,
    CONSTRAINT fk_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

**SQLModel Definition:**
```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"
    
    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    role: str = Field(max_length=20)  # 'user' or 'assistant'
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
```

---

### 4.3 Existing Tables (No Changes)

- `users` - Unchanged from Phase II
- `tasks` - Unchanged from Phase II
- Better Auth tables - Unchanged

---

## 5. API Specification

### 5.1 Chat Endpoint

**POST** `/api/{user_id}/chat`

**Description**: Send message to AI agent and receive response

**Authentication**: Required (JWT Bearer token)

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | UUID | Yes | User ID (must match JWT token) |

**Request Body:**
```json
{
  "conversation_id": 123,  // Integer or null (creates new)
  "message": "Add a task to buy groceries"  // Required, 1-2000 chars
}
```

**Success Response (200 OK):**
```json
{
  "conversation_id": 123,
  "response": "✅ I've added 'Buy groceries' to your task list.",
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Buy groceries",
        "description": null
      },
      "result": {
        "task_id": 42,
        "status": "created",
        "title": "Buy groceries"
      }
    }
  ]
}
```

**Error Responses:**

**401 Unauthorized:**
```json
{
  "detail": "Invalid or expired token"
}
```

**404 Not Found:**
```json
{
  "detail": "Not found"
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Failed to process message",
  "error": "OpenAI API rate limit exceeded"
}
```

---

## 6. MCP Tool Specifications

### 6.1 Tool: add_task

**Purpose**: Create new task for authenticated user

**Tool Definition:**
```python
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
                    "description": "Optional task description (max 1000 characters)"
                }
            },
            "required": ["user_id", "title"]
        }
    }
}
```

**Returns:**
```json
{
  "task_id": 42,
  "status": "created",
  "title": "Buy groceries",
  "description": null
}
```

---

### 6.2 Tool: list_tasks

**Purpose**: Retrieve user's tasks with optional status filter

**Tool Definition:**
```python
{
    "type": "function",
    "function": {
        "name": "list_tasks",
        "description": "Get all tasks for the user, optionally filtered by completion status",
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
                    "description": "Filter tasks by status (default: all)"
                }
            },
            "required": ["user_id"]
        }
    }
}
```

**Returns:**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Buy groceries",
      "description": null,
      "completed": false,
      "created_at": "2026-01-08T10:00:00Z"
    }
  ],
  "count": 1
}
```

---

### 6.3 Tool: complete_task

**Purpose**: Mark task as complete

**Tool Definition:**
```python
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
                    "description": "ID of the task to mark complete"
                }
            },
            "required": ["user_id", "task_id"]
        }
    }
}
```

**Returns:**
```json
{
  "task_id": 1,
  "status": "completed",
  "title": "Buy groceries"
}
```

---

### 6.4 Tool: update_task

**Purpose**: Update task title or description

**Tool Definition:**
```python
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
                    "description": "New task title (optional)"
                },
                "description": {
                    "type": "string",
                    "description": "New task description (optional)"
                }
            },
            "required": ["user_id", "task_id"]
        }
    }
}
```

**Returns:**
```json
{
  "task_id": 1,
  "status": "updated",
  "title": "Buy groceries and fruits"
}
```

---

### 6.5 Tool: delete_task

**Purpose**: Remove task permanently

**Tool Definition:**
```python
{
    "type": "function",
    "function": {
        "name": "delete_task",
        "description": "Permanently delete a task from the user's list",
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
```

**Returns:**
```json
{
  "task_id": 1,
  "status": "deleted",
  "title": "Buy groceries"
}
```

---

## 7. Agent Behavior Specification

### 7.1 Intent Recognition Patterns

| Intent | Trigger Phrases | Tool Called |
|--------|----------------|-------------|
| Create Task | "Add task", "Create todo", "Remember to", "I need to", "Don't forget" | `add_task` |
| List Tasks | "Show tasks", "List todos", "What do I have", "What's pending", "What's done" | `list_tasks` |
| Complete Task | "Mark as done", "Completed", "Finished", "I did", "Done with" | `complete_task` |
| Update Task | "Change X to Y", "Update X", "Rename X", "Modify X", "Edit X" | `update_task` |
| Delete Task | "Delete X", "Remove X", "Cancel X", "Get rid of X", "Erase X" | `delete_task` |

### 7.2 Response Guidelines

**Success Confirmations:**
- Use ✅ checkmark emoji
- Echo the action taken
- Be concise and friendly
- Example: "✅ Added 'Buy groceries' to your task list."

**List Formatting:**
- Numbered or bulleted lists
- Show status indicators
- Keep clean and scannable

**Error Messages:**
- Be helpful, not technical
- Suggest alternatives
- Example: "I couldn't find that task. Could you describe it differently?"

**Clarifications:**
- Ask specific questions
- Provide options
- Example: "Did you mean task #1 'Buy groceries' or task #3 'Get groceries'?"

---

## 8. Security & User Isolation

### 8.1 Authentication Layers

**Layer 1: JWT Validation**
- Every request validates Bearer token
- Extract `user_id` from token payload
- Reject invalid/expired tokens with 401

**Layer 2: Path Parameter Verification**
- Ensure path `{user_id}` matches token `user_id`
- Return 404 (not 403) on mismatch to prevent user enumeration

**Layer 3: Database Query Filtering**
- All conversation queries: `WHERE user_id = {token_user_id}`
- All message queries: `WHERE user_id = {token_user_id}`
- All task queries: Inherited from Phase II user isolation

**Layer 4: MCP Tool Enforcement**
- Every tool receives `user_id` from token (not from user input)
- Tools cannot operate without valid `user_id`
- Cross-user operations impossible by design

### 8.2 Security Requirements

- ✅ Passwords hashed with bcrypt (Phase II)
- ✅ JWT tokens expire after 7 days (Phase II)
- ✅ HTTPS enforced in production
- ✅ SQL injection prevention via SQLModel
- ✅ XSS prevention via input sanitization
- ✅ Rate limiting (future enhancement)
- ✅ Secrets in environment variables

---

## 9. OpenAI ChatKit Configuration

### 9.1 Domain Allowlist Setup

**Critical Requirement**: ChatKit requires domain allowlisting

**Steps:**
1. Deploy frontend to production (get URL)
2. Visit: https://platform.openai.com/settings/organization/security/domain-allowlist
3. Click "Add domain"
4. Enter production URL (e.g., `https://panaversity-spec-driven-todo.vercel.app`)
5. Save and copy the domain key
6. Add to Vercel: `NEXT_PUBLIC_OPENAI_DOMAIN_KEY=<key>`

**Local Development:**
- `localhost:3000` usually works without allowlisting
- If blocked, add `http://localhost:3000` to allowlist

### 9.2 ChatKit Integration Code

**Frontend Component:**
```typescript
import { ChatKit } from '@openai/chatkit';
import { useSession } from 'next-auth/react';

export default function ChatInterface() {
  const { data: session } = useSession();
  const userId = session?.user?.id;
  const jwtToken = session?.user?.token;

  return (
    <ChatKit
      apiUrl={`/api/${userId}/chat`}
      domainKey={process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY}
      headers={{
        Authorization: `Bearer ${jwtToken}`
      }}
    />
  );
}
```

---

## 10. Success Criteria Checklist

### 10.1 Functional Requirements

- [ ] User can open chat from dashboard
- [ ] User can create tasks via natural language
- [ ] User can list tasks with filtering (all/pending/completed)
- [ ] User can mark tasks complete via natural language
- [ ] User can update tasks via natural language
- [ ] User can delete tasks via natural language
- [ ] Conversation history persists across sessions
- [ ] Agent provides helpful, context-aware responses
- [ ] Agent handles errors gracefully
- [ ] All 5 MCP tools implemented and tested
- [ ] User isolation enforced at all layers
- [ ] Stateless architecture (no in-memory state)
- [ ] All Phase II features continue working

### 10.2 Technical Requirements

- [ ] OpenAI Agents SDK integrated
- [ ] Official MCP SDK used
- [ ] Database models (Conversation, Message) created
- [ ] Chat API endpoint with JWT auth
- [ ] ChatKit UI with domain allowlist configured
- [ ] Conversation persistence working
- [ ] Multiple conversations supported per user
- [ ] Error handling and validation
- [ ] API documentation updated
- [ ] Type safety (TypeScript frontend, Python type hints)

### 10.3 Performance Requirements

- Chat response time: < 3 seconds (typical)
- Tool execution: < 500ms per tool
- Database queries: < 100ms
- Conversation history load: < 200ms
- Concurrent users: 100+ (stateless architecture)

---

## 11. Testing Scenarios

### 11.1 Happy Path Tests

**Test 1: Create Task**
1. User: "Add task to buy milk"
2. Verify: `add_task` tool called
3. Verify: Task in database
4. Verify: Bot confirms creation

**Test 2: List Tasks**
1. User: "Show my tasks"
2. Verify: `list_tasks` tool called
3. Verify: Correct tasks returned
4. Verify: Formatted nicely

**Test 3: Complete Task**
1. User: "Mark buy milk as done"
2. Verify: `complete_task` tool called
3. Verify: Task updated in DB
4. Verify: Bot confirms

**Test 4: Conversation Persistence**
1. User sends 3 messages
2. Close browser
3. Reopen chat
4. Verify: All 3 messages visible

### 11.2 Error Handling Tests

**Test 5: Task Not Found**
1. User: "Delete task 9999"
2. Verify: Error message returned
3. Verify: Friendly error shown

**Test 6: Ambiguous Command**
1. User: "Do the thing"
2. Verify: Clarification requested

**Test 7: Invalid Token**
1. Send expired JWT
2. Verify: 401 Unauthorized
3. Verify: No operations performed

### 11.3 User Isolation Tests

**Test 8: Cross-User Access**
1. User A creates tasks
2. User B logs in
3. User B: "Show tasks"
4. Verify: Only User B's tasks shown

**Test 9: Conversation Isolation**
1. User A has conversation ID 10
2. User B sends message with conversation_id=10
3. Verify: 404 Not Found

---

## 12. Dependencies

### 12.1 New Python Packages

```toml
# Add to backend/pyproject.toml
openai = "^1.54.0"
mcp = "^1.0.0"  # Official MCP SDK
```

### 12.2 New Frontend Packages

```json
{
  "@openai/chatkit": "^1.0.0"
}
```

### 12.3 Environment Variables

**Backend (.env):**
```env
OPENAI_API_KEY=sk-proj-...
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=dk-...
```

---

## 13. Deliverables

### 13.1 Code Files

**Backend (New Files):**
```
backend/src/
├── models/
│   ├── conversation.py          # NEW
│   └── message.py               # NEW
├── routers/
│   └── chat.py                  # NEW
├── mcp/
│   ├── __init__.py             # NEW
│   ├── server.py               # NEW
│   └── tools.py                # NEW
├── agent/
│   ├── __init__.py             # NEW
│   └── runner.py               # NEW
└── main.py                     # UPDATED (register chat router)
```

**Frontend (New Files):**
```
frontend/
├── app/
│   ├── chat/
│   │   └── page.tsx            # NEW
│   └── dashboard/
│       └── page.tsx            # UPDATED (add chat button)
└── components/
    └── ChatInterface.tsx       # NEW
```

### 13.2 Documentation

- [ ] Updated README.md with Phase III setup
- [ ] API documentation for chat endpoint
- [ ] MCP tool documentation
- [ ] Deployment guide for ChatKit
- [ ] Updated CLAUDE.md

### 13.3 Deployment

- [ ] Backend deployed to Hugging Face Spaces
- [ ] Frontend deployed to Vercel
- [ ] OpenAI domain allowlist configured
- [ ] Demo video (90 seconds)

---

## 14. Timeline

**Day 1-2**: Database models + migrations  
**Day 3-4**: MCP Server + tools  
**Day 5-6**: Agent integration + chat endpoint  
**Day 7**: ChatKit frontend  
**Day 8-9**: Testing + bug fixes  
**Day 10**: Deployment + demo video

---

## 15. Approval

**Status**: Ready for Planning Phase  
**Next Step**: Create `plan.md` (architecture and component design)  
**Created By**: Ahmed Khan  
**Date**: January 8, 2026

---

**END OF SPECIFICATION**
