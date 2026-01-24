# GKE Deployment Checklist - Phase 5 Todo App

## Current Status

**Deployed on:** Google Cloud Platform (GCP)  
**Project:** intense-optics-485323-f3  
**Cluster:** panaversity-todo (asia-south1)  
**Public URL:** http://34.93.106.63  
**Frontend Version:** 5.0.5 (building - architectural authentication fix)  
**Backend Version:** 5.0.3 (deployed)

---

## Issues Fixed in Frontend 5.0.5

### Root Cause
Frontend Better Auth was configured with direct PostgreSQL database connection (Kysely + pg Pool), causing browser-side code to attempt connection to `127.0.0.1:5432` (ECONNREFUSED error).

### Architectural Fix
**BEFORE (5.0.4 - WRONG):**
```typescript
// lib/auth.config.ts
import { Kysely, PostgresDialect } from "kysely"
import { Pool } from "pg"

const db = new Kysely<Database>({
  dialect: new PostgresDialect({
    pool: new Pool({ connectionString: process.env.DATABASE_URL }),
  }),
})

export const auth = betterAuth({
  database: { provider: "pg", db: db }, // ❌ Frontend has database connection
  // ...
})
```

**AFTER (5.0.5 - CORRECT):**
```typescript
// lib/auth.config.ts
import { betterAuth } from "better-auth"
import { nextCookies } from "better-auth/next-js"

export const auth = betterAuth({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  trustedOrigins: ["http://localhost:3000", "http://34.93.106.63"],
  plugins: [nextCookies()],
  // ✅ No database connection - frontend is thin client only
})
```

### Changes Applied

1. **lib/auth.config.ts** - Removed database connection
   - Deleted: Kysely, PostgresDialect, Pool imports
   - Deleted: database dialect configuration
   - Deleted: `database: { provider: "pg", db: db }`
   - Result: Thin Better Auth client that delegates to backend API

2. **app/api/auth/better-register/route.ts** - Direct backend API call
   - Deleted: `auth.api.signUpEmail()` call (requires database)
   - Added: Direct `fetch(${API_URL}/api/auth/register)` to backend
   - Result: Single authentication layer (backend only)

3. **app/api/auth/better-login/route.ts** - Direct backend API call
   - Deleted: `auth.api.signInEmail()` call (requires database)
   - Added: Direct `fetch(${API_URL}/api/auth/login)` to backend
   - Result: Consistent with registration pattern

---

## Deployment Steps (Post-Build)

### 1. Tag and Push to Google Container Registry

```powershell
# Wait for build to complete
docker images | Select-String "todo-frontend"

# Tag for GCR
docker tag todo-frontend:5.0.5 gcr.io/intense-optics-485323-f3/todo-frontend:5.0.5

# Push to registry
docker push gcr.io/intense-optics-485323-f3/todo-frontend:5.0.5
```

### 2. Update Kubernetes Deployment Manifest

Edit `phase-5-gke/frontend-deployment.yaml`:

```yaml
# Change image version from 5.0.4 to 5.0.5
spec:
  template:
    spec:
      containers:
      - name: todo-frontend
        image: gcr.io/intense-optics-485323-f3/todo-frontend:5.0.5  # ⬅️ Update this
        imagePullPolicy: Always
```

### 3. Deploy to GKE

```powershell
# Apply updated manifest
kubectl apply -f phase-5-gke/frontend-deployment.yaml

# Force pod restart
kubectl delete pod -n todo-app -l app=todo-frontend

# Wait 30 seconds for new pods
Start-Sleep -Seconds 30

# Verify new pods running
kubectl get pods -n todo-app

# Confirm image version
kubectl describe pod -l app=todo-frontend -n todo-app | Select-String "Image:"
```

Expected output:
```
NAME                             READY   STATUS    RESTARTS   AGE
postgres-XXXXXX                  1/1     Running   0          XXm
todo-backend-XXXXXX              2/2     Running   0          XXm
todo-backend-XXXXXX              2/2     Running   0          XXm
todo-frontend-XXXXXX             1/1     Running   0          XXs  ⬅️ New pods
todo-frontend-XXXXXX             1/1     Running   0          XXs  ⬅️ New pods

Image: gcr.io/intense-optics-485323-f3/todo-frontend:5.0.5  ⬅️ Verify version
```

---

## Testing Authentication (CRITICAL)

### 1. Clear Browser Cache
```
Browser: Ctrl+Shift+Delete
Select: "All time"
Check: "Cached images and files"
Click: "Clear data"
```

