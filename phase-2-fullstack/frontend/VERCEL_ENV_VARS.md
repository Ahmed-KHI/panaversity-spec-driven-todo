# Vercel Environment Variables Configuration

## Add these in Vercel Dashboard after initial deployment:

1. Go to: https://vercel.com/YOUR-USERNAME/YOUR-PROJECT-NAME/settings/environment-variables

2. Add these variables:

### NEXT_PUBLIC_API_URL
```
https://ahmedkhi-todo-api-phase2.hf.space
```
**Important:** No trailing slash!

### BETTER_AUTH_SECRET
```
hackathon-phase2-secret-key-change-in-production-min32chars
```
**Must match backend!**

### BETTER_AUTH_URL
```
https://YOUR-VERCEL-APP.vercel.app
```
**Update after first deployment with your actual Vercel URL**

### DATABASE_URL
```
YOUR_NEON_DATABASE_URL
```
**Copy from backend .env file**

---

## Deployment Steps:

1. Run: `vercel login`
2. Run: `vercel --prod`
3. Follow prompts
4. After deployment, add environment variables in Vercel dashboard
5. Redeploy: `vercel --prod`
6. Update backend CORS_ORIGINS to include Vercel URL
