#!/usr/bin/env python3
"""
Database schema migration script
Adds process monitoring columns to existing alerts table
"""

import sqlite3
import os

DB_PATH = "epa.db"

def migrate_database():
    """Add process monitoring columns to alerts table"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Check current schema
        cur.execute("PRAGMA table_info(alerts)")
        columns = [row[1] for row in cur.fetchall()]
        
        print("Current alerts table columns:")
        for col in columns:
            print(f"  - {col}")
        
        # Add missing columns
        new_columns = {
            'process_id': 'INTEGER',
            'process_name': 'TEXT',
            'process_cmdline': 'TEXT',
            'process_parent': 'TEXT'
        }
        
        added = []
        for col_name, col_type in new_columns.items():
            if col_name not in columns:
                print(f"\n➕ Adding column: {col_name} ({col_type})")
                cur.execute(f"ALTER TABLE alerts ADD COLUMN {col_name} {col_type}")
                added.append(col_name)
        
        if added:
            conn.commit()
            print(f"\n✅ Successfully added {len(added)} columns: {', '.join(added)}")
        else:
            print("\n✅ All columns already exist - no migration needed")
        
        # Verify final schema
        cur.execute("PRAGMA table_info(alerts)")
        final_columns = [row[1] for row in cur.fetchall()]
        
        print("\nFinal alerts table columns:")
        for col in final_columns:
            print(f"  - {col}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("EPA Database Schema Migration")
    print("=" * 60)
    print()
    
    success = migrate_database()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Migration complete! Please refresh the dashboard.")
    else:
        print("❌ Migration failed. Please check the error above.")
    print("=" * 60)
