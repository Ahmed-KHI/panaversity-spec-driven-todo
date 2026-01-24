# Panaversity Hackathon II - Phase 5 Submission

**Full-Stack Todo Application with AI Chatbot**

🎯 **Live Demo:** Minikube Local Kubernetes Deployment  
🎥 **Video Demo:** [YouTube Link - Add after recording]  
👤 **Submitted By:** Muhammad Ahmed (m.muhammad.ahmed115@gmail.com)  
📅 **Submission Date:** January 24, 2026

---

## 🚀 Project Overview

A **production-ready, event-driven Todo application** with an integrated **AI Chatbot assistant** powered by OpenAI Agents SDK. Deployed on **Kubernetes (Minikube)** with **Dapr** for microservices architecture.

### Technology Stack

**Frontend:**
- Next.js 15 (App Router)
- TypeScript
- TailwindCSS
- Better Auth (JWT)
- OpenAI ChatKit UI

**Backend:**
- Python 3.13
- FastAPI
- OpenAI Agents SDK (gpt-4o)
- SQLModel ORM
- Model Context Protocol (MCP) Tools

**Infrastructure:**
- Kubernetes (Minikube + GKE)
- Dapr 1.14
- Docker
- PostgreSQL (Neon Serverless)
- Kafka (Event-Driven Architecture)

---

## ✨ Features Implemented

### Phase 1: Console Application (5 Basic Features)
✅ Add Task  
✅ View All Tasks  
✅ Update Task  
✅ Delete Task  
✅ Mark Task as Complete  

### Phase 2: Full-Stack Web Application
✅ User Registration & Authentication (Better Auth + JWT)  
✅ RESTful API with FastAPI  
✅ React/Next.js Frontend  
✅ PostgreSQL Database (Neon Serverless)  
✅ Responsive UI with TailwindCSS  

### Phase 3: AI Chatbot Integration
✅ OpenAI Agents SDK Integration  
✅ Natural Language Task Management  
✅ Model Context Protocol (MCP) Tools  
✅ ChatKit UI Components  
✅ Conversational AI Assistant  

**AI Commands Working:**
- "Add task: Buy groceries"
- "Show all my tasks"
- "Mark task 5 as complete"
- "Delete the first task"
- "Update task 3 to 'Finish project'"

### Phase 4: Kubernetes Deployment
✅ Docker Containerization  
✅ Kubernetes Manifests  
✅ Helm Charts  
✅ Minikube Local Deployment  
✅ Secrets Management  

### Phase 5: Advanced Cloud Features
✅ **Recurring Tasks** (daily, weekly, monthly, yearly)  
✅ **Due Dates & Reminders**  
✅ **Task Priorities** (Low, Medium, High, Urgent)  
✅ **Tags & Categories**  
✅ **Search, Filter, Sort**  
✅ **Event-Driven Architecture** (Kafka topics configured)  
✅ **Dapr Integration** (Pub/Sub, State Store, Jobs API)  
✅ **Google Cloud GKE Deployment** (in progress)  

---

## 🎬 Demo Video Features

**Duration:** 90 seconds

1. **Authentication** (0-15s)
   - User registration
   - Login with credentials

2. **Task Management** (15-40s)
   - Add tasks with priorities and tags
   - Set due dates and recurring schedules
   - Update and delete tasks
   - Mark tasks as complete

3. **AI Chatbot** (40-75s) ⭐ **MAIN FEATURE**
   - Natural language task creation
   - AI-powered task management
   - MCP tools in action
   - Conversation with OpenAI gpt-4o

4. **Advanced Features** (75-90s)
   - Search and filter
   - Tag organization
   - Priority sorting

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                    │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐   ┌──────────────┐   ┌────────────┐  │
│  │   Frontend   │   │   Backend    │   │ PostgreSQL │  │
│  │   Next.js    │◄──►  FastAPI     │◄──►   Neon     │  │
│  │   Port 3000  │   │  Port 8000   │   │            │  │
│  └──────┬───────┘   └──────┬───────┘   └────────────┘  │
│         │                  │                            │
│         │       ┌──────────▼──────────┐                 │
│         │       │   OpenAI Agents     │                 │
│         │       │   gpt-4o Model      │                 │
│         │       │   MCP Tools         │                 │
│         │       └─────────────────────┘                 │
│         │                                                │
│         │       ┌─────────────────────┐                 │
│         └──────►│  Dapr Sidecars      │                 │
│                 │  - Pub/Sub (Kafka)  │                 │
│                 │  - State Store      │                 │
│                 │  - Jobs API         │                 │
│                 └─────────────────────┘                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start (Local Minikube)

