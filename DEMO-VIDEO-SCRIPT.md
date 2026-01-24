# Demo Video Recording Guide

**Target Duration:** 90 seconds (judges only watch first 90 seconds!)  
**Platform:** Screen recording software (OBS Studio, Loom, or Windows Game Bar)

---

## 📹 Recording Setup

### Tools Required:
- **Screen Recorder:** OBS Studio (free) or Loom
- **Audio:** Built-in microphone (optional narration)
- **Browser:** Chrome/Edge with localhost:3000 open

### Recording Settings:
- **Resolution:** 1920x1080 (1080p)
- **Frame Rate:** 30 FPS
- **Audio:** Clear narration or on-screen text
- **Format:** MP4

---

## 🎬 Shot-by-Shot Script (90 seconds)

### Scene 1: Introduction (0-10 seconds)
**Action:**
- Show splash screen or homepage
- Display project title

**Narration/Text:**
> "AI-Powered Todo Application with Kubernetes Deployment"
> "Built with Next.js, FastAPI, OpenAI Agents SDK"

**What to Show:**
- Quick overview of tech stack logos
- Localhost URL visible: http://localhost:3000

---

### Scene 2: Authentication (10-20 seconds)
**Action:**
1. Click "Register" button
2. Fill form quickly:
   - Name: Demo User
   - Email: demo@test.com
   - Password: ••••••••
3. Click "Sign Up"
4. Auto-redirect to dashboard

**Narration/Text:**
> "Secure authentication with Better Auth and JWT tokens"

**Tips:**
- Have registration form already open
- Use autofill if possible
- Show smooth transition

---

### Scene 3: Task Management (20-40 seconds)
**Action:**
1. **Add Task:**
   - Click "Add Task"
   - Title: "Complete hackathon submission"
   - Priority: High (red badge)
   - Tags: work, urgent
   - Due Date: Tomorrow
   - Click "Create"

2. **Show Task List:**
   - Task appears instantly
   - Priority badge visible
   - Tags displayed

3. **Update Task:**
   - Click edit icon
   - Change priority to "Urgent"
   - Save

4. **Mark Complete:**
   - Click checkbox
   - Task strikethrough effect

**Narration/Text:**
> "Full CRUD operations with priorities, tags, and due dates"

**Tips:**
- Pre-create 2-3 sample tasks for context
- Show smooth animations
- Highlight priority colors

---

### Scene 4: AI Chatbot ⭐ (40-75 seconds) **MOST IMPORTANT**
**Action:**
1. Click "AI Chat" in navigation
2. Chat interface loads with ChatKit UI

3. **First Interaction:**
   - Type: "hello"
   - AI responds: "Hi! I'm your AI task assistant..."

4. **Create Task via AI:**
   - Type: "Add task: Buy groceries with high priority"
   - Show AI thinking indicator
   - AI responds: "I've created a new task..."
   - Task appears in list

5. **List Tasks:**
   - Type: "Show all my tasks"
   - AI lists all tasks with IDs

6. **Update Task:**
   - Type: "Mark task 3 as complete"
   - AI confirms completion

**Narration/Text:**
> "AI-powered task management using OpenAI GPT-4o"
> "Natural language processing with Model Context Protocol tools"
> "Conversational interface for hands-free task management"

**Tips:**
- THIS IS THE STAR FEATURE - spend 35 seconds here!
- Show network tab briefly to prove API calls work
- Highlight AI thinking/typing indicators
- Show task list updating in real-time

---

### Scene 5: Advanced Features (75-90 seconds)
**Action:**
1. **Search:**
   - Type "groceries" in search box
   - Filtered results appear

2. **Filter:**
   - Click "High Priority" filter
   - Only high-priority tasks show

3. **Tags:**
   - Show tag organization
   - Click tag to filter

4. **Recurring Tasks:**
   - Quick glimpse of recurring task setup

**Narration/Text:**
> "Advanced features: Search, filter, tags, recurring tasks"
> "Deployed on Kubernetes with Dapr for microservices"

**Closing Screen:**
- Project name
- Your name: Muhammad Ahmed
- GitHub: github.com/Ahmed-KHI/panaversity-spec-driven-todo
- Tech stack summary

---

## 🎯 Recording Checklist

### Before Recording:
- [ ] Minikube running (`minikube status`)
- [ ] Pods running (`kubectl get pods -n todo-app`)
- [ ] Port forwards active (3000, 8000)
- [ ] Browser open at http://localhost:3000
- [ ] Clear browser cache and cookies (fresh start)
- [ ] Close unnecessary tabs
- [ ] Hide bookmarks bar (cleaner look)
- [ ] Prepare sample tasks (2-3 pre-created)
- [ ] Test AI chat is working
- [ ] Clear chat history (optional, for clean demo)
- [ ] Increase font size for readability
- [ ] Turn off notifications
- [ ] Close Slack, Discord, etc.

