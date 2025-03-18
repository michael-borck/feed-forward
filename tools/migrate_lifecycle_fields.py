#!/usr/bin/env python
"""
Migration script to add lifecycle management fields to existing tables
Adds status fields to users, courses, and assignments tables
"""
import sqlite3
import os
import pathlib
from datetime import datetime

# Get the database path
project_root = pathlib.Path(__file__).parent.parent
db_path = project_root / "data" / "users.db"

def get_current_time():
    """Return current time in ISO format"""
    return datetime.now().isoformat()

def migrate_tables():
    print(f"Starting migration for lifecycle management fields in {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Migrate users table
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [column[1] for column in cursor.fetchall()]
        
        changes_made = False
        
        # Check and add status field to users table
        if 'status' not in user_columns:
            print("Adding status field to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'active'")
            changes_made = True
        
        # Check and add last_active field to users table
        if 'last_active' not in user_columns:
            print("Adding last_active field to users table...")
            cursor.execute(f"ALTER TABLE users ADD COLUMN last_active TEXT DEFAULT '{get_current_time()}'")
            changes_made = True
        
        # Migrate courses table
        cursor.execute("PRAGMA table_info(courses)")
        course_columns = [column[1] for column in cursor.fetchall()]
        
        # Check and add status field to courses table
        if 'status' not in course_columns:
            print("Adding status field to courses table...")
            cursor.execute("ALTER TABLE courses ADD COLUMN status TEXT DEFAULT 'active'")
            changes_made = True
        
        # Check and add created_at field to courses table
        if 'created_at' not in course_columns:
            print("Adding created_at field to courses table...")
            cursor.execute(f"ALTER TABLE courses ADD COLUMN created_at TEXT DEFAULT '{get_current_time()}'")
            changes_made = True
        
        # Check and add updated_at field to courses table
        if 'updated_at' not in course_columns:
            print("Adding updated_at field to courses table...")
            cursor.execute(f"ALTER TABLE courses ADD COLUMN updated_at TEXT DEFAULT '{get_current_time()}'")
            changes_made = True
        
        # Migrate assignments table
        cursor.execute("PRAGMA table_info(assignments)")
        assignment_columns = [column[1] for column in cursor.fetchall()]
        
        # Check and add status field to assignments table
        if 'status' not in assignment_columns:
            print("Adding status field to assignments table...")
            cursor.execute("ALTER TABLE assignments ADD COLUMN status TEXT DEFAULT 'active'")
            changes_made = True
        
        # Check and add created_at field to assignments table
        if 'created_at' not in assignment_columns:
            print("Adding created_at field to assignments table...")
            cursor.execute(f"ALTER TABLE assignments ADD COLUMN created_at TEXT DEFAULT '{get_current_time()}'")
            changes_made = True
        
        # Check and add updated_at field to assignments table
        if 'updated_at' not in assignment_columns:
            print("Adding updated_at field to assignments table...")
            cursor.execute(f"ALTER TABLE assignments ADD COLUMN updated_at TEXT DEFAULT '{get_current_time()}'")
            changes_made = True
        
        # Commit the changes
        conn.commit()
        
        if changes_made:
            print("Migration completed successfully!")
        else:
            print("No changes needed. All fields already exist.")
    
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        conn.rollback()
    
    finally:
        # Close the connection
        conn.close()

if __name__ == "__main__":
    migrate_tables()