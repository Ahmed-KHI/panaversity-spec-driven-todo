"""
Master migration script for Phase V.
[Task]: T-A-008 (Run Migrations)
[From]: specs/005-phase-v-cloud/phase5-cloud.tasks.md

Runs all Phase V migrations in the correct order:
1. Add advanced task fields
2. Create tags tables
3. Create event_log table

Run with: uv run python migrations/run_phase5_migrations.py
"""

import sys
import subprocess
from pathlib import Path


def run_migration(script_name: str) -> bool:
    """Run a migration script and return success status."""
    script_path = Path(__file__).parent / script_name
    
    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            capture_output=False
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Migration failed: {script_name}")
        print(f"Error: {e}")
        return False


def main():
    """Run all Phase V migrations."""
    
    print("🚀 Starting Phase V Database Migrations")
    print("=" * 60)
    
    migrations = [
        "add_advanced_task_fields.py",
        "create_tags_tables.py",
        "create_event_log_table.py"
    ]
    
    failed_migrations = []
    
    for migration in migrations:
        success = run_migration(migration)
        if not success:
            failed_migrations.append(migration)
            
            # Ask if user wants to continue
            response = input("\n⚠️  Migration failed. Continue with remaining migrations? (yes/no): ")
            if response.lower() != "yes":
                break
    
    print("\n" + "=" * 60)
    if failed_migrations:
        print("❌ Some migrations failed:")
        for migration in failed_migrations:
            print(f"  - {migration}")
        sys.exit(1)
    else:
        print("✅ All Phase V migrations completed successfully!")
        print("\nNew database structure:")
        print("  Tasks table:")
        print("    - priority (low/medium/high/urgent)")
        print("    - due_date")
        print("    - reminder_time")
        print("    - is_recurring")
        print("    - recurrence_pattern (JSONB)")
        print("\n  Tags tables:")
        print("    - tags (id, name, color, created_at, created_by)")
        print("    - task_tags (task_id, tag_id)")
        print("\n  Event log:")
        print("    - event_log (audit trail for all events)")
        print("\n🎉 Database is ready for Phase V features!")


if __name__ == "__main__":
    main()
