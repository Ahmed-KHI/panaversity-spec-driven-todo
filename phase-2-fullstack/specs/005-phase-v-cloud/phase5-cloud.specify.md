# Phase V: Advanced Cloud Deployment - Specification

**Project:** Panaversity Hackathon II - Todo Application  
**Phase:** V - Advanced Cloud Deployment  
**Version:** 1.0  
**Date:** January 21, 2026  
**Status:** Draft  

---

## 1. Overview

### 1.1 Purpose
This specification defines the requirements for implementing advanced features and deploying the Todo application to production-grade Kubernetes clusters (Azure AKS/Google Cloud GKE/Oracle OKE) with event-driven architecture using Kafka and Dapr.

### 1.2 Scope
- Advanced Level features: Recurring Tasks, Due Dates & Reminders
- Intermediate Level features: Priorities, Tags, Search, Filter, Sort
- Event-driven architecture with Kafka
- Dapr distributed application runtime integration
- Local deployment to Minikube with full Dapr stack
- Production deployment to cloud Kubernetes with CI/CD pipeline

### 1.3 Success Criteria
- [ ] All Advanced and Intermediate features implemented and working
- [ ] Event-driven architecture with Kafka fully operational
- [ ] Dapr components integrated (Pub/Sub, State, Jobs API, Secrets, Service Invocation)
- [ ] Successfully deployed to Minikube locally
- [ ] Successfully deployed to cloud Kubernetes cluster
- [ ] CI/CD pipeline operational with GitHub Actions
- [ ] 90-second demo video completed
- [ ] All documentation updated

---

## 2. Functional Requirements

### 2.1 Advanced Features - Recurring Tasks

#### 2.1.1 User Story
**As a user**, I want to create recurring tasks (daily, weekly, monthly, yearly), so that I don't have to manually recreate repetitive tasks.

#### 2.1.2 Requirements
- **REQ-ADV-001**: User can set a task as recurring with frequency: daily, weekly, monthly, yearly
- **REQ-ADV-002**: User can specify recurrence patterns:
  - Daily: Every N days
  - Weekly: Specific days of week (e.g., Mon, Wed, Fri)
  - Monthly: Day of month (e.g., 1st, 15th) or relative (e.g., first Monday)
  - Yearly: Specific date (e.g., Jan 1)
- **REQ-ADV-003**: When a recurring task is marked complete, system automatically creates the next occurrence
- **REQ-ADV-004**: User can edit/delete recurring task series or single instance
- **REQ-ADV-005**: User can stop recurrence (mark as "no longer recurring")

#### 2.1.3 Acceptance Criteria
```gherkin
Given I create a task "Team Meeting"
And I set recurrence to "Weekly: Every Monday at 10:00 AM"
When I mark the task complete
Then a new instance of "Team Meeting" is created for next Monday at 10:00 AM
And the completed task is archived with completion date
```

#### 2.1.4 Event-Driven Implementation
- When task is marked complete, publish `task.completed` event to Kafka `task-events` topic
- Recurring Task Service consumes event and creates next occurrence
- New task created event published back to `task-events` topic

---

### 2.2 Advanced Features - Due Dates & Reminders

#### 2.2.1 User Story
**As a user**, I want to set due dates on tasks and receive reminders, so I never miss important deadlines.

#### 2.2.2 Requirements
- **REQ-ADV-006**: User can set a due date and time for any task
- **REQ-ADV-007**: User can configure reminder timing:
  - At time of due date
  - 15 minutes before
  - 1 hour before
  - 1 day before
  - 1 week before
  - Custom time
- **REQ-ADV-008**: User receives reminders via:
  - In-app notification
  - Email (optional)
  - Push notification (optional)
- **REQ-ADV-009**: Tasks are visually highlighted when approaching due date:
  - Green: Due in > 7 days
  - Yellow: Due in 1-7 days
  - Red: Due in < 1 day or overdue
- **REQ-ADV-010**: User can view overdue tasks in a dedicated filter

#### 2.2.3 Acceptance Criteria
```gherkin
Given I create a task "Submit Report"
And I set due date to "Jan 25, 2026 5:00 PM"
And I set reminder to "1 hour before"
When the time reaches "Jan 25, 2026 4:00 PM"
Then I receive a notification "Submit Report is due in 1 hour"
And the task is highlighted in yellow on my task list
```

