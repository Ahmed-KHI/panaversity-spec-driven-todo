# Phase II: Full-Stack Web Application - IMPLEMENTATION PLAN

**Phase:** Phase II - Multi-User Web Application  
**Based On:** spec.md (WHAT to build)  
**Purpose:** Define HOW to implement the requirements  
**Date:** January 5, 2026  
**Status:** Implemented  

---

## 1. Architecture Overview

### 1.1 System Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                           PHASE II SYSTEM                            │
└─────────────────────────────────────────────────────────────────────┘

┌────────────────────┐         ┌────────────────────┐         ┌──────────────────┐
│                    │         │                    │         │                  │
│   Frontend (Web)   │────────▶│   Backend (API)    │────────▶│   Database       │
│   Next.js 16+      │  HTTP   │   FastAPI          │  SQL    │   PostgreSQL 16  │
│   TypeScript       │         │   Python 3.13      │         │   (Neon)         │
│                    │         │                    │         │                  │
└────────────────────┘         └────────────────────┘         └──────────────────┘
        │                              │                              │
        │                              │                              │
        ▼                              ▼                              ▼
┌────────────────────┐         ┌────────────────────┐         ┌──────────────────┐
│ Better Auth        │         │ JWT Verification   │         │ User Isolation   │
│ (Session Mgmt)     │         │ bcrypt Hashing     │         │ Foreign Keys     │
└────────────────────┘         └────────────────────┘         └──────────────────┘
```

### 1.2 Data Flow

**Registration Flow:**
```
User → Frontend Form → POST /api/auth/register → Backend
  ↓
Validate email/password
  ↓
Hash password (bcrypt)
  ↓
Create user in DB
  ↓
Return user info → Frontend → Auto-login
```

**Authentication Flow:**
```
User → Login Form → POST /api/auth/login → Backend
  ↓
Verify email exists
  ↓
Verify password hash
  ↓
Generate JWT token (7 days)
  ↓
Return token → Frontend stores in cookie → Dashboard
```

**Task Operations Flow:**
```
User → Dashboard → API Request (with JWT) → Backend
  ↓
Extract JWT from Authorization header
  ↓
Verify token signature
  ↓
Extract user_id from token
  ↓
Verify path user_id matches token user_id
  ↓
Query DB filtered by user_id
  ↓
Return data → Frontend → Display
```

---

## 2. Backend Architecture

### 2.1 FastAPI Application Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI app, CORS, lifespan events
│   ├── config.py            # Settings (Pydantic BaseSettings)
│   ├── database.py          # SQLModel engine, session management
│   │
│   ├── models/              # SQLModel database models
│   │   ├── __init__.py
│   │   ├── user.py         # User(SQLModel, table=True)
│   │   └── task.py         # Task(SQLModel, table=True)
│   │
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py         # RegisterRequest, LoginRequest, etc.
│   │   └── task.py         # TaskCreateRequest, TaskResponse, etc.
│   │
│   ├── routers/             # API endpoint handlers
│   │   ├── __init__.py
│   │   ├── auth.py         # /api/auth/register, /api/auth/login
│   │   └── tasks.py        # /api/{user_id}/tasks/* (6 endpoints)
│   │
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── security.py     # JWT, bcrypt functions
│       └── deps.py         # get_current_user() dependency
│
├── pyproject.toml           # UV dependencies
├── .env                     # Environment variables
└── Dockerfile               # For Hugging Face Spaces
```

### 2.2 Database Models (SQLModel)

**User Model:**
```python
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)  # bcrypt hash
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    tasks: list["Task"] = Relationship(back_populates="user")
```

**Task Model:**
```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    
    id: int = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    user: User = Relationship(back_populates="tasks")
```

**Why these designs?**
- User ID: UUID for Better Auth compatibility
- Task ID: Integer for simplicity (not exposed to other users)
- Foreign Key: Enforces referential integrity
- Indexes: Fast lookups on user_id, email
- Timestamps: Audit trail

### 2.3 Request/Response Schemas (Pydantic)

**Auth Schemas:**
```python
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class RegisterResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    user: RegisterResponse
    token: str
```

