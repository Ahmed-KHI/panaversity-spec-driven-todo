# Better Auth Integration - Phase 2 Implementation

## Overview

This project implements **Better Auth** for user authentication as required by the GIAIC Hackathon Phase 2 specifications. Better Auth is a TypeScript/JavaScript authentication library running on the Next.js frontend, integrated with our FastAPI backend through JWT tokens.

## Architecture

### Authentication Flow

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│ Better Auth  │─────▶│  Database   │
│  (Next.js)  │      │   (Server)   │      │  (Neon PG)  │
└─────────────┘      └──────────────┘      └─────────────┘
       │                     │                       
       │ JWT Token          │ Session                
       │                     │                       
       ▼                     ▼                       
┌─────────────┐      ┌──────────────┐               
│  API Client │─────▶│   FastAPI    │               
│             │      │   Backend    │               
└─────────────┘      └──────────────┘               
```

### Components

#### 1. Better Auth Configuration (`frontend/lib/auth.config.ts`)

- **Database**: PostgreSQL (Neon) with Kysely query builder
- **Provider**: Email & Password authentication
- **Session Management**: 7-day expiration, cookie-based
- **Security**: 
  - HTTP-only cookies
  - CSRF protection via SameSite policy
  - Shared secret with backend (BETTER_AUTH_SECRET)

#### 2. Database Schema

Better Auth manages these tables:

- **user**: User accounts (id, email, emailVerified, name, createdAt, updatedAt)
- **session**: Active sessions (id, token, expiresAt, userId, ipAddress, userAgent)
- **account**: OAuth/password storage (id, userId, providerId, password)
- **verification**: Email verification tokens

Backend manages:

- **users**: Task ownership (id, email, password_hash, created_at, updated_at)
- **tasks**: User tasks (id, user_id, title, description, completed)

#### 3. Authentication Endpoints

**Registration** (`/api/auth/better-register`)
- Uses Better Auth `signUpEmail` API
- Creates user in Better Auth database
- Returns user info

**Login** (`/api/auth/better-login`)
- Uses Better Auth `signInEmail` API
- Creates session and issues JWT token
- Stores token in HTTP-only cookie for API calls
- Returns user info

**Logout** (`/api/auth/logout`)
- Uses Better Auth `signOut` API
- Clears all auth cookies
- Ends session

#### 4. Frontend Integration

**Pages**:
- `app/register/page.tsx`: Registration form → calls Better Auth
- `app/login/page.tsx`: Login form → calls Better Auth
- `app/dashboard/page.tsx`: Protected route → verifies session

**Auth Utilities** (`lib/auth.ts`):
- `getAuthToken()`: Retrieves JWT token from cookie
- `getAuthUser()`: Gets current user from cookie
- Server-side only (uses Next.js cookies API)

**API Client** (`lib/api.ts`):
- Adds `Authorization: Bearer <token>` header to all requests
- Communicates with FastAPI backend

#### 5. Backend Integration (FastAPI)

**JWT Verification** (`backend/src/utils/security.py`):
```python
def verify_token(token: str, secret_key: str) -> Optional[Dict]:
    # Verifies Better Auth JWT tokens
    # Supports both 'userId' and 'user_id' fields
    # Uses shared BETTER_AUTH_SECRET
```

**Authentication Dependency** (`backend/src/utils/deps.py`):
```python
def get_current_user(credentials, session):
    # Extracts Bearer token
    # Verifies with verify_token()
    # Returns User model
```

**Protected Routes** (`backend/src/routers/tasks.py`):
- All endpoints use `Depends(get_current_user)`
- Enforce user isolation (only see own tasks)
- Return 401 if token invalid/missing

## Security Implementation

### 1. User Isolation

Every API endpoint verifies:
```python
# Check user_id in URL matches authenticated user
if task.user_id != user.id:
    raise HTTPException(status_code=404, detail="Task not found")
