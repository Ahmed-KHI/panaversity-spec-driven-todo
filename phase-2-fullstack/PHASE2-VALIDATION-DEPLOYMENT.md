# PHASE 2: VALIDATION CHECKLIST & DEPLOYMENT GUIDE

## 📋 VALIDATION CHECKLIST (Map to Marking Rubric)

### 1. Backend API Validation (30 points)

#### Authentication Endpoints (10 points)
- [ ] **POST /api/auth/register** working
  - [ ] Valid email + password creates account
  - [ ] Duplicate email returns 409 Conflict
  - [ ] Invalid email returns 400 Bad Request
  - [ ] Password minimum 8 characters enforced
  - [ ] Password hashed with bcrypt (never plaintext)
  - [ ] Returns JWT token immediately

- [ ] **POST /api/auth/login** working
  - [ ] Valid credentials return JWT token
  - [ ] Invalid credentials return 401 Unauthorized
  - [ ] Token contains user_id and expiration
  - [ ] Token works for subsequent requests

#### Task CRUD Endpoints (20 points)
- [ ] **GET /api/{user_id}/tasks** working
  - [ ] Returns only authenticated user's tasks
  - [ ] Filter by completed status works
  - [ ] Returns empty array when no tasks
  - [ ] Sorted by created_at descending
  - [ ] 401 without JWT token
  - [ ] 404 if path user_id doesn't match token user_id

- [ ] **POST /api/{user_id}/tasks** working
  - [ ] Creates task with title and description
  - [ ] Title validation (1-200 chars) enforced
  - [ ] Description validation (max 1000 chars) enforced
  - [ ] Auto-generates id, timestamps, completed=false
  - [ ] Associates with correct user
  - [ ] Returns 201 Created

- [ ] **GET /api/{user_id}/tasks/{task_id}** working
  - [ ] Returns task if owned by user
  - [ ] Returns 404 if not owned by user
  - [ ] Returns 404 if task doesn't exist

- [ ] **PUT /api/{user_id}/tasks/{task_id}** working
  - [ ] Updates title and/or description
  - [ ] Updates updated_at timestamp
  - [ ] Returns 404 if not owned by user
  - [ ] Validation rules enforced

- [ ] **PATCH /api/{user_id}/tasks/{task_id}** working
  - [ ] Toggles completed status
  - [ ] Updates updated_at timestamp
  - [ ] Returns updated task

- [ ] **DELETE /api/{user_id}/tasks/{task_id}** working
  - [ ] Deletes task if owned by user
  - [ ] Returns 204 No Content
  - [ ] Returns 404 if not owned by user

### 2. User Isolation Security (20 points - CRITICAL)

- [ ] **Database Queries** ALL filter by user_id
  ```python
  # Every query must look like this:
  tasks = session.exec(
      select(Task).where(Task.user_id == current_user.id)
  ).all()
  ```

- [ ] **Authorization Checks** on ALL endpoints
  ```python
  # Every endpoint must verify:
  if str(current_user.id) != str(user_id):
      raise HTTPException(status_code=404, detail="Not found")
  ```

- [ ] **404 (not 403)** for unauthorized access
  - Never return 403 Forbidden (leaks information)
  - Always return 404 Not Found

- [ ] **Cross-User Access Tests**:
  - [ ] Create User A with tasks
  - [ ] Login as User B
  - [ ] Attempt to view User A's tasks via URL manipulation
  - [ ] Verify 404 response (no data leaked)

### 3. Frontend Implementation (20 points)

#### Authentication Pages (5 points)
- [ ] **Registration Page** (/register)
  - [ ] Form with email, password, confirm password
  - [ ] Client-side validation before submission
  - [ ] Displays errors (duplicate email, weak password)
  - [ ] Redirects to dashboard after success
  - [ ] Link to login page

- [ ] **Login Page** (/login)
  - [ ] Form with email, password
  - [ ] Displays authentication errors
  - [ ] Redirects to dashboard after success
  - [ ] Link to registration page

#### Task Management UI (15 points)
- [ ] **Dashboard Page** (/)
  - [ ] Protected route (requires authentication)
  - [ ] Displays all user's tasks
  - [ ] Visual status indicators (checkboxes)
  - [ ] Completed tasks styled differently
  - [ ] Empty state message when no tasks
  - [ ] Button to create new task
  - [ ] Logout button

