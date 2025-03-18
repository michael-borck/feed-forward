#!/usr/bin/env python
"""
Migration script to update the ai_models table schema
Adds owner_type and owner_id fields for supporting both system-wide and instructor-specific models
"""
import sqlite3
import os
import pathlib

# Get the database path
project_root = pathlib.Path(__file__).parent.parent
db_path = project_root / "data" / "users.db"

def migrate_ai_models_table():
    print(f"Starting migration for AI models table in {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ai_models'")
        if not cursor.fetchone():
            print("ai_models table does not exist. No migration needed.")
            return
        
        # Check if the columns already exist
        cursor.execute("PRAGMA table_info(ai_models)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'owner_type' not in columns and 'owner_id' not in columns:
            print("Adding new columns to ai_models table...")
            
            # Add new columns
            cursor.execute("ALTER TABLE ai_models ADD COLUMN owner_type TEXT DEFAULT 'system'")
            cursor.execute("ALTER TABLE ai_models ADD COLUMN owner_id TEXT DEFAULT ''")
            
            # Commit the changes
            conn.commit()
            print("Migration completed successfully!")
        else:
            print("Columns already exist. No migration needed.")
    
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        conn.rollback()
    
    finally:
        # Close the connection
        conn.close()

if __name__ == "__main__":
    migrate_ai_models_table()