# 🎬 Phase II Demo Video Guide

**Duration:** 90 seconds (strict)  
**Format:** MP4, 1080p recommended  
**Upload:** YouTube (unlisted) or Loom  

---

## 🎯 Quick Recording Options

### **Option 1: Screen Recording Software (Recommended)**

**For Windows:**
- **OBS Studio** (Free, professional) - [Download](https://obsproject.com/)
- **ShareX** (Free, simple) - [Download](https://getsharex.com/)
- **Windows Game Bar** (Built-in) - Press `Win + G`

**For Mac:**
- **QuickTime Player** (Built-in) - File → New Screen Recording
- **OBS Studio** (Free, professional)

**For Online (No Installation):**
- **Loom** - [loom.com](https://loom.com) - Records & uploads automatically
- **Kapwing** - [kapwing.com](https://kapwing.com) - Browser-based

### **Option 2: Using Loom (Easiest - 5 minutes setup)**

1. Go to [loom.com](https://loom.com)
2. Sign up (free account)
3. Install browser extension or desktop app
4. Click "New Video" → "Screen + Camera" or "Screen Only"
5. Follow script below
6. Video auto-uploads, get link instantly

---

## 📝 90-Second Script

**Your Deployment URLs:**
- Frontend: https://panaversity-spec-driven-todo.vercel.app
- Backend API: https://ahmedkhi-todo-api-phase2.hf.space/docs

### **Timeline Breakdown**

```
0:00-0:10 (10s) - Introduction
0:10-0:25 (15s) - Registration & Login
0:25-0:55 (30s) - Task Operations (Add, Update, Complete, Delete)
0:55-1:10 (15s) - User Isolation Demo
1:10-1:30 (20s) - Tech Stack & Spec-Driven Development
```

---

## 🎤 Full Script with Actions

### **Scene 1: Introduction (0:00-0:10)**

**What to Show:**
- Your deployed app homepage
- Briefly show the URL in browser

**What to Say:**
```
"Hi, this is Ahmed's Phase II submission for the GIAIC Hackathon II. 
This is a full-stack Todo application with user authentication, 
deployed on Vercel and Hugging Face. Let me show you the features."
```

**Actions:**
1. Open: https://panaversity-spec-driven-todo.vercel.app
2. Show the homepage/login page

---

### **Scene 2: Registration & Login (0:10-0:25)**

**What to Show:**
- Register a new account
- Show successful login
- Show redirect to dashboard

**What to Say:**
```
"First, I'll register a new account. The system uses Better Auth 
with JWT tokens that expire after 7 days. Passwords are hashed 
with bcrypt. Let me log in."
```

**Actions:**
1. Click "Register" or "Sign Up"
2. Fill form:
   - Email: `demo@example.com`
   - Password: `password123`
3. Submit and show success
4. Show automatic redirect to dashboard

**⏱️ Timing Tip:** Pre-type credentials or use autofill to save time

---

### **Scene 3: Task Operations (0:25-0:55)**

**What to Show:**
- Add 2 tasks quickly
- Mark one as complete
- Update a task
- Delete a task

**What to Say:**
```
"The app implements all 5 basic level features. 
I'll add some tasks, mark one complete, update another, 
and delete one. Notice how the UI updates in real-time."
```

**Actions:**

**0:25-0:35 (10s) - Add Tasks:**
1. Click "Add Task" or "New Task"
2. Add first task:
   - Title: "Buy groceries"
   - Description: "Milk, eggs, bread"
   - Submit
3. Add second task:
   - Title: "Finish hackathon"
   - Description: "Complete demo video"
   - Submit

**0:35-0:45 (10s) - Complete & Update:**
4. Click checkbox on "Buy groceries" → Shows completed state
5. Click "Edit" on "Finish hackathon"
6. Change title to "Complete Phase II demo"
7. Save

**0:45-0:55 (10s) - Delete:**
8. Click "Delete" on completed task
9. (Optional) Show confirmation dialog if you have one
10. Task disappears from list

**⏱️ Timing Tip:** Have tasks pre-written on notepad to copy-paste

---

### **Scene 4: User Isolation (0:55-1:10)**

**What to Show:**
- Logout
- Login as different user
- Show different/empty task list
- Critical security feature

**What to Say:**
```
"Now let me demonstrate user isolation - a critical security requirement. 
When I log out and log in as a different user, they see only their own 
tasks, not mine. Every query is filtered by user ID."
```

**Actions:**
1. Click "Logout"
2. Click "Login"
3. Login with different account:
   - Email: `user2@example.com`
   - Password: `password123`
4. Show empty task list or different tasks

**⚠️ IMPORTANT:** Register `user2@example.com` BEFORE recording!

---

### **Scene 5: Tech Stack & Wrap-up (1:10-1:30)**

**What to Show:**
- Briefly show API docs (optional)
- Show code structure in VS Code (optional)
- Or just your GitHub repo

**What to Say:**
```
"The backend uses FastAPI with SQLModel ORM and PostgreSQL from Neon. 
Frontend is Next.js 16 with Better Auth. This project demonstrates 
spec-driven development using Claude Code. All specifications, 
constitution, and implementation are in the GitHub repository. 
Thank you for watching!"
```

**Actions:**
1. Open new tab: https://ahmedkhi-todo-api-phase2.hf.space/docs
2. Briefly show Swagger UI (3 seconds)
3. OR show your GitHub repo: https://github.com/Ahmed-KHI/panaversity-spec-driven-todo
4. End recording

---

## 🎬 Recording Checklist

### **Before Recording:**

```
□ Pre-register two test accounts:
  - demo@example.com / password123
  - user2@example.com / password123

□ Clear browser cache/cookies for clean demo

□ Close unnecessary browser tabs

□ Disable desktop notifications

□ Test app once to ensure it's working

□ Have task text ready to copy-paste:
  - "Buy groceries" + "Milk, eggs, bread"
  - "Finish hackathon" + "Complete demo video"

□ Set up screen recording software

□ Do a 30-second test recording first

□ Check audio levels (if using microphone)
```

---

## 🎙️ Recording Tips

### **Audio:**
- **Option 1:** Record with microphone (recommended)
- **Option 2:** Add voice-over after recording
- **Option 3:** Text captions only (acceptable)

### **Visual:**
- **Resolution:** 1920x1080 (1080p) or 1280x720 (720p)
- **Frame Rate:** 30 FPS minimum
- **Cursor:** Make sure it's visible
- **Zoom:** Use Ctrl + Plus to enlarge text if needed

### **Performance:**
- Speak clearly but naturally
- Don't rush - 90 seconds is enough
- Pause briefly between sections
- Smile! (if using camera)

### **Common Mistakes to Avoid:**
- ❌ Going over 90 seconds (judges stop watching)
- ❌ Mumbling or speaking too fast
- ❌ Not showing user isolation
- ❌ Spending too much time on one feature
- ❌ Forgetting to show the deployed URL

---

## ⚙️ OBS Studio Quick Setup (If Using OBS)

1. **Download OBS:** https://obsproject.com/download
2. **Install and open OBS**
3. **Create Scene:**
   - Click "+" under "Scenes" → Name it "Demo"
4. **Add Source:**
   - Click "+" under "Sources"
   - Select "Display Capture" (full screen) or "Window Capture" (browser only)
   - Select your monitor/browser window
5. **Add Microphone (Optional):**
   - Click "+" under "Sources"
   - Select "Audio Input Capture"
   - Choose your microphone
6. **Start Recording:**
   - Click "Start Recording" (bottom right)
   - Follow script
   - Click "Stop Recording" when done
7. **Find Video:**
   - File → Show Recordings
   - Video saved as .mp4

---

## 📤 Upload & Submit

### **Step 1: Upload Video**

**Option A: YouTube (Recommended)**
1. Go to [youtube.com](https://youtube.com)
2. Click "Create" → "Upload Video"
3. Select your video file
4. Title: "Phase II - Full-Stack Todo App - GIAIC Hackathon II"
5. Description: "Spec-driven development demo for GIAIC Hackathon II Phase II"
6. Visibility: **Unlisted** (not private!)
7. Publish
8. Copy the video link

**Option B: Loom**
- Video auto-uploads
- Click "Copy Link"
- Done!

**Option C: Google Drive**
1. Upload to Google Drive
2. Right-click → Share → "Anyone with the link"
3. Copy link

**Option D: Vimeo**
1. Sign up at vimeo.com
2. Upload video
3. Privacy: "Anyone"
4. Copy link

---

### **Step 2: Verify Video Length**

**CRITICAL:** Judges only watch first 90 seconds!

Check your video:
```
✓ Length: 85-90 seconds (perfect)
✓ Length: 75-85 seconds (acceptable)
✗ Length: 95+ seconds (judges stop at 90s)
✗ Length: Under 60 seconds (too short)
```

If over 90 seconds, trim it:
- **Windows:** Photos app → Edit → Trim
- **Mac:** QuickTime → Edit → Trim
- **Online:** [kapwing.com/tools/trim-video](https://www.kapwing.com/tools/trim-video)

---

### **Step 3: Submit to Hackathon**

**Submission Form:** https://forms.gle/KMKEKaFUD6ZX4UtY8

**What to Submit:**
```
✅ GitHub Repository URL:
   https://github.com/Ahmed-KHI/panaversity-spec-driven-todo

✅ Deployed Frontend URL:
   https://panaversity-spec-driven-todo.vercel.app

✅ Demo Video Link:
   [Your YouTube/Loom link here]

✅ WhatsApp Number:
   [Your number for presentation invitation]
```

---

## 🎯 Quick Start: 15-Minute Recording Plan

**Preparation (5 minutes):**
1. Register two test accounts
2. Open Loom or OBS
3. Practice script once (without recording)

**Recording (3 minutes):**
1. Take 1: Follow script (aim for 85-90 seconds)
2. Review: Watch your recording
3. Take 2: Re-record if needed (most people get it right on take 2)

**Upload & Submit (7 minutes):**
1. Upload to YouTube/Loom
2. Copy link
3. Submit form

**Total Time:** 15 minutes

---

## 🆘 Troubleshooting

### **Problem: Video is too long (95+ seconds)**

**Solution 1:** Speed up sections
- Registration: Auto-fill credentials
- Task operations: Pre-type text, copy-paste faster
- Skip optional parts (API docs)

**Solution 2:** Trim video
- Use Kapwing, Windows Photos, or QuickTime
- Cut 3-5 seconds from intro or outro

---

### **Problem: App is slow during recording**

**Solution:**
- Refresh page before recording
- Close other browser tabs
- Check your internet connection
- Record during off-peak hours

---

### **Problem: Forgot to register second user**

**Solution:**
- Pause recording (OBS)
- Register user2@example.com quickly
- Resume recording from logout scene

---

### **Problem: Made a mistake during recording**

**Solution:**
- For major mistakes: Just restart (takes 2 minutes)
- For minor mistakes: Keep going - authenticity is fine!
- You can do multiple takes

---

## ✅ Final Checklist Before Submitting

```
□ Video is 85-90 seconds long
□ Shows registration/login
□ Shows all 5 task operations (add, view, update, delete, complete)
□ Demonstrates user isolation (critical!)
□ Shows deployed URL in browser
□ Audio is clear (if using voice)
□ Video is uploaded to YouTube/Loom
□ Video link works (test in incognito mode)
□ Video is "Unlisted" (not "Private")
□ Form submitted with all required fields
```

---

## 🎓 Sample Video References

**Good Examples:**
- Fast-paced but clear
- Shows all required features
- Under 90 seconds
- Professional but not over-produced

**What Judges Look For:**
1. ✅ All 5 basic features working
2. ✅ User authentication functional
3. ✅ User isolation demonstrated
4. ✅ Professional presentation
5. ✅ Spec-driven development mentioned

---

## 📞 Need Help?

If you encounter issues:
1. Test your recording software first (30-second test)
2. Check the app is working in production
3. Have backup credentials ready
4. Record multiple takes if needed (it's normal!)

---

## 🚀 Ready to Record?

**You've got this!** Follow the script, keep it under 90 seconds, and you're done.

**Remember:**
- Preparation: 5 minutes
- Recording: 3 minutes (maybe 2 takes)
- Upload: 2 minutes
- **Total: 10 minutes**

Good luck! 🎉

---

**Last Updated:** January 8, 2026  
**Phase:** Phase II Submission  
**Hackathon:** GIAIC Hackathon II - The Evolution of Todo
