# Phase III: AI-Powered Todo Chatbot - TASK BREAKDOWN

**Project:** Hackathon II - The Evolution of Todo  
**Phase:** III - AI Chatbot with MCP Integration  
**Document Type:** Implementation Tasks  
**Version:** 1.0  
**Date:** January 8, 2026  
**References:** spec.md, plan.md

---

## Task Index

| Task ID | Title | Status | Files |
|---------|-------|--------|-------|
| T-001 | Create Conversation Model | ⏳ Ready | `backend/src/models/conversation.py` |
| T-002 | Create Message Model | ⏳ Ready | `backend/src/models/message.py` |
| T-003 | Create Database Migration | ⏳ Ready | `backend/migrations/` |
| T-004 | Implement MCP Tools | ⏳ Ready | `backend/src/mcp/tools.py` |
| T-005 | Implement MCP Server | ⏳ Ready | `backend/src/mcp/server.py` |
| T-006 | Implement Agent Runner | ⏳ Ready | `backend/src/agent/runner.py` |
| T-007 | Implement Chat Router | ⏳ Ready | `backend/src/routers/chat.py` |
| T-008 | Update Main App | ⏳ Ready | `backend/src/main.py` |
| T-009 | Create Chat Interface Component | ⏳ Ready | `frontend/components/ChatInterface.tsx` |
| T-010 | Create Chat Page | ⏳ Ready | `frontend/app/chat/page.tsx` |
| T-011 | Update Dashboard | ⏳ Ready | `frontend/app/dashboard/page.tsx` |
| T-012 | Update Backend Dependencies | ⏳ Ready | `backend/pyproject.toml` |
| T-013 | Update Frontend Dependencies | ⏳ Ready | `frontend/package.json` |
| T-014 | Update Backend Environment Config | ⏳ Ready | `backend/.env.example` |
| T-015 | Update Frontend Environment Config | ⏳ Ready | `frontend/.env.local.example` |
| T-016 | Update Constitution | ⏳ Ready | `phase-2-fullstack/constitution.md` |
| T-017 | Update Main README | ⏳ Ready | `README.md` |
| T-018 | End-to-End Testing | ⏳ Ready | Manual testing |
| T-019 | Deploy Backend | ⏳ Ready | Hugging Face Spaces |
| T-020 | Deploy Frontend | ⏳ Ready | Vercel |

---

## BACKEND TASKS

### T-001: Create Conversation Model

**Priority:** Critical  
**Estimated Time:** 15 minutes  
**Dependencies:** None  
**Status:** ⏳ Ready

**Description:**  
Create SQLModel class for conversations table to store chat sessions.

**Preconditions:**
- Backend Phase II code is functional
- SQLModel already configured

**Implementation Steps:**
1. Create new file: `backend/src/models/conversation.py`
2. Import necessary modules: `SQLModel`, `Field`, `Relationship`, `datetime`, `UUID`
3. Define `Conversation` class:
   - Inherits from `SQLModel` with `table=True`
   - Fields: `id`, `user_id`, `created_at`, `updated_at`
   - Foreign key relationship to users table
   - Relationship to messages list
4. Add docstring referencing spec.md §4.1
5. Add task reference comment

