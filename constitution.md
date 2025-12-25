# Project Constitution

## Purpose

This document defines the immutable principles, constraints, and standards for the Hackathon II Todo Application project. All phases must comply with these rules.

## Project Identity

**Name:** Evolution of Todo - Spec-Driven Development Journey  
**Hackathon:** Panaversity Hackathon II  
**Methodology:** Spec-Driven Development (SDD) using Claude Code and Spec-Kit Plus  

## Core Principles

### 1. Spec-Driven Development (Non-Negotiable)

**Rule:** No code shall be written manually. All implementation must be generated through Claude Code based on complete specifications.

- Every feature must have a `.specify` file (WHAT)
- Every feature must have a `.plan` file (HOW)
- Every feature must have a `.tasks` file (BREAKDOWN)
- Implementation follows only after specification approval

**Constraint:** If specification is incomplete or ambiguous, STOP and refine the spec. Never improvise.

### 2. Progressive Evolution

The project evolves through 5 distinct phases:

1. **Phase I:** In-Memory Python Console App (Basic Level)
2. **Phase II:** Full-Stack Web Application (Basic Level + Auth)
3. **Phase III:** AI-Powered Chatbot (Basic Level + AI)
4. **Phase IV:** Local Kubernetes Deployment (Basic Level + K8s)
5. **Phase V:** Advanced Cloud Deployment (All Levels + Event-Driven)

**Rule:** Each phase builds upon the previous. No phase-skipping allowed.

### 3. Feature Progression

#### Basic Level Features (Phases I-V)
1. Add Task – Create new todo items
2. Delete Task – Remove tasks from the list
3. Update Task – Modify existing task details
4. View Task List – Display all tasks
5. Mark as Complete – Toggle task completion status

#### Intermediate Level Features (Phase V)
6. Priorities & Tags/Categories
7. Search & Filter
8. Sort Tasks

#### Advanced Level Features (Phase V)
9. Recurring Tasks
10. Due Dates & Time Reminders

**Rule:** Basic features must work flawlessly before advancing to Intermediate/Advanced.

## Technology Stack Constraints

### Phase I: Console App
- **Language:** Python 3.13+
- **Package Manager:** UV
- **Storage:** In-memory (Python data structures)
- **Dev Tools:** Claude Code, Spec-Kit Plus

### Phase II: Web Application
- **Frontend:** Next.js 16+ (App Router), TypeScript, Tailwind CSS
- **Backend:** Python FastAPI
- **ORM:** SQLModel
- **Database:** Neon Serverless PostgreSQL
- **Auth:** Better Auth with JWT
- **Deployment:** Vercel (frontend), Cloud provider (backend)

### Phase III: AI Chatbot
- **Frontend:** OpenAI ChatKit
- **Backend:** FastAPI + OpenAI Agents SDK
- **MCP:** Official MCP SDK (Python)
- **Database:** Neon PostgreSQL (conversations, messages)
- **Auth:** Better Auth JWT

### Phase IV: Local Kubernetes
- **Container:** Docker (Docker Desktop with Gordon AI)
- **Orchestration:** Kubernetes (Minikube)
- **Package Manager:** Helm Charts
- **AIOps:** kubectl-ai, kagent

### Phase V: Cloud Deployment
- **Cloud Platform:** DigitalOcean Kubernetes (DOKS) OR Oracle Cloud (OKE) OR Azure (AKS) OR Google Cloud (GKE)
- **Event Streaming:** Kafka (Strimzi self-hosted OR Redpanda Cloud)
- **Distributed Runtime:** Dapr (Pub/Sub, State, Jobs API, Secrets)
- **CI/CD:** GitHub Actions

## Coding Standards

### Python (Phases I, II, III+)

**Style:**
- Follow PEP 8 strictly
- Use type hints for all function signatures
- Docstrings for all modules, classes, and public functions
- Maximum line length: 100 characters

**Patterns:**
- Use dataclasses or Pydantic models for data structures
- Prefer async/await for I/O operations (Phase II+)
- Use context managers for resource management
- Handle errors explicitly, never silent failures

