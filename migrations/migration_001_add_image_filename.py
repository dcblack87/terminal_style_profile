#!/usr/bin/env python3
"""
Migration 001: Add image_filename column to portfolio_items table

This migration adds a new image_filename column to store uploaded image files,
while keeping the existing image_url column for backwards compatibility.

Run with: python migrations/migration_001_add_image_filename.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import PortfolioItem
from sqlalchemy import text

def upgrade():
    """Add image_filename column to portfolio_items table."""
    print("🔄 Running Migration 001: Add image_filename column")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            with db.engine.connect() as connection:
                result = connection.execute(text("""
                    SELECT COUNT(*) as count 
                    FROM pragma_table_info('portfolio_items') 
                    WHERE name='image_filename'
                """)).fetchone()
                
                if result.count > 0:
                    print("✅ Column 'image_filename' already exists, skipping migration")
                    return
                
                # Add the new column
                connection.execute(text("""
                    ALTER TABLE portfolio_items 
                    ADD COLUMN image_filename VARCHAR(255)
                """))
                
                # Commit the transaction
                connection.commit()
            
            print("✅ Successfully added 'image_filename' column to portfolio_items table")
            print("📝 Note: Existing image_url values are preserved")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            raise

def downgrade():
    """Remove image_filename column from portfolio_items table."""
    print("🔄 Rolling back Migration 001: Remove image_filename column")
    
    app = create_app()
    
    with app.app_context():
        try:
            # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
            # This is a destructive operation, so we'll just warn the user
            print("⚠️  SQLite doesn't support DROP COLUMN.")
            print("⚠️  To rollback, you would need to recreate the database.")
            print("⚠️  Make sure you have a backup before proceeding.")
            
        except Exception as e:
            print(f"❌ Rollback failed: {str(e)}")
            raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Portfolio Image Migration')
    parser.add_argument('--rollback', action='store_true', help='Rollback the migration')
    
    args = parser.parse_args()
    
    if args.rollback:
        downgrade()
    else:
        upgrade()
        
    print("🎉 Migration completed successfully!")