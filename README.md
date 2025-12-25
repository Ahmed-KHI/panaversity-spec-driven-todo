# Hackathon II - Todo App (Phase I)

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Phase](https://img.shields.io/badge/Phase-I%2FV-00D084?style=for-the-badge)
![Methodology](https://img.shields.io/badge/Methodology-Spec--Driven-FF6B6B?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Complete-28A745?style=for-the-badge)
![Panaversity](https://img.shields.io/badge/Panaversity-Hackathon%20II-9B59B6?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

**Evolution of Todo - Spec-Driven Development Journey**

This project is part of **Panaversity Hackathon II**, demonstrating mastery of Spec-Driven Development using Claude Code and Spec-Kit Plus.

**Repository:** [github.com/Ahmed-KHI/panaversity-spec-driven-todo](https://github.com/Ahmed-KHI/panaversity-spec-driven-todo)

---

## 📋 Project Overview

A command-line todo application built with **Python 3.13+** using **Spec-Driven Development** methodology. This is **Phase I** of a 5-phase journey that evolves from a simple console app to a cloud-native AI-powered system.

### Current Phase: Phase I - In-Memory Console App

**Status:** ✅ Complete  
**Features:** Basic Level (5 Core Features)  
**Due Date:** December 7, 2025  
**Points:** 100

---

## ✨ Features

### Basic Level Features (Phase I)

1. ✅ **Add Task** - Create new todo items with title and optional description
2. ✅ **Delete Task** - Remove tasks from the list with confirmation
3. ✅ **Update Task** - Modify existing task title and description
4. ✅ **View Task List** - Display all tasks with status indicators
5. ✅ **Mark as Complete** - Toggle task completion status

---

## 🛠️ Technology Stack

- **Language:** Python 3.13+
- **Package Manager:** UV
- **Storage:** In-memory (Python data structures)
- **Development Method:** Spec-Driven Development
- **AI Tools:** Claude Code, Spec-Kit Plus

---

## 📁 Project Structure

```
hackathon-todo/
├── .spec-kit/
│   └── config.yaml              # Spec-Kit configuration
├── specs/
│   ├── phase1-console-app.specify.md   # Requirements (WHAT)
│   ├── phase1-console-app.plan.md      # Architecture (HOW)
│   └── phase1-console-app.tasks.md     # Task Breakdown (BREAKDOWN)
├── src/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # CLI interface and entry point
│   ├── models.py                # Task entity and storage
│   └── services.py              # Business logic and validation
├── constitution.md              # Project principles and constraints
├── AGENTS.md                    # AI agent instructions
├── CLAUDE.md                    # Claude Code entry point
├── README.md                    # This file
├── pyproject.toml               # UV project configuration
└── .gitignore                   # Git ignore rules
```

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.13+** installed
2. **UV package manager** installed
3. **Git** (for cloning)

### Installation Steps

#### For Windows (WSL 2 Required)

```powershell
# 1. Install WSL 2 (if not already installed)
wsl --install

# 2. Set WSL 2 as default
wsl --set-default-version 2

# 3. Install Ubuntu
wsl --install -d Ubuntu-22.04

# 4. Inside WSL, install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 5. Clone the repository
git clone <your-repo-url>
cd hackathon-todo

# 6. Run the application
python src/main.py
```

#### For macOS/Linux

```bash
# 1. Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone the repository
git clone <your-repo-url>
cd hackathon-todo

# 3. Run the application
python src/main.py
```

---

## 📖 Usage Guide

### Starting the Application

```bash
python src/main.py
```

You'll see the welcome screen:

```
==================================================
         Todo App - Phase I
         Spec-Driven Development
==================================================

Type 'help' for available commands

> _
```

### Available Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `add` | a, new | Add a new task |
| `list` | l, ls, show | View all tasks |
| `view` | v, detail | View task details |
| `update` | u, edit | Update a task |
| `delete` | d, remove, rm | Delete a task |
| `complete` | c, done | Mark task as complete |
| `incomplete` | ic, undone, pending | Mark task as incomplete |
| `help` | h, ? | Show help message |
| `exit` | quit, q | Exit application |

### Example Workflow

```
# Add a task
> add
Enter task title: Buy groceries
Enter task description (optional): Milk, eggs, bread, butter
✓ Task added successfully!
  ID: 1
  Title: Buy groceries
  Status: Pending

# List all tasks
> list
==================================================
         Your Todo List
==================================================

[1] [✗] Buy groceries

--------------------------------------------------
Total: 1 tasks (0 completed, 1 pending)

# Mark task as complete
> complete
Enter task ID: 1
✓ Task marked as completed!

# View task details
> view
Enter task ID: 1
==================================================
Task #1
==================================================
Title:       Buy groceries
Description: Milk, eggs, bread, butter
Status:      ✓ Completed
Created:     2025-12-25 14:30:00

# Exit application
> exit
Goodbye! 👋
```

---

## 🧪 Testing

### Manual Testing

Run through these test scenarios:

#### Happy Path Test
1. Start application
2. Add 3 tasks with different titles
3. List all tasks
4. View details of one task
5. Update a task's title
6. Mark a task as complete
7. Mark it as incomplete again
8. Delete a task
9. List to verify deletion
10. Exit application

#### Error Handling Test
1. Try adding task with empty title (should fail)
2. Try adding task with title > 200 characters (should fail)
3. Try viewing non-existent task ID (should fail)
4. Try updating non-existent task (should fail)
5. Try deleting non-existent task (should fail)
6. Enter non-numeric input for task ID (should fail gracefully)
7. Test unknown command (should show error + hint)

#### Edge Cases Test
1. Add task with maximum length title (200 chars)
2. Add task with maximum length description (1000 chars)
3. Add 10 tasks rapidly, verify IDs are sequential
4. Toggle task complete/incomplete multiple times
5. Update task with same values (should succeed)
6. Cancel task deletion (type 'n')

---

## 📚 Spec-Driven Development Methodology

This project follows the **Agentic Dev Stack** workflow:

```
Specify → Plan → Tasks → Implement
```

### Specification Files

1. **[phase1-console-app.specify.md](specs/phase1-console-app.specify.md)** - The WHAT
   - User stories
   - Acceptance criteria
   - Functional requirements
   - Data requirements

2. **[phase1-console-app.plan.md](specs/phase1-console-app.plan.md)** - The HOW
   - Architecture design
   - Component breakdown
   - Data model design
   - Implementation approach

3. **[phase1-console-app.tasks.md](specs/phase1-console-app.tasks.md)** - The BREAKDOWN
   - 12 atomic tasks (T-001 to T-012)
   - Dependencies and order
   - Acceptance criteria per task
   - Testing checklist

### Code References

Every function includes task reference comments:

```python
def create_task(self, title: str, description: Optional[str] = None) -> Task:
    """
    Create a new task with validation.
    
    [Task]: T-003
    [From]: phase1-console-app.specify.md §3.1
    """
```

This ensures **full traceability** from requirements to implementation.

---

## 🎯 Phase I Success Criteria

- [x] All 5 Basic Level features implemented
- [x] Clean Python code structure (models, services, main)
- [x] Type hints on all functions
- [x] Docstrings with task references
- [x] Complete specs (specify, plan, tasks)
- [x] README with setup instructions
- [x] Manual testing passed

---

## 🔮 Future Phases

### Phase II: Full-Stack Web Application (Due: Dec 14, 2025)
- Next.js frontend
- FastAPI backend
- Neon PostgreSQL database
- User authentication with Better Auth

### Phase III: AI-Powered Chatbot (Due: Dec 21, 2025)
- OpenAI ChatKit interface
- OpenAI Agents SDK
- MCP server with tools
- Natural language commands

### Phase IV: Local Kubernetes Deployment (Due: Jan 4, 2026)
- Docker containers
- Minikube deployment
- Helm charts
- kubectl-ai, kagent

### Phase V: Advanced Cloud Deployment (Due: Jan 18, 2026)
- DigitalOcean Kubernetes
- Kafka event streaming
- Dapr distributed runtime
- Advanced features (priorities, tags, recurring tasks)

---

## 📊 Hackathon Scoring

| Phase | Points | Status |
|-------|--------|--------|
| Phase I: Console App | 100 | ✅ Complete |
| Phase II: Web App | 150 | 🔜 Next |
| Phase III: AI Chatbot | 200 | 📅 Upcoming |
| Phase IV: K8s Local | 250 | 📅 Upcoming |
| Phase V: Cloud Deploy | 300 | 📅 Upcoming |
| **Total Base Points** | **1,000** | |

### Bonus Points (Available)
- Reusable Intelligence (Subagents/Skills): +200
- Cloud-Native Blueprints: +200
- Multi-language Support (Urdu): +100
- Voice Commands: +200

---

## 📝 Key Learnings

### Spec-Driven Development Benefits

1. **Clarity:** Every feature is fully specified before coding
2. **Traceability:** Every line of code maps back to a requirement
3. **Quality:** Specs are reviewed before implementation
4. **Collaboration:** Multiple developers/agents can work from same specs
5. **Evolution:** Easy to add phases without breaking existing code

### Python Best Practices Applied

- **Type hints** for all function signatures
- **Dataclasses** for clean data models
- **Separation of concerns** (models, services, CLI)
- **Dependency injection** (service receives storage)
- **Error handling** with clear messages
- **PEP 8 compliance** throughout

---

## 🤝 Contributing

This is an individual hackathon submission. However, the methodology and structure can be studied and adapted for team projects.

---

## 📄 License

This project is created for educational purposes as part of Panaversity Hackathon II.

---

## 👤 Author

**[Your Name]**  
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com
- WhatsApp: [Your Number] (for presentation invitation)

---

## 🙏 Acknowledgments

- **Panaversity Team** - For organizing Hackathon II
- **Claude Code** - AI pair programming assistant
- **Spec-Kit Plus** - Specification management framework
- **PIAIC & GIAIC** - AI education community

---

## 📞 Support

For questions about this project:

1. Check the [specification files](specs/) for detailed requirements
2. Review the [constitution.md](constitution.md) for project principles
3. Read the [AGENTS.md](AGENTS.md) for development workflow
4. Submit questions via hackathon submission form

---

## 🎬 Demo Video

**Coming Soon** - Maximum 90 seconds demonstrating:
- All 5 Basic Level features
- Spec-driven development workflow
- Error handling
- Code structure with task references

---

## 🔗 Links

- **Hackathon Documentation:** [Link to Hackathon Requirements]
- **Submission Form:** https://forms.gle/KMKEKaFUD6ZX4UtY8
- **Panaversity:** https://panaversity.org
- **Zoom Presentations:** Sundays at 8:00 PM

---

**Built with ❤️ using Spec-Driven Development**

*"No code without specs. No specs without requirements. No requirements without understanding the problem."*