**Structure:**
```
src/
├── __init__.py
├── main.py           # Entry point
├── models.py         # Data models
├── services.py       # Business logic
├── utils.py          # Helper functions
└── tests/            # Unit tests
```

### TypeScript/Next.js (Phase II+)

**Style:**
- Use TypeScript strict mode
- No `any` types unless absolutely necessary
- Prefer functional components with hooks
- Use Tailwind CSS classes (no inline styles)

**Patterns:**
- Server Components by default
- Client Components only for interactivity
- API calls through dedicated API client (`/lib/api.ts`)
- Environment variables for configuration

### FastAPI (Phase II+)

**Patterns:**
- Pydantic models for request/response validation
- Dependency injection for database sessions
- HTTPException for error responses
- Separate routers for logical API groupings

**Structure:**
```
backend/
├── main.py           # FastAPI app
├── models.py         # SQLModel database models
├── schemas.py        # Pydantic request/response schemas
├── routes/           # API route handlers
│   ├── tasks.py
│   └── auth.py
├── db.py             # Database connection
└── config.py         # Configuration
```

## Architecture Constraints

### Data Storage

**Phase I:** In-memory Python list/dict  
**Phase II+:** Neon PostgreSQL via SQLModel  
**Phase III+:** Add conversation history tables  

**Rule:** Never use SQLite or local files for production (Phase II+). Always use Neon PostgreSQL.

### Authentication (Phase II+)

**Rule:** Use Better Auth with JWT tokens. Backend must verify JWT on every protected endpoint.

**Flow:**
1. User logs in via Better Auth (frontend)
2. Better Auth issues JWT token
3. Frontend includes token in `Authorization: Bearer <token>` header
4. Backend verifies token and extracts user_id
5. All operations filtered by authenticated user

### AI Architecture (Phase III+)

**Rule:** Use stateless architecture. Server holds NO conversation state in memory.

**Pattern:**
```
Request → Fetch history from DB → Build message array → 
Run OpenAI Agent with MCP tools → Store response in DB → Return to client
```

**MCP Tools:**
- `add_task(user_id, title, description)`
- `list_tasks(user_id, status)`
- `complete_task(user_id, task_id)`
- `delete_task(user_id, task_id)`
- `update_task(user_id, task_id, title, description)`

**Rule:** MCP tools are also stateless. They read/write to database directly.

### Event-Driven Architecture (Phase V)

**Rule:** Use Kafka for event streaming with Dapr abstraction.

**Kafka Topics:**
- `task-events` – All CRUD operations
- `reminders` – Scheduled reminder triggers
- `task-updates` – Real-time sync events

**Dapr Building Blocks:**
- **Pub/Sub:** Kafka abstraction
- **State Management:** Conversation/task cache
- **Jobs API:** Scheduled reminders (NOT cron bindings)
- **Secrets:** API keys, DB credentials
- **Service Invocation:** Inter-service communication

### Kubernetes Deployment (Phase IV+)

**Phase IV (Local):**
- Deploy on Minikube
- Use Helm charts
- Docker images built with Gordon AI assistance
- Basic monitoring

**Phase V (Cloud):**
- Deploy on DigitalOcean DOKS / Oracle OKE / Azure AKS / Google GKE
- Kafka on Strimzi (self-hosted) OR Redpanda Cloud
- Full Dapr deployment
- CI/CD with GitHub Actions
- Production monitoring

## Security Constraints

### Authentication
- JWT tokens must expire (7 days max)
- Refresh tokens for long sessions
- Password hashing with bcrypt/argon2

### API Security
- All endpoints require authentication (except login/signup)
- User data isolation (users only see their own tasks)
- Input validation on all endpoints
- Rate limiting (Phase V)

### Secrets Management
- Environment variables for sensitive data
- Never commit secrets to Git
- Use `.env.local` for development
- Use Dapr Secrets API or Kubernetes Secrets (Phase IV+)

## Testing Requirements

### Phase I
- Manual testing via console
- Test all 5 Basic Level features

### Phase II+
- Unit tests for business logic
- API endpoint tests
- Frontend component tests (optional but recommended)

### Phase III+
- Test MCP tool invocations
- Test conversation persistence

### Phase IV+
- Test Helm chart deployment
- Test pod readiness/liveness