- [ ] **TaskList Component**
  - [ ] Fetches tasks on mount
  - [ ] Displays loading state
  - [ ] Displays error state
  - [ ] Maps tasks to TaskItem components

- [ ] **TaskItem Component**
  - [ ] Displays title, description, status
  - [ ] Checkbox to toggle completion
  - [ ] Edit button (navigates to edit page)
  - [ ] Delete button (shows confirmation)

- [ ] **Create Task Page** (/tasks/new)
  - [ ] Form with title, description
  - [ ] Inline validation
  - [ ] Redirects to dashboard after creation

- [ ] **Edit Task Page** (/tasks/[id])
  - [ ] Pre-fills form with existing data
  - [ ] Updates task on submission
  - [ ] Redirects to dashboard after update

### 4. Responsive Design (5 points)

- [ ] **Mobile** (< 768px)
  - [ ] Forms stack vertically
  - [ ] Buttons full width
  - [ ] Text readable
  - [ ] No horizontal scroll

- [ ] **Tablet** (768px - 1024px)
  - [ ] Optimal layout
  - [ ] Touch-friendly targets

- [ ] **Desktop** (> 1024px)
  - [ ] Max width container
  - [ ] Comfortable spacing

### 5. Spec-Driven Development (15 points)

- [ ] **/specs folder exists** with:
  - [ ] spec.md (requirements, user stories)
  - [ ] plan.md (architecture, API contracts)
  - [ ] tasks.md (task breakdown)
  - [ ] contracts/ (OpenAPI specs - optional)

- [ ] **Code comments** reference specs:
  ```python
  # [Task]: T-007
  # [From]: spec.md §3.2, plan.md §5.3
  ```

- [ ] **CLAUDE.md** with:
  - [ ] Project context
  - [ ] Architecture patterns
  - [ ] Security requirements
  - [ ] Development workflow

### 6. Code Quality (5 points)

- [ ] **Backend**:
  - [ ] Type hints on all functions
  - [ ] Docstrings on public functions
  - [ ] Modular structure (models, schemas, routers)
  - [ ] Error handling (try/except where appropriate)

- [ ] **Frontend**:
  - [ ] TypeScript (no `any` types)
  - [ ] Proper component separation (Server vs Client)
  - [ ] Consistent styling (Tailwind classes)
  - [ ] Error boundaries

### 7. Documentation (5 points)

- [ ] **README.md** includes:
  - [ ] Project overview
  - [ ] Technology stack
  - [ ] Setup instructions (step-by-step)
  - [ ] Environment variables
  - [ ] Running locally
  - [ ] Deployment instructions
  - [ ] API documentation link

- [ ] **API Documentation**:
  - [ ] Swagger UI accessible at /docs
  - [ ] All endpoints documented
  - [ ] Request/response examples

---

## 🚢 DEPLOYMENT GUIDE

### Step 1: Prepare for Deployment

#### 1.1 Verify Local Works
```bash
# Start services
docker-compose up

# Test all features:
# 1. Register new user
# 2. Login
# 3. Create 3 tasks
# 4. Toggle completion
# 5. Edit task
# 6. Delete task
# 7. Logout
```

#### 1.2 Create Production Branches
```bash
git checkout -b production
git add .
git commit -m "Phase 2: Full-stack application ready for deployment"
git push origin production
```

### Step 2: Deploy Database (Neon)

1. **Login**: https://neon.tech
2. **Create Project**: "hackathon-todo-phase2"
3. **Copy Connection String**:
   ```
   postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```
4. **Test Connection**:
   ```bash
   psql "postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require"
   ```

### Step 3: Deploy Backend (Vercel)

#### 3.1 Install Vercel CLI
```bash
npm install -g vercel
```

#### 3.2 Configure Backend for Vercel

**Create**: `backend/vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "src/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "src/main.py"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.13"
  }
}
```

**Create**: `backend/requirements.txt`
```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
sqlmodel>=0.0.22
psycopg2-binary>=2.9.10
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.12
pydantic[email]>=2.10.0
python-dotenv>=1.0.1
```

