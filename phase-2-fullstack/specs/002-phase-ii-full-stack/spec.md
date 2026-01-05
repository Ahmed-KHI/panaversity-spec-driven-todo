# Phase II: Full-Stack Web Application - SPECIFICATION

## Document Information

**Phase:** Phase II - Full-Stack Web Application with Authentication  
**Status:** Active  
**Version:** 1.0  
**Last Updated:** January 4, 2026  
**Based On:** 
- Hackathon II Document (GIAIC)
- Phase I Console App (Completed)
- Reference Repository: Ameen-Alam/Full-Stack-Web-Application

---

## 1. Overview

### 1.1 Purpose

Transform the Phase I in-memory console application into a production-ready, multi-user web application with persistent storage, user authentication, and a modern responsive interface.

### 1.2 Scope

Implement a full-stack Todo application with:
- **Frontend**: Next.js 16+ with App Router, TypeScript, Tailwind CSS
- **Backend**: FastAPI with SQLModel ORM, async operations
- **Database**: Neon Serverless PostgreSQL with proper schema
- **Authentication**: Better Auth with JWT tokens
- **Security**: User data isolation, password hashing, token verification

### 1.3 Key Objectives

1. **Multi-User Support**: Each user has their own isolated task list
2. **RESTful API**: Standard HTTP endpoints for all operations
3. **Modern UI**: Responsive, accessible interface
4. **Security**: Proper authentication and authorization
5. **Scalability**: Cloud-ready architecture with Docker support

### 1.4 Out of Scope (For Phase II)

- AI Chatbot integration (Phase III)
- Kubernetes deployment (Phase IV)
- Event-driven architecture with Kafka (Phase V)
- Advanced features: priorities, tags, recurring tasks (Phase V)
- Mobile applications
- Real-time collaboration

---

## 2. User Stories

### 2.1 User Registration & Authentication

**US-001: User Registration**
- **As a** new user
- **I want to** create an account with email and password
- **So that** I can securely manage my personal todo list

**Acceptance Criteria**:
- Email must be valid format and unique
- Password minimum 8 characters
- Password must be hashed (bcrypt) before storage
- Account created immediately on valid submission
- User automatically logged in after registration
- Error messages for duplicate email or invalid input

**US-002: User Login**
- **As a** registered user
- **I want to** log in with my credentials
- **So that** I can access my todo list from any device

**Acceptance Criteria**:
- Login with email and password
- JWT token issued on successful login
- Token stored securely (httpOnly cookie or localStorage)
- Invalid credentials show clear error message
- Redirect to dashboard after successful login
- Token expires after 7 days

### 2.2 Task Management (Basic Level - Phase II)

**US-003: View All My Tasks**
- **As a** logged-in user
- **I want to** see all my tasks in a list
- **So that** I can review what needs to be done

**Acceptance Criteria**:
- Only my tasks are visible (user isolation enforced)
- Tasks display title, description, completion status
- Empty state message when no tasks exist
- Sorted by creation date (newest first)
- Completed tasks visually distinguished

**US-004: Create New Task**
- **As a** logged-in user
- **I want to** add a new task with title and description
- **So that** I can remember what I need to do

**Acceptance Criteria**:
- Title is required (1-200 characters)
- Description is optional (max 1000 characters)
- Task created immediately on submission
- Redirected to task list after creation
- New task appears at top of list
- Validation errors shown inline

**US-005: Update Existing Task**
- **As a** logged-in user
- **I want to** modify a task's title or description
- **So that** I can correct mistakes or add details

**Acceptance Criteria**:
- Can edit title and/or description
- Changes saved immediately
- Updated timestamp tracked
- Cannot edit other users' tasks (404 if attempted)
- Validation rules apply (same as creation)

**US-006: Mark Task Complete/Incomplete**
- **As a** logged-in user
- **I want to** toggle task completion status
- **So that** I can track my progress

**Acceptance Criteria**:
- Single click/tap to toggle status
- Visual feedback (checkbox, strikethrough, color change)
- Status persists across sessions
- Can toggle between complete and incomplete
- Updated timestamp tracked

**US-007: Delete Task**
- **As a** logged-in user
- **I want to** remove tasks I no longer need
- **So that** my list stays clean and relevant

**Acceptance Criteria**:
- Confirmation dialog before deletion
- Task permanently removed from database
- Cannot delete other users' tasks (404 if attempted)
- No undo functionality (Phase II limitation)
- Redirect to task list after deletion

---

## 3. Functional Requirements

### 3.1 Authentication System

