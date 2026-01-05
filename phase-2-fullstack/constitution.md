# Project Constitution - Phase II Todo Application

**Project:** Hackathon II - Full-Stack Web Application  
**Phase:** Phase II - Multi-User Web Application  
**Date Created:** January 5, 2026  
**Status:** Active  

---

## Purpose

This constitution defines the immutable principles, constraints, and architectural decisions that govern the development of the Phase II Todo Application. All code, features, and architectural decisions must align with these foundational rules.

---

## 1. Core Principles

### 1.1 Security First

**Principle:** Security is non-negotiable. User data protection takes precedence over convenience or speed.

**Mandates:**
- All user data MUST be isolated by `user_id`
- Passwords MUST NEVER be stored in plain text
- All passwords MUST be hashed using bcrypt with minimum 12 salt rounds
- JWT tokens MUST expire after maximum 7 days
- All API endpoints (except auth) MUST require valid authentication
- HTTPS MUST be enforced in production

**Forbidden:**
- Storing passwords in plain text
- Logging sensitive data (passwords, tokens)
- Cross-user data access
- Unauthenticated access to protected resources

---

### 1.2 User Privacy & Data Isolation

**Principle:** Each user's data is sacred and completely isolated from other users.

**Mandates:**
- Every task MUST have a `user_id` foreign key
- All database queries MUST filter by authenticated user's ID
- API path `user_id` MUST match JWT token `user_id`
- No endpoint may return another user's data
- Failed user verification MUST return 404 (not 403) to prevent user enumeration

**Critical Rule:**
```python
# MANDATORY pattern for all task endpoints
if str(current_user.id) != str(user_id):
    raise HTTPException(status_code=404, detail="Not found")
```

---

### 1.3 Spec-Driven Development

**Principle:** No code shall be written without a specification that defines WHAT to build.

**Mandates:**
- All features MUST be specified in `/specs` before implementation
- All code files MUST include task references: `[Task]: T-XXX`
- All architectural decisions MUST be documented in `plan.md`
- Claude Code is the PRIMARY implementation tool
- Manual coding is ONLY permitted for specifications themselves

**Workflow:**
1. Write `spec.md` (WHAT to build)
2. Generate `plan.md` (HOW to build)
3. Break down `tasks.md` (step-by-step)
4. Implement via Claude Code

---

### 1.4 Type Safety

**Principle:** Type errors should be caught at compile time, not runtime.

**Mandates:**
- Frontend MUST use TypeScript with strict mode enabled
- Backend MUST use Python type hints (PEP 484)
- Pydantic models MUST validate all API request/response data
- SQLModel MUST define all database schema types
- No `any` type in TypeScript (use `unknown` if necessary)

---

## 2. Technology Constraints

### 2.1 Approved Technology Stack

**These technologies are IMMUTABLE for Phase II:**

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| **Frontend** |
| Framework | Next.js (App Router) | 16+ | React 19 support, server components |
| UI Library | React | 19+ | Latest stable with concurrent rendering |
| Language | TypeScript | 5+ | Type safety, IntelliSense |
| Styling | Tailwind CSS | 3.4+ | Utility-first, rapid development |
| **Backend** |
| Framework | FastAPI | Latest | Async support, auto-docs, performance |
| ORM | SQLModel | Latest | Type-safe, Pydantic integration |
| Language | Python | 3.13+ | Latest stable, performance improvements |
| Package Manager | UV | Latest | Fast, deterministic dependency resolution |
| **Database** |
| DBMS | PostgreSQL | 16 | ACID compliance, reliability |
| Provider | Neon Serverless | Latest | Free tier, auto-scaling, branching |
| **Authentication** |
| Library | Better Auth | 1.4+ | TypeScript-native, JWT support |
| Token Type | JWT | - | Stateless, scalable |
| Token Algorithm | HS256 | - | Symmetric key signing |
| **DevOps** |
| Containerization | Docker Compose | 3.8+ | Local development parity |
| Frontend Hosting | Vercel | - | Free tier, instant deployments |
| Backend Hosting | Hugging Face Spaces | - | Free tier, Docker support |

