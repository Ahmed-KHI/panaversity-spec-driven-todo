# Phase V: Advanced Cloud Deployment - Technical Plan

**Project:** Panaversity Hackathon II - Todo Application  
**Phase:** V - Advanced Cloud Deployment  
**Version:** 1.0  
**Date:** January 21, 2026  
**Status:** Draft  
**Based On:** `phase5-cloud.specify.md` v1.0

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                              KUBERNETES CLUSTER (Minikube/AKS/GKE/OKE)               │
│                                                                                       │
│  ┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐        │
│  │   Frontend Pod      │   │   Backend Pod       │   │  Recurring Task Pod │        │
│  │ ┌────────┐ ┌──────┐ │   │ ┌────────┐ ┌──────┐ │   │ ┌────────┐ ┌──────┐ │        │
│  │ │Next.js │ │Dapr  │ │   │ │FastAPI │ │Dapr  │ │   │ │Python  │ │Dapr  │ │        │
│  │ │  App   │◀┼▶Sidecar│   │ │+ MCP   │◀┼▶Sidecar│   │ │Consumer│◀┼▶Sidecar│        │
│  │ └────────┘ └──────┘ │   │ └────────┘ └──────┘ │   │ └────────┘ └──────┘ │        │
│  └──────────┬──────────┘   └──────────┬──────────┘   └──────────┬──────────┘        │
│             │                         │                         │                    │
│             │         Service Invocation (Dapr)                 │                    │
│             └─────────────────────────┼─────────────────────────┘                    │
│                                       │                                              │
│                          ┌────────────▼───────────────┐                              │
│                          │   DAPR CONTROL PLANE       │                              │
│                          │  ┌──────────────────────┐  │                              │
│                          │  │ pubsub.kafka         │──┼────▶ Kafka Cluster          │
│                          │  ├──────────────────────┤  │                              │
│                          │  │ state.postgresql     │──┼────▶ Neon DB (External)     │
│                          │  ├──────────────────────┤  │                              │
│                          │  │ jobs API             │  │  (Reminder Scheduling)       │
│                          │  ├──────────────────────┤  │                              │
│                          │  │ secretstores.k8s     │  │  (API Keys, Credentials)     │
│                          │  └──────────────────────┘  │                              │
│                          └──────────────────────────────┘                            │
│                                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐         │
│  │                      KAFKA CLUSTER (Strimzi/Redpanda)                   │         │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐            │         │
│  │  │ task-events    │  │ reminders      │  │ task-updates   │            │         │
│  │  │ (3 partitions) │  │ (1 partition)  │  │ (3 partitions) │            │         │
│  │  └────────────────┘  └────────────────┘  └────────────────┘            │         │
│  └─────────────────────────────────────────────────────────────────────────┘         │
│                                                                                       │
│  ┌─────────────────────┐                                                             │
│  │ Notification Pod    │                                                             │
│  │ ┌────────┐ ┌──────┐ │                                                             │
│  │ │Notif   │ │Dapr  │ │  Consumes from 'reminders'                                  │
│  │ │Service │◀┼▶Sidecar│  Sends notifications                                        │
│  │ └────────┘ └──────┘ │                                                             │
│  └─────────────────────┘                                                             │
└──────────────────────────────────────────────────────────────────────────────────────┘
         │
         └─────────▶ External Services: Neon DB, Email Provider, Push Notification
```

### 1.2 Component Responsibilities

| Component | Responsibility | Scaling Strategy |
|-----------|---------------|------------------|
| **Frontend Pod** | Serve Next.js UI, handle user interactions | Horizontal (3 replicas) |
| **Backend Pod** | REST API, MCP tools, event publishing | Horizontal (3+ replicas) |
| **Recurring Task Service** | Consume task.completed events, create next occurrence | Horizontal (2 replicas) |
| **Notification Service** | Consume reminder events, send notifications | Horizontal (2 replicas) |
| **Kafka Cluster** | Event streaming backbone | 3 brokers (production) |
| **Dapr Control Plane** | Service mesh, sidecar orchestration | Managed by Dapr operator |
| **Neon DB** | Persistent data storage | Managed external service |

---

## 2. Database Schema Extensions

### 2.1 Updated Tasks Table

```sql
-- Add new columns to existing tasks table
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'medium';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS reminder_time TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN DEFAULT FALSE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_pattern JSONB;