**FR-001: User Registration**
- Email validation (RFC 5322 compliant)
- Password strength: minimum 8 characters
- Password hashing: bcrypt with salt rounds ≥ 10
- Duplicate email detection: return 409 Conflict
- UUID generation for user ID
- Timestamp tracking (created_at)

**FR-002: User Login**
- Email + password authentication
- JWT token generation with 7-day expiration
- Token payload: user_id, email, issued_at, expires_at
- Shared secret between frontend and backend (BETTER_AUTH_SECRET)
- Return token + user info on successful login
- 401 Unauthorized for invalid credentials

**FR-003: Token Verification**
- JWT verification on every protected endpoint
- Extract user_id from validated token
- 401 Unauthorized for missing/invalid/expired token
- No session state on server (stateless authentication)

### 3.2 Task CRUD Operations

**FR-004: Create Task**
- Endpoint: POST /api/{user_id}/tasks
- Request: `{ title: string, description?: string }`
- Validate: title required, 1-200 chars; description max 1000 chars
- Auto-generate: id, created_at, updated_at, completed=false
- Associate with authenticated user
- Return: 201 Created with task object

**FR-005: List Tasks**
- Endpoint: GET /api/{user_id}/tasks
- Query params: completed=[all|pending|completed] (optional)
- Filter by authenticated user ONLY
- Sort by created_at descending
- Return: 200 OK with array of task objects

**FR-006: Get Single Task**
- Endpoint: GET /api/{user_id}/tasks/{task_id}
- Validate: task belongs to authenticated user
- Return: 200 OK with task object
- Error: 404 Not Found if not owned by user

**FR-007: Update Task (Full)**
- Endpoint: PUT /api/{user_id}/tasks/{task_id}
- Request: `{ title?: string, description?: string }`
- Validate: ownership, field constraints
- Update: updated_at timestamp
- Return: 200 OK with updated task

**FR-008: Update Task (Partial - Toggle Complete)**
- Endpoint: PATCH /api/{user_id}/tasks/{task_id}
- Request: `{ completed: boolean }`
- Validate: ownership
- Toggle completion status
- Update: updated_at timestamp
- Return: 200 OK with updated task

**FR-009: Delete Task**
- Endpoint: DELETE /api/{user_id}/tasks/{task_id}
- Validate: ownership
- Permanently delete from database
- Return: 204 No Content
- Error: 404 Not Found if not owned by user

### 3.3 User Interface

**FR-010: Registration Page**
- Form fields: email, password, confirm password
- Client-side validation before submission
- Display validation errors inline
- Redirect to dashboard after successful registration
- Link to login page

**FR-011: Login Page**
- Form fields: email, password
- "Remember me" checkbox (optional Phase II)
- Display authentication errors
- Redirect to dashboard after successful login
- Link to registration page

**FR-012: Dashboard / Task List Page**
- Display all user's tasks
- Visual status indicators (checkboxes)
- Completed tasks styled differently (strikethrough, muted color)
- Empty state when no tasks
- Button to create new task
- Logout button

**FR-013: Task Item Component**
- Display: title, description (truncated), status
- Actions: toggle complete, edit, delete
- Delete requires confirmation
- Click task to view/edit details

**FR-014: Create/Edit Task Form**
- Fields: title (required), description (optional)
- Inline validation
- Submit button
- Cancel button (returns to list)
- Pre-fill fields when editing

---

## 4. Non-Functional Requirements

### 4.1 Performance

- **API Response Time**: < 500ms for p95
- **Page Load Time**: < 2s for first contentful paint
- **Database Queries**: Indexed on user_id, optimized joins
- **Concurrent Users**: Support 100+ simultaneous users

### 4.2 Security

- **Password Storage**: bcrypt hashing, never plaintext
- **JWT Tokens**: Signed with strong secret (min 32 chars)
- **User Isolation**: MANDATORY - all queries filter by user_id
- **Authorization Check**: Path user_id must match authenticated user
- **SQL Injection**: Protected via SQLModel parameterized queries
- **XSS Protection**: Input sanitization, output encoding
- **CORS**: Configured for frontend domain only

### 4.3 Scalability

- **Stateless Backend**: No session storage, JWT-only auth
- **Horizontal Scaling**: Backend can run multiple instances
- **Database Connection Pooling**: Managed by SQLModel
- **Docker Ready**: Both frontend and backend containerized

### 4.4 Usability

- **Responsive Design**: Mobile, tablet, desktop support
- **Accessibility**: WCAG 2.1 Level AA compliance (Phase II best effort)
- **Error Messages**: Clear, actionable feedback
- **Loading States**: Visual indicators for async operations
- **Consistent UI**: Tailwind CSS design system