#### 2.2.4 Event-Driven Implementation
- When task with due date is created/updated, publish `reminder.scheduled` event to Kafka `reminders` topic
- Use Dapr Jobs API to schedule exact-time reminder triggers
- Notification Service consumes reminder events and sends notifications
- No polling required - event-driven scheduling

---

### 2.3 Intermediate Features - Priorities

#### 2.3.1 User Story
**As a user**, I want to assign priorities to tasks, so I can focus on what's most important.

#### 2.3.2 Requirements
- **REQ-INT-001**: User can set task priority: Low, Medium, High, Urgent
- **REQ-INT-002**: Tasks display priority indicator (color/icon)
- **REQ-INT-003**: Default sort shows urgent tasks first
- **REQ-INT-004**: User can filter by priority level
- **REQ-INT-005**: Priority can be changed at any time

#### 2.3.3 Acceptance Criteria
```gherkin
Given I have multiple tasks with different priorities
When I view my task list with default sort
Then tasks are displayed in order: Urgent, High, Medium, Low
And each task shows a colored indicator for its priority
```

---

### 2.4 Intermediate Features - Tags

#### 2.4.1 User Story
**As a user**, I want to add tags to tasks, so I can organize them by categories or projects.

#### 2.4.2 Requirements
- **REQ-INT-006**: User can add multiple tags to a task
- **REQ-INT-007**: Tags are created dynamically (user types tag name)
- **REQ-INT-008**: User can filter tasks by one or more tags
- **REQ-INT-009**: User can see all existing tags with task counts
- **REQ-INT-010**: User can rename or delete tags (affects all tasks)

#### 2.4.3 Acceptance Criteria
```gherkin
Given I create a task "Review PR #123"
And I add tags: "work", "code-review", "urgent"
When I filter by tag "code-review"
Then I see all tasks tagged with "code-review"
And the count shows "5 tasks"
```

---

### 2.5 Intermediate Features - Search, Filter, Sort

#### 2.5.1 User Story
**As a user**, I want to search, filter, and sort tasks, so I can quickly find what I need.

#### 2.5.2 Requirements
- **REQ-INT-011**: User can search tasks by:
  - Title (partial match, case-insensitive)
  - Description (full-text search)
  - Tags
- **REQ-INT-012**: User can filter tasks by:
  - Status: Active, Completed, All
  - Priority: Low, Medium, High, Urgent
  - Tags (multiple selection)
  - Due date range
  - Overdue only
- **REQ-INT-013**: User can sort tasks by:
  - Due date (ascending/descending)
  - Priority (urgent first/low first)
  - Created date (newest/oldest)
  - Alphabetical (A-Z/Z-A)
- **REQ-INT-014**: Search and filters can be combined
- **REQ-INT-015**: Sort order is preserved in user session

#### 2.5.3 Acceptance Criteria
```gherkin
Given I have 50 tasks with various properties
When I search for "report"
And I filter by priority "High"
And I sort by due date ascending
Then I see only tasks containing "report" with High priority
And they are ordered by earliest due date first
```

---

## 3. Event-Driven Architecture Requirements

### 3.1 Kafka Topics

#### 3.1.1 Topic: `task-events`
**Purpose**: All task CRUD operations

**Event Types**:
- `task.created`
- `task.updated`
- `task.completed`
- `task.deleted`

**Event Schema**:
```json
{
  "event_type": "task.created",
  "event_id": "uuid",
  "timestamp": "2026-01-21T10:00:00Z",
  "user_id": "user-123",
  "task_id": 42,
  "task_data": {
    "id": 42,
    "title": "Task title",
    "description": "Task description",
    "status": "active",
    "priority": "high",
    "tags": ["work", "urgent"],
    "due_date": "2026-01-25T17:00:00Z",
    "recurrence": {
      "frequency": "weekly",
      "days": ["monday", "wednesday"]
    }
  }
}
```

#### 3.1.2 Topic: `reminders`
**Purpose**: Scheduled reminder triggers

**Event Types**:
- `reminder.scheduled`
- `reminder.due`
- `reminder.cancelled`

**Event Schema**:
```json
{
  "event_type": "reminder.due",
  "event_id": "uuid",
  "timestamp": "2026-01-25T16:00:00Z",
  "task_id": 42,
  "user_id": "user-123",
  "reminder_time": "2026-01-25T16:00:00Z",
  "due_time": "2026-01-25T17:00:00Z",
  "task_title": "Submit Report"
}
```

#### 3.1.3 Topic: `task-updates`
**Purpose**: Real-time sync across clients