### 2. Test Registration
1. Navigate to http://34.93.106.63
2. Click "Sign Up"
3. Enter:
   - Email: test@hackathon.com
   - Password: Test1234!
   - Name: Test User
4. Click "Create Account"

**Expected Result:**
- ✅ Success message "Registration successful"
- ✅ Redirected to dashboard
- ✅ No "ECONNREFUSED" errors in browser console (F12)
- ✅ User appears in database

**To verify in database:**
```powershell
kubectl exec -it -n todo-app deployment/postgres -- psql -U todouser -d tododb -c "SELECT id, email, name FROM users;"
```

### 3. Test Login
1. Click "Logout"
2. Enter same credentials
3. Click "Sign In"

**Expected Result:**
- ✅ Successfully logged in
- ✅ Redirected to dashboard
- ✅ JWT token stored in cookies

---

## Testing Phase 5 Features

### 1. Manual Task Creation
1. Click "+ New Task"
2. Fill form:
   - Title: "Test Phase 5 Features"
   - Description: "Verify all Phase 5 functionality"
   - Priority: HIGH
   - Due Date: Tomorrow
   - Tags: "testing,hackathon"
   - Recurring: ✅ Yes
   - Frequency: Daily
3. Click "Create Task"

**Expected Result:**
- ✅ Task appears with 🟠 HIGH badge (orange)
- ✅ Due date shows 📅 Tomorrow's date
- ✅ Recurring indicator 🔄 RECURRING
- ✅ Tags appear as clickable badges

### 2. AI Chat Task Creation
1. Click "💬 AI Chat" button
2. Type: "Add task for gym Monday, priority urgent, recurring weekly"
3. Send message

**Expected Result:**
- ✅ AI responds confirming task creation
- ✅ Task appears in dashboard
- ✅ 🔴 URGENT badge (red)
- ✅ 🔄 RECURRING badge
- ✅ Due date set to next Monday
- ✅ Recurrence frequency = weekly

### 3. Test All Priority Levels
Create tasks with all priorities:
- URGENT (🔴 Red)
- HIGH (🟠 Orange)
- MEDIUM (🟡 Yellow)
- LOW (🟢 Green)

### 4. Test Recurring Frequencies
Create tasks with:
- Daily recurrence
- Weekly recurrence
- Monthly recurrence

### 5. Test Search/Filter/Sort
- Search by title
- Filter by priority
- Filter by tags
- Sort by due date
- Sort by priority
- Sort by created date

---

## Backend Verification

### Check Backend Logs
```powershell
kubectl logs -n todo-app -l app=todo-backend --tail=50
```

Expected: No errors, successful authentication logs

### Check Database Connectivity
```powershell
kubectl exec -it -n todo-app deployment/todo-backend -- python -c "import os; print(os.environ.get('DATABASE_URL'))"
```

Expected: `postgresql://todouser:todopass123@postgres:5432/tododb`

### Verify MCP Tools
```powershell
kubectl logs -n todo-app -l app=todo-backend | Select-String "MCP"
```

Expected: Tool definitions loaded without user_id parameter

---

## Demo Video Recording (90 seconds)

### Structure

**0-15 seconds: Introduction**
- Show URL bar: http://34.93.106.63
- Show login screen
- Quick registration or login

**15-30 seconds: Manual Task Creation**
- Click "+ New Task"
- Show Phase 5 form:
  - Priority dropdown (4 levels)
  - Due date picker
  - Recurring checkbox
  - Frequency selector
- Create task
- Show task in dashboard with colored badges

**30-65 seconds: AI Chat (MAIN FEATURE - 35 seconds)**
- Click "💬 AI Chat"
- Type: "Add task for grocery shopping Friday, priority high, recurring weekly"
- Show AI response
- Navigate back to dashboard
- **Highlight:** Task created with correct priority, due date, recurrence

**65-90 seconds: Feature Showcase**
- Scroll through task list
- Show multiple tasks with:
  - 🔴🟠🟡🟢 Colored priority badges
  - 🔄 Recurring indicators
  - 📅 Due dates
- Quick filter demonstration
- End screen: "Phase 5 Complete - Cloud Deployed"

### Recording Tools
- Windows Game Bar: Win+G (built-in, easy)
- OBS Studio (professional, free)
- Screen recording size: 1920x1080 minimum
- Export: MP4, H.264 codec

---

## YouTube Upload

