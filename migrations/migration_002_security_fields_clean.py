"""
Clean migration to add security and spam detection fields.
Run with: python migrations/migration_002_security_fields_clean.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upgrade():
    """Add security fields to contact_messages and create contact_submission_logs table."""
    app = create_app()
    
    with app.app_context():
        try:
            connection = db.engine.connect()
            
            # Check if columns already exist before adding them
            logger.info("Checking existing schema...")
            
            # Get current columns in contact_messages table
            result = connection.execute(text("PRAGMA table_info(contact_messages)"))
            existing_columns = [row[1] for row in result.fetchall()]
            logger.info(f"Existing columns: {existing_columns}")
            
            # Add new columns only if they don't exist
            new_columns = [
                ("ip_address", "VARCHAR(45)"),
                ("user_agent", "VARCHAR(500)"),
                ("is_spam", "BOOLEAN DEFAULT FALSE"),
                ("spam_score", "FLOAT DEFAULT 0.0")
            ]
            
            for column_name, column_def in new_columns:
                if column_name not in existing_columns:
                    sql = f"ALTER TABLE contact_messages ADD COLUMN {column_name} {column_def}"
                    connection.execute(text(sql))
                    logger.info(f"Added column: {column_name}")
                else:
                    logger.info(f"Column {column_name} already exists, skipping")
            
            # Create contact_submission_logs table if it doesn't exist
            logger.info("Creating contact_submission_logs table...")
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS contact_submission_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address VARCHAR(45) NOT NULL,
                    email VARCHAR(120),
                    submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN DEFAULT TRUE,
                    user_agent VARCHAR(500)
                )
            """))
            
            # Create indexes if they don't exist
            logger.info("Creating indexes...")
            indexes = [
                ("idx_contact_messages_ip_address", "contact_messages", "ip_address"),
                ("idx_submission_logs_ip_address", "contact_submission_logs", "ip_address"),
                ("idx_submission_logs_submitted_at", "contact_submission_logs", "submitted_at"),
                ("idx_submission_logs_email", "contact_submission_logs", "email")
            ]
            
            for index_name, table_name, column_name in indexes:
                try:
                    connection.execute(text(f"""
                        CREATE INDEX IF NOT EXISTS {index_name} 
                        ON {table_name}({column_name})
                    """))
                    logger.info(f"Created index: {index_name}")
                except Exception as e:
                    logger.warning(f"Index {index_name} might already exist: {e}")
            
            # Commit all changes
            connection.commit()
            connection.close()
            
            logger.info("✅ Migration completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            if 'connection' in locals():
                connection.rollback()
                connection.close()
            return False

def downgrade():
    """Remove security fields (for rollback if needed)."""
    app = create_app()
    
    with app.app_context():
        try:
            connection = db.engine.connect()
            
            logger.info("Rolling back migration...")
            
            # SQLite doesn't support DROP COLUMN easily, so we'd need to:
            # 1. Create new table without the columns
            # 2. Copy data
            # 3. Drop old table
            # 4. Rename new table
            
            # For now, just drop the submission logs table
            connection.execute(text("DROP TABLE IF EXISTS contact_submission_logs"))
            logger.info("Dropped contact_submission_logs table")
            
            # Drop indexes
            indexes_to_drop = [
                "idx_contact_messages_ip_address",
                "idx_submission_logs_ip_address", 
                "idx_submission_logs_submitted_at",
                "idx_submission_logs_email"
            ]
            
            for index_name in indexes_to_drop:
                try:
                    connection.execute(text(f"DROP INDEX IF EXISTS {index_name}"))
                    logger.info(f"Dropped index: {index_name}")
                except Exception as e:
                    logger.warning(f"Could not drop index {index_name}: {e}")
            
            connection.commit()
            connection.close()
            
            logger.info("⚠️  Partial rollback completed (columns remain due to SQLite limitations)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            if 'connection' in locals():
                connection.rollback()
                connection.close()
            return False

def check_migration_status():
    """Check if migration has been applied."""
    app = create_app()
    
    with app.app_context():
        try:
            connection = db.engine.connect()
            
            # Check contact_messages columns
            result = connection.execute(text("PRAGMA table_info(contact_messages)"))
            columns = [row[1] for row in result.fetchall()]
            
            security_columns = ['ip_address', 'user_agent', 'is_spam', 'spam_score']
            missing_columns = [col for col in security_columns if col not in columns]
            
            # Check if submission logs table exists
            result = connection.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='contact_submission_logs'
            """))
            submission_table_exists = result.fetchone() is not None
            
            connection.close()
            
            if missing_columns:
                logger.info(f"❌ Migration NOT applied. Missing columns: {missing_columns}")
                return False
            elif not submission_table_exists:
                logger.info("❌ Migration NOT applied. Missing contact_submission_logs table")
                return False
            else:
                logger.info("✅ Migration already applied successfully")
                return True
                
        except Exception as e:
            logger.error(f"❌ Could not check migration status: {e}")
            return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Database migration for contact form security')
    parser.add_argument('action', choices=['upgrade', 'downgrade', 'status'], 
                       help='Migration action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'upgrade':
        success = upgrade()
        sys.exit(0 if success else 1)
    elif args.action == 'downgrade':
        success = downgrade()
        sys.exit(0 if success else 1)
    elif args.action == 'status':
        is_applied = check_migration_status()
        sys.exit(0 if is_applied else 1)