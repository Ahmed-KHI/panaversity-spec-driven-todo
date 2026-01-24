"""
Database migration script for Phase V: Create tags tables.
[Task]: T-A-002
[From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §2.4
        specs/005-phase-v-cloud/phase5-cloud.plan.md §2.2

This script creates:
- tags table (id, name, color, created_at, created_by)
- task_tags junction table (task_id, tag_id)

Run with: uv run python migrations/create_tags_tables.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlmodel import create_engine, text
from src.config import settings


def upgrade():
    """Create tags and task_tags tables."""
    
    print("🔗 Connecting to database...")
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    print("\n📋 Creating tags tables...")
    
    with engine.begin() as conn:
        # Check if tables already exist
        check_tags = text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'tags'
            )
        """)
        check_task_tags = text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'task_tags'
            )
        """)
        
        tags_exists = conn.execute(check_tags).scalar()
        task_tags_exists = conn.execute(check_task_tags).scalar()
        
        # Create tags table
        if not tags_exists:
            print("Creating table: tags")
            conn.execute(text("""
                CREATE TABLE tags (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) UNIQUE NOT NULL,
                    color VARCHAR(7) DEFAULT '#3B82F6' NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
                )
            """))
            print("✓ Table created: tags")
        else:
            print("⚠️  Table 'tags' already exists, skipping...")
        
        # Create task_tags junction table
        if not task_tags_exists:
            print("Creating table: task_tags")
            conn.execute(text("""
                CREATE TABLE task_tags (
                    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
                    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
                    PRIMARY KEY (task_id, tag_id)
                )
            """))
            print("✓ Table created: task_tags")
        else:
            print("⚠️  Table 'task_tags' already exists, skipping...")
        
        print("\n📊 Creating indexes...")
        
        # Create indexes for performance
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_tags_name 
                ON tags(name)
            """))
            print("✓ Index created: idx_tags_name")
        except Exception as e:
            print(f"⚠️  Index may already exist: {e}")
        
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_task_tags_task 
                ON task_tags(task_id)
            """))
            print("✓ Index created: idx_task_tags_task")
        except Exception as e:
            print(f"⚠️  Index may already exist: {e}")
        
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_task_tags_tag 
                ON task_tags(tag_id)
            """))
            print("✓ Index created: idx_task_tags_tag")
        except Exception as e:
            print(f"⚠️  Index may already exist: {e}")
    
    print("\n✅ Migration completed successfully!")
    print("Tables created:")
    print("  - tags (id, name, color, created_at, created_by)")
    print("  - task_tags (task_id, tag_id)")
    print("\nIndexes created:")
    print("  - idx_tags_name")
    print("  - idx_task_tags_task")
    print("  - idx_task_tags_tag")


def downgrade():
    """Drop tags and task_tags tables (rollback)."""
    
    print("🔗 Connecting to database...")
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    print("\n⚠️  Rolling back migration...")
    print("This will drop the following tables:")
    print("  - task_tags")
    print("  - tags")
    
    confirm = input("\nAre you sure you want to continue? (yes/no): ")
    if confirm.lower() != "yes":
        print("❌ Rollback cancelled.")
        return
    
    with engine.begin() as conn:
        print("\n🗑️  Dropping tables...")
        conn.execute(text("DROP TABLE IF EXISTS task_tags CASCADE"))
        print("✓ Dropped table: task_tags")
        
        conn.execute(text("DROP TABLE IF EXISTS tags CASCADE"))
        print("✓ Dropped table: tags")
    
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
