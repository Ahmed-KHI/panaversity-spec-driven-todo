"""
Unit tests for Phase V advanced task endpoints.
[Task]: T-B-011 (Advanced Task API Tests)
[From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §5.1-5.3,
        specs/005-phase-v-cloud/phase5-cloud.tasks.md §B.11
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from uuid import uuid4
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from src.main import app
from src.database import get_session
from src.models import User, Task, Tag, Priority, RecurrenceFrequency
from src.utils.auth import create_access_token


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """Create in-memory test database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with dependency override."""
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create test user."""
    user = User(
        id=uuid4(),
        email="test@example.com",
        password_hash="$2b$12$test_hash",
        full_name="Test User",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(test_user: User):
    """Create authentication headers."""
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


# ===== Task Creation with Phase V Fields Tests =====

def test_create_task_with_priority(client: TestClient, test_user: User, auth_headers: dict):
    """Test creating task with priority field."""
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={
            "title": "High Priority Task",
            "description": "Important work",
            "priority": "high"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "High Priority Task"
    assert data["priority"] == "high"


def test_create_task_with_due_date(client: TestClient, test_user: User, auth_headers: dict):
    """Test creating task with due date."""
    due_date = (datetime.utcnow() + timedelta(days=3)).isoformat()
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={
            "title": "Task with Deadline",
            "due_date": due_date,
            "priority": "medium"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["due_date"] is not None


def test_create_task_with_reminder(client: TestClient, test_user: User, auth_headers: dict):
    """Test creating task with reminder time."""
    due_date = (datetime.utcnow() + timedelta(days=2)).isoformat()
    reminder_time = (datetime.utcnow() + timedelta(days=1)).isoformat()
    
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={
            "title": "Task with Reminder",
            "due_date": due_date,
            "reminder_time": reminder_time,
            "priority": "medium"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["reminder_time"] is not None


def test_create_recurring_task_daily(client: TestClient, test_user: User, auth_headers: dict):
    """Test creating daily recurring task."""
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={
            "title": "Daily Exercise",
            "is_recurring": True,
            "recurrence_pattern": {
                "frequency": "daily",
                "interval": 1,
                "occurrences": 30
            },
            "priority": "medium"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["is_recurring"] is True
    assert data["recurrence_pattern"]["frequency"] == "daily"


def test_create_recurring_task_weekly(client: TestClient, test_user: User, auth_headers: dict):
    """Test creating weekly recurring task."""
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={
            "title": "Weekly Team Meeting",
            "is_recurring": True,
            "recurrence_pattern": {
                "frequency": "weekly",
                "interval": 1,
                "days_of_week": [0, 2, 4]  # Mon, Wed, Fri
            },
            "priority": "medium"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["recurrence_pattern"]["days_of_week"] == [0, 2, 4]


def test_create_task_with_tags(client: TestClient, test_user: User, auth_headers: dict):
    """Test creating task with tags."""
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={
            "title": "Tagged Task",
            "tags": ["Work", "Urgent"],
            "priority": "high"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["tags"]) == 2
    tag_names = [t["name"] for t in data["tags"]]
    assert "Work" in tag_names
    assert "Urgent" in tag_names


# ===== Validation Tests =====

def test_create_task_due_date_in_past_fails(client: TestClient, test_user: User, auth_headers: dict):
    """Test that creating task with past due date fails."""
    past_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={
            "title": "Past Due Task",
            "due_date": past_date,
            "priority": "medium"
        },
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "past" in response.json()["detail"].lower()


def test_create_task_reminder_after_due_date_fails(client: TestClient, test_user: User, auth_headers: dict):
    """Test that reminder after due date fails validation."""
    due_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
    reminder_time = (datetime.utcnow() + timedelta(days=2)).isoformat()
    
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={
            "title": "Invalid Reminder",
            "due_date": due_date,
            "reminder_time": reminder_time,
            "priority": "medium"
        },
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "before" in response.json()["detail"].lower()


def test_create_recurring_task_without_pattern_fails(client: TestClient, test_user: User, auth_headers: dict):
    """Test that recurring task without pattern fails."""
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={
            "title": "Invalid Recurring",
            "is_recurring": True,
            "priority": "medium"
        },
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "pattern" in response.json()["detail"].lower()


def test_create_weekly_task_without_days_fails(client: TestClient, test_user: User, auth_headers: dict):
    """Test that weekly recurrence without days_of_week fails."""
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={
            "title": "Invalid Weekly",
            "is_recurring": True,
            "recurrence_pattern": {
                "frequency": "weekly",
                "interval": 1
            },
            "priority": "medium"
        },
        headers=auth_headers
    )
    assert response.status_code == 400


# ===== Search and Filter Tests =====

def test_search_tasks_by_title(client: TestClient, test_user: User, auth_headers: dict, session: Session):
    """Test searching tasks by title."""
    # Create test tasks
    task1 = Task(user_id=test_user.id, title="Python Programming", priority=Priority.MEDIUM)
    task2 = Task(user_id=test_user.id, title="JavaScript Learning", priority=Priority.LOW)
    task3 = Task(user_id=test_user.id, title="Python Django", priority=Priority.HIGH)
    session.add_all([task1, task2, task3])
    session.commit()
    
    response = client.get(
        f"/api/{test_user.id}/tasks?search=python",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2


def test_filter_tasks_by_priority(client: TestClient, test_user: User, auth_headers: dict, session: Session):
    """Test filtering tasks by priority."""
    task1 = Task(user_id=test_user.id, title="Task 1", priority=Priority.HIGH)
    task2 = Task(user_id=test_user.id, title="Task 2", priority=Priority.LOW)
    task3 = Task(user_id=test_user.id, title="Task 3", priority=Priority.HIGH)
    session.add_all([task1, task2, task3])
    session.commit()
    
    response = client.get(
        f"/api/{test_user.id}/tasks?priority=high",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2


def test_filter_tasks_by_completion(client: TestClient, test_user: User, auth_headers: dict, session: Session):
    """Test filtering by completion status."""
    task1 = Task(user_id=test_user.id, title="Done", completed=True, priority=Priority.MEDIUM)
    task2 = Task(user_id=test_user.id, title="Pending", completed=False, priority=Priority.MEDIUM)
    session.add_all([task1, task2])
    session.commit()
    
    response = client.get(
        f"/api/{test_user.id}/tasks?completed=completed",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1


def test_filter_tasks_by_date_range(client: TestClient, test_user: User, auth_headers: dict, session: Session):
    """Test filtering by due date range."""
    now = datetime.utcnow()
    task1 = Task(user_id=test_user.id, title="Soon", due_date=now + timedelta(days=1), priority=Priority.MEDIUM)
    task2 = Task(user_id=test_user.id, title="Later", due_date=now + timedelta(days=10), priority=Priority.MEDIUM)
    session.add_all([task1, task2])
    session.commit()
    
    due_before = (now + timedelta(days=5)).isoformat()
    response = client.get(
        f"/api/{test_user.id}/tasks?due_before={due_before}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1


def test_sort_tasks_by_priority(client: TestClient, test_user: User, auth_headers: dict, session: Session):
    """Test sorting tasks by priority."""
    task1 = Task(user_id=test_user.id, title="Low", priority=Priority.LOW)
    task2 = Task(user_id=test_user.id, title="High", priority=Priority.HIGH)
    task3 = Task(user_id=test_user.id, title="Urgent", priority=Priority.URGENT)
    session.add_all([task1, task2, task3])
    session.commit()
    
    response = client.get(
        f"/api/{test_user.id}/tasks?sort_by=priority&sort_order=desc",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tasks"][0]["priority"] == "urgent"


def test_pagination(client: TestClient, test_user: User, auth_headers: dict, session: Session):
    """Test task pagination."""
    for i in range(25):
        task = Task(user_id=test_user.id, title=f"Task {i}", priority=Priority.MEDIUM)
        session.add(task)
    session.commit()
    
    response = client.get(
        f"/api/{test_user.id}/tasks?page=1&page_size=10",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 10
    assert data["count"] == 25


# ===== Update Task Tests =====

def test_update_task_priority(client: TestClient, test_user: User, auth_headers: dict, session: Session):
    """Test updating task priority."""
    task = Task(user_id=test_user.id, title="Task", priority=Priority.LOW)
    session.add(task)
    session.commit()
    session.refresh(task)
    
    response = client.put(
        f"/api/{test_user.id}/tasks/{task.id}",
        json={"priority": "urgent"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["priority"] == "urgent"


def test_update_task_add_tags(client: TestClient, test_user: User, auth_headers: dict, session: Session):
    """Test adding tags to existing task."""
    task = Task(user_id=test_user.id, title="Task", priority=Priority.MEDIUM)
    session.add(task)
    session.commit()
    session.refresh(task)
    
    response = client.put(
        f"/api/{test_user.id}/tasks/{task.id}",
        json={"tags": ["Important", "Work"]},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["tags"]) == 2


# ===== Statistics Tests =====

def test_get_task_statistics(client: TestClient, test_user: User, auth_headers: dict, session: Session):
    """Test getting task statistics."""
    # Create diverse tasks
    now = datetime.utcnow()
    tasks = [
        Task(user_id=test_user.id, title="Done", completed=True, priority=Priority.HIGH),
        Task(user_id=test_user.id, title="Pending", completed=False, priority=Priority.MEDIUM),
        Task(user_id=test_user.id, title="Overdue", completed=False, 
             due_date=now - timedelta(days=1), priority=Priority.URGENT),
        Task(user_id=test_user.id, title="Today", completed=False, 
             due_date=now + timedelta(hours=5), priority=Priority.HIGH),
    ]
    session.add_all(tasks)
    session.commit()
    
    response = client.get(
        f"/api/{test_user.id}/stats/tasks",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4
    assert data["completed"] == 1
    assert data["pending"] == 3
    assert data["overdue"] == 1
    assert data["completion_rate"] == 25.0


def test_statistics_by_priority(client: TestClient, test_user: User, auth_headers: dict, session: Session):
    """Test statistics breakdown by priority."""
    tasks = [
        Task(user_id=test_user.id, title="T1", priority=Priority.HIGH),
        Task(user_id=test_user.id, title="T2", priority=Priority.HIGH),
        Task(user_id=test_user.id, title="T3", priority=Priority.LOW),
    ]
    session.add_all(tasks)
    session.commit()
    
    response = client.get(
        f"/api/{test_user.id}/stats/tasks",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["by_priority"]["high"] == 2
    assert data["by_priority"]["low"] == 1