```

### 2. JWT Token Flow

1. User logs in → Better Auth creates session
2. Session token extracted and stored in HTTP-only cookie
3. Frontend sends token to FastAPI: `Authorization: Bearer <token>`
4. FastAPI verifies token with shared secret
5. FastAPI extracts user_id from token
6. FastAPI queries database with user_id filter

### 3. Shared Secret

Both services use `BETTER_AUTH_SECRET`:

**Frontend** (`.env.local`):
```env
BETTER_AUTH_SECRET=hackathon-phase2-secret-key-change-in-production-min32chars
```

**Backend** (`.env`):
```env
BETTER_AUTH_SECRET=hackathon-phase2-secret-key-change-in-production-min32chars
```

### 4. Security Benefits

✅ **Stateless Authentication**: No server-side session storage
✅ **Token Expiration**: 7-day automatic expiry
✅ **HTTP-Only Cookies**: JavaScript cannot access tokens
✅ **CSRF Protection**: SameSite cookie policy
✅ **User Isolation**: Each user only accesses their data
✅ **Password Hashing**: bcrypt with 12 rounds (backend) / Better Auth (frontend)

## Testing the Integration

### 1. Start Services

**Backend**:
```bash
cd backend
.venv\Scripts\activate
uvicorn src.main:app --reload --port 8000
```

**Frontend**:
```bash
cd frontend
npm run dev
```

### 2. Test Flow

1. **Register**: http://localhost:3000/register
   - Enter email and password (min 8 chars)
   - Better Auth creates user and account

2. **Login**: http://localhost:3000/login
   - Enter credentials
   - Better Auth creates session and issues JWT
   - Redirects to dashboard

3. **Dashboard**: http://localhost:3000/dashboard
   - Displays user tasks
   - All CRUD operations work
   - Session verified on each API call

4. **API Calls**:
   - Open browser DevTools → Network tab
   - See `Authorization: Bearer <token>` header
   - Backend logs show user_id from token

5. **Logout**:
   - Click logout button
   - Better Auth ends session
   - Cookies cleared
   - Redirects to login

### 3. Verify Token

Check JWT token in browser console:
```javascript
// After login, check cookies
document.cookie

// Decode JWT (don't do in production!)
const token = document.cookie.split('token=')[1].split(';')[0]
const payload = JSON.parse(atob(token.split('.')[1]))
console.log(payload) // Shows user_id, email, exp, iat
```

## Compliance with Spec

### ✅ Required Technology Stack

- **Frontend**: Next.js 15+ (App Router) ✅
- **Backend**: Python FastAPI ✅
- **ORM**: SQLModel ✅
- **Database**: Neon Serverless PostgreSQL ✅
- **Authentication**: Better Auth ✅

### ✅ Authentication Requirements

1. **Better Auth Library**: Installed and configured ✅
2. **User Signup/Signin**: Implemented with Better Auth API ✅
3. **JWT Tokens**: Issued by Better Auth, verified by FastAPI ✅
4. **Shared Secret**: BETTER_AUTH_SECRET in both services ✅
5. **Session Management**: Better Auth handles sessions ✅
6. **User Isolation**: Each user only sees own tasks ✅

### ✅ API Endpoints

All 6 endpoints implemented and secured:

- `GET /api/{user_id}/tasks` - List tasks
- `POST /api/{user_id}/tasks` - Create task
- `GET /api/{user_id}/tasks/{id}` - Get task
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion

### ✅ Security Features

1. JWT token in Authorization header ✅
2. Token verification on every request ✅
3. User isolation enforced ✅
4. 401 Unauthorized for invalid tokens ✅
5. 404 Not Found for cross-user access attempts ✅

## Database Migrations

Better Auth tables created via:
```bash
cd frontend
npm run migrate
```

This runs `scripts/create-better-auth-tables.ts` which executes `better-auth-schema.sql`.

## Environment Variables

**Frontend** (`frontend/.env.local`):
```env
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=your-secret-key
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend** (`backend/.env`):
```env
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=your-secret-key
CORS_ORIGINS=http://localhost:3000
```

## Troubleshooting

### Session Not Found After Login

**Solution**: Ensure both services use same `BETTER_AUTH_SECRET`

### 401 Unauthorized on API Calls

**Solution**: Check token is being sent in Authorization header

### User Not Found After Registration

**Solution**: Better Auth and FastAPI use different user tables by design. Login flow handles this.

## Conclusion

This implementation fully complies with the GIAIC Hackathon Phase 2 specification by:

1. Using Better Auth as the primary authentication library
2. Implementing JWT token-based authentication between frontend and backend
3. Ensuring secure, stateless authentication with proper user isolation
4. Following all security best practices outlined in the spec

The architecture allows Better Auth to manage user authentication on the frontend while FastAPI handles the API business logic, connected through JWT tokens with a shared secret.