**Event Types**:
- `task.sync`

**Event Schema**:
```json
{
  "event_type": "task.sync",
  "event_id": "uuid",
  "timestamp": "2026-01-21T10:00:00Z",
  "user_id": "user-123",
  "operation": "update",
  "task_id": 42,
  "changes": {
    "status": "completed"
  }
}
```

### 3.2 Kafka Service Requirements
- **REQ-KAFKA-001**: Use Redpanda Cloud (serverless free tier) OR self-hosted Strimzi on Kubernetes
- **REQ-KAFKA-002**: At least 3 topics: `task-events`, `reminders`, `task-updates`
- **REQ-KAFKA-003**: Retention period: 7 days minimum
- **REQ-KAFKA-004**: Replication factor: 3 for production, 1 for local development

---

## 4. Dapr Integration Requirements

### 4.1 Dapr Building Blocks

#### 4.1.1 Pub/Sub (Kafka Abstraction)
- **REQ-DAPR-001**: Backend publishes events via Dapr Pub/Sub API (not direct Kafka client)
- **REQ-DAPR-002**: Consumer services subscribe via Dapr
- **REQ-DAPR-003**: Component: `pubsub.kafka` with connection to Kafka cluster

#### 4.1.2 State Management
- **REQ-DAPR-004**: Use Dapr State API for conversation history storage
- **REQ-DAPR-005**: Component: `state.postgresql` connected to Neon DB
- **REQ-DAPR-006**: Alternative: `state.redis` for session cache

#### 4.1.3 Service Invocation
- **REQ-DAPR-007**: Frontend calls backend via Dapr Service Invocation API
- **REQ-DAPR-008**: Built-in service discovery, retries, and circuit breakers
- **REQ-DAPR-009**: mTLS enabled for service-to-service communication

#### 4.1.4 Scheduled Reminders (Jobs API or Bindings)

**Primary Approach: Dapr Jobs API (Recommended)**
- **REQ-DAPR-010**: Use Dapr Jobs API for exact-time reminder scheduling
- **REQ-DAPR-011**: No polling - jobs trigger at exact scheduled time
- **REQ-DAPR-012**: Job callback endpoint: `/api/jobs/trigger`
- **Benefits**: Exact timing (±1 second), no polling overhead, callback-based

**Alternative Approach: Dapr Cron Bindings**
- **REQ-DAPR-010-ALT**: Use Dapr Cron Bindings for scheduled reminder checks
- **REQ-DAPR-011-ALT**: Cron job runs every N minutes, checks database for due reminders
- **REQ-DAPR-012-ALT**: Binding input endpoint: `/api/cron/check-reminders`
- **Component**: `bindings.cron` with schedule expression

**Note**: The hackathon document mentions "Bindings (cron)" in requirements but recommends Jobs API in the detailed section. Both approaches satisfy the requirement. Jobs API is preferred for exact-time notifications; Bindings work for periodic checks.

#### 4.1.5 Secrets Management
- **REQ-DAPR-013**: Store API keys, DB credentials in Kubernetes Secrets
- **REQ-DAPR-014**: Access via Dapr Secrets API
- **REQ-DAPR-015**: Component: `secretstores.kubernetes`

### 4.2 Dapr Component Configuration
All Dapr components must be defined as YAML and applied to Kubernetes:
- `kafka-pubsub.yaml` - Pub/Sub component
- `statestore.yaml` - State management component
- `kubernetes-secrets.yaml` - Secrets component

---

## 5. Microservices Architecture Requirements

### 5.1 Service Breakdown

#### 5.1.1 Backend API Service (Existing + Enhanced)
**Responsibilities**:
- Handle REST API requests
- **Execute MCP tools (continue from Phase III)** - All chatbot MCP tools remain functional
- Publish events to Kafka (via Dapr)
- Handle Dapr job callbacks

**Existing MCP Tools (Maintained)**:
- `create_task` - Enhanced with new fields
- `list_tasks` - Enhanced with search/filter/sort
- `update_task` - Enhanced with new fields
- `delete_task` - Unchanged
- `complete_task` - Enhanced to trigger recurring task creation

**New Endpoints**:
- `POST /api/tasks` - Enhanced with recurrence, due dates, priorities, tags
- `GET /api/tasks/search` - Search tasks
- `GET /api/tasks/filter` - Filter tasks
- `POST /api/jobs/trigger` - Dapr job callback handler