### 4.5 Reliability

- **Error Handling**: Graceful degradation, user-friendly messages
- **Data Validation**: Client-side and server-side
- **Database Transactions**: ACID compliance for critical operations
- **Logging**: Structured logs for debugging (FastAPI)

### 4.6 Maintainability

- **Code Quality**: Type hints (Python), TypeScript (frontend)
- **Documentation**: Inline comments, README, API docs (Swagger)
- **Modular Architecture**: Clear separation of concerns
- **Testing**: Unit tests for critical paths (optional Phase II)

---

## 5. Technical Constraints

### 5.1 Technology Stack (Non-Negotiable)

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Next.js | 16+ |
| UI Library | React | 19+ |
| Styling | Tailwind CSS | 4.x |
| Backend | FastAPI | Latest |
| ORM | SQLModel | Latest |
| Database | PostgreSQL (Neon) | 16 |
| Auth | Better Auth + JWT | Latest |
| Language (Backend) | Python | 3.13+ |
| Language (Frontend) | TypeScript | 5.x+ |
| Package Manager (Backend) | UV | Latest |
| Package Manager (Frontend) | npm | Latest |
| Containerization | Docker | Latest |

### 5.2 Development Environment

- **Windows Users**: Must use WSL 2 (Windows Subsystem for Linux)
- **IDE**: Claude Code recommended for spec-driven development
- **Version Control**: Git with GitHub repository
- **Spec-Driven Workflow**: Spec-Kit Plus mandatory

### 5.3 Deployment Requirements

- **Frontend**: Deploy on Vercel (free tier)
- **Backend**: Deploy on Vercel, Railway, or similar (free tier)
- **Database**: Neon Serverless PostgreSQL (free tier)
- **Environment Variables**: Managed via .env files (not committed)
- **Docker Support**: docker-compose.yml for local development

---

## 6. API Specifications

### 6.1 Authentication Endpoints

**POST /api/auth/register**
```json
Request:
{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response 201:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "message": "Account created successfully"
}

Response 400:
{
  "detail": "Invalid email format"
}

Response 409:
{
  "detail": "An account with this email already exists"
}
```

**POST /api/auth/login**
```json
Request:
{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response 200:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com"
  }
}

Response 401:
{
  "detail": "Invalid email or password"
}
```

### 6.2 Task Endpoints (All Require JWT)

**GET /api/{user_id}/tasks**
```json
Query Params: ?completed=[all|pending|completed]

Response 200:
{
  "tasks": [
    {
      "id": 1,
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2026-01-04T10:00:00Z",
      "updated_at": "2026-01-04T10:00:00Z"
    }
  ],
  "count": 1
}

Response 401:
{
  "detail": "Not authenticated"
}
```

**POST /api/{user_id}/tasks**
```json
Request:
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}

Response 201:
{
  "id": 1,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-01-04T10:00:00Z",
  "updated_at": "2026-01-04T10:00:00Z"
}

Response 400:
{
  "detail": "Title is required"
}
```

**GET /api/{user_id}/tasks/{task_id}**
```json
Response 200:
{
  "id": 1,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-01-04T10:00:00Z",
  "updated_at": "2026-01-04T10:00:00Z"
}

Response 404:
{
  "detail": "Task not found"
}
```

**PUT /api/{user_id}/tasks/{task_id}**
```json
Request:
{
  "title": "Buy groceries and fruits",
  "description": "Milk, eggs, bread, apples, bananas"
}

Response 200:
{
  "id": 1,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries and fruits",
  "description": "Milk, eggs, bread, apples, bananas",
  "completed": false,
  "created_at": "2026-01-04T10:00:00Z",
  "updated_at": "2026-01-04T12:30:00Z"
}

Response 404:
{
  "detail": "Task not found"
}
```

**PATCH /api/{user_id}/tasks/{task_id}**
```json
Request:
{
  "completed": true
}

Response 200:
{
  "id": 1,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": true,
  "created_at": "2026-01-04T10:00:00Z",
  "updated_at": "2026-01-04T15:00:00Z"
}
```

**DELETE /api/{user_id}/tasks/{task_id}**
```
Response 204: No Content

Response 404:
{
  "detail": "Task not found"
}
```

---

## 7. Data Model

### 7.1 Database Schema

**users**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

**tasks**
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
```

### 7.2 Entity Relationships

```
users (1) ----< (many) tasks