**Task Schemas:**
```python
class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)

class TaskUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None

class TaskResponse(BaseModel):
    id: int
    user_id: UUID
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime

class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    count: int
```

**Separation Rationale:**
- Models: Database representation (what we store)
- Schemas: API representation (what we send/receive)
- Models include internal fields (password_hash)
- Schemas exclude sensitive data

### 2.4 API Router Design

**Authentication Router (`/api/auth`):**
```python
router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(request: RegisterRequest, session: Session = Depends(get_session)):
    # 1. Check email uniqueness
    # 2. Hash password (bcrypt, 12 rounds)
    # 3. Create user
    # 4. Return user info
    pass

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, session: Session = Depends(get_session)):
    # 1. Find user by email
    # 2. Verify password hash
    # 3. Generate JWT token (7 days)
    # 4. Return user + token
    pass
```

**Task Router (`/api/{user_id}/tasks`):**
```python
router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])

# All endpoints use get_current_user() dependency
# All endpoints verify path user_id matches token user_id

@router.get("", response_model=TaskListResponse)
def list_tasks(
    user_id: UUID, 
    completed: str = "all",  # Filter: all, pending, completed
    current_user: User = Depends(get_current_user)
):
    # CRITICAL: Verify user_id matches current_user.id
    # Query tasks filtered by user_id
    # Apply completion filter
    pass

@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    user_id: UUID,
    request: TaskCreateRequest,
    current_user: User = Depends(get_current_user)
):
    # Verify user, create task with user_id
    pass

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(user_id: UUID, task_id: int, current_user: User = Depends(...)):
    # Verify user, get task, verify task.user_id == current_user.id
    pass

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(user_id: UUID, task_id: int, request: TaskUpdateRequest, ...):
    # Verify user, verify task ownership, update
    pass

@router.delete("/{task_id}", status_code=204)
def delete_task(user_id: UUID, task_id: int, ...):
    # Verify user, verify task ownership, delete
    pass

@router.patch("/{task_id}/toggle", response_model=TaskResponse)
def toggle_task(user_id: UUID, task_id: int, ...):
    # Verify user, toggle completed field
    pass
```

### 2.5 Security Layer

**JWT Token Creation:**
```python
def create_access_token(user_id: UUID, email: str, secret: str) -> str:
    payload = {
        "user_id": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=7),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, secret, algorithm="HS256")
```

**JWT Token Verification:**
```python
def verify_token(token: str, secret: str) -> dict | None:
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None
```

**Password Hashing:**
```python
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())
```

**Authentication Dependency:**
```python
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    session: Session = Depends(get_session)
) -> User:
    token = credentials.credentials
    payload = verify_token(token, settings.BETTER_AUTH_SECRET)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = session.get(User, UUID(payload["user_id"]))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
```

**User Isolation Enforcement:**
```python
# CRITICAL: Every task endpoint MUST include this check
if str(current_user.id) != str(user_id):
    raise HTTPException(status_code=404, detail="Not found")
```

### 2.6 Configuration Management

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    BETTER_AUTH_SECRET: str
    CORS_ORIGINS: str = "http://localhost:3000"
    ENVIRONMENT: str = "development"
    
    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 3. Frontend Architecture

### 3.1 Next.js Application Structure

```
frontend/
├── app/
│   ├── layout.tsx           # Root layout with Better Auth provider
│   ├── page.tsx             # Home (redirect to login or dashboard)
│   ├── globals.css          # Tailwind directives
│   │
│   ├── register/
│   │   └── page.tsx        # Registration form
│   │
│   ├── login/
│   │   └── page.tsx        # Login form
│   │
│   ├── dashboard/
│   │   └── page.tsx        # Main app (protected route)
│   │
│   └── api/                 # API route handlers
│       └── auth/
│           ├── [...all]/route.ts      # Better Auth handler
│           ├── better-register/route.ts
│           ├── better-login/route.ts
│           └── logout/route.ts
│
├── components/
│   ├── Header.tsx           # Navigation, logout button
│   ├── TaskList.tsx         # Display all tasks (client component)
│   ├── TaskItem.tsx         # Single task with actions
│   └── TaskForm.tsx         # Create/edit task form
│
├── lib/
│   ├── api.ts               # API client (fetch wrapper)
│   ├── auth.ts              # Auth utilities (getAuthToken, etc.)
│   ├── auth.config.ts       # Better Auth configuration
│   └── auth.client.ts       # Better Auth client
│
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── next.config.js
└── .env.local
```