### Video Details
- **Title:** "Phase 5 Todo App - AI Chat + GKE Cloud Deployment | Panaversity Hackathon II"
- **Description:**
  ```
  Phase 5 Todo Application deployed on Google Cloud GKE
  
  Tech Stack:
  - Frontend: Next.js 15.0.4, TypeScript, TailwindCSS
  - Backend: FastAPI, Python 3.13, SQLModel
  - AI: OpenAI Agents SDK (GPT-4o)
  - Database: PostgreSQL 16
  - Orchestration: Kubernetes (GKE), 5 pods, LoadBalancer
  - Cloud: Google Cloud Platform (asia-south1)
  
  Features:
  ✅ AI Chat - Natural language task creation
  ✅ Priority Levels - 4 levels with color-coded badges
  ✅ Recurring Tasks - Daily/Weekly/Monthly patterns
  ✅ Due Dates - Calendar picker with reminders
  ✅ Advanced Filtering - Search, filter by priority/tags, sort
  ✅ Real-time Sync - Multiple replicas with database persistence
  
  Architecture:
  - 2 Backend replicas (FastAPI + OpenAI Agents)
  - 2 Frontend replicas (Next.js 15)
  - 1 PostgreSQL database (10GB persistent disk)
  - Kubernetes LoadBalancer (Public IP)
  - Dapr sidecar for event-driven architecture
  
  GitHub: https://github.com/Ahmed-KHI/panaversity-spec-driven-todo
  Live App: http://34.93.106.63
  
  Panaversity Hackathon II - Full-Stack Web Application Development
  ```
- **Privacy:** Unlisted
- **Category:** Science & Technology
- **Tags:** kubernetes, gke, nextjs, fastapi, openai, ai-chat, todo-app, panaversity

### Upload Steps
1. Go to YouTube Studio: https://studio.youtube.com/
2. Click "Create" → "Upload videos"
3. Select your MP4 file
4. Fill in title and description
5. Set privacy to "Unlisted"
6. Add thumbnail (optional but recommended)
7. Click "Next" → "Next" → "Publish"
8. Copy YouTube URL: https://youtu.be/XXXXXX

---

## Hackathon Submission

### Form URL
https://forms.gle/KMKEKaFUD6ZX4UtY8

### Required Fields

1. **Name:** [Your Full Name]
2. **Email:** [Your Email]
3. **WhatsApp Number:** [Your Phone]
4. **Roll Number:** [Your Student ID]

5. **GitHub Repository URL:**
   ```
   https://github.com/Ahmed-KHI/panaversity-spec-driven-todo
   ```

6. **YouTube Demo Video URL:**
   ```
   https://youtu.be/XXXXXX  ⬅️ Get from upload
   ```

7. **Deployed Application URL:**
   ```
   http://34.93.106.63
   ```

8. **Project Description:**
   ```
   Phase 5 Complete - AI-Powered Todo Application with Cloud Deployment
   
   This project implements a full-stack todo application with advanced AI capabilities, deployed on Google Cloud GKE. The application demonstrates mastery of modern cloud-native development, event-driven architecture, and AI integration.
   
   Technical Highlights:
   
   Architecture:
   - Microservices architecture with 5 Kubernetes pods
   - 2 backend replicas for high availability
   - 2 frontend replicas with LoadBalancer
   - PostgreSQL database with 10GB persistent storage
   - Dapr sidecar for event-driven capabilities
   
   AI Integration (Phase 5):
   - OpenAI Agents SDK with GPT-4o model
   - Natural language task creation via AI Chat
   - MCP (Model Context Protocol) server with 8 tools
   - Context-aware conversations with database persistence
   
   Features:
   - Priority Management: 4 levels (Urgent/High/Medium/Low) with color-coded badges
   - Recurring Tasks: Flexible patterns (daily/weekly/monthly)
   - Due Dates: Calendar picker with date formatting
   - Advanced Search: Filter by priority, tags, status; Sort by date/priority
   - Real-time Sync: Multi-pod deployment with database consistency
   
   Frontend (Next.js 15):
   - App Router with TypeScript
   - TailwindCSS for styling
   - Better Auth for authentication
   - Phase 5 UI enhancements (colored badges, recurring indicators)
   
   Backend (FastAPI):
   - Python 3.13 with SQLModel ORM
   - JWT authentication with bcrypt password hashing
   - RESTful API with 12 endpoints
   - OpenAI Agents SDK integration
   - Event log for audit trail
   
   Database (PostgreSQL 16):
   - 7 tables (users, tasks, tags, task_tags, conversations, messages, event_log)
   - Proper foreign key relationships
   - Indexed for performance
   
   Cloud Deployment:
   - Google Cloud Platform (GCP)
   - GKE cluster in asia-south1 region
   - Container Registry for image storage
   - LoadBalancer with public IP (34.93.106.63)
   - Kubernetes secrets for secure credential management
   
   Security:
   - OpenAI API key protected via Kubernetes secrets
   - .gitignore for sensitive files
   - JWT tokens for API authentication
   - HTTPS-ready configuration
   
   Development Process:
   - Spec-Driven Development (SDD) methodology
   - Constitution.md for principles
   - Specification → Plan → Tasks → Implementation workflow
   - Full documentation in PHASE5-SUBMISSION-GUIDE.md
   
   This project showcases enterprise-grade development practices including containerization, orchestration, CI/CD readiness, AI integration, and cloud-native architecture.
   ```

