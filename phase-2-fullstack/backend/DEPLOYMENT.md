# Hugging Face Spaces Deployment Guide

This backend is deployed on **Hugging Face Spaces** (free tier) using Docker.

## 📋 Prerequisites

1. Hugging Face account (free): https://huggingface.co/join
2. Access token: https://huggingface.co/settings/tokens

## 🚀 Deployment Steps

### Step 1: Create Hugging Face Space

1. Go to https://huggingface.co/new-space
2. Fill in:
   - **Space name:** `todo-api-phase2` (or your choice)
   - **SDK:** **Docker** ⚠️ Important!
   - **Visibility:** Public
   - **Space hardware:** CPU basic (free)
3. Click **Create Space**

### Step 2: Configure Space Settings

In your Space settings:

1. Go to **Settings** → **Variables and secrets**
2. Add these secrets:

```
DATABASE_URL=postgresql://neondb_owner:YOUR_PASSWORD@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=your-secret-key-here
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app
ENVIRONMENT=production
```

### Step 3: Deploy to Space

#### Option A: Using Git (Recommended)

```bash
cd backend

# Install huggingface_hub
pip install huggingface_hub

# Login to Hugging Face
huggingface-cli login
# Paste your access token when prompted

# Clone your space (replace with your space)
git clone https://huggingface.co/spaces/YOUR_USERNAME/todo-api-phase2

# Copy backend files to space directory
cp -r src/ todo-api-phase2/
cp Dockerfile todo-api-phase2/
cp requirements.txt todo-api-phase2/
cp pyproject.toml todo-api-phase2/

# Commit and push
cd todo-api-phase2
git add .
git commit -m "Initial deployment"
git push
```

#### Option B: Using Web Interface

1. In your Space, click **Files** → **Add file** → **Upload files**
2. Upload these files:
   - `Dockerfile`
   - `requirements.txt`
   - `src/` folder (all Python files)
3. Click **Commit new files to main**

### Step 4: Wait for Build

- HF Spaces will automatically build your Docker container
- Check **Logs** tab to monitor build progress
- Build time: 3-5 minutes
- Status will change to "Running" when ready

### Step 5: Test Your API

Your API will be available at:
```
https://YOUR_USERNAME-todo-api-phase2.hf.space
```

Test endpoints:
```bash
# Health check
curl https://YOUR_USERNAME-todo-api-phase2.hf.space/health

# API docs
open https://YOUR_USERNAME-todo-api-phase2.hf.space/docs
```

## 🔧 Troubleshooting

### Build Fails

**Check Logs:**
- Go to Space → Logs tab
- Look for error messages

**Common Issues:**

1. **Missing dependencies:**
   - Ensure all packages in `requirements.txt`
   - Check Python version compatibility

2. **Port not 7860:**
   - HF Spaces requires port 7860
   - Check Dockerfile: `EXPOSE 7860`
   - Check CMD: `--port 7860`

3. **Environment variables:**
   - Check Space Settings → Variables and secrets
   - Ensure DATABASE_URL is correct
   - Test database connection from local

### API Not Responding

1. **Check Space Status:**
   - Should show "Running" with green indicator
   - If "Building" - wait for build to complete
   - If "Error" - check Logs

2. **Check Database Connection:**
   - Verify Neon database is running
   - Test connection string locally
   - Check IP whitelist (Neon allows all by default)

3. **Check CORS:**
   - Ensure CORS_ORIGINS includes your frontend URL
   - Check browser console for CORS errors

## 📝 Update Deployment

To update your deployed API:

```bash
cd backend/todo-api-phase2

# Make changes to files
# Then commit and push

git add .
git commit -m "Update: description of changes"
git push
```

HF Spaces will automatically rebuild and redeploy.

## 🔗 Next Steps

After successful deployment:

1. **Copy your Space URL:** `https://YOUR_USERNAME-todo-api-phase2.hf.space`
2. **Update Frontend:** Set `NEXT_PUBLIC_API_URL` in Vercel to your Space URL
3. **Update CORS:** Add your Vercel URL to `CORS_ORIGINS` in Space settings
4. **Test Full Flow:** Register → Login → Create Task → Verify

## 📚 Resources

- [HF Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Docker SDK Guide](https://huggingface.co/docs/hub/spaces-sdks-docker)
- [Environment Variables](https://huggingface.co/docs/hub/spaces-overview#managing-secrets)

## 💰 Pricing

**Free Tier:**
- CPU basic (2 vCPU, 16GB RAM)
- Always-on (no sleep)
- Perfect for hackathon projects!

**Limitations:**
- Public visibility required for free tier
- Build time limits (15 minutes)
- No GPU on free tier (not needed for this project)
