# Phase V: Advanced Cloud Deployment - Task Breakdown

**Project:** Panaversity Hackathon II - Todo Application  
**Phase:** V - Advanced Cloud Deployment  
**Version:** 1.0  
**Date:** January 21, 2026  
**Status:** Ready for Implementation  
**Based On**:
- `phase5-cloud.specify.md` v1.0 (WHAT)
- `phase5-cloud.plan.md` v1.0 (HOW)

---

## Task Overview

This phase is broken down into **5 major sections** with **50 atomic tasks**:

| Section | Task Count | Estimated Time |
|---------|-----------|----------------|
| A. Database & Models | 10 tasks | 4-6 hours |
| B. Backend Features | 12 tasks | 6-8 hours |
| C. Event-Driven Architecture | 10 tasks | 6-8 hours |
| D. Dapr Integration | 8 tasks | 4-6 hours |
| E. Kubernetes Deployment | 10 tasks | 8-10 hours |

**Total Estimated Time**: 28-38 hours  
**Recommended Approach**: Complete sections sequentially, test after each section

---

## Section A: Database Schema & Data Models

### T-A-001: Create Database Migration for New Columns
**Priority**: High  
**Depends On**: None  
**Estimated Time**: 30 minutes  

**Description**: Add new columns to existing `tasks` table for advanced features.

**Files to Modify**:
- Create: `phase-2-fullstack/backend/migrations/versions/XXX_add_advanced_task_fields.py`

**Acceptance Criteria**:
- [ ] Migration adds: `priority`, `due_date`, `reminder_time`, `is_recurring`, `recurrence_pattern`
- [ ] Indexes created for: `due_date`, `priority`, `is_recurring`
- [ ] Check constraint for priority enum
- [ ] Migration is reversible
- [ ] Test migration on local DB

**Implementation Notes**:
```sql
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) DEFAULT 'medium';
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP WITH TIME ZONE;
-- ... (see plan.md §2.1)
```

**References**:
- Specify: §2.1-2.5
- Plan: §2.1

---

### T-A-002: Create Tags Table Migration
**Priority**: High  
**Depends On**: None  
**Estimated Time**: 30 minutes  

**Description**: Create `tags` and `task_tags` junction table.

**Files to Modify**:
- Create: `phase-2-fullstack/backend/migrations/versions/XXX_create_tags_table.py`

**Acceptance Criteria**:
- [ ] `tags` table created with columns: id, name, color, created_at, created_by
- [ ] `task_tags` junction table created
- [ ] Foreign keys and indexes set up
- [ ] Unique constraint on tag name
- [ ] Migration reversible

**References**:
- Specify: §2.4
- Plan: §2.2

---

### T-A-003: Create Event Log Table Migration
**Priority**: Medium  
**Depends On**: None  
**Estimated Time**: 30 minutes  

**Description**: Create `event_log` table for audit trail.

**Files to Modify**:
- Create: `phase-2-fullstack/backend/migrations/versions/XXX_create_event_log.py`

**Acceptance Criteria**:
- [ ] Table created with proper schema
- [ ] Indexes on: timestamp, task_id, event_type
- [ ] JSONB payload column
- [ ] Migration reversible

**References**:
- Specify: §3.1
- Plan: §2.4

---

### T-A-004: Update Task Model with New Fields
**Priority**: High  
**Depends On**: T-A-001  
**Estimated Time**: 45 minutes  

**Description**: Update `Task` SQLModel class with new fields and relationships.

**Files to Modify**:
- `phase-2-fullstack/backend/src/models.py`

**Acceptance Criteria**:
- [ ] Priority enum added
- [ ] New fields added to Task model
- [ ] RecurrencePattern model created
- [ ] Property/setter for recurrence (JSONB)
- [ ] Tags relationship defined
- [ ] Type hints correct

**References**:
- Plan: §3.1

---

### T-A-005: Create Tag Model
**Priority**: High  
**Depends On**: T-A-002  
**Estimated Time**: 30 minutes  

**Description**: Create `Tag` and `TaskTag` SQLModel classes.

**Files to Modify**:
- `phase-2-fullstack/backend/src/models.py`

**Acceptance Criteria**:
- [ ] Tag model with all fields
- [ ] TaskTag link model
- [ ] Relationship to Task model
- [ ] Validation for tag name (max length, allowed chars)

**References**:
- Plan: §3.1

---

### T-A-006: Create EventLog Model
**Priority**: Medium  
**Depends On**: T-A-003  
**Estimated Time**: 30 minutes  

**Description**: Create `EventLog` SQLModel class.

**Files to Modify**:
- `phase-2-fullstack/backend/src/models.py`

**Acceptance Criteria**:
- [ ] EventLog model with all fields
- [ ] JSON payload handling
- [ ] Relationships to Task and User

**References**:
- Plan: §3.1

---

### T-A-007: Create Pydantic Schemas for Request/Response
**Priority**: High  
**Depends On**: T-A-004, T-A-005  
**Estimated Time**: 45 minutes  

**Description**: Create request/response schemas for new API endpoints.

**Files to Modify**:
- Create: `phase-2-fullstack/backend/src/schemas.py` (if not exists, or add to models.py)

**Acceptance Criteria**:
- [ ] TaskCreate schema with all new fields
- [ ] TaskUpdate schema
- [ ] TaskResponse schema
- [ ] TagCreate/Response schemas
- [ ] SearchFilters schema
- [ ] RecurrencePatternCreate schema

