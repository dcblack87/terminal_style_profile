#!/usr/bin/env python3
"""
Database Migration Runner

Runs database migrations for the terminal portfolio site.
Works on both local development and PythonAnywhere.

Usage:
    python migrate.py                   # Run all pending migrations
    python migrate.py --list            # List all migrations
    python migrate.py --rollback        # Rollback last migration
    python migrate.py --specific 001    # Run specific migration
"""

import os
import sys
import importlib.util
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def get_migration_files():
    """Get all migration files sorted by number."""
    migrations_dir = Path("migrations")
    migration_files = []
    
    for file in migrations_dir.glob("migration_*.py"):
        if file.name != "__init__.py":
            migration_files.append(file)
    
    # Sort by migration number
    migration_files.sort(key=lambda x: x.stem.split('_')[1])
    return migration_files

def run_migration(migration_file, rollback=False):
    """Run a specific migration file."""
    print(f"{'='*60}")
    print(f"🚀 {'Rolling back' if rollback else 'Running'}: {migration_file.name}")
    print(f"{'='*60}")
    
    # Import the migration module
    spec = importlib.util.spec_from_file_location("migration", migration_file)
    migration_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration_module)
    
    # Run the appropriate function
    if rollback:
        if hasattr(migration_module, 'downgrade'):
            migration_module.downgrade()
        else:
            print("⚠️  No downgrade function found in migration")
    else:
        if hasattr(migration_module, 'upgrade'):
            migration_module.upgrade()
        else:
            print("❌ No upgrade function found in migration")

def create_migrations_table():
    """Create a table to track applied migrations."""
    app = create_app()
    
    with app.app_context():
        try:
            with db.engine.connect() as connection:
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        migration_name VARCHAR(255) NOT NULL UNIQUE,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                connection.commit()
            print("✅ Schema migrations table ready")
        except Exception as e:
            print(f"❌ Failed to create migrations table: {e}")

def mark_migration_applied(migration_name):
    """Mark a migration as applied."""
    app = create_app()
    
    with app.app_context():
        try:
            with db.engine.connect() as connection:
                connection.execute(
                    text("INSERT OR IGNORE INTO schema_migrations (migration_name) VALUES (:name)"), 
                    {"name": migration_name}
                )
                connection.commit()
            print(f"📝 Marked {migration_name} as applied")
        except Exception as e:
            print(f"⚠️  Could not mark migration as applied: {e}")

def is_migration_applied(migration_name):
    """Check if a migration has been applied."""
    app = create_app()
    
    with app.app_context():
        try:
            with db.engine.connect() as connection:
                result = connection.execute(
                    text("SELECT COUNT(*) as count FROM schema_migrations WHERE migration_name = :name"), 
                    {"name": migration_name}
                ).fetchone()
                return result.count > 0
        except:
            # If table doesn't exist, no migrations have been applied
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Migration Runner')
    parser.add_argument('--list', action='store_true', help='List all migration files')
    parser.add_argument('--rollback', action='store_true', help='Rollback the last migration')
    parser.add_argument('--specific', type=str, help='Run specific migration by number (e.g., 001)')
    parser.add_argument('--force', action='store_true', help='Force run migration even if already applied')
    
    args = parser.parse_args()
    
    print("🔧 Terminal Portfolio Migration Runner")
    print("=" * 50)
    
    # Create migrations tracking table
    create_migrations_table()
    
    migration_files = get_migration_files()
    
    if args.list:
        print("\n📋 Available Migrations:")
        for migration_file in migration_files:
            status = "✅ Applied" if is_migration_applied(migration_file.stem) else "⏳ Pending"
            print(f"  {migration_file.stem} - {status}")
        return
    
    if args.specific:
        # Run specific migration
        target_migration = None
        for migration_file in migration_files:
            if args.specific in migration_file.stem:
                target_migration = migration_file
                break
        
        if target_migration:
            if args.force or not is_migration_applied(target_migration.stem):
                run_migration(target_migration, rollback=args.rollback)
                if not args.rollback:
                    mark_migration_applied(target_migration.stem)
            else:
                print(f"⚠️  Migration {target_migration.stem} already applied. Use --force to run anyway.")
        else:
            print(f"❌ Migration {args.specific} not found")
        return
    
    if args.rollback:
        # Find the last applied migration
        print("🔄 Rolling back last migration...")
        # This would need more sophisticated tracking for proper rollbacks
        print("⚠️  Rollback functionality requires manual specification with --specific")
        return
    
    # Run all pending migrations
    print("🚀 Running all pending migrations...")
    pending_count = 0
    
    for migration_file in migration_files:
        if not is_migration_applied(migration_file.stem) or args.force:
            run_migration(migration_file)
            mark_migration_applied(migration_file.stem)
            pending_count += 1
        else:
            print(f"⏭️  Skipping {migration_file.stem} (already applied)")
    
    if pending_count == 0:
        print("✅ No pending migrations found. Database is up to date!")
    else:
        print(f"🎉 Successfully applied {pending_count} migration(s)!")

if __name__ == "__main__":
    main()