-- Add indexes for performance
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_is_recurring ON tasks(is_recurring) WHERE is_recurring = TRUE;

-- Add check constraint for priority
ALTER TABLE tasks ADD CONSTRAINT chk_priority 
  CHECK (priority IN ('low', 'medium', 'high', 'urgent'));
```

### 2.2 New Tags Table

```sql
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(7) DEFAULT '#3B82F6',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS task_tags (
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);

CREATE INDEX idx_task_tags_task ON task_tags(task_id);
CREATE INDEX idx_task_tags_tag ON task_tags(tag_id);
```

### 2.3 Recurrence Pattern JSONB Schema

```json
{
  "frequency": "weekly",  // "daily" | "weekly" | "monthly" | "yearly"
  "interval": 1,          // Every N days/weeks/months/years
  "days_of_week": [1, 3, 5],  // For weekly: 0=Sunday, 6=Saturday
  "day_of_month": 15,     // For monthly: 1-31
  "month": 1,             // For yearly: 1-12
  "end_date": "2027-01-01T00:00:00Z",  // Optional end date
  "occurrences": 10       // Optional: stop after N occurrences
}
```

### 2.4 Event Log Table (Audit Trail)

```sql
CREATE TABLE IF NOT EXISTS event_log (
    id SERIAL PRIMARY KEY,
    event_id UUID UNIQUE NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    topic VARCHAR(50) NOT NULL,
    task_id INTEGER REFERENCES tasks(id),
    user_id INTEGER REFERENCES users(id),
    payload JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_event_log_timestamp ON event_log(timestamp);
CREATE INDEX idx_event_log_task ON event_log(task_id);
CREATE INDEX idx_event_log_type ON event_log(event_type);
```

---

## 3. Backend API Enhancements

### 3.1 New Data Models (SQLModel)

```python
# models.py

from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum
import json

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class RecurrenceFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class RecurrencePattern(SQLModel):
    """Stored as JSONB in database"""
    frequency: RecurrenceFrequency
    interval: int = 1
    days_of_week: Optional[List[int]] = None
    day_of_month: Optional[int] = None
    month: Optional[int] = None
    end_date: Optional[datetime] = None
    occurrences: Optional[int] = None

class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, unique=True, index=True)
    color: str = Field(default="#3B82F6", max_length=7)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: int = Field(foreign_key="users.id")
    
    tasks: List["Task"] = Relationship(back_populates="tags", link_model="TaskTag")

class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"
    
    task_id: int = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, index=True)
    description: Optional[str] = None
    status: str = Field(default="active", index=True)
    priority: Priority = Field(default=Priority.MEDIUM, index=True)
    due_date: Optional[datetime] = Field(default=None, index=True)
    reminder_time: Optional[datetime] = None
    is_recurring: bool = Field(default=False, index=True)
    recurrence_pattern: Optional[str] = None  # JSONB stored as string
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="users.id")
    
    tags: List[Tag] = Relationship(back_populates="tasks", link_model=TaskTag)
    
    @property
    def recurrence(self) -> Optional[RecurrencePattern]:
        if self.recurrence_pattern:
            return RecurrencePattern(**json.loads(self.recurrence_pattern))
        return None
    
    @recurrence.setter
    def recurrence(self, pattern: Optional[RecurrencePattern]):
        self.recurrence_pattern = pattern.model_dump_json() if pattern else None

class EventLog(SQLModel, table=True):
    __tablename__ = "event_log"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str = Field(unique=True, index=True)
    event_type: str = Field(max_length=50, index=True)
    topic: str = Field(max_length=50)
    task_id: Optional[int] = Field(foreign_key="tasks.id")
    user_id: Optional[int] = Field(foreign_key="users.id")
    payload: str  # JSONB stored as string
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    processed: bool = Field(default=False)
```

### 3.2 Event Publishing Service

```python
# services/event_publisher.py

