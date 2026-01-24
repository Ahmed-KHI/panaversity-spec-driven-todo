"""
Seed database with sample data for Phase V testing.
[Task]: T-A-009 (Phase V Seed Data)
[From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §2.1-2.5,
        specs/005-phase-v-cloud/phase5-cloud.tasks.md §A.9
"""

import asyncio
from datetime import datetime, timedelta
from uuid import UUID
from sqlmodel import Session, select
from src.database import engine
from src.models import User, Task, Tag, TaskTag, Priority, RecurrenceFrequency, RecurrencePattern


async def seed_data():
    """Seed database with Phase V sample data."""
    print("🌱 Seeding database with Phase V data...")
    
    with Session(engine) as session:
        # Check if we already have data
        existing_tasks = session.exec(select(Task)).first()
        if existing_tasks:
            print("⚠️  Database already contains data. Skipping seed.")
            return
        
        # Create test user (use existing user if available)
        test_user = session.exec(
            select(User).where(User.email == "test@example.com")
        ).first()
        
        if not test_user:
            print("❌ No test user found. Please create a user first.")
            return
        
        print(f"👤 Using test user: {test_user.email} (ID: {test_user.id})")
        
        # Create tags
        tags_data = [
            {"name": "Work", "color": "#3B82F6"},  # Blue
            {"name": "Personal", "color": "#10B981"},  # Green
            {"name": "Urgent", "color": "#EF4444"},  # Red
            {"name": "Learning", "color": "#8B5CF6"},  # Purple
            {"name": "Health", "color": "#F59E0B"},  # Amber
        ]
        
        tags = []
        for tag_data in tags_data:
            tag = Tag(
                name=tag_data["name"],
                color=tag_data["color"],
                created_by=test_user.id
            )
            session.add(tag)
            tags.append(tag)
        
        session.commit()
        for tag in tags:
            session.refresh(tag)
        print(f"✅ Created {len(tags)} tags")
        
        # Create sample tasks with Phase V features
        now = datetime.utcnow()
        
        tasks_data = [
            {
                "title": "Complete project report",
                "description": "Finish the Q4 project summary report",
                "priority": Priority.HIGH,
                "due_date": now + timedelta(days=2),
                "reminder_time": now + timedelta(days=1, hours=9),
                "tags": ["Work", "Urgent"],
            },
            {
                "title": "Daily standup meeting",
                "description": "Team standup every weekday at 9 AM",
                "priority": Priority.MEDIUM,
                "due_date": now + timedelta(days=1, hours=9),
                "is_recurring": True,
                "recurrence_pattern": {
                    "frequency": RecurrenceFrequency.WEEKLY,
                    "interval": 1,
                    "days_of_week": [0, 1, 2, 3, 4],  # Monday to Friday
                },
                "tags": ["Work"],
            },
            {
                "title": "Gym workout",
                "description": "30 minutes cardio + strength training",
                "priority": Priority.MEDIUM,
                "due_date": now + timedelta(hours=18),
                "is_recurring": True,
                "recurrence_pattern": {
                    "frequency": RecurrenceFrequency.WEEKLY,
                    "interval": 1,
                    "days_of_week": [0, 2, 4],  # Mon, Wed, Fri
                    "occurrences": 12,
                },
                "tags": ["Personal", "Health"],
            },
            {
                "title": "Review Python course",
                "description": "Complete FastAPI advanced module",
                "priority": Priority.LOW,
                "due_date": now + timedelta(days=7),
                "tags": ["Learning", "Personal"],
            },
            {
                "title": "Pay electricity bill",
                "description": "Monthly electricity bill payment",
                "priority": Priority.HIGH,
                "due_date": now + timedelta(days=5),
                "reminder_time": now + timedelta(days=4, hours=10),
                "is_recurring": True,
                "recurrence_pattern": {
                    "frequency": RecurrenceFrequency.MONTHLY,
                    "interval": 1,
                    "day_of_month": 15,
                },
                "tags": ["Personal", "Urgent"],
            },
            {
                "title": "Team retrospective",
                "description": "Monthly team retrospective meeting",
                "priority": Priority.MEDIUM,
                "due_date": now + timedelta(days=25),
                "is_recurring": True,
                "recurrence_pattern": {
                    "frequency": RecurrenceFrequency.MONTHLY,
                    "interval": 1,
                    "day_of_month": 1,
                    "occurrences": 6,
                },
                "tags": ["Work"],
            },
            {
                "title": "Read book chapter",
                "description": "Read one chapter of 'Clean Architecture' daily",
                "priority": Priority.LOW,
                "is_recurring": True,
                "recurrence_pattern": {
                    "frequency": RecurrenceFrequency.DAILY,
                    "interval": 1,
                    "end_date": (now + timedelta(days=30)).date(),
                },
                "tags": ["Learning", "Personal"],
            },
            {
                "title": "Submit tax documents",
                "description": "Annual tax filing deadline",
                "priority": Priority.URGENT,
                "due_date": datetime(2025, 4, 15, 23, 59),
                "reminder_time": datetime(2025, 4, 1, 9, 0),
                "tags": ["Personal", "Urgent"],
            },
            {
                "title": "Water plants",
                "description": "Water all indoor plants",
                "priority": Priority.LOW,
                "is_recurring": True,
                "recurrence_pattern": {
                    "frequency": RecurrenceFrequency.WEEKLY,
                    "interval": 1,
                    "days_of_week": [6],  # Sunday
                },
                "tags": ["Personal"],
            },
            {
                "title": "Code review for PR #245",
                "description": "Review authentication refactoring PR",
                "priority": Priority.HIGH,
                "due_date": now + timedelta(hours=6),
                "reminder_time": now + timedelta(hours=3),
                "tags": ["Work", "Urgent"],
            },
        ]
        
        for task_data in tasks_data:
            # Extract tags from task data
            tag_names = task_data.pop("tags", [])
            
            # Convert recurrence_pattern dict to RecurrencePattern model
            if "recurrence_pattern" in task_data and task_data["recurrence_pattern"]:
                pattern_dict = task_data["recurrence_pattern"]
                pattern = RecurrencePattern(**pattern_dict)
                task_data["recurrence_pattern"] = pattern.model_dump()
            
            # Create task
            task = Task(
                user_id=test_user.id,
                **task_data
            )
            session.add(task)
            session.flush()  # Get task ID
            
            # Associate tags
            for tag_name in tag_names:
                tag = next((t for t in tags if t.name == tag_name), None)
                if tag:
                    task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
                    session.add(task_tag)
        
        session.commit()
        print(f"✅ Created {len(tasks_data)} sample tasks with priorities, due dates, recurrence, and tags")
        
        # Summary
        print("\n📊 Seed Summary:")
        print(f"   - Tags: {len(tags)}")
        print(f"   - Tasks: {len(tasks_data)}")
        print(f"   - Recurring tasks: {sum(1 for t in tasks_data if t.get('is_recurring', False))}")
        print(f"   - High priority tasks: {sum(1 for t in tasks_data if t.get('priority') == Priority.HIGH)}")
        print(f"   - Urgent tasks: {sum(1 for t in tasks_data if t.get('priority') == Priority.URGENT)}")
        print("\n✅ Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_data())