#### 3.3 Deploy Backend
```bash
cd backend
vercel --prod

# Set environment variables in Vercel dashboard:
# DATABASE_URL=<neon-connection-string>
# SECRET_KEY=<generate-32-char-secret>
# BETTER_AUTH_SECRET=<generate-32-char-secret>
# ENVIRONMENT=production
# CORS_ORIGINS=<frontend-url>
```

**Backend URL**: https://your-backend.vercel.app

#### 3.4 Verify Backend
```bash
curl https://your-backend.vercel.app/health
# Should return: {"status": "healthy", "environment": "production"}
```

### Step 4: Deploy Frontend (Vercel)

#### 4.1 Update API URL

**Edit**: `frontend/.env.production`
```env
NEXT_PUBLIC_API_URL=https://your-backend.vercel.app
NEXT_PUBLIC_BETTER_AUTH_SECRET=<same-as-backend>
```

#### 4.2 Build and Test
```bash
cd frontend
npm run build
npm run start  # Test production build locally
```

#### 4.3 Deploy Frontend
```bash
vercel --prod

# Set environment variables in Vercel dashboard:
# NEXT_PUBLIC_API_URL=https://your-backend.vercel.app
# NEXT_PUBLIC_BETTER_AUTH_SECRET=<same-as-backend>
```

**Frontend URL**: https://your-frontend.vercel.app

### Step 5: Configure CORS

Update backend CORS to allow production frontend:

**Vercel Dashboard** → Backend Project → Settings → Environment Variables:
```
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

**Redeploy backend** for changes to take effect.

### Step 6: Final Validation

#### 6.1 Test Production Application
1. Open: https://your-frontend.vercel.app
2. Register new account
3. Create tasks
4. Toggle completion
5. Edit task
6. Delete task
7. Logout and login again

#### 6.2 Test API Directly
```bash
# Register
curl -X POST https://your-backend.vercel.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Login
curl -X POST https://your-backend.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# List tasks (replace TOKEN and USER_ID)
curl https://your-backend.vercel.app/api/{user_id}/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🎥 DEMO VIDEO SCRIPT (90 seconds)

### Script Outline:

**0:00-0:10** (10s) - Introduction
- "Hi, I'm [Name]. This is my Phase 2 submission for the GIAIC Hackathon."
- "A full-stack todo application with Next.js, FastAPI, and PostgreSQL."

**0:10-0:25** (15s) - Registration
- Navigate to registration page
- Fill form: email, password
- Submit
- "User registration with password hashing and immediate JWT token issuance."

**0:25-0:35** (10s) - Login
- Logout
- Login again with same credentials
- "Secure JWT-based authentication."

**0:35-0:50** (15s) - Create Tasks
- Click "New Task"
- Create 3 tasks quickly:
  - "Buy groceries"
  - "Call dentist"
  - "Finish project"
- "All tasks persisted in Neon PostgreSQL."

**0:50-0:60** (10s) - CRUD Operations
- Toggle one task complete
- Edit another task
- Delete a task
- "Complete CRUD operations with real-time UI updates."

**0:60-0:75** (15s) - User Isolation Demo
- Logout
- Register second user
- Show empty task list
- "Each user has isolated data - cannot see other users' tasks."

**0:75-0:85** (10s) - Architecture
- Show quick view of:
  - /specs folder (spec-driven development)
  - Backend code (FastAPI + SQLModel)
  - Frontend code (Next.js + TypeScript)
- "Built using spec-driven development with Claude Code."

**0:85-0:90** (5s) - Closing
- "Thank you! Links in description."
- Show GitHub repo URL
- Show deployed app URL

### Recording Tips:
1. **Practice** 2-3 times before recording
2. **Script on paper** beside your screen
3. **Use Loom** (loom.com) for easy recording
4. **Speak clearly** and at moderate pace
5. **Show URLs** clearly for 2-3 seconds each
6. **Edit** if you make mistakes (Loom allows trimming)

---

## 📤 SUBMISSION GUIDE

### Submission Form: https://forms.gle/KMKEKaFUD6ZX4UtY8

### Required Information:

1. **GitHub Repository URL**
   - Example: https://github.com/Ahmed-KHI/hackathon-ii-phase2
   - Must be PUBLIC
   - Must include:
     - All source code (frontend, backend)
     - /specs folder with documentation
     - README.md with setup instructions
     - CLAUDE.md with Claude Code usage
     - .gitignore (no secrets committed)