**Expected Output:**
```python
"""
Conversation model for storing chat sessions.
[Task]: T-001
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

**Files Modified:**
- CREATE: `backend/src/models/conversation.py`

**Testing:**
- Verify file creation
- Check imports work
- Ensure no syntax errors

**Acceptance Criteria:**
- [ ] File created at correct path
- [ ] Class inherits from SQLModel
- [ ] All fields defined with correct types
- [ ] Foreign key relationship configured
- [ ] Task reference comment present

---

### T-002: Create Message Model

**Priority:** Critical  
**Estimated Time:** 15 minutes  
**Dependencies:** T-001  
**Status:** ⏳ Ready

**Description:**  
Create SQLModel class for messages table to store conversation messages.

**Preconditions:**
- T-001 complete (Conversation model exists)

**Implementation Steps:**
1. Create new file: `backend/src/models/message.py`
2. Import necessary modules
3. Define `Message` class:
   - Fields: `id`, `conversation_id`, `user_id`, `role`, `content`, `created_at`
   - Foreign keys to conversations and users
   - Indexes on conversation_id, user_id, created_at
4. Add docstring and task reference

**Expected Output:**
```python
"""
Message model for storing conversation messages.
[Task]: T-002
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

**Files Modified:**
- CREATE: `backend/src/models/message.py`

**Testing:**
- Verify imports
- Check relationship to Conversation works

**Acceptance Criteria:**
- [ ] File created at correct path
- [ ] All fields defined correctly
- [ ] Foreign keys configured
- [ ] Indexes specified
- [ ] Relationship to Conversation defined

---

### T-003: Create Database Migration

**Priority:** Critical  
**Estimated Time:** 20 minutes  
**Dependencies:** T-001, T-002  
**Status:** ⏳ Ready

**Description:**  
Generate and apply Alembic migration to create conversations and messages tables.

**Preconditions:**
- T-001 and T-002 complete
- Database connection configured

**Implementation Steps:**
1. Import new models in `backend/src/database.py`:
   ```python
   from src.models.conversation import Conversation
   from src.models.message import Message
   ```
2. Generate migration:
   ```bash
   cd backend
   uv run alembic revision --autogenerate -m "Add conversations and messages tables"
   ```
3. Review generated migration file
4. Apply migration locally:
   ```bash
   uv run alembic upgrade head
   ```
5. Test on production database

**Expected Output:**
- New migration file in `backend/migrations/versions/`
- Tables created: `conversations`, `messages`
- Indexes created as specified
- Foreign key constraints established

**Files Modified:**
- CREATE: `backend/migrations/versions/<timestamp>_add_conversations_messages.py`
- UPDATE: `backend/src/database.py` (import statements)

**Testing:**
```sql
-- Verify tables exist
SELECT * FROM conversations LIMIT 1;
SELECT * FROM messages LIMIT 1;

-- Verify indexes
\d conversations
\d messages
```

**Acceptance Criteria:**
- [ ] Migration generated successfully
- [ ] Tables created in database
- [ ] Foreign keys work correctly
- [ ] Indexes created
- [ ] No errors during migration

---

### T-004: Implement MCP Tools

**Priority:** Critical  
**Estimated Time:** 45 minutes  
**Dependencies:** None  
**Status:** ⏳ Ready

**Description:**  
Implement 5 MCP tool functions for task management operations.

**Preconditions:**
- Phase II Task model exists

**Implementation Steps:**
1. Create new file: `backend/src/mcp/tools.py`
2. Implement `add_task(session, user_id, title, description?)` → returns task JSON
3. Implement `list_tasks(session, user_id, status?)` → returns task list
4. Implement `complete_task(session, user_id, task_id)` → marks complete
5. Implement `update_task(session, user_id, task_id, title?, description?)` → updates task
6. Implement `delete_task(session, user_id, task_id)` → deletes task
7. Each function must:
   - Accept SQLModel session
   - Enforce user_id filtering
   - Return structured JSON
   - Handle errors gracefully
8. Add docstrings and task references

**Expected Output:**
See plan.md §2.1.2 for complete implementation.

**Files Modified:**
- CREATE: `backend/src/mcp/tools.py`

**Testing:**
```python
# Unit tests
def test_add_task():
    result = add_task(session, user_id, "Test task")
    assert result["status"] == "created"

def test_list_tasks():
    result = list_tasks(session, user_id)
    assert "tasks" in result
    assert "count" in result
```

**Acceptance Criteria:**
- [ ] All 5 functions implemented
- [ ] User isolation enforced
- [ ] Error handling implemented
- [ ] JSON responses structured correctly
- [ ] No direct database commits in tools (session.commit() called by caller)

---

### T-005: Implement MCP Server

**Priority:** Critical  
**Estimated Time:** 30 minutes  
**Dependencies:** T-004  
**Status:** ⏳ Ready

**Description:**  
Create MCP server module that registers tools in OpenAI function calling format.

**Preconditions:**
- T-004 complete (MCP tools implemented)

**Implementation Steps:**
1. Create file: `backend/src/mcp/__init__.py` (empty)
2. Create file: `backend/src/mcp/server.py`
3. Implement `get_mcp_tools()` function that returns list of tool definitions
4. Each tool definition must follow OpenAI schema:
   ```python
   {
       "type": "function",
       "function": {
           "name": "tool_name",
           "description": "...",
           "parameters": {
               "type": "object",
               "properties": {...},
               "required": [...]
           }
       }
   }
   ```
5. Define all 5 tools (see plan.md §2.1.2)
6. Add docstrings and task references

**Expected Output:**
See plan.md §2.1.2 for complete `get_mcp_tools()` implementation.

**Files Modified:**
- CREATE: `backend/src/mcp/__init__.py`
- CREATE: `backend/src/mcp/server.py`

**Testing:**
```python
def test_get_mcp_tools():
    tools = get_mcp_tools()
    assert len(tools) == 5
    assert all("function" in tool for tool in tools)
```

**Acceptance Criteria:**
- [ ] Function returns list of 5 tools
- [ ] Each tool has correct schema
- [ ] All parameters documented
- [ ] Required fields specified

---

### T-006: Implement Agent Runner

**Priority:** Critical  
**Estimated Time:** 60 minutes  
**Dependencies:** T-004, T-005  
**Status:** ⏳ Ready

**Description:**  
Create agent runner module that orchestrates OpenAI API calls with MCP tools.

**Preconditions:**
- T-004 complete (MCP tools)
- T-005 complete (MCP server)
- OpenAI API key available

**Implementation Steps:**
1. Create file: `backend/src/agent/__init__.py` (empty)
2. Create file: `backend/src/agent/runner.py`
3. Implement `run_agent(session, user_id, messages)` function:
   - Configure OpenAI client
   - Build system prompt
   - Combine system + message history
   - Register MCP tools
   - Call OpenAI Chat Completions API
   - Handle tool calls (if any)
   - Execute tools via MCP
   - Return response + tool metadata
4. Implement `_generate_confirmation(tool_calls)` helper
5. Add error handling for OpenAI API failures
6. Add docstrings and task references

**Expected Output:**
See plan.md §2.1.3 for complete implementation.

**Files Modified:**
- CREATE: `backend/src/agent/__init__.py`
- CREATE: `backend/src/agent/runner.py`

**Testing:**
```python
def test_agent_with_simple_message():
    messages = [{"role": "user", "content": "Hello"}]
    result = run_agent(session, user_id, messages)
    assert "response" in result
    
def test_agent_creates_task():
    messages = [{"role": "user", "content": "Add task to buy milk"}]
    result = run_agent(session, user_id, messages)
    assert len(result["tool_calls"]) > 0
    assert result["tool_calls"][0]["tool"] == "add_task"
```

**Acceptance Criteria:**
- [ ] OpenAI API integration works
- [ ] System prompt configured
- [ ] MCP tools registered
- [ ] Tool calls executed correctly
- [ ] User ID enforced (never from user input)
- [ ] Errors handled gracefully

---

### T-007: Implement Chat Router

**Priority:** Critical  
**Estimated Time:** 60 minutes  
**Dependencies:** T-001, T-002, T-003, T-006  
**Status:** ⏳ Ready

**Description:**  
Create FastAPI router for chat endpoint with full authentication and conversation management.

**Preconditions:**
- T-001, T-002, T-003 complete (database models)
- T-006 complete (agent runner)
- Phase II auth working

**Implementation Steps:**
1. Create file: `backend/src/routers/chat.py`
2. Define router with prefix `/api/{user_id}/chat`
3. Define `ChatRequest` schema (conversation_id?, message)
4. Define `ChatResponse` schema (conversation_id, response, tool_calls)
5. Implement `POST /api/{user_id}/chat` endpoint:
   - Validate JWT token (get_current_user dependency)
   - Verify path user_id matches token user_id
   - Validate message length (1-2000 chars)
   - Get or create conversation
   - Load message history
   - Store user message
   - Call agent runner
   - Store assistant message
   - Update conversation timestamp
   - Return response
6. Add error handling (401, 404, 422, 500)
7. Add docstrings and task references

**Expected Output:**
See plan.md §2.1.4 for complete implementation.

**Files Modified:**
- CREATE: `backend/src/routers/chat.py`

**Testing:**
```python
def test_chat_endpoint_auth_required():
    response = client.post(f"/api/{user_id}/chat", json={...})
    assert response.status_code == 401

def test_chat_creates_conversation():
    response = client.post(
        f"/api/{user_id}/chat",
        json={"conversation_id": None, "message": "Hello"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "conversation_id" in response.json()
```

**Acceptance Criteria:**
- [ ] Endpoint created
- [ ] JWT validation enforced
- [ ] User ID verification works
- [ ] Conversation management works
- [ ] Message persistence works
- [ ] Agent integration works
- [ ] Error handling complete

---

### T-008: Update Main App

**Priority:** High  
**Estimated Time:** 10 minutes  
**Dependencies:** T-007  
**Status:** ⏳ Ready

**Description:**  
Register chat router in main FastAPI application.

**Preconditions:**
- T-007 complete (chat router)

**Implementation Steps:**
1. Open `backend/src/main.py`
2. Import chat router:
   ```python
   from src.routers import chat
   ```
3. Register router:
   ```python
   app.include_router(chat.router)
   ```
4. Verify CORS configuration allows frontend domain

**Expected Output:**
```python
# backend/src/main.py
from src.routers import auth, tasks, chat

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(chat.router)  # NEW
```

**Files Modified:**
- UPDATE: `backend/src/main.py`

**Testing:**
```bash
# Start server
cd backend
uv run fastapi dev src/main.py

# Test endpoint appears in docs
# Visit: http://localhost:8000/docs
# Verify: POST /api/{user_id}/chat is listed
```

**Acceptance Criteria:**
- [ ] Router registered
- [ ] Endpoint appears in /docs
- [ ] No startup errors

---

## FRONTEND TASKS

### T-009: Create Chat Interface Component

**Priority:** Critical  
**Estimated Time:** 45 minutes  
**Dependencies:** None  
**Status:** ⏳ Ready

**Description:**  
Create React component that integrates OpenAI ChatKit UI.

**Preconditions:**
- Phase II frontend working
- OpenAI domain key available

**Implementation Steps:**
1. Create file: `frontend/components/ChatInterface.tsx`
2. Import ChatKit from `@openai/chatkit`
3. Define component props: `userId`, `jwtToken`
4. Implement component:
   - Configure API URL (backend chat endpoint)
   - Configure domain key (from env)
   - Set authorization headers
   - Handle conversation state
   - Add error boundary for missing config
5. Add initial welcome message
6. Add docstring and task reference

**Expected Output:**
See plan.md §2.2.2 for complete implementation.

**Files Modified:**
- CREATE: `frontend/components/ChatInterface.tsx`

**Testing:**
```bash
# Manual test in browser
npm run dev
# Visit: http://localhost:3000/chat
# Verify: ChatKit UI renders
```

**Acceptance Criteria:**
- [ ] Component renders ChatKit
- [ ] API URL configured correctly
- [ ] Domain key loaded from env
- [ ] JWT token included in requests
- [ ] Error handling for missing config

---

### T-010: Create Chat Page

**Priority:** Critical  
**Estimated Time:** 30 minutes  
**Dependencies:** T-009  
**Status:** ⏳ Ready

**Description:**  
Create Next.js page for chat interface with authentication.

**Preconditions:**
- T-009 complete (ChatInterface component)
- Phase II auth working

**Implementation Steps:**
1. Create file: `frontend/app/chat/page.tsx`
2. Import auth function from `@/lib/auth`
3. Import ChatInterface component
4. Implement server component:
   - Check authentication
   - Redirect to login if not authenticated
   - Extract user ID from session
   - Render ChatInterface with user ID and JWT
5. Add page title and description
6. Add docstring and task reference

**Expected Output:**
See plan.md §2.2.1 for complete implementation.

**Files Modified:**
- CREATE: `frontend/app/chat/page.tsx`

**Testing:**
- Test unauthenticated access (should redirect to /login)
- Test authenticated access (should show chat UI)

**Acceptance Criteria:**
- [ ] Page created at correct path
- [ ] Authentication required
- [ ] User ID passed to component
- [ ] JWT token passed to component
- [ ] Page renders correctly

---

### T-011: Update Dashboard

**Priority:** Medium  
**Estimated Time:** 15 minutes  
**Dependencies:** T-010  
**Status:** ⏳ Ready

**Description:**  
Add "Chat with AI" button/link to existing dashboard page.

**Preconditions:**
- T-010 complete (chat page exists)

**Implementation Steps:**
1. Open `frontend/app/dashboard/page.tsx`
2. Import `Link` from `next/link`
3. Add link/button to chat page in appropriate location:
   ```tsx
   <Link
     href="/chat"
     className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
   >
     💬 Chat with AI Assistant
   </Link>
   ```
4. Position button near "Add Task" button

**Expected Output:**
Dashboard now has "Chat with AI Assistant" button that navigates to `/chat`.

**Files Modified:**
- UPDATE: `frontend/app/dashboard/page.tsx`

**Testing:**
- Visit dashboard
- Click "Chat with AI" button
- Verify navigation to /chat works

**Acceptance Criteria:**
- [ ] Button/link added to dashboard
- [ ] Navigation works
- [ ] Styling matches existing design

---

## CONFIGURATION TASKS

### T-012: Update Backend Dependencies

**Priority:** High  
**Estimated Time:** 10 minutes  
**Dependencies:** None  
**Status:** ⏳ Ready

**Description:**  
Add OpenAI and MCP dependencies to backend.

**Preconditions:**
- Phase II backend dependencies installed

**Implementation Steps:**
1. Open `backend/pyproject.toml`
2. Add to `dependencies` array:
   ```toml
   "openai>=1.54.0",
   "mcp>=1.0.0"
   ```
3. Run `uv sync` to install

**Expected Output:**
```toml
[project]
dependencies = [
    # Existing
    "fastapi>=0.115.0",
    "sqlmodel>=0.0.22",
    "python-jose>=3.3.0",
    "bcrypt>=4.2.1",
    "psycopg2-binary>=2.9.9",
    # New
    "openai>=1.54.0",
    "mcp>=1.0.0"
]
```

**Files Modified:**
- UPDATE: `backend/pyproject.toml`

**Testing:**
```bash
cd backend
uv sync
python -c "import openai; print(openai.__version__)"
python -c "import mcp; print('MCP installed')"
```

**Acceptance Criteria:**
- [ ] Dependencies added to pyproject.toml
- [ ] Packages installed successfully
- [ ] No version conflicts

---

### T-013: Update Frontend Dependencies

**Priority:** High  
**Estimated Time:** 15 minutes  
**Dependencies:** None  
**Status:** ⏳ Ready

**Description:**  
Add OpenAI ChatKit dependency to frontend.

**Preconditions:**
- Phase II frontend dependencies installed

**Implementation Steps:**
1. Open `frontend/package.json`
2. Add to `dependencies`:
   ```json
   "@openai/chatkit": "^1.0.0"
   ```
3. Run `npm install` or `npm install @openai/chatkit`

**Expected Output:**
```json
{
  "dependencies": {
    "next": "^16.1.1",
    "react": "^19.2.3",
    "@openai/chatkit": "^1.0.0"
  }
}
```

**Files Modified:**
- UPDATE: `frontend/package.json`
- UPDATE: `frontend/package-lock.json`

**Testing:**
```bash
cd frontend
npm install
npm run build  # Verify no errors
```

**Acceptance Criteria:**
- [ ] Dependency added to package.json
- [ ] Package installed successfully
- [ ] No build errors

---

### T-014: Update Backend Environment Config

**Priority:** High  
**Estimated Time:** 5 minutes  
**Dependencies:** None  
**Status:** ⏳ Ready

**Description:**  
Add OpenAI API key to backend environment configuration.

**Preconditions:**
- OpenAI API key obtained

**Implementation Steps:**
1. Open `backend/.env.example`
2. Add:
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=sk-proj-...
   ```
3. Update local `.env` file with actual key
4. Update `backend/src/config.py` if needed to load `OPENAI_API_KEY`

**Expected Output:**
```env
# Existing variables
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...
JWT_SECRET_KEY=...

# New variable
OPENAI_API_KEY=sk-proj-...
```

**Files Modified:**
- UPDATE: `backend/.env.example`
- UPDATE: `backend/.env` (local only, not committed)
- UPDATE: `backend/src/config.py` (if needed)

**Testing:**
```python
from src.config import settings
assert settings.OPENAI_API_KEY is not None
```

**Acceptance Criteria:**
- [ ] Variable added to .env.example
- [ ] Local .env updated
- [ ] Config.py loads variable
- [ ] No errors loading config

---

### T-015: Update Frontend Environment Config

**Priority:** High  
**Estimated Time:** 10 minutes  
**Dependencies:** None  
**Status:** ⏳ Ready

**Description:**  
Add OpenAI domain key to frontend environment configuration.

**Preconditions:**
- OpenAI domain key obtained from platform

**Implementation Steps:**
1. Configure OpenAI domain allowlist:
   - Visit: https://platform.openai.com/settings/organization/security/domain-allowlist
   - Add domain: `https://panaversity-spec-driven-todo.vercel.app`
   - Copy generated domain key
2. Open `frontend/.env.local.example`
3. Add:
   ```env
   # OpenAI ChatKit Configuration
   NEXT_PUBLIC_OPENAI_DOMAIN_KEY=dk-...
   ```
4. Update local `.env.local` with actual key

**Expected Output:**
```env
# Existing variables
NEXT_PUBLIC_API_URL=https://...
BETTER_AUTH_SECRET=...
DATABASE_URL=...

# New variable
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=dk-...
```

**Files Modified:**
- UPDATE: `frontend/.env.local.example`
- UPDATE: `frontend/.env.local` (local only)

**Testing:**
```bash
# In frontend component
console.log(process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY)
# Should print: dk-...
```

**Acceptance Criteria:**
- [ ] Domain added to OpenAI allowlist
- [ ] Domain key obtained
- [ ] Variable added to .env.local.example
- [ ] Local .env.local updated
- [ ] ChatKit loads without errors

---

## DOCUMENTATION TASKS

### T-016: Update Constitution

**Priority:** Medium  
**Estimated Time:** 30 minutes  
**Dependencies:** None  
**Status:** ⏳ Ready

**Description:**  
Add Phase III principles to project constitution.

**Preconditions:**
- Existing constitution.md exists in phase-2-fullstack/

**Implementation Steps:**
1. Open `phase-2-fullstack/constitution.md`
2. Add new section: "Phase III: AI Agent Principles"
3. Document principles:
   - Stateless agent architecture
   - User isolation at all layers
   - MCP tool standards
   - OpenAI API best practices
   - Conversation persistence
   - Error handling for AI failures
   - Token usage optimization
4. Add references to spec.md and plan.md

**Expected Output:**
```markdown
## Phase III: AI Agent Principles

### Agent Architecture
- **Stateless Design**: All conversation state persisted to database
- **No Global State**: Each request is independent
- **Horizontal Scalability**: No session affinity required

### Security & User Isolation
- **4-Layer Enforcement**:
  1. JWT validation
  2. Path parameter verification
  3. Database query filtering
  4. MCP tool user_id injection
- **Never Trust User Input**: Always use user_id from JWT token

### MCP Tool Standards
- **Stateless Functions**: No global variables
- **Database-Backed**: All operations query database
- **Structured Responses**: Always return JSON
- **Error Handling**: Graceful failures with error messages

### OpenAI API Usage
- **Model**: gpt-4-turbo-preview for speed
- **System Prompt**: Clear instructions for agent behavior
- **Tool Registration**: OpenAI function calling format
- **Token Optimization**: Limit message history (50 messages)
- **Error Handling**: Retry logic with exponential backoff

### Conversation Management
- **Persistence**: All messages stored in database
- **History Loading**: Chronological order
- **Timestamp Tracking**: conversation.updated_at for sorting
```

**Files Modified:**
- UPDATE: `phase-2-fullstack/constitution.md`

**Acceptance Criteria:**
- [ ] New section added
- [ ] All principles documented
- [ ] References to spec/plan included

---

### T-017: Update Main README

**Priority:** Medium  
**Estimated Time:** 20 minutes  
**Dependencies:** T-019, T-020  
**Status:** ⏳ Ready

**Description:**  
Update root README.md with Phase III information and deployment links.

**Preconditions:**
- Phase III deployed

**Implementation Steps:**
1. Open `README.md` (root)
2. Add Phase III section:
   - Feature description
   - Architecture overview
   - Deployment links
3. Update technology stack section
4. Add Phase III demo video link (after recording)

**Expected Output:**
```markdown
## Phase III: AI-Powered Chatbot ✅

**Status**: Deployed  
**Features**:
- Natural language task management
- OpenAI GPT-4 agent
- MCP tool integration
- Persistent conversations
- Stateless architecture

**Deployment**:
| Component | Link |
|-----------|------|
| Chat UI | https://panaversity-spec-driven-todo.vercel.app/chat |
| Backend API | https://ahmedkhi-todo-api-phase2.hf.space/docs |
| Demo Video | [YouTube link] |

**Technology Stack**:
- AI: OpenAI GPT-4 Turbo, MCP Server
- Frontend: OpenAI ChatKit
- Backend: FastAPI, SQLModel, PostgreSQL
- Deployment: Vercel + Hugging Face Spaces
```

**Files Modified:**
- UPDATE: `README.md`

**Acceptance Criteria:**
- [ ] Phase III section added
- [ ] Deployment links updated
- [ ] Technology stack updated
- [ ] Demo video link included

---

## TESTING & DEPLOYMENT TASKS

### T-018: End-to-End Testing

**Priority:** Critical  
**Estimated Time:** 60 minutes  
**Dependencies:** T-001 through T-015  
**Status:** ⏳ Ready

**Description:**  
Comprehensive testing of Phase III features before deployment.

**Preconditions:**
- All implementation tasks complete
- Local environment working

**Test Scenarios:**

**1. Authentication Flow**
- [ ] Unauthenticated user cannot access /chat (redirects to /login)
- [ ] Authenticated user can access /chat
- [ ] JWT token passed correctly to backend

**2. Conversation Creation**
- [ ] New chat creates conversation in database
- [ ] Conversation ID returned in response
- [ ] Subsequent messages use same conversation ID

**3. Task Operations via Chat**
- [ ] "Add task to buy milk" → Creates task in database
- [ ] "Show my tasks" → Returns task list
- [ ] "Mark task 1 as complete" → Updates task.completed = true
- [ ] "Change task 2 to 'Call John'" → Updates task title
- [ ] "Delete task 3" → Removes task from database

**4. User Isolation**
- [ ] User A cannot see User B's conversations
- [ ] User A cannot manipulate User B's tasks
- [ ] Path user_id mismatch returns 404

**5. Message Persistence**
- [ ] User messages stored in database
- [ ] Assistant responses stored in database
- [ ] Message history loads correctly

**6. Error Handling**
- [ ] Invalid message (empty) returns 422
- [ ] Invalid conversation_id returns 404
- [ ] OpenAI API error returns 500 with friendly message

**7. Frontend UI**
- [ ] ChatKit renders correctly
- [ ] Messages display in chat bubbles
- [ ] Loading indicator while processing
- [ ] Error messages display correctly

**Test Commands:**
```bash
# Backend unit tests
cd backend
uv run pytest tests/

# Frontend build test
cd frontend
npm run build
npm run start

# Manual testing
# 1. Start backend: cd backend && uv run fastapi dev src/main.py
# 2. Start frontend: cd frontend && npm run dev
# 3. Open browser: http://localhost:3000/chat
# 4. Test each scenario above
```

**Files Modified:**
- None (testing only)

**Acceptance Criteria:**
- [ ] All test scenarios pass
- [ ] No console errors
- [ ] Performance acceptable (<3s per request)
- [ ] UI responsive

---

### T-019: Deploy Backend

**Priority:** Critical  
**Estimated Time:** 30 minutes  
**Dependencies:** T-018  
**Status:** ⏳ Ready

**Description:**  
Deploy Phase III backend to Hugging Face Spaces.

**Preconditions:**
- T-018 complete (testing passed)
- Hugging Face Spaces account configured

**Deployment Steps:**

**1. Database Migration**
```bash
# Connect to Neon production database
psql $DATABASE_URL

# Run migrations
cd backend
uv run alembic upgrade head

# Verify tables
SELECT * FROM conversations LIMIT 1;
SELECT * FROM messages LIMIT 1;
```

**2. Update Environment Variables**
- Go to: Hugging Face Space Settings
- Add: `OPENAI_API_KEY=sk-proj-...`
- Verify: `DATABASE_URL` is set
- Verify: `BETTER_AUTH_SECRET` is set

**3. Push Code**
```bash
git add .
git commit -m "Phase III: Add AI chatbot with MCP integration"
git push origin main
```

**4. Verify Deployment**
- Visit: https://ahmedkhi-todo-api-phase2.hf.space/docs
- Check: POST /api/{user_id}/chat endpoint exists
- Test: Send sample request with valid JWT

**5. Smoke Test**
```bash
# Get JWT token (login via frontend or Postman)
TOKEN="eyJ..."
USER_ID="..."

# Test chat endpoint
curl -X POST "https://ahmedkhi-todo-api-phase2.hf.space/api/$USER_ID/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": null, "message": "Hello"}'

# Should return: {"conversation_id": 1, "response": "...", "tool_calls": []}
```

**Files Modified:**
- None (deployment only)

**Acceptance Criteria:**
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] Code deployed successfully
- [ ] API endpoint accessible
- [ ] Smoke test passes

---

### T-020: Deploy Frontend

**Priority:** Critical  
**Estimated Time:** 30 minutes  
**Dependencies:** T-019  
**Status:** ⏳ Ready

**Description:**  
Deploy Phase III frontend to Vercel with OpenAI domain configuration.

**Preconditions:**
- T-019 complete (backend deployed)
- Vercel account configured

**Deployment Steps:**

**1. Configure OpenAI Domain Allowlist**
- Visit: https://platform.openai.com/settings/organization/security/domain-allowlist
- Add domain: `https://panaversity-spec-driven-todo.vercel.app`
- Copy domain key: `dk-...`

**2. Update Vercel Environment Variables**
- Go to: Vercel Dashboard → Project Settings → Environment Variables
- Add: `NEXT_PUBLIC_OPENAI_DOMAIN_KEY=dk-...`
- Verify: `NEXT_PUBLIC_API_URL` points to HF Spaces backend
- Verify: `DATABASE_URL` is set (for Better Auth)
- Verify: `BETTER_AUTH_SECRET` is set

**3. Deploy**
```bash
git add .
git commit -m "Phase III: Add ChatKit frontend integration"
git push origin main

# Vercel auto-deploys from main branch
```

**4. Verify Deployment**
- Visit: https://panaversity-spec-driven-todo.vercel.app
- Login with test account
- Click "Dashboard"
- Click "Chat with AI Assistant" button
- Verify: Chat page loads
- Verify: ChatKit UI renders
- Test: Send message "Hello"

**5. End-to-End Test**
```
1. Login
2. Navigate to /chat
3. Send: "Add task to buy groceries"
   → Bot confirms task creation
4. Go to /dashboard
   → Task appears in list
5. Go back to /chat
6. Send: "Show my tasks"
   → Bot lists "Buy groceries"
7. Send: "Mark task 1 as complete"
   → Bot confirms completion
8. Go to /dashboard
   → Task marked as complete
```

**Files Modified:**
- None (deployment only)

**Acceptance Criteria:**
- [ ] OpenAI domain configured
- [ ] Environment variables set
- [ ] Code deployed successfully
- [ ] Chat UI accessible
- [ ] End-to-end test passes
- [ ] No console errors

---

## Implementation Order

### Sprint 1: Backend Core (4-5 hours)
1. T-001: Create Conversation Model
2. T-002: Create Message Model
3. T-003: Create Database Migration
4. T-004: Implement MCP Tools
5. T-005: Implement MCP Server
6. T-006: Implement Agent Runner
7. T-007: Implement Chat Router
8. T-008: Update Main App

### Sprint 2: Frontend Core (2-3 hours)
9. T-009: Create Chat Interface Component
10. T-010: Create Chat Page
11. T-011: Update Dashboard

### Sprint 3: Configuration (1 hour)
12. T-012: Update Backend Dependencies
13. T-013: Update Frontend Dependencies
14. T-014: Update Backend Environment Config
15. T-015: Update Frontend Environment Config

### Sprint 4: Documentation (1 hour)
16. T-016: Update Constitution
17. T-017: Update Main README

### Sprint 5: Testing & Deployment (2-3 hours)
18. T-018: End-to-End Testing
19. T-019: Deploy Backend
20. T-020: Deploy Frontend

**Total Estimated Time:** 10-13 hours

---

## Quality Gates

### Before Implementation
- [ ] Spec.md reviewed and approved
- [ ] Plan.md reviewed and approved
- [ ] Tasks.md reviewed and approved

### After Backend Implementation
- [ ] All backend files created
- [ ] Database models work
- [ ] MCP tools work
- [ ] Agent runner works
- [ ] Chat endpoint works
- [ ] Unit tests pass

### After Frontend Implementation
- [ ] All frontend files created
- [ ] ChatKit renders
- [ ] Authentication works
- [ ] API integration works

### Before Deployment
- [ ] All tasks complete
- [ ] End-to-end test passes
- [ ] No errors in logs
- [ ] Performance acceptable
- [ ] Documentation updated

### After Deployment
- [ ] Backend accessible
- [ ] Frontend accessible
- [ ] Production smoke test passes
- [ ] Demo video recorded
- [ ] README updated

---

## Success Criteria

Phase III is complete when:

1. ✅ All 20 tasks completed
2. ✅ Backend deployed to Hugging Face Spaces
3. ✅ Frontend deployed to Vercel
4. ✅ End-to-end test passes in production
5. ✅ User can chat with AI to manage tasks
6. ✅ Conversations persist across sessions
7. ✅ User isolation enforced
8. ✅ No errors in production logs
9. ✅ Documentation updated
10. ✅ Demo video recorded

---

**STATUS**: Ready for Implementation  
**Next Action**: Begin T-001 (Create Conversation Model)  
**Created By**: Ahmed Khan  
**Date**: January 8, 2026

---

**END OF TASK BREAKDOWN**