### 2.2 Forbidden Technologies

**NOT PERMITTED in Phase II:**
- ❌ MongoDB or NoSQL databases (PostgreSQL only)
- ❌ Firebase/Supabase (Neon only for Phase II)
- ❌ Express.js or Node.js backend (FastAPI only)
- ❌ JavaScript for backend (Python only)
- ❌ Class-based React components (function components only)
- ❌ Pages Router (App Router only)
- ❌ CSS/SCSS (Tailwind CSS only)

---

## 3. Security Requirements

### 3.1 Authentication

**JWT Token Specification:**
- **Algorithm:** HS256 (symmetric)
- **Expiration:** 7 days maximum (604800 seconds)
- **Shared Secret:** `BETTER_AUTH_SECRET` environment variable
- **Storage:** HTTP-only cookies (frontend)
- **Transmission:** `Authorization: Bearer <token>` header to backend

**Password Requirements:**
- Minimum length: 8 characters
- Hashing: bcrypt with 12 salt rounds
- Never transmitted in GET requests
- Never logged or displayed

**Better Auth Configuration:**
```typescript
{
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24      // Update daily
  }
}
```

---

### 3.2 Authorization

**User Verification Pattern:**
```python
# MANDATORY for all protected endpoints
def verify_user_access(path_user_id: UUID, current_user: User):
    if str(current_user.id) != str(path_user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"  # Don't reveal "unauthorized"
        )
```

**Why 404 instead of 403?**
- Prevents user enumeration attacks
- Doesn't reveal whether user exists
- Industry best practice for resource access

---

### 3.3 CORS Configuration

**Backend CORS Policy:**
```python
allow_origins=[
    "http://localhost:3000",          # Local development
    "https://your-app.vercel.app"     # Production
]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

**Frontend API Requests:**
- MUST include credentials: `credentials: 'include'`
- MUST use HTTPS in production
- MUST validate SSL certificates

---

## 4. Database Design Principles

### 4.1 Schema Rules

**User Table (managed by Better Auth):**
- Primary key: UUID (not auto-increment integer)
- Email must have unique constraint
- Password stored as bcrypt hash
- Timestamps: `created_at`, `updated_at`

**Task Table:**
- Primary key: Serial integer (auto-increment)
- Foreign key: `user_id` references `users.id`
- ON DELETE: CASCADE (delete user's tasks when user deleted)
- Required fields: `title`, `user_id`, `completed`
- Optional fields: `description`

**Indexes:**
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
```

---

### 4.2 Query Principles

**MANDATORY:**
- All queries MUST filter by `user_id`
- Use SQLModel for all database operations (no raw SQL)
- Use async operations where possible
- Always use parameterized queries (SQLModel does this automatically)

**FORBIDDEN:**
- Raw SQL strings (except migrations)
- Queries without user_id filter
- `SELECT *` on tables with sensitive data

---

## 5. API Design Standards

### 5.1 RESTful Conventions

**Endpoint Structure:**
```
/api/auth/register           POST    Register new user
/api/auth/login              POST    Login user
/api/{user_id}/tasks         GET     List tasks (filtered by user)
/api/{user_id}/tasks         POST    Create task
/api/{user_id}/tasks/{id}    GET     Get single task
/api/{user_id}/tasks/{id}    PUT     Update task
/api/{user_id}/tasks/{id}    DELETE  Delete task
/api/{user_id}/tasks/{id}/toggle PATCH Toggle completion
```

**HTTP Status Codes:**
- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Invalid/missing token
- `404 Not Found` - Resource not found / user mismatch
- `409 Conflict` - Duplicate resource (e.g., email)
- `500 Internal Server Error` - Server error

---

### 5.2 Request/Response Format

**All responses MUST be JSON:**
```json
{
  "field": "value",
  "camelCase": "for consistency"
}
```