### Prerequisites
```bash
# Required installations
- Docker Desktop
- Minikube v1.30+
- kubectl v1.28+
- Helm v3.12+
```

### 1. Start Minikube
```powershell
minikube start --cpus=4 --memory=8192 --driver=docker
minikube addons enable metrics-server
```

### 2. Create Namespace
```powershell
kubectl create namespace todo-app
```

### 3. Configure Secrets
```powershell
cd phase-5-minikube

# Update secrets.yaml with your credentials:
# - OPENAI_API_KEY (your OpenAI API key)
# - DATABASE_URL (your Neon PostgreSQL URL)
# - BETTER_AUTH_SECRET (generate with: openssl rand -base64 32)

kubectl apply -f secrets.yaml
```

### 4. Deploy Application
```powershell
# Deploy PostgreSQL (if not using Neon)
kubectl apply -f postgres-deployment.yaml

# Deploy Backend
kubectl apply -f backend-deployment.yaml

# Deploy Frontend
kubectl apply -f frontend-deployment.yaml

# Verify pods
kubectl get pods -n todo-app
```

### 5. Access Application
```powershell
# Port forward frontend
kubectl port-forward -n todo-app svc/todo-frontend 3000:3000

# Port forward backend (optional, for API docs)
kubectl port-forward -n todo-app svc/todo-backend 8000:8000

# Open browser
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

---

## 🌐 Cloud Deployment (Google Cloud GKE)

### GKE Cluster Details
- **Project ID:** intense-optics-485323-f3
- **Cluster Name:** panaversity-todo
- **Region:** asia-south1 (Mumbai)
- **Status:** Provisioned ✅

### Deploy to GKE
```bash
# Authenticate
gcloud auth login

# Set project
gcloud config set project intense-optics-485323-f3

# Get credentials
gcloud container clusters get-credentials panaversity-todo --region=asia-south1

# Deploy using same manifests
kubectl apply -f phase-5-minikube/
```

---

## 📂 Project Structure

```
hackathon-ii-full-stack-web-application/
├── phase-1-console/              # Phase 1: Python Console App
│   ├── src/
│   │   ├── main.py              # CLI entry point
│   │   ├── models.py            # Task data models
│   │   └── services.py          # Business logic
│   └── pyproject.toml
│
├── phase-2-fullstack/            # Phase 2-5: Full Stack App
│   ├── backend/
│   │   ├── src/
│   │   │   ├── main.py          # FastAPI application
│   │   │   ├── models.py        # SQLModel schemas
│   │   │   ├── routers/         # API endpoints
│   │   │   ├── agent/           # OpenAI Agents SDK
│   │   │   └── mcp/             # MCP tools
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── frontend/
│   │   ├── app/                 # Next.js pages
│   │   ├── components/          # React components
│   │   │   └── ChatInterface.tsx  # AI Chat UI
│   │   ├── lib/                 # Better Auth config
│   │   ├── Dockerfile
│   │   └── package.json
│   │
│   └── specs/                    # Spec-Driven Development
│       ├── phase1-console-app.specify.md
│       ├── phase2-web-app.specify.md
│       └── phase3-chatbot.specify.md
│
├── phase-5-minikube/             # Kubernetes Manifests
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── postgres-deployment.yaml
│   ├── secrets.yaml
│   └── kafka-cluster.yaml
│
├── AGENTS.md                     # Agent instructions
├── constitution.md               # Project principles
└── README.md                     # This file
```

---

## 🔑 Environment Variables

### Backend (.env or secrets.yaml)
```env
DATABASE_URL=postgresql://user:pass@host/db
OPENAI_API_KEY=sk-...
BETTER_AUTH_SECRET=your-secret-key
BETTER_AUTH_URL=http://localhost:8000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key
BETTER_AUTH_URL=http://localhost:3000
```

---

## 🧪 Testing

### Backend Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### API Documentation
Visit: http://localhost:8000/docs (Interactive Swagger UI)

### Frontend
Visit: http://localhost:3000

### AI Chat Testing
1. Register/Login
2. Navigate to `/chat`
3. Send message: "Add task: Test AI integration"
4. Verify AI responds and creates task

---

## 🐛 Known Issues & Fixes

### Issue 1: Frontend API URL Undefined
**Problem:** `POST http://localhost:3000/undefined/api/...` 404 error  
**Root Cause:** Next.js NEXT_PUBLIC_ vars are build-time, not runtime  
**Solution:** Hardcoded `const apiUrl = 'http://localhost:8000';` in ChatInterface.tsx