---

## Post-Submission

### Keep Running
**Important:** Keep the GKE cluster running for evaluation period (at least 7 days)

### Monitor Costs
```powershell
# Check GCP billing
gcloud beta billing accounts list
gcloud beta billing projects list
```

### Backup Database
```powershell
# Export PostgreSQL database
kubectl exec -n todo-app deployment/postgres -- pg_dump -U todouser tododb > backup.sql

# Or use persistent disk snapshot
gcloud compute disks list
gcloud compute disks snapshot todo-postgres-disk --zone=asia-south1-a
```

### Documentation
All deployment documentation in:
- phase-5-gke/ (Kubernetes manifests)
- PHASE5-SUBMISSION-GUIDE.md (Complete guide)
- This file (GKE-DEPLOYMENT-CHECKLIST.md)

---

## Troubleshooting

### If Authentication Still Fails

1. Check backend logs:
   ```powershell
   kubectl logs -n todo-app -l app=todo-backend --tail=100
   ```

2. Verify frontend environment variables:
   ```powershell
   kubectl exec -n todo-app deployment/todo-frontend -- env | Select-String "API"
   ```

3. Check database connection:
   ```powershell
   kubectl exec -it -n todo-app deployment/postgres -- psql -U todouser -d tododb -c "\dt"
   ```

4. Verify image versions:
   ```powershell
   kubectl describe pod -l app=todo-frontend -n todo-app | Select-String "Image:"
   kubectl describe pod -l app=todo-backend -n todo-app | Select-String "Image:"
   ```

### If Pods Not Starting

1. Check pod status:
   ```powershell
   kubectl get pods -n todo-app
   kubectl describe pod <pod-name> -n todo-app
   ```

2. Check logs:
   ```powershell
   kubectl logs <pod-name> -n todo-app
   kubectl logs <pod-name> -n todo-app --previous  # If crashed
   ```

3. Check secrets:
   ```powershell
   kubectl get secrets -n todo-app
   kubectl describe secret postgres-secret -n todo-app
   ```

### If LoadBalancer Not Accessible

1. Check service:
   ```powershell
   kubectl get svc -n todo-app
   ```

2. Verify External IP assigned:
   ```
   NAME            TYPE           EXTERNAL-IP     PORT(S)
   todo-frontend   LoadBalancer   34.93.106.63    80:xxxxx/TCP  ⬅️ Should have IP
   ```

3. Check GCP firewall rules:
   ```powershell
   gcloud compute firewall-rules list
   ```

---

## Success Criteria

### Phase 5 Complete When:

✅ Frontend 5.0.5 deployed to GKE  
✅ Registration works without ECONNREFUSED errors  
✅ Login works with JWT token storage  
✅ Manual task creation with all Phase 5 fields functional  
✅ AI Chat creates tasks with correct attributes  
✅ Colored priority badges display correctly  
✅ Recurring indicators show properly  
✅ Due dates format correctly  
✅ Search/filter/sort working  
✅ 90-second demo video recorded  
✅ YouTube video uploaded (Unlisted)  
✅ Hackathon form submitted with all URLs  

---

## Timeline

**Immediate (5-10 minutes):**
- Wait for frontend 5.0.5 build
- Push to GCR
- Deploy to GKE
- Test authentication

**Short-term (15-20 minutes):**
- Test all Phase 5 features
- Verify no errors

**Medium-term (20-30 minutes):**
- Record demo video
- Edit if needed

**Final (5 minutes):**
- Upload to YouTube
- Submit hackathon form

**Total:** ~40-70 minutes to completion

---

**Last Updated:** December 26, 2025  
**Status:** Frontend 5.0.5 building with architectural authentication fix  
**Next Action:** Deploy and test authentication on http://34.93.106.63
