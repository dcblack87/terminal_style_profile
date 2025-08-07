"""
Database migration to add security and spam detection fields.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db
import logging

logger = logging.getLogger(__name__)

def upgrade():
    """Add security fields to contact_messages and create contact_submission_logs table."""
    app = create_app()
    
    with app.app_context():
        try:
            # Add new columns to contact_messages table
            db.engine.execute("""
                ALTER TABLE contact_messages 
                ADD COLUMN ip_address VARCHAR(45);
            """)
            
            db.engine.execute("""
                ALTER TABLE contact_messages 
                ADD COLUMN user_agent VARCHAR(500);
            """)
            
            db.engine.execute("""
                ALTER TABLE contact_messages 
                ADD COLUMN is_spam BOOLEAN DEFAULT FALSE;
            """)
            
            db.engine.execute("""
                ALTER TABLE contact_messages 
                ADD COLUMN spam_score FLOAT DEFAULT 0.0;
            """)
            
            # Create index on ip_address for faster lookups
            db.engine.execute("""
                CREATE INDEX IF NOT EXISTS idx_contact_messages_ip_address 
                ON contact_messages(ip_address);
            """)
            
            # Create contact_submission_logs table
            db.engine.execute("""
                CREATE TABLE IF NOT EXISTS contact_submission_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address VARCHAR(45) NOT NULL,
                    email VARCHAR(120),
                    submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN DEFAULT TRUE,
                    user_agent VARCHAR(500)
                );
            """)
            
            # Create indexes for submission logs
            db.engine.execute("""
                CREATE INDEX IF NOT EXISTS idx_submission_logs_ip_address 
                ON contact_submission_logs(ip_address);
            """)
            
            db.engine.execute("""
                CREATE INDEX IF NOT EXISTS idx_submission_logs_submitted_at 
                ON contact_submission_logs(submitted_at);
            """)
            
            db.engine.execute("""
                CREATE INDEX IF NOT EXISTS idx_submission_logs_email 
                ON contact_submission_logs(email);
            """)
            
            logger.info("Successfully added security fields and submission tracking table")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False

def downgrade():
    """Remove security fields (for rollback if needed)."""
    try:
        # Remove columns from contact_messages (SQLite doesn't support DROP COLUMN easily)
        # In a production environment, you'd want to create a new table and migrate data
        logger.warning("Downgrade not fully implemented for SQLite - would require table recreation")
        
        # Drop the submission logs table
        db.engine.execute("DROP TABLE IF EXISTS contact_submission_logs;")
        
        logger.info("Partially rolled back security migration")
        return True
        
    except Exception as e:
        logger.error(f"Migration rollback failed: {e}")
        return False

if __name__ == "__main__":
    # Allow running migration directly
    from app import create_app
    
    app = create_app()
    with app.app_context():
        success = upgrade()
        if success:
            print("✅ Migration completed successfully")
        else:
            print("❌ Migration failed")