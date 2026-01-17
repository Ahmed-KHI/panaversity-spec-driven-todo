# OpenAI ChatKit Setup Guide - Phase III

**Document:** ChatKit Domain Allowlist Configuration  
**Phase:** III - AI Chatbot with MCP Integration  
**Task Reference:** T-015 (Frontend Environment Config)  
**Created:** January 17, 2026

---

## Overview

Phase III uses **OpenAI ChatKit** for the conversational UI. ChatKit requires domain allowlist configuration on the OpenAI platform for security.

---

## Prerequisites

- OpenAI account with API access
- Deployed frontend URL (Vercel, GitHub Pages, or custom domain)
- Admin access to OpenAI organization settings

---

## Step 1: Deploy Your Frontend

Before configuring ChatKit, deploy your frontend to get a production URL:

### Option A: Vercel (Recommended)
```bash
cd phase-2-fullstack/frontend
vercel deploy --prod
```
**Result:** `https://your-project.vercel.app`

### Option B: GitHub Pages
**Result:** `https://username.github.io/repo-name`

### Option C: Custom Domain
**Result:** `https://yourdomain.com`

### For Local Development
**URL:** `http://localhost:3000` (usually works without allowlist config)

---

## Step 2: Configure OpenAI Domain Allowlist

### 2.1 Navigate to Security Settings
1. Go to: [https://platform.openai.com/settings/organization/security/domain-allowlist](https://platform.openai.com/settings/organization/security/domain-allowlist)
2. Log in to your OpenAI account
3. Select your organization (if you have multiple)

### 2.2 Add Your Domain
1. Click **"Add domain"** button
2. Enter your frontend URL:
   - ✅ `https://your-project.vercel.app` (no trailing slash)
   - ✅ `https://yourdomain.com`
   - ✅ `http://localhost:3000` (for local dev)
   - ❌ `https://your-project.vercel.app/` (with trailing slash)
3. Click **"Save"**

### 2.3 Get Your Domain Key
After adding the domain, OpenAI will provide a **domain key**:
- This is a unique identifier for your approved domain
- Copy this key - you'll need it for the next step
- Example format: `dk_abc123xyz...`

---

## Step 3: Configure Environment Variables

### 3.1 Frontend Environment Variable

Add the domain key to your frontend environment:

#### Local Development
```bash
# Edit: phase-2-fullstack/frontend/.env.local
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=dk_your_actual_domain_key_here
```

#### Vercel Deployment
```bash
# Via Vercel CLI:
vercel env add NEXT_PUBLIC_OPENAI_DOMAIN_KEY

# Or via Vercel Dashboard:
# Project Settings → Environment Variables → Add Variable
# Name: NEXT_PUBLIC_OPENAI_DOMAIN_KEY
# Value: dk_your_actual_domain_key_here
# Environments: Production, Preview, Development
```

### 3.2 Complete Environment Setup

Your `.env.local` should now have:
```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Auth Configuration
BETTER_AUTH_SECRET=hackathon-phase2-secret-key-change-in-production-min32chars
BETTER_AUTH_URL=http://localhost:3000

# OpenAI ChatKit (Phase III)
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=dk_your_actual_domain_key_here
```

---

## Step 4: Verify Installation

### 4.1 Install Dependencies
```bash
cd phase-2-fullstack/frontend
npm install
```

This will install `@openai/chatkit` along with other dependencies.

### 4.2 Start Development Server
```bash
npm run dev
```

### 4.3 Test ChatKit Integration
1. Navigate to: `http://localhost:3000/login`
2. Log in with your credentials
3. Go to: `http://localhost:3000/chat`
4. You should see the ChatKit UI
5. Try sending a message: "Add task to test ChatKit"

---

## Step 5: Production Deployment

### 5.1 Deploy Frontend
```bash
vercel --prod
```

### 5.2 Verify Environment Variables
```bash
# Check Vercel environment variables
vercel env ls

# Should show:
# NEXT_PUBLIC_API_URL
# NEXT_PUBLIC_OPENAI_DOMAIN_KEY
# BETTER_AUTH_SECRET
# BETTER_AUTH_URL
```

### 5.3 Test Production Deployment
1. Visit your production URL
2. Log in
3. Navigate to `/chat`
4. Test conversation functionality

---

## Troubleshooting

### Issue: "Domain not allowed" error

**Cause:** Domain not in allowlist or domain key mismatch

**Solution:**
1. Verify domain is added to OpenAI allowlist (exact match, no trailing slash)
2. Ensure `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` matches the key from OpenAI dashboard
3. Rebuild and redeploy: `vercel --prod`

### Issue: ChatKit component not rendering

**Cause:** Missing dependency or import error

**Solution:**
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Issue: "Cannot find module '@openai/chatkit'"

**Cause:** Package not installed

**Solution:**
```bash
npm install @openai/chatkit
```

### Issue: Chat messages not sending

**Cause:** Backend API URL misconfigured or backend not running

**Solution:**
1. Verify `NEXT_PUBLIC_API_URL` points to your backend
2. Check backend is running and accessible
3. Test API endpoint: `curl https://your-backend.hf.space/health`

### Issue: Authentication errors

**Cause:** JWT token not being passed correctly

**Solution:**
1. Verify user is logged in
2. Check `jwtToken` prop is passed to `ChatInterface`
3. Inspect browser console for auth errors

---

## ChatKit Configuration Reference

The ChatKit component accepts these configuration options:

```typescript
interface ChatKitConfig {
  apiUrl: string;                    // Your chat API endpoint
  domainKey: string;                 // From OpenAI allowlist
  headers?: Record<string, string>;  // Custom headers (JWT auth)
  initialMessage?: {                 // Welcome message
    role: 'assistant';
    content: string;
  };
  onMessage: (message: string) => Promise<any>;  // Message handler
  placeholder?: string;              // Input placeholder
  maxLength?: number;                // Max message length
  theme?: {                          // UI customization
    primaryColor?: string;
    backgroundColor?: string;
    userMessageColor?: string;
    assistantMessageColor?: string;
    borderRadius?: string;
  };
}
```

---

## Security Notes

### ✅ Best Practices
- Never commit `.env.local` to Git
- Use different domain keys for dev/staging/prod
- Rotate domain keys if compromised
- Keep domain allowlist minimal

### ❌ Common Mistakes
- Committing domain keys to public repos
- Using production keys in development
- Adding wildcard domains to allowlist
- Exposing keys in client-side code

---

## Next Steps

After ChatKit is configured:

1. ✅ Test all chat functionality
2. ✅ Deploy backend to Hugging Face Spaces
3. ✅ Deploy frontend to Vercel
4. ✅ Update README with deployment URLs
5. ✅ Record 90-second demo video
6. 🚀 Move to Phase IV (Kubernetes)

---

## Resources

- [OpenAI ChatKit Documentation](https://platform.openai.com/docs/chatkit)
- [Domain Allowlist Settings](https://platform.openai.com/settings/organization/security/domain-allowlist)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Phase III Specification](./specs/003-phase-iii-chatbot/spec.md)

---

**Status:** Configuration Guide Complete  
**Last Updated:** January 17, 2026  
**Phase:** III - AI Chatbot with MCP Integration