### During Recording:
- [ ] Steady mouse movements (not too fast)
- [ ] Show each feature clearly
- [ ] Wait for animations to complete
- [ ] Clear narration (or on-screen text)
- [ ] NO MISTAKES - practice first!
- [ ] Keep within 90 seconds

### After Recording:
- [ ] Review full video
- [ ] Check audio quality
- [ ] Trim to exactly 90 seconds
- [ ] Add opening/closing screens (optional)
- [ ] Export as MP4 (1920x1080, 30fps)

---

## 🎥 Recording Commands

### Start Everything:
```powershell
# 1. Start Minikube (if not running)
minikube start

# 2. Check pods
kubectl get pods -n todo-app

# 3. Port forward frontend
Start-Job -Name "frontend-pf" -ScriptBlock { 
    kubectl port-forward -n todo-app svc/todo-frontend 3000:3000 
}

# 4. Port forward backend
Start-Job -Name "backend-pf" -ScriptBlock { 
    kubectl port-forward -n todo-app svc/todo-backend 8000:8000 
}

# 5. Open browser
Start-Process "http://localhost:3000"

# 6. Wait 5 seconds for everything to load
Start-Sleep -Seconds 5
```

### Quick Test Before Recording:
```powershell
# Test frontend
curl http://localhost:3000

# Test backend health
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

---

## 📱 Upload to YouTube

### Steps:
1. Go to: https://studio.youtube.com
2. Click "Upload Videos"
3. Select your MP4 file

**Video Details:**
- **Title:** Panaversity Hackathon II - AI Todo App (Muhammad Ahmed)
- **Description:**
```
Full-stack Todo application with AI chatbot assistant.

Features:
✅ Next.js 15 + FastAPI
✅ OpenAI GPT-4o Integration
✅ Model Context Protocol Tools
✅ Kubernetes Deployment (Minikube + GKE)
✅ Dapr Microservices
✅ Better Auth (JWT)
✅ PostgreSQL (Neon)

GitHub: https://github.com/Ahmed-KHI/panaversity-spec-driven-todo

#Panaversity #Hackathon #AI #Kubernetes #NextJS #FastAPI #OpenAI
```

- **Visibility:** Unlisted (share link only with judges)
- **Thumbnail:** Screenshot of AI chat interface

4. Click "Publish"
5. Copy video link
6. Add to submission form

---

## 🎬 Alternative: Loom Recording

If using Loom (simpler):
1. Install Loom desktop app
2. Click "Record Screen"
3. Select full screen
4. Follow script above
5. Stop recording
6. Loom auto-uploads
7. Copy shareable link
8. Use in submission

---

## 🚨 Common Mistakes to Avoid

❌ **DON'T:**
- Rush through AI chat section (it's the main feature!)
- Show errors or loading failures
- Spend too much time on basic CRUD
- Go over 90 seconds
- Have messy UI (clear old test data)
- Show sensitive info (API keys, passwords)
- Record in low resolution

✅ **DO:**
- Focus 40% of time on AI chatbot
- Show smooth, polished interactions
- Practice 2-3 times before final recording
- Use clear narration or on-screen text
- Show technology stack
- Keep it professional
- Smile in your voice! (if narrating)

---

## ⏱️ Timing Breakdown

```
0:00 - 0:10  | Introduction         | 11%
0:10 - 0:20  | Authentication       | 11%
0:20 - 0:40  | Task Management      | 22%
0:40 - 0:75  | AI Chatbot ⭐        | 39%  ← FOCUS HERE
0:75 - 0:90  | Advanced + Closing   | 17%
```

**Total: 90 seconds = 100% of judge attention**

---

## 🎯 Key Messages to Convey

1. **Full-Stack Mastery:** Next.js + FastAPI integration
2. **AI Innovation:** OpenAI Agents SDK with MCP tools
3. **Cloud-Native:** Kubernetes deployment with Dapr
4. **Production-Ready:** Authentication, database, error handling
5. **Modern Architecture:** Event-driven, microservices, scalable

---

## 📊 Success Criteria

Your video is good if:
- ✅ All features visible in 90 seconds
- ✅ AI chat works perfectly
- ✅ No errors or crashes shown
- ✅ Professional presentation
- ✅ Clear audio/text
- ✅ Tech stack mentioned
- ✅ GitHub link visible at end

---

## 🎬 Ready to Record?

**Final Checklist:**
1. [ ] Read this script 3 times
2. [ ] Practice recording once (don't save)
3. [ ] Clear browser cache
4. [ ] Start all services
5. [ ] Test AI chat manually
6. [ ] Take a deep breath
7. [ ] **RECORD!**

**Remember:** Judges watch MANY videos. Make yours:
- **Clear** - Easy to understand
- **Concise** - No wasted time
- **Impressive** - Show AI as the hero feature
- **Professional** - No mistakes

---

**Good luck! You've built something amazing - now show it off! 🚀**