2. **Deployed Frontend URL**
   - Example: https://hackathon-todo-phase2.vercel.app
   - Must be working (test before submitting)

3. **Deployed Backend URL**
   - Example: https://hackathon-todo-backend.vercel.app
   - Test /health endpoint before submitting
   - API docs should be accessible at /docs

4. **Demo Video URL**
   - Example: https://www.loom.com/share/xxxxx
   - Must be under 90 seconds
   - Must be publicly accessible
   - Should cover all features

5. **WhatsApp Number**
   - Include country code
   - For live presentation invitation (top submissions only)

### Pre-Submission Checklist:
- [ ] All tests pass locally
- [ ] Backend deployed and health check works
- [ ] Frontend deployed and loads correctly
- [ ] CORS configured (frontend can call backend)
- [ ] Database connected (Neon)
- [ ] User registration works
- [ ] User login works
- [ ] All CRUD operations work
- [ ] User isolation verified (critical!)
- [ ] Demo video recorded and uploaded
- [ ] GitHub repository is public
- [ ] README has complete setup instructions
- [ ] No secrets in Git history

---

## 🏆 SCORING RUBRIC ALIGNMENT

| Category | Points | Your Score |
|----------|--------|------------|
| **Backend Implementation** | 30 | ___/30 |
| - Auth endpoints (register, login) | 10 | |
| - Task CRUD endpoints (6 endpoints) | 20 | |
| **Security (User Isolation)** | 20 | ___/20 |
| - All queries filter by user_id | 8 | |
| - Authorization checks on all endpoints | 8 | |
| - 404 (not 403) for unauthorized access | 4 | |
| **Frontend Implementation** | 20 | ___/20 |
| - Auth pages (register, login) | 5 | |
| - Task management UI (list, create, edit, delete) | 15 | |
| **Responsive Design** | 5 | ___/5 |
| - Mobile, tablet, desktop support | 5 | |
| **Spec-Driven Development** | 15 | ___/15 |
| - Complete specs folder | 8 | |
| - Code references to specs | 4 | |
| - CLAUDE.md instructions | 3 | |
| **Code Quality** | 5 | ___/5 |
| - Type hints, modular structure | 5 | |
| **Documentation** | 5 | ___/5 |
| - README, API docs, demo video | 5 | |
| **TOTAL** | **100** | **___/100** |

### Target Score: 90+ points for excellent submission

---

## 🆘 TROUBLESHOOTING

### Issue: "Cannot connect to database"
**Solution**:
```bash
# Test Neon connection
psql $DATABASE_URL

# Verify URL format:
# postgresql://user:pass@host/db?sslmode=require
# sslmode=require is REQUIRED for Neon
```

### Issue: "CORS error in browser"
**Solution**:
```python
# backend/src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend.vercel.app"  # Add your production URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

### Issue: "JWT token invalid"
**Solution**:
- Ensure BETTER_AUTH_SECRET matches in both frontend and backend
- Check token expiration (7 days default)
- Verify token format: "Bearer <token>"

### Issue: "User can see other users' tasks"
**Solution** (CRITICAL):
```python
# EVERY endpoint must have these checks:

# 1. Verify path user_id matches token user_id
if str(current_user.id) != str(user_id):
    raise HTTPException(status_code=404, detail="Not found")

# 2. Filter query by user_id
tasks = session.exec(
    select(Task).where(Task.user_id == current_user.id)
).all()
```

### Issue: "Vercel deployment fails"
**Solutions**:
- Check Python version in vercel.json (3.13)
- Verify all dependencies in requirements.txt
- Check build logs in Vercel dashboard
- Ensure DATABASE_URL set in environment variables

### Issue: "Frontend build fails"
**Solutions**:
```bash
# Clear cache and rebuild
rm -rf .next node_modules
npm install
npm run build

# Check for TypeScript errors
npm run lint
```

---

## 📞 SUPPORT RESOURCES

- **GIAIC Discord**: [Community Support]
- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs
- **SQLModel Docs**: https://sqlmodel.tiangolo.com
- **Neon Docs**: https://neon.tech/docs

---

**You're ready to submit Phase 2! Good luck! 🚀**

**Remember**: Test everything locally first, then deploy, then test production, then submit.