### Phase V
- Integration tests with Kafka/Dapr
- Load testing (optional)

## Documentation Requirements

### Every Phase Must Include:

1. **README.md**
   - Project overview
   - Setup instructions (step-by-step)
   - Usage guide with examples
   - Technology stack
   - Deployment instructions

2. **CLAUDE.md**
   - Claude Code instructions
   - How to use Spec-Kit workflow
   - Project-specific conventions

3. **specs/**
   - `<feature>.specify.md` – Requirements (WHAT)
   - `<feature>.plan.md` – Architecture (HOW)
   - `<feature>.tasks.md` – Task breakdown (BREAKDOWN)

4. **Demo Video**
   - Maximum 90 seconds
   - Show all implemented features
   - Show spec-driven workflow

## Submission Requirements

### Required Deliverables (Every Phase)

1. **GitHub Repository**
   - Public repository
   - Clear folder structure
   - All specs in `/specs` folder
   - README.md with setup instructions
   - CLAUDE.md with Claude Code usage

2. **Deployed Application** (Phase II+)
   - Frontend on Vercel (Phase II-V)
   - Backend on cloud provider (Phase II-V)
   - Working demo accessible via URL

3. **Demo Video**
   - Under 90 seconds
   - Show features + spec-driven workflow
   - Use NotebookLM or screen recording

4. **Submission Form**
   - GitHub repo link
   - Deployed app links
   - Demo video link
   - WhatsApp number (for presentation invitation)

## Evaluation Criteria

### Each Phase Scored On:

1. **Spec Completeness (30%)**
   - Are all specs present and detailed?
   - Do specs follow Specify → Plan → Tasks structure?

2. **Implementation Quality (40%)**
   - Does code match the specs?
   - Are all required features working?
   - Code quality and organization

3. **Documentation (20%)**
   - Clear README with setup instructions
   - CLAUDE.md with proper instructions
   - Video demo quality

4. **Spec-Driven Workflow (10%)**
   - Evidence of spec-first development
   - Iteration history in specs folder

### Bonus Points (Phase-Dependent)

- Reusable Intelligence (Claude Code Subagents/Agent Skills): +200
- Cloud-Native Blueprints via Agent Skills: +200
- Multi-language Support (Urdu): +100
- Voice Commands: +200

## Prohibited Practices

**NEVER:**
- Write code manually (must use Claude Code)
- Skip specification phase
- Implement features not in spec
- Hardcode secrets or credentials
- Deploy without testing
- Submit incomplete phases
- Use technologies outside approved stack
- Copy code without understanding
- Create fake demos or screenshots

## Change Management

### Updating This Constitution

Changes to this constitution require:
1. Justification document in `/specs/constitution-amendments/`
2. Approval rationale
3. Update version number in `.spec-kit/config.yaml`

### Spec Changes During Development

**Process:**
1. Update `.specify` file with new requirements
2. Regenerate `.plan` if architecture changes
3. Update `.tasks` with new breakdown
4. Implement via Claude Code
5. Document change in spec history

## Success Criteria

### Phase I Success
- All 5 Basic Level features working in console
- Clean Python code structure
- Complete specs (specify, plan, tasks)
- README with setup instructions

### Phase II Success
- All Basic Level features in web UI
- User authentication working
- Frontend + Backend deployed
- API endpoints tested

### Phase III Success
- Chatbot understands natural language
- All 5 MCP tools working
- Conversation persistence
- Stateless architecture

### Phase IV Success
- Application running on Minikube
- Helm charts working
- Docker images built
- kubectl-ai/kagent demonstrated

### Phase V Success
- Deployed on cloud Kubernetes
- Kafka event streaming working
- Dapr integration complete
- Advanced features implemented
- CI/CD pipeline active

## Conclusion

This constitution serves as the immutable foundation for the Hackathon II Todo project. Every decision, every line of code, and every architectural choice must align with these principles.

**Remember:** Spec-Driven Development means specifications come first, implementation follows. If specs are unclear, refine them. Never improvise.

---

**Version:** 1.0  
**Last Updated:** December 25, 2025  
**Authority:** Panaversity Hackathon II Requirements