#### 5.1.2 Recurring Task Service (New)
**Responsibilities**:
- Consume `task.completed` events
- Check if task is recurring
- Create next occurrence
- Publish `task.created` event

**Requirements**:
- **REQ-SVC-001**: Runs as separate deployment
- **REQ-SVC-002**: Subscribes to Kafka `task-events` topic via Dapr
- **REQ-SVC-003**: Stateless (can scale horizontally)

#### 5.1.3 Notification Service (New)
**Responsibilities**:
- Consume `reminder.due` events
- Send notifications (in-app, email, push)
- Track notification delivery status

**Requirements**:
- **REQ-SVC-004**: Runs as separate deployment
- **REQ-SVC-005**: Subscribes to Kafka `reminders` topic via Dapr
- **REQ-SVC-006**: Integrates with notification providers (email, push)

#### 5.1.4 Audit Service (Optional)
**Responsibilities**:
- Consume all `task-events`
- Maintain complete audit log
- Provide activity timeline

---

## 6. Deployment Requirements

### 6.1 Local Deployment (Minikube)

#### 6.1.1 Prerequisites
- **REQ-DEPLOY-001**: Minikube installed and running
- **REQ-DEPLOY-002**: kubectl configured
- **REQ-DEPLOY-003**: Dapr CLI installed
- **REQ-DEPLOY-004**: Helm installed

#### 6.1.2 Components
- **REQ-DEPLOY-005**: Kafka deployed via Strimzi operator OR Redpanda container
- **REQ-DEPLOY-006**: Dapr initialized on Kubernetes (`dapr init -k`)
- **REQ-DEPLOY-007**: All services deployed with Dapr sidecars
- **REQ-DEPLOY-008**: PostgreSQL (Neon DB external connection)

#### 6.1.3 Success Criteria
```bash
# All pods running
kubectl get pods -n todo-app
NAME                                READY   STATUS    RESTARTS   AGE
backend-66c7f5d9b4-8x9zq           2/2     Running   0          5m
frontend-7b8c9d6e5f-4k2l1          2/2     Running   0          5m
recurring-task-svc-5d7c8e9f6-3j1k  2/2     Running   0          5m
notification-svc-6e8d9f7g8-2h3m    2/2     Running   0          5m
kafka-0                            1/1     Running   0          10m
```

### 6.2 Cloud Deployment

#### 6.2.1 Cloud Provider Selection
- **Option A**: Azure Kubernetes Service (AKS) - $200 credit for 30 days
- **Option B**: Google Kubernetes Engine (GKE) - $300 credit for 90 days
- **Option C**: Oracle Kubernetes Engine (OKE) - Always free tier (4 OCPU, 24GB RAM)

**REQ-DEPLOY-009**: At least one cloud provider must be selected

#### 6.2.2 Kubernetes Cluster
- **REQ-DEPLOY-010**: Minimum 3 nodes
- **REQ-DEPLOY-011**: Node size: 2 vCPU, 4GB RAM per node (minimum)
- **REQ-DEPLOY-012**: kubectl configured with cluster credentials
- **REQ-DEPLOY-013**: Helm installed on cluster

#### 6.2.3 Managed Kafka
- **REQ-DEPLOY-014**: Redpanda Cloud (free serverless tier) OR self-hosted Strimzi
- **REQ-DEPLOY-015**: Bootstrap server endpoint configured in Dapr component
- **REQ-DEPLOY-016**: SASL/SSL authentication configured

#### 6.2.4 CI/CD Pipeline
- **REQ-DEPLOY-017**: GitHub Actions workflow for automated deployment
- **REQ-DEPLOY-018**: Docker images built and pushed to registry
- **REQ-DEPLOY-019**: Helm charts deployed to Kubernetes
- **REQ-DEPLOY-020**: Automated smoke tests post-deployment

#### 6.2.5 Monitoring & Logging
- **REQ-DEPLOY-021**: Application logs collected (stdout/stderr)
- **REQ-DEPLOY-022**: Metrics collected (CPU, memory, request rate)
- **REQ-DEPLOY-023**: Dapr dashboard accessible
- **REQ-DEPLOY-024**: Kafka metrics visible

---

## 7. Non-Functional Requirements

### 7.1 Performance
- **REQ-PERF-001**: Task search returns results in < 200ms for 1000 tasks
- **REQ-PERF-002**: Event publishing to Kafka in < 50ms (p95)
- **REQ-PERF-003**: Reminder triggers fire within 1 second of scheduled time