---

### T-A-008: Run Migrations on Development Database
**Priority**: High  
**Depends On**: T-A-001, T-A-002, T-A-003  
**Estimated Time**: 15 minutes  

**Description**: Apply all migrations to Neon development database.

**Commands**:
```bash
cd phase-2-fullstack/backend
alembic upgrade head
```

**Acceptance Criteria**:
- [ ] All migrations applied successfully
- [ ] Tables created in database
- [ ] Verify schema with `psql` or DB client

---

### T-A-009: Seed Test Data with New Fields
**Priority**: Medium  
**Depends On**: T-A-008  
**Estimated Time**: 30 minutes  

**Description**: Create seed script with sample data for testing.

**Files to Modify**:
- Create: `phase-2-fullstack/backend/src/seed_data.py`

**Acceptance Criteria**:
- [ ] Script creates tasks with priorities
- [ ] Script creates tasks with due dates
- [ ] Script creates recurring tasks
- [ ] Script creates tags
- [ ] Script associates tags with tasks

---

### T-A-010: Validate Database Schema
**Priority**: High  
**Depends On**: T-A-009  
**Estimated Time**: 30 minutes  

**Description**: Write tests to validate database schema and relationships.

**Files to Modify**:
- Create: `phase-2-fullstack/backend/tests/test_models.py`

**Acceptance Criteria**:
- [ ] Test task creation with new fields
- [ ] Test tag creation and association
- [ ] Test recurrence pattern JSONB serialization
- [ ] Test foreign key constraints
- [ ] All tests pass

---

## Section B: Backend API Features

### T-B-001: Enhance Create Task Endpoint
**Priority**: High  
**Depends On**: T-A-004, T-A-005  
**Estimated Time**: 1 hour  

**Description**: Update POST /api/tasks to accept new fields.

**Files to Modify**:
- `phase-2-fullstack/backend/src/api/tasks.py`

**Acceptance Criteria**:
- [ ] Accepts priority, due_date, reminder_time, is_recurring, recurrence_pattern, tags
- [ ] Validates recurrence pattern
- [ ] Creates/associates tags
- [ ] Returns enriched task response
- [ ] Error handling for invalid data

**References**:
- Specify: REQ-ADV-001 to REQ-INT-010
- Plan: §3.3

---

### T-B-002: Implement Search Tasks Endpoint
**Priority**: High  
**Depends On**: T-A-004  
**Estimated Time**: 1 hour  

**Description**: Create GET /api/tasks/search endpoint.

**Files to Modify**:
- `phase-2-fullstack/backend/src/api/tasks.py`

**Acceptance Criteria**:
- [ ] Search by title (partial, case-insensitive)
- [ ] Search by description
- [ ] Search by tags
- [ ] Returns matching tasks
- [ ] Pagination support
- [ ] Performance: < 200ms for 1000 tasks

**References**:
- Specify: REQ-INT-011
- Plan: §3.3

---

### T-B-003: Implement Filter Tasks Endpoint
**Priority**: High  
**Depends On**: T-A-004, T-A-005  
**Estimated Time**: 1.5 hours  

**Description**: Create GET /api/tasks/filter endpoint with multiple filters.

**Files to Modify**:
- `phase-2-fullstack/backend/src/api/tasks.py`

**Acceptance Criteria**:
- [ ] Filter by status (active, completed)
- [ ] Filter by priority
- [ ] Filter by tags (multiple)
- [ ] Filter by due date range
- [ ] Filter overdue tasks only
- [ ] Combine filters (AND logic)
- [ ] Efficient SQL queries (use indexes)

**References**:
- Specify: REQ-INT-012
- Plan: §3.3

---

### T-B-004: Implement Sort Tasks Functionality
**Priority**: Medium  
**Depends On**: T-B-002, T-B-003  
**Estimated Time**: 45 minutes  

**Description**: Add sorting to search and filter endpoints.

**Files to Modify**:
- `phase-2-fullstack/backend/src/api/tasks.py`

**Acceptance Criteria**:
- [ ] Sort by due_date (asc/desc)
- [ ] Sort by priority (urgent first / low first)
- [ ] Sort by created_at (newest/oldest)
- [ ] Sort by title (A-Z / Z-A)
- [ ] Default sort: priority desc, due_date asc

**References**:
- Specify: REQ-INT-013
- Plan: §3.3

---

### T-B-005: Implement Tag CRUD Endpoints
**Priority**: Medium  
**Depends On**: T-A-005  
**Estimated Time**: 1 hour  

**Description**: Create endpoints for tag management.

**Files to Modify**:
- Create: `phase-2-fullstack/backend/src/api/tags.py`

**Acceptance Criteria**:
- [ ] GET /api/tags - List all tags with task counts
- [ ] POST /api/tags - Create new tag
- [ ] PATCH /api/tags/{id} - Update tag (rename, change color)
- [ ] DELETE /api/tags/{id} - Delete tag (removes from all tasks)

**References**:
- Specify: REQ-INT-006 to REQ-INT-010

---

### T-B-006: Implement Complete Task Endpoint
**Priority**: High  
**Depends On**: T-A-004  
**Estimated Time**: 45 minutes  

**Description**: Update PATCH /api/tasks/{id}/complete to handle recurring tasks.

**Files to Modify**:
- `phase-2-fullstack/backend/src/api/tasks.py`