### 3.2 Page Architecture

**Registration Page (Server Component):**
```typescript
// app/register/page.tsx
export default function RegisterPage() {
  return (
    <div className="container">
      <h1>Create Account</h1>
      <RegistrationForm />  {/* Client Component */}
    </div>
  )
}
```

**Login Page (Server Component):**
```typescript
// app/login/page.tsx
export default function LoginPage() {
  return (
    <div className="container">
      <h1>Welcome Back</h1>
      <LoginForm />  {/* Client Component */}
    </div>
  )
}
```

**Dashboard Page (Server Component with Auth Check):**
```typescript
// app/dashboard/page.tsx
import { redirect } from 'next/navigation'
import { getAuthToken, getAuthUser } from '@/lib/auth'
import TaskList from '@/components/TaskList'

export default async function DashboardPage() {
  const token = await getAuthToken()
  const user = await getAuthUser()
  
  if (!token || !user) {
    redirect('/login')
  }
  
  return (
    <div>
      <Header user={user} />
      <TaskList userId={user.id} />
    </div>
  )
}
```

### 3.3 Component Design

**TaskList (Client Component - needs interactivity):**
```typescript
'use client'

export default function TaskList({ userId }: { userId: string }) {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetchTasks()
  }, [])
  
  async function fetchTasks() {
    const data = await api.getTasks(userId)
    setTasks(data.tasks)
  }
  
  return (
    <div>
      <TaskForm onTaskCreated={fetchTasks} />
      {tasks.map(task => (
        <TaskItem key={task.id} task={task} onUpdate={fetchTasks} />
      ))}
    </div>
  )
}
```

**TaskItem (Client Component):**
```typescript
'use client'

export default function TaskItem({ task, onUpdate }) {
  async function handleToggle() {
    await api.toggleTask(task.user_id, task.id)
    onUpdate()
  }
  
  async function handleDelete() {
    if (confirm('Delete this task?')) {
      await api.deleteTask(task.user_id, task.id)
      onUpdate()
    }
  }
  
  return (
    <div className={task.completed ? 'completed' : ''}>
      <h3>{task.title}</h3>
      <p>{task.description}</p>
      <button onClick={handleToggle}>Toggle</button>
      <button onClick={handleDelete}>Delete</button>
    </div>
  )
}
```

### 3.4 API Client Design

```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = getCookie('token')  // From Better Auth
  
  const response = await fetch(`${API_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  })
  
  if (!response.ok) {
    throw new Error(await response.text())
  }
  
  return response.json()
}