import httpx
import uuid
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class DaprEventPublisher:
    """Publish events to Kafka via Dapr Pub/Sub API"""
    
    def __init__(self, dapr_url: str = "http://localhost:3500"):
        self.dapr_url = dapr_url
        self.pubsub_name = "kafka-pubsub"
    
    async def publish(self, topic: str, event_type: str, data: Dict[str, Any], 
                     user_id: int, task_id: Optional[int] = None):
        """
        Publish event to Kafka via Dapr
        
        [Task]: T-005
        [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §3.1
        """
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "task_id": task_id,
            "data": data
        }
        
        url = f"{self.dapr_url}/v1.0/publish/{self.pubsub_name}/{topic}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=event, timeout=5.0)
                response.raise_for_status()
                logger.info(f"Published event {event_type} to {topic}")
                return event
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            raise
```

### 3.3 Enhanced Task Endpoints

```python
# api/tasks.py

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from sqlmodel import select, col
from services.event_publisher import DaprEventPublisher

router = APIRouter(prefix="/api/tasks", tags=["tasks"])
publisher = DaprEventPublisher()

@router.post("/", response_model=Task)
async def create_task(
    task: TaskCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create task with advanced features
    
    [Task]: T-004
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §2.1-2.5
    """
    db_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        reminder_time=task.reminder_time,
        is_recurring=task.is_recurring,
        user_id=current_user.id
    )
    
    if task.recurrence_pattern:
        db_task.recurrence = task.recurrence_pattern
    
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    
    # Handle tags
    if task.tags:
        for tag_name in task.tags:
            tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
            if not tag:
                tag = Tag(name=tag_name, created_by=current_user.id)
                session.add(tag)
            db_task.tags.append(tag)
        session.commit()
    
    # Publish event to Kafka
    await publisher.publish(
        topic="task-events",
        event_type="task.created",
        data=db_task.model_dump(),
        user_id=current_user.id,
        task_id=db_task.id
    )
    
    # Schedule reminder if due date set
    if db_task.due_date and db_task.reminder_time:
        await schedule_reminder(db_task)
    
    return db_task

@router.get("/search")
async def search_tasks(
    q: str = Query(..., min_length=1),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Search tasks by title or description
    
    [Task]: T-008
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §2.5.2
    """
    statement = select(Task).where(
        Task.user_id == current_user.id,
        col(Task.title).ilike(f"%{q}%") | col(Task.description).ilike(f"%{q}%")
    )
    results = session.exec(statement).all()
    return results

@router.get("/filter")
async def filter_tasks(
    status: Optional[str] = None,
    priority: Optional[Priority] = None,
    tags: Optional[List[str]] = Query(None),
    due_before: Optional[datetime] = None,
    due_after: Optional[datetime] = None,
    overdue: bool = False,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Filter tasks by multiple criteria
    
    [Task]: T-009
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §2.5.2
    """
    statement = select(Task).where(Task.user_id == current_user.id)
    
    if status:
        statement = statement.where(Task.status == status)
    
    if priority:
        statement = statement.where(Task.priority == priority)
    
    if due_before:
        statement = statement.where(Task.due_date <= due_before)
    
    if due_after:
        statement = statement.where(Task.due_date >= due_after)
    
    if overdue:
        statement = statement.where(
            Task.due_date < datetime.utcnow(),
            Task.status != "completed"
        )
    
    results = session.exec(statement).all()
    
    # Filter by tags if provided
    if tags:
        results = [
            task for task in results 
            if any(tag.name in tags for tag in task.tags)
        ]
    
    return results

@router.patch("/{task_id}/complete")
async def complete_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Mark task complete and publish event
    
    [Task]: T-010
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §2.1.3
    """
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(404, "Task not found")
    
    task.status = "completed"
    task.updated_at = datetime.utcnow()
    session.commit()
    
    # Publish completion event (triggers recurring task creation)
    await publisher.publish(
        topic="task-events",
        event_type="task.completed",
        data=task.model_dump(),
        user_id=current_user.id,
        task_id=task.id
    )
    
    return task
```

### 3.4 Dapr Jobs API Integration

```python
# services/reminder_scheduler.py

import httpx
from datetime import datetime
from models import Task

async def schedule_reminder(task: Task):
    """
    Schedule reminder using Dapr Jobs API
    
    [Task]: T-011
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §4.1.4
    """
    dapr_url = "http://localhost:3500"
    job_name = f"reminder-task-{task.id}"
    
    payload = {
        "schedule": task.reminder_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data": {
            "task_id": task.id,
            "user_id": task.user_id,
            "task_title": task.title,
            "type": "reminder"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{dapr_url}/v1.0-alpha1/jobs/{job_name}",
            json=payload
        )
        response.raise_for_status()

@router.post("/api/jobs/trigger")
async def handle_job_trigger(request: Request):
    """
    Dapr calls this endpoint when job fires
    
    [Task]: T-012
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §4.1.4
    """
    job_data = await request.json()
    
    if job_data["data"]["type"] == "reminder":
        # Publish reminder event
        await publisher.publish(
            topic="reminders",
            event_type="reminder.due",
            data=job_data["data"],
            user_id=job_data["data"]["user_id"],
            task_id=job_data["data"]["task_id"]
        )
    
    return {"status": "SUCCESS"}
```

---

## 4. Consumer Services

### 4.1 Recurring Task Service

```python
# services/recurring_task_consumer.py

import asyncio
import httpx
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger(__name__)

class RecurringTaskConsumer:
    """
    Consumes task.completed events and creates next occurrence
    
    [Task]: T-013
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §5.1.2
    """
    
    def __init__(self, dapr_url: str = "http://localhost:3500"):
        self.dapr_url = dapr_url
        self.pubsub_name = "kafka-pubsub"
        self.topic = "task-events"
    
    def calculate_next_occurrence(self, task_data: dict) -> datetime:
        """Calculate next occurrence based on recurrence pattern"""
        pattern = task_data["recurrence_pattern"]
        completed_at = datetime.fromisoformat(task_data["updated_at"])
        
        if pattern["frequency"] == "daily":
            return completed_at + timedelta(days=pattern["interval"])
        
        elif pattern["frequency"] == "weekly":
            next_date = completed_at + timedelta(weeks=pattern["interval"])
            # Adjust to next specified day of week
            if pattern.get("days_of_week"):
                target_day = pattern["days_of_week"][0]
                days_ahead = target_day - next_date.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                next_date += timedelta(days=days_ahead)
            return next_date
        
        elif pattern["frequency"] == "monthly":
            return completed_at + relativedelta(months=pattern["interval"])
        
        elif pattern["frequency"] == "yearly":
            return completed_at + relativedelta(years=pattern["interval"])
        
        return completed_at
    
    async def process_event(self, event: dict):
        """Process task.completed event"""
        if event["event_type"] != "task.completed":
            return
        
        task_data = event["data"]
        
        if not task_data.get("is_recurring"):
            return
        
        # Calculate next occurrence
        next_due = self.calculate_next_occurrence(task_data)
        
        # Create next task via Backend API
        new_task = {
            "title": task_data["title"],
            "description": task_data["description"],
            "priority": task_data["priority"],
            "due_date": next_due.isoformat(),
            "is_recurring": True,
            "recurrence_pattern": task_data["recurrence_pattern"],
            "tags": [tag["name"] for tag in task_data.get("tags", [])]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.dapr_url}/v1.0/invoke/backend-service/method/api/tasks",
                json=new_task,
                headers={"Authorization": f"Bearer {task_data['user_id']}"}
            )
            response.raise_for_status()
            logger.info(f"Created next occurrence for task {task_data['id']}")
    
    async def start(self):
        """Start consuming events via Dapr Pub/Sub"""
        logger.info("Starting Recurring Task Consumer")
        # Dapr will call /subscribe endpoint to register this consumer
        # Events will be pushed to /events endpoint

# FastAPI app for consumer
from fastapi import FastAPI, Request

app = FastAPI()
consumer = RecurringTaskConsumer()

@app.get("/dapr/subscribe")
async def subscribe():
    """Dapr calls this to register subscriptions"""
    return [{
        "pubsubname": "kafka-pubsub",
        "topic": "task-events",
        "route": "/events"
    }]

@app.post("/events")
async def handle_event(request: Request):
    """Dapr pushes events here"""
    event = await request.json()
    await consumer.process_event(event)
    return {"status": "SUCCESS"}
```

### 4.2 Notification Service

```python
# services/notification_consumer.py

import httpx
from fastapi import FastAPI, Request
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Consumes reminder events and sends notifications
    
    [Task]: T-014
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §5.1.3
    """
    
    async def send_notification(self, event: dict):
        """Send notification to user"""
        data = event["data"]
        
        # In-app notification (store in DB)
        notification = {
            "user_id": data["user_id"],
            "type": "reminder",
            "title": "Task Reminder",
            "message": f"'{data['task_title']}' is due soon",
            "task_id": data["task_id"],
            "created_at": datetime.utcnow().isoformat()
        }
        
        # TODO: Store in database via Dapr State API
        # TODO: Send email via SendGrid/SES
        # TODO: Send push notification via Firebase
        
        logger.info(f"Sent notification for task {data['task_id']} to user {data['user_id']}")
    
    async def process_event(self, event: dict):
        """Process reminder.due event"""
        if event["event_type"] == "reminder.due":
            await self.send_notification(event)

app = FastAPI()
service = NotificationService()

@app.get("/dapr/subscribe")
async def subscribe():
    return [{
        "pubsubname": "kafka-pubsub",
        "topic": "reminders",
        "route": "/events"
    }]

@app.post("/events")
async def handle_event(request: Request):
    event = await request.json()
    await service.process_event(event)
    return {"status": "SUCCESS"}
```

---

## 5. Dapr Configuration

### 5.1 Dapr Components

#### 5.1.1 Kafka Pub/Sub Component

```yaml
# dapr-components/kafka-pubsub.yaml

apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    # For local Minikube (Strimzi)
    - name: brokers
      value: "taskflow-kafka-kafka-bootstrap.kafka:9092"
    - name: consumerGroup
      value: "todo-service"
    - name: clientId
      value: "todo-backend"
    
    # For production (Redpanda Cloud) - use secrets
    # - name: brokers
    #   secretKeyRef:
    #     name: kafka-secrets
    #     key: bootstrap-servers
    # - name: authType
    #   value: "sasl"
    # - name: saslUsername
    #   secretKeyRef:
    #     name: kafka-secrets
    #     key: sasl-username
    # - name: saslPassword
    #   secretKeyRef:
    #     name: kafka-secrets
    #     key: sasl-password
```

#### 5.1.2 PostgreSQL State Store

```yaml
# dapr-components/statestore.yaml

apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-app
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: postgres-secrets
        key: connection-string
    - name: tableName
      value: "dapr_state"
    - name: actorStateStore
      value: "true"
```

#### 5.1.3 Kubernetes Secrets Store

```yaml
# dapr-components/kubernetes-secrets.yaml

apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: todo-app
spec:
  type: secretstores.kubernetes
  version: v1
  metadata:
    - name: vaultKubeMountPath
      value: "kubernetes"
```

### 5.2 Kubernetes Secrets

```yaml
# kubernetes/secrets.yaml

apiVersion: v1
kind: Secret
metadata:
  name: postgres-secrets
  namespace: todo-app
type: Opaque
stringData:
  connection-string: "postgresql://user:password@neon.tech:5432/tododb?sslmode=require"

---
apiVersion: v1
kind: Secret
metadata:
  name: kafka-secrets
  namespace: todo-app
type: Opaque
stringData:
  bootstrap-servers: "your-cluster.redpanda.cloud:9092"
  sasl-username: "your-username"
  sasl-password: "your-password"

---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: todo-app
type: Opaque
stringData:
  openai-api-key: "sk-..."
  better-auth-secret: "your-secret-here"
```

---

## 6. Kubernetes Deployments

### 6.1 Backend Deployment with Dapr

```yaml
# kubernetes/backend-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: todo-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend-service"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
        dapr.io/enable-api-logging: "true"
    spec:
      containers:
      - name: backend
        image: your-registry/todo-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-secrets
              key: connection-string
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: todo-app
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### 6.2 Frontend Deployment with Dapr

```yaml
# kubernetes/frontend-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: todo-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "frontend-service"
        dapr.io/app-port: "3000"
    spec:
      containers:
      - name: frontend
        image: your-registry/todo-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "http://backend-service:8000"
        - name: BETTER_AUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: better-auth-secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: todo-app
spec:
  selector:
    app: frontend
  ports:
  - port: 3000
    targetPort: 3000
  type: LoadBalancer
```

### 6.3 Recurring Task Service Deployment

```yaml
# kubernetes/recurring-task-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: recurring-task-svc
  namespace: todo-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: recurring-task-svc
  template:
    metadata:
      labels:
        app: recurring-task-svc
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "recurring-task-service"
        dapr.io/app-port: "8001"
    spec:
      containers:
      - name: recurring-task-consumer
        image: your-registry/recurring-task-service:latest
        ports:
        - containerPort: 8001
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

### 6.4 Notification Service Deployment

```yaml
# kubernetes/notification-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-svc
  namespace: todo-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: notification-svc
  template:
    metadata:
      labels:
        app: notification-svc
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "notification-service"
        dapr.io/app-port: "8002"
    spec:
      containers:
      - name: notification-consumer
        image: your-registry/notification-service:latest
        ports:
        - containerPort: 8002
        env:
        - name: SENDGRID_API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: sendgrid-api-key
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

---

## 7. Kafka Deployment

### 7.1 Option A: Strimzi Operator (Self-Hosted)

```yaml
# kafka/strimzi-kafka-cluster.yaml

apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: taskflow-kafka
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
    storage:
      type: persistent-claim
      size: 10Gi
      deleteClaim: false
  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 5Gi
      deleteClaim: false
  entityOperator:
    topicOperator: {}
    userOperator: {}

---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: kafka
  labels:
    strimzi.io/cluster: taskflow-kafka
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 604800000  # 7 days

---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  namespace: kafka
  labels:
    strimzi.io/cluster: taskflow-kafka
spec:
  partitions: 1
  replicas: 3
  config:
    retention.ms: 604800000

---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
  namespace: kafka
  labels:
    strimzi.io/cluster: taskflow-kafka
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 604800000
```

### 7.2 Option B: Redpanda Cloud (Managed)

1. Sign up at redpanda.com/cloud
2. Create Serverless cluster (free tier)
3. Create topics via Redpanda Console:
   - `task-events` (3 partitions)
   - `reminders` (1 partition)
   - `task-updates` (3 partitions)
4. Copy bootstrap servers and credentials
5. Update `kafka-pubsub.yaml` with Redpanda connection details

---

## 8. CI/CD Pipeline

### 8.1 GitHub Actions Workflow

```yaml
# .github/workflows/deploy-phase5.yml

name: Deploy Phase 5 to Cloud

on:
  push:
    branches: [main]
    paths:
      - 'phase-2-fullstack/backend/**'
      - 'phase-2-fullstack/frontend/**'
      - 'phase-5-services/**'
      - 'kubernetes/**'
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    strategy:
      matrix:
        service:
          - name: backend
            context: ./phase-2-fullstack/backend
            dockerfile: Dockerfile
          - name: frontend
            context: ./phase-2-fullstack/frontend
            dockerfile: Dockerfile
          - name: recurring-task-service
            context: ./phase-5-services/recurring-task
            dockerfile: Dockerfile
          - name: notification-service
            context: ./phase-5-services/notification
            dockerfile: Dockerfile
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: ${{ matrix.service.context }}
          file: ${{ matrix.service.context }}/${{ matrix.service.dockerfile }}
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}-${{ matrix.service.name }}:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}-${{ matrix.service.name }}:${{ github.sha }}
  
  deploy-to-kubernetes:
    needs: build-and-push
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
      
      - name: Configure kubectl
        run: |
          echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > kubeconfig.yaml
          export KUBECONFIG=kubeconfig.yaml
      
      - name: Install Dapr (if not exists)
        run: |
          dapr init -k
      
      - name: Deploy Kafka (Strimzi)
        run: |
          kubectl apply -f kafka/strimzi-kafka-cluster.yaml
      
      - name: Deploy Dapr Components
        run: |
          kubectl apply -f dapr-components/
      
      - name: Deploy Kubernetes Secrets
        run: |
          kubectl apply -f kubernetes/secrets.yaml
      
      - name: Deploy Services
        run: |
          kubectl apply -f kubernetes/
      
      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/backend -n todo-app
          kubectl rollout status deployment/frontend -n todo-app
          kubectl rollout status deployment/recurring-task-svc -n todo-app
          kubectl rollout status deployment/notification-svc -n todo-app
      
      - name: Run smoke tests
        run: |
          FRONTEND_URL=$(kubectl get svc frontend-service -n todo-app -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
          curl -f http://$FRONTEND_URL:3000/health || exit 1
```

---

## 9. Monitoring & Observability

### 9.1 Dapr Dashboard

```bash
# Access Dapr dashboard
dapr dashboard -k -p 9999
```

Navigate to `http://localhost:9999` to view:
- Service topology
- Component status
- Pub/Sub subscriptions
- State store data

### 9.2 Prometheus & Grafana (Optional)

```yaml
# monitoring/prometheus.yaml
# Deploy Prometheus to scrape Dapr metrics

apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: todo-app
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
      - job_name: 'dapr'
        kubernetes_sd_configs:
        - role: pod
        relabel_configs:
        - source_labels: [__meta_kubernetes_pod_annotation_dapr_io_enabled]
          action: keep
          regex: true
        - source_labels: [__meta_kubernetes_pod_annotation_dapr_io_app_id]
          target_label: app_id
```

---

## 10. Deployment Strategy

### 10.1 Phase 5A: Local Minikube Deployment

**Steps**:
1. Start Minikube: `minikube start --cpus=4 --memory=8192`
2. Install Dapr: `dapr init -k`
3. Install Strimzi operator: `kubectl apply -f strimzi-operator.yaml`
4. Deploy Kafka cluster: `kubectl apply -f kafka/strimzi-kafka-cluster.yaml`
5. Wait for Kafka: `kubectl wait kafka/taskflow-kafka --for=condition=Ready --timeout=300s -n kafka`
6. Deploy Dapr components: `kubectl apply -f dapr-components/`
7. Create namespace: `kubectl create namespace todo-app`
8. Deploy secrets: `kubectl apply -f kubernetes/secrets.yaml`
9. Build Docker images: `./scripts/build-images.sh`
10. Load images to Minikube: `./scripts/load-images-minikube.sh`
11. Deploy services: `kubectl apply -f kubernetes/`
12. Port forward: `kubectl port-forward svc/frontend-service 3000:3000 -n todo-app`
13. Test: Navigate to `http://localhost:3000`

**Success Criteria**:
- All pods in `Running` state
- All Dapr sidecars healthy
- Kafka topics created
- Frontend accessible
- Events flowing through Kafka

### 10.2 Phase 5B: Cloud Deployment (AKS/GKE/OKE)

**Prerequisites**:
- Cloud provider account with credits
- `kubectl` configured with cluster
- `helm` installed
- Container registry set up (GitHub Container Registry or Docker Hub)

**Steps**:
1. Create Kubernetes cluster (via cloud console or CLI)
2. Connect kubectl: `gcloud container clusters get-credentials` or `az aks get-credentials`
3. Install Dapr: `dapr init -k`
4. Set up Redpanda Cloud:
   - Create cluster at redpanda.com/cloud
   - Create topics
   - Copy credentials
5. Update Dapr component with Redpanda credentials
6. Push Docker images to registry: `./scripts/push-images.sh`
7. Update Kubernetes manifests with registry URLs
8. Deploy via GitHub Actions or manually:
   ```bash
   kubectl apply -f kubernetes/secrets.yaml
   kubectl apply -f dapr-components/
   kubectl apply -f kubernetes/
   ```
9. Wait for LoadBalancer IP: `kubectl get svc frontend-service -n todo-app`
10. Configure DNS (optional)
11. Test deployment

**Success Criteria**:
- All services deployed to cloud
- LoadBalancer accessible from internet
- CI/CD pipeline runs successfully
- Monitoring operational

---

## 11. Testing Strategy

### 11.1 Unit Tests
- Test task CRUD operations
- Test recurrence calculation logic
- Test event publishing
- Test filter/search logic

### 11.2 Integration Tests
- Test Kafka event flow (publish → consume)
- Test Dapr Pub/Sub integration
- Test Dapr Service Invocation
- Test Dapr Jobs API

### 11.3 End-to-End Tests
- Create recurring task → complete → verify next occurrence created
- Create task with due date → verify reminder fires
- Search/filter tasks → verify results
- Multi-client sync test

---

## 12. Rollback Strategy

### 12.1 Kubernetes Rollback
```bash
# Rollback to previous deployment
kubectl rollout undo deployment/backend -n todo-app

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=2 -n todo-app
```

### 12.2 Database Migrations
- Use Alembic for migrations
- Keep backward-compatible changes
- Test rollback before deploying

---

## 13. Performance Tuning

### 13.1 Kafka Tuning
- **Partitions**: 3 for high-throughput topics (task-events, task-updates)
- **Replication**: 3 for production, 1 for local
- **Retention**: 7 days

### 13.2 Dapr Tuning
- **Sidecar resources**: 100m CPU, 128Mi memory (minimum)
- **Log level**: `info` for production, `debug` for troubleshooting
- **API logging**: Disable in production for performance

### 13.3 Kubernetes Scaling
```yaml
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: todo-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## 14. Security Considerations

### 14.1 Network Policies
```yaml
# Restrict traffic between services
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
  namespace: todo-app
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: kafka
```

### 14.2 RBAC
- Use service accounts with minimal permissions
- Dapr requires specific RBAC permissions (auto-created by `dapr init -k`)

### 14.3 mTLS
- Enabled by default with Dapr
- All service-to-service communication encrypted

---

## 15. Documentation Requirements

### 15.1 README Updates
- Add Phase 5 section
- Include architecture diagrams
- Deployment instructions for Minikube and cloud
- Troubleshooting guide

### 15.2 API Documentation
- Document new endpoints:
  - `/api/tasks/search`
  - `/api/tasks/filter`
  - `/api/jobs/trigger`
- Update OpenAPI/Swagger spec

### 15.3 Demo Video Script
1. **Intro (5s)**: "Phase 5: Advanced Cloud Deployment"
2. **Features Demo (40s)**:
   - Create recurring task
   - Set due date and reminder
   - Add priorities and tags
   - Search and filter
   - Complete recurring task → show next occurrence
3. **Architecture (20s)**:
   - Show Kafka topics
   - Show Dapr dashboard
   - Show Kubernetes pods
4. **Deployment (20s)**:
   - Show CI/CD pipeline
   - Show cloud deployment
   - Show LoadBalancer URL
5. **Outro (5s)**: "Thank you!"

---

## 16. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Feature Completeness** | 100% | All requirements from specify.md implemented |
| **Event Latency** | < 50ms p95 | Kafka publish time |
| **Reminder Accuracy** | ±1 second | Dapr Jobs API trigger time |
| **Search Performance** | < 200ms | 1000 tasks, keyword search |
| **Deployment Time** | < 10 minutes | CI/CD pipeline duration |
| **Uptime** | 99.9% | Cloud deployment availability |

---

## 17. Dependencies

### 17.1 External Services
- Neon DB (PostgreSQL)
- Redpanda Cloud OR Strimzi (Kafka)
- GitHub Container Registry
- Cloud provider (Azure/GCP/Oracle)

### 17.2 Tools & SDKs
- Dapr CLI v1.12+
- kubectl v1.28+
- Helm v3.12+
- Docker v24+
- Minikube v1.31+

---

## 18. Approval & Next Steps

**Plan Status**: Draft  
**Requires Approval From**: Project Lead  

**After Approval**:
1. Create `phase5-cloud.tasks.md` - Break down into atomic tasks
2. Begin implementation following Spec-Driven Development
3. Track progress with task completion

---

**Document Control**  
**Version History**:
- v1.0 (2026-01-21): Initial plan created from specification

**Maintained By**: Claude Code via Spec-Driven Development  
**Last Updated**: 2026-01-21

**References**:
- `specs/005-phase-v-cloud/phase5-cloud.specify.md` - Requirements specification
- `constitution.md` - Project principles
- `AGENTS.md` - Development workflow