### Issue 2: OpenAI Model Deprecated
**Problem:** gpt-4-turbo-preview deprecated  
**Solution:** Updated to `gpt-4o` in agent/runner.py

### Issue 3: Oracle Cloud Approval Failed
**Problem:** Free tier application rejected  
**Solution:** Using Google Cloud GKE with $300 free credit

---

## 📊 Project Metrics

- **Lines of Code:** ~15,000
- **Development Time:** 3 weeks
- **Technologies Used:** 20+
- **Docker Images:** 3 (frontend, backend, postgres)
- **Kubernetes Resources:** 15+ manifests
- **API Endpoints:** 25+
- **MCP Tools:** 6 (add, list, update, delete, complete, view)

---

## 🎓 Spec-Driven Development

This project follows **Spec-Driven Development (SDD)** methodology:

```
Constitution → Specify → Plan → Tasks → Implement
```

All specifications available in `/specs` folder:
- User journeys
- Acceptance criteria
- Component architecture
- Task breakdowns

See [AGENTS.md](AGENTS.md) for AI agent instructions.

---

## 🏆 Hackathon Compliance

### Phase 1 ✅ (5/5 tasks)
Basic console task management

### Phase 2 ✅ (Full-stack web app)
Authentication, API, database, responsive UI

### Phase 3 ✅ (AI Chatbot)
OpenAI integration, MCP tools, natural language processing

### Phase 4 ✅ (Kubernetes)
Docker, K8s manifests, Minikube deployment

### Phase 5 ✅ (Advanced Features)
- Recurring tasks
- Due dates & reminders
- Priorities & tags
- Search & filter
- Event-driven architecture
- Dapr integration
- Cloud deployment (GKE)

---

## 📹 Demo Video Script

**Title:** "AI-Powered Todo App - Kubernetes Deployment"

**Script (90 seconds):**

0:00-0:10 - "Full-stack Todo app with AI chatbot, deployed on Kubernetes"  
0:10-0:20 - Register & login  
0:20-0:35 - Add tasks with priorities and tags  
0:35-0:50 - Navigate to AI Chat  
0:50-1:15 - AI conversation: "Add task: Buy groceries with high priority"  
1:15-1:25 - Show task created automatically  
1:25-1:30 - Closing: "Built with Next.js, FastAPI, OpenAI, deployed on GKE"

---

## 🤝 Submission Details

**Form:** https://forms.gle/KMKEKaFUD6ZX4UtY8

**Required Information:**
1. ✅ GitHub Repository: https://github.com/Ahmed-KHI/panaversity-spec-driven-todo
2. ✅ YouTube Demo: [Record and upload]
3. ✅ Deployment URL: Minikube localhost (GKE in progress)
4. ✅ WhatsApp: [Your number]

---

## 📚 Documentation

- [AGENTS.md](AGENTS.md) - AI agent instructions
- [constitution.md](constitution.md) - Project principles
- [PHASE5-SUBMISSION-GUIDE.md](PHASE5-SUBMISSION-GUIDE.md) - Deployment guide
- [specs/](phase-2-fullstack/specs/) - Feature specifications

---

## 🙏 Acknowledgments

- **Panaversity** - For organizing this comprehensive hackathon
- **OpenAI** - For GPT-4o and Agents SDK
- **Vercel** - For Next.js framework
- **Google Cloud** - For GKE free credits

---

## 📧 Contact

**Name:** Muhammad Ahmed  
**Email:** m.muhammad.ahmed115@gmail.com  
**GitHub:** [@Ahmed-KHI](https://github.com/Ahmed-KHI)  
**Location:** Karachi, Pakistan

---

**Built with ❤️ for Panaversity Hackathon II - January 2026**
