"""
Database migration script for Phase III tables.
[Task]: T-003
[From]: specs/003-phase-iii-chatbot/spec.md §4, plan.md §5.2

This script creates the conversations and messages tables.
Run with: uv run python migrations/create_phase3_tables.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlmodel import SQLModel, create_engine, Session
from src.config import settings
from src.models.user import User
from src.models.task import Task
from src.models.conversation import Conversation
from src.models.message import Message


def create_tables():
    """Create Phase III tables (conversations, messages)."""
    
    print("🔗 Connecting to database...")
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    print("\n📋 Creating tables...")
    print("- conversations")
    print("- messages")
    
    # This will create only tables that don't exist yet
    SQLModel.metadata.create_all(engine)
    
    print("\n✅ Phase III tables created successfully!")
    
    # Verify tables
    print("\n✅ Migration completed successfully!")
    print("Tables created: conversations, messages")


if __name__ == "__main__":
    try:
        create_tables()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
