"""
Integration tests for event flow and Kafka integration.
[Task]: T-C-010 (Event Flow Integration Tests)
[From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §3,
        specs/005-phase-v-cloud/phase5-cloud.tasks.md §C.10
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from sqlmodel import Session, create_engine, SQLModel, select
from sqlmodel.pool import StaticPool
from src.services.event_publisher import EventPublisher, get_event_publisher
from src.services.reminder_scheduler import ReminderScheduler
from src.models import User, Task, EventLog, Priority


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


# ===== Event Publisher Tests =====

def test_event_publisher_initialization():
    """Test event publisher initializes correctly."""
    publisher = EventPublisher()
    assert publisher is not None
    assert publisher.TASK_CREATED == "task.created"
    assert publisher.TOPIC_TASK_EVENTS == "task-events"


def test_publish_to_database_when_kafka_disabled(session: Session, test_user: User):
    """Test events are logged to database when Kafka unavailable."""
    publisher = EventPublisher()
    publisher.kafka_enabled = False  # Ensure database mode
    
    event_id = publisher.publish(
        event_type="task.created",
        topic="task-events",
        payload={"test": "data"},
        task_id=123,
        user_id=str(test_user.id),
        session=session
    )
    
    assert event_id is not None
    
    # Verify event logged to database
    event_log = session.exec(
        select(EventLog).where(EventLog.event_id == event_id)
    ).first()
    
    assert event_log is not None
    assert event_log.event_type == "task.created"
    assert event_log.topic == "task-events"
    assert event_log.task_id == 123
    assert event_log.user_id == str(test_user.id)


def test_publish_task_created_event(session: Session, test_user: User):
    """Test publishing task.created event."""
    publisher = EventPublisher()
    publisher.kafka_enabled = False
    
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "priority": "high",
        "due_date": datetime.utcnow().isoformat(),
        "is_recurring": False
    }
    
    event_id = publisher.publish_task_created(
        task_id=1,
        user_id=str(test_user.id),
        task_data=task_data,
        session=session
    )
    
    assert event_id is not None
    
    # Verify event
    event = session.exec(
        select(EventLog).where(EventLog.event_id == event_id)
    ).first()
    
    assert event.event_type == "task.created"
    assert event.topic == "task-events"
    assert "title" in event.payload_dict["data"]


def test_publish_task_updated_event(session: Session, test_user: User):
    """Test publishing task.updated event."""
    publisher = EventPublisher()
    publisher.kafka_enabled = False
    
    changes = {
        "title": "Updated Title",
        "priority": "urgent"
    }
    
    event_id = publisher.publish_task_updated(
        task_id=1,
        user_id=str(test_user.id),
        changes=changes,
        session=session
    )
    
    assert event_id is not None
    
    event = session.exec(
        select(EventLog).where(EventLog.event_id == event_id)
    ).first()
    
    assert event.event_type == "task.updated"
    assert event.topic == "task-updates"


def test_publish_task_completed_event(session: Session, test_user: User):
    """Test publishing task.completed event."""
    publisher = EventPublisher()
    publisher.kafka_enabled = False
    
    event_id = publisher.publish_task_completed(
        task_id=1,
        user_id=str(test_user.id),
        completed=True,
        session=session
    )
    
    assert event_id is not None
    
    event = session.exec(
        select(EventLog).where(EventLog.event_id == event_id)
    ).first()
    
    assert event.event_type == "task.completed"
    assert event.payload_dict["data"]["completed"] is True


def test_publish_reminder_scheduled_event(session: Session, test_user: User):
    """Test publishing reminder.scheduled event."""
    publisher = EventPublisher()
    publisher.kafka_enabled = False
    
    reminder_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    
    event_id = publisher.publish_reminder_scheduled(
        task_id=1,
        user_id=str(test_user.id),
        reminder_time=reminder_time,
        session=session
    )
    
    assert event_id is not None
    
    event = session.exec(
        select(EventLog).where(EventLog.event_id == event_id)
    ).first()
    
    assert event.event_type == "reminder.scheduled"
    assert event.topic == "reminders"


# ===== Reminder Scheduler Tests =====

def test_get_due_reminders(session: Session, test_user: User):
    """Test getting tasks with due reminders."""
    scheduler = ReminderScheduler()
    
    # Create tasks with reminders
    now = datetime.utcnow()
    task1 = Task(
        user_id=test_user.id,
        title="Reminder Soon",
        reminder_time=now + timedelta(minutes=30),
        priority=Priority.MEDIUM
    )
    task2 = Task(
        user_id=test_user.id,
        title="Reminder Later",
        reminder_time=now + timedelta(hours=2),
        priority=Priority.LOW
    )
    task3 = Task(
        user_id=test_user.id,
        title="Completed Task",
        reminder_time=now + timedelta(minutes=15),
        completed=True,
        priority=Priority.MEDIUM
    )
    session.add_all([task1, task2, task3])
    session.commit()
    
    # Get reminders in next 60 minutes
    reminders = scheduler.get_due_reminders(session, lookahead_minutes=60)
    
    # Should find task1 only (task2 is beyond 60 min, task3 is completed)
    assert len(reminders) == 1
    assert reminders[0]["title"] == "Reminder Soon"
    assert reminders[0]["user_email"] == test_user.email


def test_get_overdue_tasks(session: Session, test_user: User):
    """Test getting overdue tasks."""
    scheduler = ReminderScheduler()
    
    now = datetime.utcnow()
    task1 = Task(
        user_id=test_user.id,
        title="Overdue Task",
        due_date=now - timedelta(days=1),
        completed=False,
        priority=Priority.HIGH
    )
    task2 = Task(
        user_id=test_user.id,
        title="Future Task",
        due_date=now + timedelta(days=1),
        completed=False,
        priority=Priority.MEDIUM
    )
    task3 = Task(
        user_id=test_user.id,
        title="Completed Overdue",
        due_date=now - timedelta(hours=2),
        completed=True,
        priority=Priority.LOW
    )
    session.add_all([task1, task2, task3])
    session.commit()
    
    overdue = scheduler.get_overdue_tasks(session)
    
    # Should find task1 only
    assert len(overdue) == 1
    assert overdue[0]["title"] == "Overdue Task"
    assert overdue[0]["hours_overdue"] >= 23


def test_reminder_scheduler_with_no_reminders(session: Session, test_user: User):
    """Test scheduler with no tasks having reminders."""
    scheduler = ReminderScheduler()
    
    # Create task without reminder
    task = Task(
        user_id=test_user.id,
        title="No Reminder",
        priority=Priority.MEDIUM
    )
    session.add(task)
    session.commit()
    
    reminders = scheduler.get_due_reminders(session)
    assert len(reminders) == 0


# ===== Event Flow Integration Tests =====

def test_event_flow_task_lifecycle(session: Session, test_user: User):
    """Test complete event flow for task lifecycle."""
    publisher = EventPublisher()
    publisher.kafka_enabled = False
    
    # 1. Create task
    task = Task(
        user_id=test_user.id,
        title="Lifecycle Task",
        priority=Priority.HIGH,
        due_date=datetime.utcnow() + timedelta(days=1)
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    
    event1 = publisher.publish_task_created(
        task_id=task.id,
        user_id=str(test_user.id),
        task_data={"title": task.title, "priority": task.priority.value},
        session=session
    )
    
    # 2. Update task
    event2 = publisher.publish_task_updated(
        task_id=task.id,
        user_id=str(test_user.id),
        changes={"title": "Updated Title"},
        session=session
    )
    
    # 3. Complete task
    event3 = publisher.publish_task_completed(
        task_id=task.id,
        user_id=str(test_user.id),
        completed=True,
        session=session
    )
    
    # Verify all events logged
    events = session.exec(
        select(EventLog).where(EventLog.task_id == task.id)
    ).all()
    
    assert len(events) == 3
    event_types = [e.event_type for e in events]
    assert "task.created" in event_types
    assert "task.updated" in event_types
    assert "task.completed" in event_types


def test_singleton_event_publisher():
    """Test get_event_publisher returns singleton."""
    publisher1 = get_event_publisher()
    publisher2 = get_event_publisher()
    assert publisher1 is publisher2


def test_event_publisher_handles_missing_session_gracefully(test_user: User):
    """Test event publisher handles missing session without crashing."""
    publisher = EventPublisher()
    publisher.kafka_enabled = False
    
    # Should not raise exception
    event_id = publisher.publish(
        event_type="test.event",
        topic="test-topic",
        payload={"test": "data"},
        session=None  # No session provided
    )
    
    assert event_id is not None