**Error responses:**
```json
{
  "detail": "Clear error message for debugging"
}
```

**List responses:**
```json
{
  "tasks": [...],
  "count": 5
}
```

---

## 6. Code Quality Standards

### 6.1 File Organization

**Backend Structure (IMMUTABLE):**
```
backend/src/
├── main.py           # FastAPI app, CORS, startup
├── config.py         # Settings (Pydantic BaseSettings)
├── database.py       # SQLModel engine, session
├── models/           # SQLModel database models
├── schemas/          # Pydantic request/response schemas
├── routers/          # API endpoint handlers
└── utils/            # Security, dependencies, helpers
```

**Frontend Structure (IMMUTABLE):**
```
frontend/
├── app/              # Next.js App Router pages
├── components/       # React components (client/server)
├── lib/              # Utilities (api, auth, types)
└── public/           # Static assets
```

---

### 6.2 Naming Conventions

**Backend (Python):**
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case()`
- Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

**Frontend (TypeScript):**
- Files: `PascalCase.tsx` (components), `camelCase.ts` (utilities)
- Components: `PascalCase`
- Functions: `camelCase()`
- Variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Types/Interfaces: `PascalCase`

---

### 6.3 Code Documentation

**Required Comments:**
```python
# [Task]: T-XXX
# [From]: spec.md §X.X, plan.md §Y.Y
# [Purpose]: Brief description
```

**Function Documentation:**
- Python: Docstrings for all public functions
- TypeScript: JSDoc comments for exported functions
- Include: Purpose, parameters, return value, exceptions

---

## 7. Environment Management

### 7.1 Environment Variables

**Backend (.env):**
```bash
DATABASE_URL=postgresql://...          # Neon connection string
BETTER_AUTH_SECRET=your-secret-here    # Shared with frontend
CORS_ORIGINS=http://localhost:3000,https://app.vercel.app
ENVIRONMENT=development                 # development | production
```

**Frontend (.env.local):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000  # Backend URL
DATABASE_URL=postgresql://...               # For Better Auth
BETTER_AUTH_SECRET=your-secret-here         # Same as backend
```

---

### 7.2 Secret Management

**MANDATORY:**
- All secrets in `.env` files (NEVER in code)
- `.env` files MUST be in `.gitignore`
- `.env.example` files with placeholder values
- Production secrets in hosting platform (Vercel secrets, HF Spaces)

**FORBIDDEN:**
- Hardcoded secrets in source code
- Committing `.env` to Git
- Sharing secrets in public channels

---

## 8. Testing & Validation

### 8.1 Manual Testing Requirements

**Before submission, MUST verify:**
- [ ] User registration with valid email
- [ ] User registration with duplicate email (should fail)
- [ ] User login with correct credentials
- [ ] User login with wrong password (should fail)
- [ ] Create task (shows in list)
- [ ] Update task title/description
- [ ] Toggle task completion
- [ ] Delete task
- [ ] User A cannot see User B's tasks
- [ ] Logout (clears session)

---

### 8.2 Security Testing

**MUST verify:**
- [ ] Cannot access `/api/{other_user_id}/tasks` with your token
- [ ] Cannot create task for another user
- [ ] Invalid JWT returns 401
- [ ] Expired JWT returns 401
- [ ] Missing JWT returns 401

---

## 9. Performance Standards

### 9.1 Response Time Targets

- API CRUD operations: < 200ms (P95)
- User authentication: < 300ms (P95)
- Page load (frontend): < 2s (P95)
- Database queries: < 50ms (P95)

---

### 9.2 Optimization Rules

**Backend:**
- Use database indexes on foreign keys
- Limit query results (pagination if > 100 items)
- Use async operations for I/O
- Cache user verification (within request)

**Frontend:**
- Use Server Components where possible
- Client Components only for interactivity
- Optimize images (next/image)
- Minimize client bundle size

---

## 10. Deployment Requirements

### 10.1 Production Readiness