Relationship:
- One user can have many tasks
- Each task belongs to exactly one user
- CASCADE DELETE: When user is deleted, all their tasks are deleted
```

---

## 8. Security Model

### 8.1 Authentication Flow

```
1. User Registration:
   User → Frontend → POST /api/auth/register → Backend
   ↓
   Backend: Hash password (bcrypt)
   ↓
   Backend: Save to database
   ↓
   Backend: Generate JWT token
   ↓
   Backend: Return token + user info
   ↓
   Frontend: Store token (localStorage or httpOnly cookie)

2. User Login:
   User → Frontend → POST /api/auth/login → Backend
   ↓
   Backend: Verify password (bcrypt.compare)
   ↓
   Backend: Generate JWT token
   ↓
   Backend: Return token + user info
   ↓
   Frontend: Store token

3. Authenticated Request:
   User → Frontend → API Request (with JWT in header) → Backend
   ↓
   Backend: Verify JWT signature
   ↓
   Backend: Extract user_id from token
   ↓
   Backend: Compare path user_id with token user_id
   ↓
   Backend: Execute query filtered by user_id
   ↓
   Backend: Return data (only user's resources)
```

### 8.2 User Isolation (CRITICAL)

**Enforcement Rules**:
1. **EVERY database query** must filter by `WHERE user_id = authenticated_user_id`
2. **EVERY endpoint** with {user_id} in path must verify it matches the JWT user
3. **404 Not Found** (not 403 Forbidden) for unauthorized access attempts
4. **No data leakage**: Never confirm resource existence to wrong user

**Example Implementation**:
```python
# CORRECT: User isolation enforced
@router.get("/api/{user_id}/tasks")
def list_tasks(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # CRITICAL: Verify path user_id matches authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(status_code=404, detail="Not found")
    
    # CRITICAL: Query filtered by user_id
    tasks = session.exec(
        select(Task).where(Task.user_id == current_user.id)
    ).all()
    return {"tasks": tasks}

# WRONG: No user isolation (NEVER DO THIS)
@router.get("/api/tasks")
def list_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(Task)).all()  # ❌ Returns ALL users' tasks!
    return {"tasks": tasks}
```

---

## 9. Success Criteria

### 9.1 Phase II Completion Checklist

**Backend**:
- [ ] FastAPI application running
- [ ] SQLModel models for User and Task
- [ ] Neon PostgreSQL connected
- [ ] All 2 auth endpoints working
- [ ] All 6 task endpoints working
- [ ] JWT authentication implemented
- [ ] User isolation enforced on ALL endpoints
- [ ] Password hashing (bcrypt) working
- [ ] CORS configured for frontend
- [ ] Swagger UI accessible at /docs

**Frontend**:
- [ ] Next.js 16+ App Router setup
- [ ] Registration page working
- [ ] Login page working
- [ ] Dashboard displaying user's tasks
- [ ] Create task form working
- [ ] Edit task functionality working
- [ ] Delete task with confirmation working
- [ ] Toggle complete/incomplete working
- [ ] Better Auth integration working
- [ ] JWT token management working
- [ ] Protected routes enforced
- [ ] Responsive design (mobile, tablet, desktop)

**Integration**:
- [ ] Frontend communicates with backend
- [ ] User can register, login, logout
- [ ] User can perform all 5 Basic Level operations
- [ ] User isolation verified (cannot see other users' tasks)
- [ ] Error handling working (network, validation, auth)
- [ ] Docker Compose setup working

### 9.2 Demo Requirements (90 seconds)

Must demonstrate:
1. **Registration**: Create new account (15s)
2. **Login**: Log in with credentials (10s)
3. **Create Tasks**: Add 2-3 tasks (15s)
4. **View List**: Show all tasks (5s)
5. **Toggle Complete**: Mark task as done (5s)
6. **Update Task**: Edit a task (10s)
7. **Delete Task**: Remove a task with confirmation (10s)
8. **User Isolation**: Show second user cannot see first user's tasks (15s)
9. **Logout**: Log out and show login screen (5s)

### 9.3 Submission Requirements

**GitHub Repository**:
- [ ] Public repository
- [ ] All source code (frontend, backend)
- [ ] /specs folder with this specification
- [ ] README.md with setup instructions
- [ ] CLAUDE.md with Claude Code usage
- [ ] .gitignore excluding secrets

**Deployed Application**:
- [ ] Frontend on Vercel (URL provided)
- [ ] Backend on Vercel/Railway (URL provided)
- [ ] Database on Neon (connection working)

**Documentation**:
- [ ] Demo video (under 90 seconds)
- [ ] Setup instructions in README
- [ ] API documentation (Swagger)
- [ ] Environment variable template

---

## 10. Testing Scenarios

### 10.1 Authentication Tests

**Test 1: User Registration**
- Input: Valid email and password
- Expected: Account created, JWT token returned
- Verify: User appears in database

**Test 2: Duplicate Registration**
- Input: Email already in database
- Expected: 409 Conflict error
- Verify: Original user unchanged

**Test 3: User Login**
- Input: Valid credentials
- Expected: JWT token returned
- Verify: Token can be used for API calls

**Test 4: Invalid Login**
- Input: Wrong password
- Expected: 401 Unauthorized
- Verify: No token issued

### 10.2 Task CRUD Tests

**Test 5: Create Task**
- Precondition: User logged in
- Input: Title and description
- Expected: Task created, appears in database
- Verify: Task associated with correct user

**Test 6: List Tasks**
- Precondition: User has 3 tasks
- Input: GET request
- Expected: Returns exactly 3 tasks
- Verify: Only user's tasks returned

**Test 7: Update Task**
- Precondition: Task exists
- Input: New title
- Expected: Task updated, updated_at changed
- Verify: Changes persisted

**Test 8: Toggle Complete**
- Precondition: Task is incomplete
- Input: PATCH with completed=true
- Expected: Task marked complete
- Verify: Status persisted

**Test 9: Delete Task**
- Precondition: Task exists
- Input: DELETE request
- Expected: Task removed from database
- Verify: Task no longer appears in list

### 10.3 User Isolation Tests (CRITICAL)

**Test 10: Cross-User Access Attempt**
- Precondition: User A has tasks, User B logged in
- Input: User B requests User A's task
- Expected: 404 Not Found
- Verify: No data leaked

**Test 11: Path Parameter Mismatch**
- Precondition: User A logged in
- Input: Request to /api/{user_b_id}/tasks with User A's token
- Expected: 404 Not Found
- Verify: Authorization check working

---

## 11. Known Limitations (Phase II)

1. **No Undo**: Deleted tasks are permanently removed
2. **No Search**: Cannot search tasks by keyword (Phase V)
3. **No Filtering**: Limited to completed/pending/all (Phase V adds more)
4. **No Priorities**: No task priority levels (Phase V)
5. **No Tags**: No task categorization (Phase V)
6. **No Due Dates**: No deadline tracking (Phase V)
7. **No Recurring Tasks**: Manual re-creation required (Phase V)
8. **No Real-Time Sync**: Must refresh to see changes from other devices
9. **No Collaboration**: Cannot share tasks with other users
10. **No Offline Mode**: Requires internet connection

---

## 12. Migration from Phase I

### 12.1 Concepts Carried Forward

| Phase I Feature | Phase II Equivalent |
|----------------|---------------------|
| In-memory storage | PostgreSQL database |
| Single user | Multi-user with authentication |
| Console commands | RESTful API endpoints |
| Task model | SQLModel Task entity |
| CRUD operations | HTTP methods (GET, POST, PUT, PATCH, DELETE) |

### 12.2 New Concepts Introduced

- User authentication and authorization
- JWT token-based security
- Client-server architecture
- RESTful API design
- Relational database with foreign keys
- Frontend-backend separation
- Docker containerization
- Cloud deployment

---

## 13. Future Phases Preview

**Phase III: AI Chatbot**
- OpenAI ChatKit interface
- OpenAI Agents SDK integration
- MCP server for task operations
- Natural language task management

**Phase IV: Kubernetes Deployment**
- Local deployment on Minikube
- Helm charts for orchestration
- kubectl-ai for AIOps
- Docker Desktop integration

**Phase V: Cloud-Native Production**
- Deployment to DigitalOcean/Azure/GCP
- Kafka event streaming
- Dapr distributed runtime
- Advanced features (priorities, tags, recurring tasks)

---

## 14. Approval

**Prepared By:** [Your Name]  
**Date:** January 4, 2026  
**Approved By:** _____________  
**Approval Date:** _____________

---

## 15. References

- **Hackathon II Document**: GIAIC Specification
- **Reference Repository**: https://github.com/Ameen-Alam/Full-Stack-Web-Application.git
- **Phase I Repository**: https://github.com/Ahmed-KHI/panaversity-spec-driven-todo.git
- **Next.js Documentation**: https://nextjs.org/docs
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **Better Auth Documentation**: https://www.better-auth.com/docs

---

**Next Document:** `plan.md` (Architecture and Implementation Plan)
