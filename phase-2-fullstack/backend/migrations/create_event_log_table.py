"""
Database migration script for Phase V: Create event_log table.
[Task]: T-A-003
[From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §3.1
        specs/005-phase-v-cloud/phase5-cloud.plan.md §2.4

This script creates the event_log table for audit trail:
- Stores all events published to Kafka
- Provides complete activity history
- Enables debugging and analytics

Run with: uv run python migrations/create_event_log_table.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlmodel import create_engine, text
from src.config import settings


def upgrade():
    """Create event_log table."""
    
    print("🔗 Connecting to database...")
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    print("\n📋 Creating event_log table...")
    
    with engine.begin() as conn:
        # Check if table already exists
        check_query = text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'event_log'
            )
        """)
        
        table_exists = conn.execute(check_query).scalar()
        
        if not table_exists:
            print("Creating table: event_log")
            conn.execute(text("""
                CREATE TABLE event_log (
                    id SERIAL PRIMARY KEY,
                    event_id UUID UNIQUE NOT NULL,
                    event_type VARCHAR(50) NOT NULL,
                    topic VARCHAR(50) NOT NULL,
                    task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
                    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
                    payload JSONB NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    processed BOOLEAN DEFAULT FALSE NOT NULL
                )
            """))
            print("✓ Table created: event_log")
        else:
            print("⚠️  Table 'event_log' already exists, skipping...")
        
        print("\n📊 Creating indexes...")
        
        # Create indexes for performance
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_event_log_timestamp 
                ON event_log(timestamp)
            """))
            print("✓ Index created: idx_event_log_timestamp")
        except Exception as e:
            print(f"⚠️  Index may already exist: {e}")
        
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_event_log_task 
                ON event_log(task_id) 
                WHERE task_id IS NOT NULL
            """))
            print("✓ Index created: idx_event_log_task")
        except Exception as e:
            print(f"⚠️  Index may already exist: {e}")
        
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_event_log_type 
                ON event_log(event_type)
            """))
            print("✓ Index created: idx_event_log_type")
        except Exception as e:
            print(f"⚠️  Index may already exist: {e}")
        
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_event_log_event_id 
                ON event_log(event_id)
            """))
            print("✓ Index created: idx_event_log_event_id")
        except Exception as e:
            print(f"⚠️  Index may already exist: {e}")
        
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_event_log_user 
                ON event_log(user_id) 
                WHERE user_id IS NOT NULL
            """))
            print("✓ Index created: idx_event_log_user")
        except Exception as e:
            print(f"⚠️  Index may already exist: {e}")
    
    print("\n✅ Migration completed successfully!")
    print("Table created:")
    print("  - event_log (id, event_id, event_type, topic, task_id, user_id, payload, timestamp, processed)")
    print("\nIndexes created:")
    print("  - idx_event_log_timestamp")
    print("  - idx_event_log_task")
    print("  - idx_event_log_type")
    print("  - idx_event_log_event_id")
    print("  - idx_event_log_user")


def downgrade():
    """Drop event_log table (rollback)."""
    
    print("🔗 Connecting to database...")
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    print("\n⚠️  Rolling back migration...")
    print("This will drop the event_log table and all audit data!")
    
    confirm = input("\nAre you sure you want to continue? (yes/no): ")
    if confirm.lower() != "yes":
        print("❌ Rollback cancelled.")
        return
    
    with engine.begin() as conn:
        print("\n🗑️  Dropping table...")
        conn.execute(text("DROP TABLE IF EXISTS event_log CASCADE"))
        print("✓ Dropped table: event_log")
    
    print("\n✅ Rollback completed successfully!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        try:
            downgrade()
        except Exception as e:
            print(f"\n❌ Rollback error: {e}")
            sys.exit(1)
    else:
        try:
            upgrade()
        except Exception as e:
            print(f"\n❌ Migration error: {e}")
            sys.exit(1)