**MUST HAVE:**
- [ ] HTTPS enforced
- [ ] Environment variables via hosting platform
- [ ] Database connection pooling
- [ ] Error logging (not console.log)
- [ ] Health check endpoint (`/health`)
- [ ] API documentation (`/docs`)

---

### 10.2 Hosting Configuration

**Frontend (Vercel):**
- Auto-deploy from `main` branch
- Environment variables in Vercel dashboard
- Build command: `npm run build`
- Output directory: `.next`

**Backend (Hugging Face Spaces):**
- Docker SDK space
- `Dockerfile` at backend root
- Environment secrets in HF Space settings
- Port: 7860 (HF Spaces requirement)

---

## 11. Git Workflow

### 11.1 Commit Standards

**Message Format:**
```
[Task]: T-XXX - Brief description

- Detailed change 1
- Detailed change 2

[From]: spec.md §X.X
```

**Forbidden:**
- Generic messages ("fix", "update", "wip")
- Commits with secrets/credentials
- Large binary files

---

### 11.2 Branch Strategy

**Phase II (Simple):**
- `main` branch for all work
- Direct commits permitted (solo project)
- Tags for submission versions: `phase-ii-v1.0`

---

## 12. Submission Requirements

**MANDATORY for acceptance:**
- [ ] constitution.md (this file)
- [ ] specs/002-phase-ii-full-stack/spec.md
- [ ] specs/002-phase-ii-full-stack/plan.md
- [ ] specs/002-phase-ii-full-stack/tasks.md
- [ ] README.md with setup instructions
- [ ] CLAUDE.md with Claude Code instructions
- [ ] Demo video (90 seconds, unlisted YouTube)
- [ ] Deployed frontend (Vercel)
- [ ] Deployed backend (Hugging Face Spaces)
- [ ] Public GitHub repository

---

## 13. Phase Boundaries

**Phase II Scope (LOCKED):**
- ✅ Multi-user web application
- ✅ Basic CRUD operations
- ✅ User authentication (Better Auth + JWT)
- ✅ User data isolation
- ✅ PostgreSQL database (Neon)

**Out of Scope (Future Phases):**
- ❌ AI chatbot (Phase III)
- ❌ Advanced features (priorities, tags, search) (Phase V)
- ❌ Kubernetes deployment (Phase IV)
- ❌ Event-driven architecture (Kafka, Dapr) (Phase V)

---

## 14. Exceptions & Overrides

This constitution may ONLY be modified under these conditions:
1. Teacher explicitly approves deviation
2. Phase requirements change officially
3. Critical security vulnerability requires immediate action

**Change Process:**
1. Document proposed change
2. Get teacher approval
3. Update constitution
4. Update all affected specs and code

---

## 15. Enforcement

**Violations:**
- Code that violates security principles MUST be rejected
- Missing task references SHOULD be added
- Unapproved technology MUST be replaced
- Spec-less code SHOULD be retroactively specified

**Authority:**
This constitution is subordinate to:
1. GIAIC Hackathon II official requirements
2. Teacher's instructions
3. Phase II specification document

---

**Constitution Adopted:** January 5, 2026  
**Status:** Active  
**Next Review:** Phase III kickoff  
**Authority:** Student (aligned with teacher requirements)  

---

## Appendix: Quick Reference

**User Isolation Check:**
```python
if str(current_user.id) != str(user_id):
    raise HTTPException(status_code=404, detail="Not found")
```

**JWT Verification:**
```python
payload = verify_token(token, settings.BETTER_AUTH_SECRET)
user = session.get(User, UUID(payload["user_id"]))
```

**Task Reference Format:**
```python
# [Task]: T-XXX
# [From]: spec.md §X.X, plan.md §Y.Y
```

**Environment Variable Access:**
```python
# Backend
from src.config import settings
db_url = settings.DATABASE_URL

# Frontend
const apiUrl = process.env.NEXT_PUBLIC_API_URL
```