**Acceptance Criteria**:
- [ ] Mark task as completed
- [ ] Update updated_at timestamp
- [ ] Check if task is recurring (don't create next occurrence here)
- [ ] Return updated task

**References**:
- Specify: §2.1.3

---

### T-B-007: Implement Due Date Validation
**Priority**: Medium  
**Depends On**: T-B-001  
**Estimated Time**: 30 minutes  

**Description**: Add validation for due dates and reminder times.

**Files to Modify**:
- `phase-2-fullstack/backend/src/api/tasks.py`
- `phase-2-fullstack/backend/src/validators.py` (create if needed)

**Acceptance Criteria**:
- [ ] Due date cannot be in the past
- [ ] Reminder time must be before due date
- [ ] Reminder time cannot be in the past
- [ ] Return clear validation errors

---

### T-B-008: Implement Recurrence Pattern Validation
**Priority**: High  
**Depends On**: T-B-001  
**Estimated Time**: 1 hour  

**Description**: Validate recurrence pattern data.

**Files to Modify**:
- `phase-2-fullstack/backend/src/validators.py`

**Acceptance Criteria**:
- [ ] Validate frequency enum
- [ ] Validate interval > 0
- [ ] For weekly: days_of_week required (0-6)
- [ ] For monthly: day_of_month (1-31)
- [ ] For yearly: month (1-12)
- [ ] End date must be after first occurrence
- [ ] Occurrences must be > 0 if specified

**References**:
- Plan: §2.3

---

### T-B-009: Update Get Tasks Endpoint
**Priority**: Medium  
**Depends On**: T-A-004, T-A-005  
**Estimated Time**: 30 minutes  

**Description**: Enhance GET /api/tasks to include new fields and relationships.

**Files to Modify**:
- `phase-2-fullstack/backend/src/api/tasks.py`

**Acceptance Criteria**:
- [ ] Return tasks with priority, due_date, tags
- [ ] Include recurrence pattern if is_recurring
- [ ] Eager load tags (avoid N+1 queries)
- [ ] Apply default sorting

---

### T-B-010: Implement Task Statistics Endpoint
**Priority**: Low  
**Depends On**: T-A-004  
**Estimated Time**: 45 minutes  

**Description**: Create GET /api/tasks/stats for dashboard.

**Files to Modify**:
- Create: `phase-2-fullstack/backend/src/api/stats.py`

**Acceptance Criteria**:
- [ ] Count active tasks
- [ ] Count completed tasks
- [ ] Count overdue tasks
- [ ] Count by priority
- [ ] Count recurring tasks
- [ ] Upcoming due dates (next 7 days)

---

### T-B-011: Write Unit Tests for New Endpoints
**Priority**: High  
**Depends On**: T-B-001 to T-B-010  
**Estimated Time**: 2 hours  

**Description**: Write comprehensive tests for all new endpoints.

**Files to Modify**:
- Create: `phase-2-fullstack/backend/tests/test_tasks_advanced.py`
- Create: `phase-2-fullstack/backend/tests/test_tags.py`

**Acceptance Criteria**:
- [ ] Test create task with all new fields
- [ ] Test search functionality
- [ ] Test filter combinations
- [ ] Test sort orders
- [ ] Test tag CRUD
- [ ] Test validation errors
- [ ] Test edge cases
- [ ] 80%+ code coverage

---

### T-B-012: Update OpenAPI Documentation
**Priority**: Low  
**Depends On**: T-B-001 to T-B-010  
**Estimated Time**: 30 minutes  

**Description**: Update API documentation with new endpoints and schemas.

**Files to Modify**:
- `phase-2-fullstack/backend/src/main.py` (FastAPI auto-generates, add examples)

**Acceptance Criteria**:
- [ ] All new endpoints documented
- [ ] Request/response examples added
- [ ] Schema descriptions clear
- [ ] Swagger UI accessible at /docs

---

## Section C: Event-Driven Architecture & Kafka

### T-C-001: Create Event Publisher Service
**Priority**: High  
**Depends On**: None  
**Estimated Time**: 1 hour  

**Description**: Create service to publish events to Kafka via Dapr.

**Files to Modify**:
- Create: `phase-2-fullstack/backend/src/services/event_publisher.py`

**Acceptance Criteria**:
- [ ] DaprEventPublisher class
- [ ] publish() method using Dapr Pub/Sub API
- [ ] Event schema validation
- [ ] UUID event_id generation
- [ ] Timestamp in ISO format
- [ ] Error handling and retries
- [ ] Logging

**References**:
- Plan: §3.2

---

### T-C-002: Integrate Event Publishing in Create Task
**Priority**: High  
**Depends On**: T-C-001, T-B-001  
**Estimated Time**: 30 minutes  

**Description**: Publish `task.created` event when task is created.

**Files to Modify**:
- `phase-2-fullstack/backend/src/api/tasks.py`

**Acceptance Criteria**:
- [ ] After task creation, publish event to `task-events` topic
- [ ] Event type: `task.created`
- [ ] Include full task data
- [ ] Async/await properly handled
- [ ] Transaction safety (publish after commit)

**References**:
- Specify: §3.1.1
- Plan: §3.2

---

### T-C-003: Integrate Event Publishing in Update Task
**Priority**: High  
**Depends On**: T-C-001  
**Estimated Time**: 30 minutes  

**Description**: Publish `task.updated` event when task is updated.

**Files to Modify**:
- `phase-2-fullstack/backend/src/api/tasks.py`

**Acceptance Criteria**:
- [ ] Publish event to `task-events` topic
- [ ] Event type: `task.updated`
- [ ] Include updated task data

---

### T-C-004: Integrate Event Publishing in Complete Task
**Priority**: High  
**Depends On**: T-C-001, T-B-006  
**Estimated Time**: 30 minutes  

**Description**: Publish `task.completed` event when task is completed.

**Files to Modify**:
- `phase-2-fullstack/backend/src/api/tasks.py`

**Acceptance Criteria**:
- [ ] Publish event to `task-events` topic
- [ ] Event type: `task.completed`
- [ ] This triggers recurring task service

**References**:
- Specify: §2.1.3

---

### T-C-005: Create Recurring Task Consumer Service
**Priority**: High  
**Depends On**: None  
**Estimated Time**: 2 hours  

**Description**: Create microservice to consume task.completed events and create next occurrence.

**Files to Modify**:
- Create: `phase-5-services/recurring-task/main.py`
- Create: `phase-5-services/recurring-task/Dockerfile`
- Create: `phase-5-services/recurring-task/requirements.txt`

**Acceptance Criteria**:
- [ ] FastAPI app with /dapr/subscribe endpoint
- [ ] /events POST handler
- [ ] calculate_next_occurrence() logic
- [ ] Calls backend API to create next task
- [ ] Handles daily, weekly, monthly, yearly frequencies
- [ ] Respects end_date and occurrences limits
- [ ] Error handling and logging

**References**:
- Plan: §4.1

---

### T-C-006: Implement Reminder Scheduler Service
**Priority**: High  
**Depends On**: T-C-001  
**Estimated Time**: 1.5 hours  

**Description**: Create service to schedule reminders using Dapr Jobs API.

**Files to Modify**:
- Create: `phase-2-fullstack/backend/src/services/reminder_scheduler.py`

**Acceptance Criteria**:
- [ ] schedule_reminder() function
- [ ] Uses Dapr Jobs API (POST /v1.0-alpha1/jobs/{job-name})
- [ ] Schedules job at reminder_time
- [ ] Job data includes task_id, user_id, task_title
- [ ] Cancel/update job when task updated/deleted

**References**:
- Plan: §3.4

---

### T-C-007: Implement Job Trigger Endpoint
**Priority**: High  
**Depends On**: T-C-006  
**Estimated Time**: 45 minutes  

**Description**: Create endpoint for Dapr to call when job fires.

**Files to Modify**:
- `phase-2-fullstack/backend/src/api/jobs.py` (create)

**Acceptance Criteria**:
- [ ] POST /api/jobs/trigger endpoint
- [ ] Receives job data from Dapr
- [ ] Publishes `reminder.due` event to `reminders` topic
- [ ] Returns {"status": "SUCCESS"}
- [ ] Error handling

**References**:
- Plan: §3.4

---

### T-C-008: Create Notification Service
**Priority**: Medium  
**Depends On**: None  
**Estimated Time**: 2 hours  

**Description**: Create microservice to consume reminder events and send notifications.

**Files to Modify**:
- Create: `phase-5-services/notification/main.py`
- Create: `phase-5-services/notification/Dockerfile`
- Create: `phase-5-services/notification/requirements.txt`

**Acceptance Criteria**:
- [ ] FastAPI app with /dapr/subscribe endpoint
- [ ] Consumes from `reminders` topic
- [ ] send_notification() method
- [ ] In-app notification storage (Dapr State API)
- [ ] Optional: Email via SendGrid
- [ ] Optional: Push notification via Firebase
- [ ] Logging

**References**:
- Plan: §4.2

---

### T-C-009: Integrate Reminder Scheduling in Create/Update Task
**Priority**: High  
**Depends On**: T-C-006, T-B-001  
**Estimated Time**: 45 minutes  

**Description**: Schedule reminder when task with due_date is created/updated.

**Files to Modify**:
- `phase-2-fullstack/backend/src/api/tasks.py`

**Acceptance Criteria**:
- [ ] After task creation/update, check if due_date and reminder_time set
- [ ] Call schedule_reminder() if both present
- [ ] Update reminder if task updated
- [ ] Cancel reminder if task completed/deleted

---

### T-C-010: Write Integration Tests for Event Flow
**Priority**: High  
**Depends On**: T-C-001 to T-C-009  
**Estimated Time**: 1.5 hours  

**Description**: Test end-to-end event flow.

**Files to Modify**:
- Create: `phase-2-fullstack/backend/tests/test_events.py`

**Acceptance Criteria**:
- [ ] Mock Dapr Pub/Sub API
- [ ] Test task.created event published
- [ ] Test task.completed event published
- [ ] Test event schema validation
- [ ] Test error handling

---

## Section D: Dapr Integration

### T-D-001: Create Kafka Pub/Sub Dapr Component
**Priority**: High  
**Depends On**: None  
**Estimated Time**: 30 minutes  

**Description**: Create Dapr component for Kafka Pub/Sub.

**Files to Modify**:
- Create: `phase-5-dapr/components/kafka-pubsub.yaml`

**Acceptance Criteria**:
- [ ] Component name: kafka-pubsub
- [ ] Type: pubsub.kafka
- [ ] Broker metadata (for local: kafka:9092, for cloud: Redpanda URL)
- [ ] Consumer group: todo-service
- [ ] SASL config for production (secretKeyRef)

**References**:
- Plan: §5.1.1

---

### T-D-002: Create PostgreSQL State Store Component
**Priority**: Medium  
**Depends On**: None  
**Estimated Time**: 30 minutes  

**Description**: Create Dapr component for state management.

**Files to Modify**:
- Create: `phase-5-dapr/components/statestore.yaml`

**Acceptance Criteria**:
- [ ] Component name: statestore
- [ ] Type: state.postgresql
- [ ] Connection string from secret
- [ ] Table name: dapr_state

**References**:
- Plan: §5.1.2

---

### T-D-003: Create Kubernetes Secrets Store Component
**Priority**: Low  
**Depends On**: None  
**Estimated Time**: 20 minutes  

**Description**: Create Dapr component for secrets.

**Files to Modify**:
- Create: `phase-5-dapr/components/kubernetes-secrets.yaml`

**Acceptance Criteria**:
- [ ] Component name: kubernetes-secrets
- [ ] Type: secretstores.kubernetes

**References**:
- Plan: §5.1.3

---

### T-D-004: Create Kubernetes Secrets Manifests
**Priority**: High  
**Depends On**: None  
**Estimated Time**: 30 minutes  

**Description**: Create K8s secrets for database, Kafka, API keys.

**Files to Modify**:
- Create: `phase-5-kubernetes/secrets.yaml`

**Acceptance Criteria**:
- [ ] postgres-secrets (connection-string)
- [ ] kafka-secrets (bootstrap-servers, sasl-username, sasl-password)
- [ ] app-secrets (openai-api-key, better-auth-secret, sendgrid-api-key)
- [ ] Base64 encoded values
- [ ] Namespace: todo-app

**References**:
- Plan: §5.2

---

### T-D-005: Update Backend Dockerfile for Dapr
**Priority**: Medium  
**Depends On**: None  
**Estimated Time**: 20 minutes  

**Description**: Ensure backend Docker image works with Dapr sidecar.

**Files to Modify**:
- `phase-2-fullstack/backend/Dockerfile`

**Acceptance Criteria**:
- [ ] Uses Python 3.11+
- [ ] Installs all dependencies
- [ ] Exposes port 8000
- [ ] Healthcheck endpoint
- [ ] Runs Uvicorn with host 0.0.0.0

---

### T-D-006: Update Backend to Use Dapr URLs
**Priority**: High  
**Depends On**: T-C-001  
**Estimated Time**: 30 minutes  

**Description**: Configure event publisher to use Dapr sidecar URL.

**Files to Modify**:
- `phase-2-fullstack/backend/src/services/event_publisher.py`
- `phase-2-fullstack/backend/src/config.py`

**Acceptance Criteria**:
- [ ] DAPR_HTTP_ENDPOINT env var (default: http://localhost:3500)
- [ ] Publisher uses Dapr URL
- [ ] Works both locally (Dapr CLI) and in K8s

---

### T-D-007: Test Backend with Dapr Locally
**Priority**: High  
**Depends On**: T-D-001, T-D-006  
**Estimated Time**: 1 hour  

**Description**: Run backend with Dapr CLI and test event publishing.

**Commands**:
```bash
dapr run --app-id backend-service --app-port 8000 --dapr-http-port 3500 \
  --resources-path ./phase-5-dapr/components \
  -- uvicorn src.main:app --host 0.0.0.0 --port 8000
```

**Acceptance Criteria**:
- [ ] Backend starts with Dapr sidecar
- [ ] Create task publishes event to Kafka
- [ ] Verify event in Kafka topic
- [ ] No errors in logs

---

### T-D-008: Document Dapr Setup Instructions
**Priority**: Low  
**Depends On**: T-D-001 to T-D-007  
**Estimated Time**: 30 minutes  

**Description**: Create guide for running services with Dapr.

**Files to Modify**:
- Create: `phase-5-dapr/README.md`

**Acceptance Criteria**:
- [ ] Installation instructions
- [ ] Local development setup
- [ ] Component explanations
- [ ] Troubleshooting tips

---

## Section E: Kubernetes Deployment

### T-E-001: Create Namespace and RBAC
**Priority**: High  
**Depends On**: None  
**Estimated Time**: 20 minutes  

**Description**: Create Kubernetes namespace and service accounts.

**Files to Modify**:
- Create: `phase-5-kubernetes/namespace.yaml`
- Create: `phase-5-kubernetes/rbac.yaml`

**Acceptance Criteria**:
- [ ] Namespace: todo-app
- [ ] Service account for each service
- [ ] RBAC roles if needed

---

### T-E-002: Create Backend Deployment Manifest
**Priority**: High  
**Depends On**: T-D-005  
**Estimated Time**: 45 minutes  

**Description**: Create K8s deployment for backend with Dapr annotations.

**Files to Modify**:
- Create: `phase-5-kubernetes/backend-deployment.yaml`

**Acceptance Criteria**:
- [ ] Deployment with 3 replicas
- [ ] Dapr annotations (app-id, app-port, enabled)
- [ ] Environment variables from secrets
- [ ] Resource requests/limits
- [ ] Liveness/readiness probes
- [ ] Service (ClusterIP, port 8000)

**References**:
- Plan: §6.1

---

### T-E-003: Create Frontend Deployment Manifest
**Priority**: High  
**Depends On**: None  
**Estimated Time**: 30 minutes  

**Description**: Create K8s deployment for frontend with Dapr.

**Files to Modify**:
- Create: `phase-5-kubernetes/frontend-deployment.yaml`

**Acceptance Criteria**:
- [ ] Deployment with 3 replicas
- [ ] Dapr annotations
- [ ] Environment variables
- [ ] Service (LoadBalancer, port 3000)

**References**:
- Plan: §6.2

---

### T-E-004: Create Recurring Task Service Deployment
**Priority**: High  
**Depends On**: T-C-005  
**Estimated Time**: 30 minutes  

**Description**: Create K8s deployment for recurring task consumer.

**Files to Modify**:
- Create: `phase-5-kubernetes/recurring-task-deployment.yaml`

**Acceptance Criteria**:
- [ ] Deployment with 2 replicas
- [ ] Dapr annotations (subscribes to task-events)
- [ ] Resource limits

**References**:
- Plan: §6.3

---

### T-E-005: Create Notification Service Deployment
**Priority**: Medium  
**Depends On**: T-C-008  
**Estimated Time**: 30 minutes  

**Description**: Create K8s deployment for notification consumer.

**Files to Modify**:
- Create: `phase-5-kubernetes/notification-deployment.yaml`

**Acceptance Criteria**:
- [ ] Deployment with 2 replicas
- [ ] Dapr annotations (subscribes to reminders)

**References**:
- Plan: §6.4

---

### T-E-006: Create Kafka Deployment (Strimzi)
**Priority**: High  
**Depends On**: None  
**Estimated Time**: 45 minutes  

**Description**: Create Kafka cluster using Strimzi operator.

**Files to Modify**:
- Create: `phase-5-kafka/strimzi-kafka-cluster.yaml`
- Create: `phase-5-kafka/topics.yaml`

**Acceptance Criteria**:
- [ ] Kafka cluster with 3 brokers (production) or 1 (local)
- [ ] Zookeeper replicas
- [ ] Persistent storage
- [ ] Topics: task-events, reminders, task-updates
- [ ] Retention: 7 days

**References**:
- Plan: §7.1

---

### T-E-007: Create Deployment Scripts
**Priority**: Medium  
**Depends On**: T-E-001 to T-E-006  
**Estimated Time**: 1 hour  

**Description**: Create bash/PowerShell scripts for deployment.

**Files to Modify**:
- Create: `phase-5-scripts/deploy-minikube.sh`
- Create: `phase-5-scripts/deploy-minikube.ps1`
- Create: `phase-5-scripts/deploy-cloud.sh`

**Acceptance Criteria**:
- [ ] Script installs Dapr (`dapr init -k`)
- [ ] Script installs Strimzi operator
- [ ] Script deploys Kafka cluster
- [ ] Script applies secrets
- [ ] Script applies Dapr components
- [ ] Script deploys all services
- [ ] Script waits for rollout completion
- [ ] Script prints access URLs

---

### T-E-008: Test Deployment on Minikube
**Priority**: High  
**Depends On**: T-E-007  
**Estimated Time**: 2 hours  

**Description**: Deploy entire stack to Minikube and test.

**Steps**:
1. Start Minikube
2. Run deployment script
3. Port forward to frontend
4. Test all features
5. Verify events in Kafka
6. Check Dapr dashboard

**Acceptance Criteria**:
- [ ] All pods running
- [ ] Frontend accessible
- [ ] Create task works
- [ ] Search/filter works
- [ ] Complete recurring task → next occurrence created
- [ ] Reminder scheduled (check Dapr logs)
- [ ] Events visible in Kafka

---

### T-E-009: Create CI/CD Pipeline (GitHub Actions)
**Priority**: Medium  
**Depends On**: T-E-002 to T-E-005  
**Estimated Time**: 2 hours  

**Description**: Set up GitHub Actions for automated deployment.

**Files to Modify**:
- Create: `.github/workflows/deploy-phase5.yml`

**Acceptance Criteria**:
- [ ] Triggers on push to main (phase-5 paths)
- [ ] Builds Docker images for all services
- [ ] Pushes to GitHub Container Registry
- [ ] Deploys to Kubernetes (Minikube or cloud)
- [ ] Runs smoke tests
- [ ] Sends notification on failure

**References**:
- Plan: §8.1

---

### T-E-010: Deploy to Cloud (AKS/GKE/OKE)
**Priority**: High  
**Depends On**: T-E-007, T-E-009  
**Estimated Time**: 3 hours  

**Description**: Deploy to production cloud Kubernetes cluster.

**Steps**:
1. Choose cloud provider (Azure/GCP/Oracle)
2. Create Kubernetes cluster
3. Configure kubectl
4. Set up Redpanda Cloud OR deploy Strimzi
5. Update secrets with production values
6. Update Dapr components with production Kafka URL
7. Push images to registry
8. Run deployment script
9. Expose frontend via LoadBalancer
10. Test production deployment

**Acceptance Criteria**:
- [ ] Cluster created and accessible
- [ ] Kafka cluster operational (Redpanda or Strimzi)
- [ ] All services deployed
- [ ] Frontend accessible via public IP/domain
- [ ] All features working
- [ ] Monitoring enabled
- [ ] CI/CD pipeline successful

**References**:
- Plan: §10.2

---

## Section F: Frontend Integration (Optional Enhancement)

These tasks are optional but recommended for better UX:

### T-F-001: Update Task Form with Advanced Fields
**Priority**: Medium  
**Estimated Time**: 1.5 hours  

**Description**: Add priority, due date, recurrence, tags to task creation form.

**Files to Modify**:
- `phase-2-fullstack/frontend/components/TaskForm.tsx`

**Acceptance Criteria**:
- [ ] Priority dropdown (Low, Medium, High, Urgent)
- [ ] Due date picker (date + time)
- [ ] Reminder time picker
- [ ] Recurrence toggle and pattern selector
- [ ] Tag input (multi-select or chips)

---

### T-F-002: Update Task List to Display New Fields
**Priority**: Medium  
**Estimated Time**: 1 hour  

**Description**: Show priority badge, due date, tags on task cards.

**Files to Modify**:
- `phase-2-fullstack/frontend/components/TaskCard.tsx`

**Acceptance Criteria**:
- [ ] Priority indicator (colored badge)
- [ ] Due date with countdown
- [ ] Overdue indicator (red)
- [ ] Tags as chips
- [ ] Recurring icon

---

### T-F-003: Implement Search Bar
**Priority**: Medium  
**Estimated Time**: 45 minutes  

**Description**: Add search input to filter tasks.

**Files to Modify**:
- `phase-2-fullstack/frontend/components/SearchBar.tsx`

**Acceptance Criteria**:
- [ ] Search input with debounce
- [ ] Calls /api/tasks/search
- [ ] Updates task list

---

### T-F-004: Implement Filter Panel
**Priority**: Medium  
**Estimated Time**: 1.5 hours  

**Description**: Add sidebar/dropdown with filters.

**Files to Modify**:
- `phase-2-fullstack/frontend/components/FilterPanel.tsx`

**Acceptance Criteria**:
- [ ] Status filter (Active, Completed, All)
- [ ] Priority filter (checkboxes)
- [ ] Tag filter (multi-select)
- [ ] Due date range picker
- [ ] Overdue toggle
- [ ] Apply filters button

---

### T-F-005: Implement Sort Dropdown
**Priority**: Low  
**Estimated Time**: 30 minutes  

**Description**: Add sort dropdown to task list.

**Files to Modify**:
- `phase-2-fullstack/frontend/components/SortDropdown.tsx`

**Acceptance Criteria**:
- [ ] Sort options: Due Date, Priority, Created Date, Alphabetical
- [ ] Ascending/descending toggle

---

## Section G: Documentation & Demo

### T-G-001: Update README with Phase 5 Instructions
**Priority**: High  
**Depends On**: T-E-010  
**Estimated Time**: 1 hour  

**Description**: Add Phase 5 section to main README.

**Files to Modify**:
- `README.md`

**Acceptance Criteria**:
- [ ] Architecture diagram
- [ ] Features list
- [ ] Local deployment instructions (Minikube)
- [ ] Cloud deployment instructions
- [ ] Environment variables documentation
- [ ] Troubleshooting section

---

### T-G-002: Create Architecture Diagrams
**Priority**: Medium  
**Depends On**: None  
**Estimated Time**: 1 hour  

**Description**: Create visual diagrams for architecture.

**Files to Modify**:
- Create: `docs/architecture/phase5-architecture.png`
- Create: `docs/architecture/event-flow.png`
- Create: `docs/architecture/dapr-components.png`

**Tools**: Excalidraw, Draw.io, Mermaid

---

### T-G-003: Create Demo Video Script
**Priority**: High  
**Depends On**: T-E-010  
**Estimated Time**: 30 minutes  

**Description**: Write script for 90-second demo video.

**Files to Modify**:
- Create: `docs/DEMO-SCRIPT.md`

**Script Structure**:
1. **Intro (5s)**: "Phase 5: Advanced Cloud Deployment"
2. **Features (40s)**:
   - Create recurring task (weekly)
   - Set priority and tags
   - Set due date and reminder
   - Search and filter
   - Complete recurring task → show next occurrence
3. **Architecture (20s)**:
   - Show Kafka dashboard
   - Show Dapr dashboard
   - Show Kubernetes pods
4. **Deployment (20s)**:
   - Show CI/CD pipeline (GitHub Actions)
   - Show cloud cluster
   - Show public URL
5. **Outro (5s)**: "Thank you!"

---

### T-G-004: Record Demo Video
**Priority**: High  
**Depends On**: T-G-003  
**Estimated Time**: 1 hour (including retakes)  

**Description**: Record and edit demo video (max 90 seconds).

**Tools**: OBS Studio, Loom, QuickTime

**Acceptance Criteria**:
- [ ] 90 seconds or less
- [ ] High quality (1080p)
- [ ] Clear audio
- [ ] Shows all features
- [ ] Shows architecture
- [ ] Shows deployment

---

### T-G-005: Create SUBMISSION.md
**Priority**: High  
**Depends On**: T-G-001, T-G-004  
**Estimated Time**: 45 minutes  

**Description**: Create submission document with all required information.

**Files to Modify**:
- Create: `PHASE5-SUBMISSION.md`

**Acceptance Criteria**:
- [ ] GitHub repository URL
- [ ] Deployed application URLs (frontend, backend)
- [ ] Demo video link (YouTube, Google Drive)
- [ ] WhatsApp number for presentation
- [ ] Features implemented checklist
- [ ] Technology stack
- [ ] Architecture overview
- [ ] Deployment instructions

---

## Task Dependencies Graph

```
Database & Models (A):
  A-001 → A-004 → A-007 → A-009
  A-002 → A-005 ↗      ↗
  A-003 → A-006 ↗
  A-001,2,3 → A-008 → A-010

Backend Features (B):
  A-004,5 → B-001 → B-002 → B-004
                  → B-003 ↗
          → B-006
          → B-007
          → B-008
          → B-009
  A-005 → B-005
  A-004 → B-010
  B-001..010 → B-011 → B-012

Events & Kafka (C):
  C-001 → C-002, C-003, C-004
  C-001, B-001 → C-009
  C-005 (independent)
  C-001 → C-006 → C-007
  C-008 (independent)
  C-001..009 → C-010

Dapr (D):
  D-001..004 (independent)
  D-005 (independent)
  C-001 → D-006
  D-001, D-006 → D-007 → D-008

Kubernetes (E):
  E-001 (independent)
  D-005 → E-002
  E-003 (independent)
  C-005 → E-004
  C-008 → E-005
  E-006 (independent)
  E-001..006 → E-007 → E-008
  E-002..005 → E-009
  E-007, E-009 → E-010

Documentation (G):
  E-010 → G-001, G-003
  G-003 → G-004
  G-001, G-004 → G-005
```

---

## Implementation Order Recommendation

**Week 1** (Database & Backend Features):
1. T-A-001 to T-A-010 (Database schema)
2. T-B-001 to T-B-006 (Core backend features)

**Week 2** (Advanced Backend & Events):
1. T-B-007 to T-B-012 (Validation & tests)
2. T-C-001 to T-C-004 (Event publishing)

**Week 3** (Microservices & Dapr):
1. T-C-005, T-C-008 (Consumer services)
2. T-C-006, T-C-007, T-C-009 (Reminder system)
3. T-C-010 (Integration tests)
4. T-D-001 to T-D-008 (Dapr components)

**Week 4** (Kubernetes & Deployment):
1. T-E-001 to T-E-006 (K8s manifests)
2. T-E-007, T-E-008 (Minikube deployment)
3. T-E-009, T-E-010 (CI/CD & cloud deployment)

**Week 5** (Frontend & Documentation):
1. T-F-001 to T-F-005 (Frontend enhancements - optional)
2. T-G-001 to T-G-005 (Documentation & demo)

---

## Progress Tracking

Use this checklist to track completion:

**Section A: Database & Models** (0/10)
- [ ] T-A-001
- [ ] T-A-002
- [ ] T-A-003
- [ ] T-A-004
- [ ] T-A-005
- [ ] T-A-006
- [ ] T-A-007
- [ ] T-A-008
- [ ] T-A-009
- [ ] T-A-010

**Section B: Backend Features** (0/12)
- [ ] T-B-001
- [ ] T-B-002
- [ ] T-B-003
- [ ] T-B-004
- [ ] T-B-005
- [ ] T-B-006
- [ ] T-B-007
- [ ] T-B-008
- [ ] T-B-009
- [ ] T-B-010
- [ ] T-B-011
- [ ] T-B-012

**Section C: Events & Kafka** (0/10)
- [ ] T-C-001
- [ ] T-C-002
- [ ] T-C-003
- [ ] T-C-004
- [ ] T-C-005
- [ ] T-C-006
- [ ] T-C-007
- [ ] T-C-008
- [ ] T-C-009
- [ ] T-C-010

**Section D: Dapr Integration** (0/8)
- [ ] T-D-001
- [ ] T-D-002
- [ ] T-D-003
- [ ] T-D-004
- [ ] T-D-005
- [ ] T-D-006
- [ ] T-D-007
- [ ] T-D-008

**Section E: Kubernetes Deployment** (0/10)
- [ ] T-E-001
- [ ] T-E-002
- [ ] T-E-003
- [ ] T-E-004
- [ ] T-E-005
- [ ] T-E-006
- [ ] T-E-007
- [ ] T-E-008
- [ ] T-E-009
- [ ] T-E-010

**Section G: Documentation** (0/5)
- [ ] T-G-001
- [ ] T-G-002
- [ ] T-G-003
- [ ] T-G-004
- [ ] T-G-005

**Total Progress**: 0/55 (0%)

---

## Quality Gates

Before marking section complete, verify:

### After Section A:
- [ ] All migrations run successfully
- [ ] Models pass unit tests
- [ ] Database schema matches plan

### After Section B:
- [ ] All endpoints return correct responses
- [ ] Validation works as expected
- [ ] Unit tests pass (80%+ coverage)

### After Section C:
- [ ] Events publish successfully
- [ ] Consumers process events
- [ ] End-to-end event flow works

### After Section D:
- [ ] Dapr components configured
- [ ] Services run with Dapr locally
- [ ] Event publishing via Dapr works

### After Section E:
- [ ] All pods running in Minikube
- [ ] All pods running in cloud
- [ ] CI/CD pipeline successful
- [ ] Application accessible

### After Section G:
- [ ] README complete and clear
- [ ] Demo video under 90 seconds
- [ ] Submission document complete

---

## Approval

**Task Breakdown Status**: Ready for Implementation  
**Approved By**: _Pending_  
**Approval Date**: _Pending_  

**Next Step**: Begin implementation starting with Section A (Database & Models)

---

**Document Control**  
**Version History**:
- v1.0 (2026-01-21): Initial task breakdown created

**Maintained By**: Claude Code via Spec-Driven Development  
**Last Updated**: 2026-01-21  

**References**:
- `specs/005-phase-v-cloud/phase5-cloud.specify.md` - Requirements (WHAT)
- `specs/005-phase-v-cloud/phase5-cloud.plan.md` - Architecture (HOW)
- `AGENTS.md` - Development workflow
- `constitution.md` - Project principles