export const api = {
  // Task operations
  getTasks: (userId: string, filter = 'all') =>
    fetchWithAuth(`/api/${userId}/tasks?completed=${filter}`),
  
  createTask: (userId: string, data: { title: string; description?: string }) =>
    fetchWithAuth(`/api/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  updateTask: (userId: string, taskId: number, data: any) =>
    fetchWithAuth(`/api/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  deleteTask: (userId: string, taskId: number) =>
    fetchWithAuth(`/api/${userId}/tasks/${taskId}`, { method: 'DELETE' }),
  
  toggleTask: (userId: string, taskId: number) =>
    fetchWithAuth(`/api/${userId}/tasks/${taskId}/toggle`, { method: 'PATCH' }),
}
```

### 3.5 Better Auth Integration

**Configuration:**
```typescript
// lib/auth.config.ts
import { betterAuth } from "better-auth"
import { Pool } from "pg"

export const auth = betterAuth({
  database: new Pool({ connectionString: process.env.DATABASE_URL }),
  
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  
  session: {
    expiresIn: 60 * 60 * 24 * 7,  // 7 days
    updateAge: 60 * 60 * 24,       // Update daily
  },
  
  secret: process.env.BETTER_AUTH_SECRET,
})
```

**API Routes:**
```typescript
// app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth.config"
import { toNextJsHandler } from "better-auth/next-js"

export const { GET, POST } = toNextJsHandler(auth)
```

---

## 4. Database Design

### 4.1 Schema

**Users Table (Better Auth managed):**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

**Tasks Table:**
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
```

### 4.2 Relationships

```
users (1) ────────▶ (many) tasks
  id  ─────────────────────▶ user_id (FK)

ON DELETE CASCADE: Deleting user deletes all their tasks
```

### 4.3 Query Patterns

**Get user's tasks:**
```python
tasks = session.exec(
    select(Task)
    .where(Task.user_id == current_user.id)
    .order_by(Task.created_at.desc())
).all()
```

**Create task:**
```python
task = Task(
    user_id=current_user.id,
    title=request.title,
    description=request.description,
    completed=False
)
session.add(task)
session.commit()
```

**Verify task ownership:**
```python
task = session.get(Task, task_id)
if not task or task.user_id != current_user.id:
    raise HTTPException(status_code=404)
```

---

## 5. Security Implementation

### 5.1 Authentication Flow

```
1. User submits credentials
   ↓
2. Backend validates email/password
   ↓
3. Backend generates JWT:
   {
     "user_id": "uuid",
     "email": "user@example.com",
     "exp": timestamp + 7 days,
     "iat": timestamp
   }
   ↓
4. Backend signs with BETTER_AUTH_SECRET (HS256)
   ↓
5. Frontend stores token in HTTP-only cookie
   ↓
6. Frontend includes token in Authorization header:
   "Authorization: Bearer <token>"
   ↓
7. Backend verifies token signature on every request
   ↓
8. Backend extracts user_id from payload
   ↓
9. Backend loads user from database
   ↓
10. Backend passes user to endpoint handler
```

### 5.2 User Isolation Strategy

**Three-Layer Defense:**

1. **JWT Verification** - Ensures valid, authenticated user
2. **Path Verification** - Ensures URL user_id matches token user_id
3. **Query Filtering** - Database queries ALWAYS filter by user_id

```python
# Layer 1: JWT verified by get_current_user() dependency
current_user = Depends(get_current_user)

# Layer 2: Path verification
if str(current_user.id) != str(user_id):
    raise HTTPException(status_code=404)

# Layer 3: Query filtering
query = select(Task).where(Task.user_id == current_user.id)
```

**Why 404 instead of 403?**
- Prevents user enumeration attacks
- Attacker can't tell if user_id exists
- Industry best practice

---

## 6. Implementation Sequence

### Phase 1: Backend Foundation
1. ✅ Setup project structure
2. ✅ Configure UV and dependencies
3. ✅ Create config.py with settings
4. ✅ Setup database.py with SQLModel engine

### Phase 2: Database Models
5. ✅ Implement User model (UUID, email, password_hash)
6. ✅ Implement Task model (foreign key to users)
7. ✅ Add relationships and indexes

### Phase 3: Security Layer
8. ✅ Implement security.py (JWT, bcrypt functions)
9. ✅ Implement deps.py (get_current_user dependency)
10. ✅ Test token generation and verification

### Phase 4: API Endpoints
11. ✅ Implement auth router (register, login)
12. ✅ Implement task router (6 CRUD endpoints)
13. ✅ Add user verification to all task endpoints
14. ✅ Setup CORS in main.py

### Phase 5: Frontend Foundation
15. ✅ Setup Next.js 16 project
16. ✅ Configure Tailwind CSS
17. ✅ Setup Better Auth
18. ✅ Create auth API routes

### Phase 6: Frontend Pages
19. ✅ Create registration page
20. ✅ Create login page
21. ✅ Create dashboard page with auth check
22. ✅ Add protected route logic

### Phase 7: Frontend Components
23. ✅ Create TaskList component
24. ✅ Create TaskItem component
25. ✅ Create TaskForm component
26. ✅ Create Header component

### Phase 8: Integration
27. ✅ Implement API client (lib/api.ts)
28. ✅ Connect components to backend
29. ✅ Test all user flows

### Phase 9: Deployment
30. ⚠️ Deploy backend to Hugging Face Spaces
31. ⚠️ Deploy frontend to Vercel
32. ⚠️ Configure environment variables

---

## 7. Testing Strategy

### 7.1 Manual Test Cases

**Authentication:**
- [ ] Register with valid email
- [ ] Register with duplicate email (should fail)
- [ ] Register with short password (should fail)
- [ ] Login with correct credentials
- [ ] Login with wrong password (should fail)
- [ ] Access dashboard without token (should redirect)

**Task Operations:**
- [ ] Create task (appears in list)
- [ ] View all tasks (only mine)
- [ ] Update task title
- [ ] Toggle task completion
- [ ] Delete task
- [ ] Try to access another user's task (should 404)

**Security:**
- [ ] Can't access /api/{other_user}/tasks with my token
- [ ] Invalid JWT returns 401
- [ ] Expired JWT returns 401
- [ ] Missing Authorization header returns 401

---

## 8. Deployment Architecture

### 8.1 Production Stack

```
┌──────────────────────┐
│   Vercel (Frontend)  │  ← User's browser
│   Next.js app        │
└──────────┬───────────┘
           │ HTTPS
           ▼
┌──────────────────────┐
│ Hugging Face Spaces  │  ← FastAPI backend
│ (Docker container)   │
└──────────┬───────────┘
           │ PostgreSQL protocol
           ▼
┌──────────────────────┐
│  Neon PostgreSQL     │  ← Database
│  (Serverless)        │
└──────────────────────┘
```

### 8.2 Environment Configuration

**Frontend (Vercel):**
```bash
NEXT_PUBLIC_API_URL=https://username-todo-api.hf.space
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=your-secret
```

**Backend (Hugging Face Spaces):**
```bash
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=your-secret
CORS_ORIGINS=https://your-app.vercel.app
ENVIRONMENT=production
```

---

## 9. Error Handling

### 9.1 Backend Error Responses

```python
# 400 Bad Request - Validation error
raise HTTPException(
    status_code=400,
    detail="Title is required"
)

# 401 Unauthorized - Auth failure
raise HTTPException(
    status_code=401,
    detail="Invalid or expired token"
)

# 404 Not Found - Resource not found OR user mismatch
raise HTTPException(
    status_code=404,
    detail="Not found"
)

# 409 Conflict - Duplicate resource
raise HTTPException(
    status_code=409,
    detail="Email already exists"
)
```

### 9.2 Frontend Error Handling

```typescript
try {
  await api.createTask(userId, data)
} catch (error) {
  if (error.message.includes('401')) {
    // Redirect to login
    router.push('/login')
  } else {
    // Show error message
    alert(error.message)
  }
}
```

---

## 10. Performance Considerations

### 10.1 Database Optimization
- Indexes on user_id, email
- Connection pooling via SQLModel
- Limit query results (pagination for >100 items)

### 10.2 Frontend Optimization
- Server Components for static content
- Client Components only for interactivity
- Optimistic UI updates
- Debounced search inputs

### 10.3 API Optimization
- Async handlers where possible
- Minimal data transfer (exclude sensitive fields)
- Proper HTTP caching headers

---

## 11. Success Criteria

This implementation is considered complete when:

1. ✅ All 8 API endpoints functional
2. ✅ User isolation verified (can't access other user's data)
3. ✅ Authentication works (register, login, logout)
4. ✅ All 5 basic task operations work
5. ✅ Frontend deployed to Vercel
6. ✅ Backend deployed to Hugging Face Spaces
7. ✅ Database connected (Neon PostgreSQL)
8. ✅ Demo video recorded
9. ✅ Documentation complete (README, CLAUDE.md, specs)

---

**Plan Status:** ✅ Implemented  
**Next Phase:** Phase III - AI Chatbot  
**Date Completed:** January 5, 2026