### 7.2 Scalability
- **REQ-SCALE-001**: Backend can scale horizontally (3+ replicas)
- **REQ-SCALE-002**: Consumer services can scale independently
- **REQ-SCALE-003**: Kafka handles 1000 events/second

### 7.3 Reliability
- **REQ-REL-001**: No data loss for events (Kafka retention + replication)
- **REQ-REL-002**: Failed consumers retry with exponential backoff
- **REQ-REL-003**: Circuit breakers prevent cascading failures

### 7.4 Security
- **REQ-SEC-001**: All service-to-service communication via Dapr mTLS
- **REQ-SEC-002**: Secrets stored in Kubernetes Secrets (not environment variables)
- **REQ-SEC-003**: Kafka connections use SASL/SSL
- **REQ-SEC-004**: API authentication with Better Auth (existing)

---

## 8. Acceptance Criteria Summary

### 8.1 Feature Completeness
- [ ] Recurring tasks work (daily, weekly, monthly, yearly)
- [ ] Due dates and reminders functional
- [ ] Priorities assigned and displayed
- [ ] Tags created and filtered
- [ ] Search returns accurate results
- [ ] Filter by status, priority, tags, due date
- [ ] Sort by due date, priority, created date, alphabetical

### 8.2 Event-Driven Architecture
- [ ] Kafka cluster operational with 3 topics
- [ ] Task operations publish events
- [ ] Recurring Task Service consumes and creates next occurrence
- [ ] Notification Service sends reminders
- [ ] Real-time sync across multiple clients

### 8.3 Dapr Integration
- [ ] Dapr sidecars running with all services
- [ ] Pub/Sub component configured and working
- [ ] State management via Dapr API
- [ ] Service invocation via Dapr
- [ ] Jobs API scheduling reminders
- [ ] Secrets accessed via Dapr Secrets API

### 8.4 Deployment
- [ ] Successfully deployed to Minikube locally
- [ ] Successfully deployed to cloud Kubernetes
- [ ] CI/CD pipeline builds and deploys automatically
- [ ] Monitoring and logging operational
- [ ] All services healthy and reachable

### 8.5 Documentation & Demo
- [ ] README.md updated with Phase 5 instructions
- [ ] Architecture diagrams included
- [ ] 90-second demo video recorded
- [ ] GitHub repository public with all code

---

## 9. Constraints & Assumptions

### 9.1 Technical Constraints
- Must use Kubernetes (Minikube locally, AKS/GKE/OKE for cloud)
- Must use Dapr for distributed application runtime
- Must use Kafka or Kafka-compatible streaming (Redpanda)
- Must maintain existing tech stack (Next.js, FastAPI, Neon DB)
- Must follow Spec-Driven Development (no manual coding)

### 9.2 Assumptions
- User has access to cloud provider credits (or uses Oracle free tier)
- User has Minikube and Docker installed locally
- Neon DB remains external (not migrated to Kubernetes)
- Better Auth authentication remains unchanged from Phase II/III

---

## 10. References

### 10.1 External Documentation
- [Dapr Documentation](https://docs.dapr.io/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Redpanda Cloud](https://redpanda.com/cloud)
- [Strimzi Operator](https://strimzi.io/)
- [Azure AKS](https://azure.microsoft.com/en-us/services/kubernetes-service/)
- [Google GKE](https://cloud.google.com/kubernetes-engine)
- [Oracle OKE](https://www.oracle.com/cloud/compute/container-engine-kubernetes.html)

### 10.2 Internal Documentation
- `constitution.md` - Project principles and constraints
- `AGENTS.md` - Agent behavior and workflow
- `specs/phase1-console-app.specify.md` - Phase I requirements
- `specs/002-phase-ii-full-stack/` - Phase II specifications
- `specs/003-phase-iii-chatbot/` - Phase III specifications
- `specs/004-phase-iv-kubernetes/` - Phase IV specifications

---

## 11. Approval

**Specification Status**: Draft  
**Requires Approval From**: Project Lead / Hackathon Judges  
**Approval Date**: _Pending_  

**Next Steps**:
1. Review and approve this specification
2. Create `phase5-cloud.plan.md` (HOW)
3. Create `phase5-cloud.tasks.md` (BREAKDOWN)
4. Begin implementation (CODE)

---

**Document Control**  
**Version History**:
- v1.0 (2026-01-21): Initial specification created

**Maintained By**: Claude Code via Spec-Driven Development  
**Last Updated**: 2026-01-21
