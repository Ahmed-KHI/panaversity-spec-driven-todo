"""
Database migration script for Phase V: Add advanced task fields.
[Task]: T-A-001
[From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §2.1-2.5
        specs/005-phase-v-cloud/phase5-cloud.plan.md §2.1

This script adds new columns to the tasks table:
- priority (enum: low, medium, high, urgent)
- due_date (timestamp with timezone)
- reminder_time (timestamp with timezone)
- is_recurring (boolean)
- recurrence_pattern (JSONB)

Run with: uv run python migrations/add_advanced_task_fields.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlmodel import create_engine, text
from src.config import settings


def upgrade():
    """Add advanced task fields to tasks table."""
    
    print("🔗 Connecting to database...")
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    print("\n📋 Adding new columns to tasks table...")
    
    with engine.begin() as conn:
        # Check if columns already exist
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tasks' 
            AND column_name IN ('priority', 'due_date', 'reminder_time', 'is_recurring', 'recurrence_pattern')
        """)
        existing_columns = [row[0] for row in conn.execute(check_query)]
        
        if existing_columns:
            print(f"\n⚠️  Some columns already exist: {existing_columns}")
            print("Skipping columns that already exist...")
        
        # Add priority column
        if 'priority' not in existing_columns:
            print("Adding column: priority")
            conn.execute(text("""
                ALTER TABLE tasks 
                ADD COLUMN priority VARCHAR(10) DEFAULT 'medium' NOT NULL
            """))
        
        # Add due_date column
        if 'due_date' not in existing_columns:
            print("Adding column: due_date")
            conn.execute(text("""
                ALTER TABLE tasks 
                ADD COLUMN due_date TIMESTAMP WITH TIME ZONE
            """))
        
        # Add reminder_time column
        if 'reminder_time' not in existing_columns:
            print("Adding column: reminder_time")
            conn.execute(text("""
                ALTER TABLE tasks 
                ADD COLUMN reminder_time TIMESTAMP WITH TIME ZONE
            """))
        
        # Add is_recurring column
        if 'is_recurring' not in existing_columns:
            print("Adding column: is_recurring")
            conn.execute(text("""
                ALTER TABLE tasks 
                ADD COLUMN is_recurring BOOLEAN DEFAULT FALSE NOT NULL
            """))
        
        # Add recurrence_pattern column (JSONB)
        if 'recurrence_pattern' not in existing_columns:
            print("Adding column: recurrence_pattern")
            conn.execute(text("""
                ALTER TABLE tasks 
                ADD COLUMN recurrence_pattern JSONB
            """))
        
        print("\n📊 Creating indexes...")
        
        # Create indexes for performance
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_tasks_due_date 
                ON tasks(due_date) 
                WHERE due_date IS NOT NULL
            """))
            print("✓ Index created: idx_tasks_due_date")
        except Exception as e:
            print(f"⚠️  Index idx_tasks_due_date may already exist: {e}")
        
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_tasks_priority 
                ON tasks(priority)
            """))
            print("✓ Index created: idx_tasks_priority")
        except Exception as e:
            print(f"⚠️  Index idx_tasks_priority may already exist: {e}")
        
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_tasks_is_recurring 
                ON tasks(is_recurring) 
                WHERE is_recurring = TRUE
            """))
            print("✓ Index created: idx_tasks_is_recurring")
        except Exception as e:
            print(f"⚠️  Index idx_tasks_is_recurring may already exist: {e}")
        
        print("\n🔒 Adding check constraint for priority...")
        
        # Add check constraint for priority enum
        try:
            conn.execute(text("""
                ALTER TABLE tasks 
                ADD CONSTRAINT chk_priority 
                CHECK (priority IN ('low', 'medium', 'high', 'urgent'))
            """))
            print("✓ Constraint added: chk_priority")
        except Exception as e:
            print(f"⚠️  Constraint chk_priority may already exist: {e}")
    
    print("\n✅ Migration completed successfully!")
    print("New columns added to tasks table:")
    print("  - priority (VARCHAR(10), default: 'medium')")
    print("  - due_date (TIMESTAMP WITH TIME ZONE)")
    print("  - reminder_time (TIMESTAMP WITH TIME ZONE)")
    print("  - is_recurring (BOOLEAN, default: FALSE)")
    print("  - recurrence_pattern (JSONB)")
    print("\nIndexes created:")
    print("  - idx_tasks_due_date")
    print("  - idx_tasks_priority")
    print("  - idx_tasks_is_recurring")
    print("\nConstraints added:")
    print("  - chk_priority (priority IN ('low', 'medium', 'high', 'urgent'))")


def downgrade():
    """Remove advanced task fields from tasks table (rollback)."""
    
    print("🔗 Connecting to database...")
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    print("\n⚠️  Rolling back migration...")
    print("This will remove the following columns from tasks table:")
    print("  - priority")
    print("  - due_date")
    print("  - reminder_time")
    print("  - is_recurring")
    print("  - recurrence_pattern")
    
    confirm = input("\nAre you sure you want to continue? (yes/no): ")
    if confirm.lower() != "yes":
        print("❌ Rollback cancelled.")
        return
    
    with engine.begin() as conn:
        print("\n🗑️  Dropping indexes...")
        conn.execute(text("DROP INDEX IF EXISTS idx_tasks_due_date"))
        conn.execute(text("DROP INDEX IF EXISTS idx_tasks_priority"))
        conn.execute(text("DROP INDEX IF EXISTS idx_tasks_is_recurring"))
        
        print("🗑️  Dropping constraint...")
        conn.execute(text("ALTER TABLE tasks DROP CONSTRAINT IF EXISTS chk_priority"))
        
        print("🗑️  Dropping columns...")
        conn.execute(text("ALTER TABLE tasks DROP COLUMN IF EXISTS priority"))
        conn.execute(text("ALTER TABLE tasks DROP COLUMN IF EXISTS due_date"))
        conn.execute(text("ALTER TABLE tasks DROP COLUMN IF EXISTS reminder_time"))
        conn.execute(text("ALTER TABLE tasks DROP COLUMN IF EXISTS is_recurring"))
        conn.execute(text("ALTER TABLE tasks DROP COLUMN IF EXISTS recurrence_pattern"))
    
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
