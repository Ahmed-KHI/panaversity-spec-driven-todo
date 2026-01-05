# Vercel Deployment Fix Guide

## Problem
Better Auth authentication is failing because database tables don't exist in Neon.

## Root Cause
The Neon database has the FastAPI backend tables (`users` and `tasks`) but is missing Better Auth tables (`user`, `session`, `account`, `verification`).

## Solution Steps

### Step 1: Create Better Auth Tables in Neon

1. Go to: https://console.neon.tech/
2. Select your project
3. Click **SQL Editor**
4. Copy and paste the contents of `scripts/setup-better-auth-db.sql`
5. Click **Run** to execute the SQL

### Step 2: Verify Environment Variables in Vercel

Go to: https://vercel.com/thor/panaversity-spec-driven-todo/settings/environment-variables

Ensure these are set for **Production**:

```env
DATABASE_URL=postgresql://neondb_owner:npg_...@ep-patient-meadow-a1vgpumd-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=hackathon-phase2-secret-key-change-in-production-min32chars
BETTER_AUTH_URL=https://panaversity-spec-driven-todo.vercel.app
NEXT_PUBLIC_API_URL=https://ahmedkhi-todo-api-phase2.hf.space
```

### Step 3: Update Backend CORS

Your backend needs to allow requests from Vercel.

**Option A: Update via Hugging Face Space**
1. Go to your Hugging Face Space settings
2. Add environment variable:
   ```
   CORS_ORIGINS=http://localhost:3000,https://panaversity-spec-driven-todo.vercel.app
   ```

**Option B: Update backend code**
Edit `backend/src/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://panaversity-spec-driven-todo.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 4: Redeploy Frontend

```bash
cd phase-2-fullstack/frontend
vercel --prod
```

### Step 5: Test Authentication

1. Go to: https://panaversity-spec-driven-todo.vercel.app/register
2. Create a new account
3. Login
4. Verify dashboard loads without errors

## Verification Checklist

- [ ] Better Auth tables exist in Neon database
- [ ] All environment variables set in Vercel
- [ ] Backend CORS includes Vercel URL
- [ ] Frontend redeployed
- [ ] Registration works
- [ ] Login works
- [ ] Dashboard loads
- [ ] Tasks can be created/updated/deleted

## Debugging

If issues persist, check:

1. **Vercel Logs:**
   ```bash
   vercel logs --prod
   ```

2. **Browser Console:**
   - Check for 401/403/500 errors
   - Verify API_URL is correct

3. **Database Connection:**
   - Test DATABASE_URL can connect
   - Verify tables exist: `\dt` in Neon SQL Editor

4. **Backend Logs:**
   - Check Hugging Face Space logs
   - Verify CORS is allowing Vercel domain

## Common Errors

### "Application error: a server-side exception"
- Missing DATABASE_URL in Vercel
- Better Auth tables don't exist in database

### "401 Unauthorized"
- Backend not allowing CORS from Vercel
- Token not being sent correctly
- User not authenticated

### "Invalid user ID detected"
- Better Auth session not created properly
- Database connection failed
- Tables missing in Neon

## Need Help?

The dashboard page now has error handling that will redirect to login if anything fails. Check browser console for detailed error messages.
