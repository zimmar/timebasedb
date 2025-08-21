#!/usr/bin/env python
"""
Check database table structure
"""
import os
import django
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def check_table_structure():
    """Check the structure of both tables"""
    cursor = connection.cursor()
    
    # Check tbdb table structure
    print("🔍 Checking tbdb table structure:")
    cursor.execute("PRAGMA table_info(timebase_tbdb)")
    tbdb_columns = cursor.fetchall()
    for col in tbdb_columns:
        print(f"   {col[1]} ({col[2]})")
    
    print("\n🔍 Checking tbdb_hourly table structure:")
    cursor.execute("PRAGMA table_info(timebase_tbdb_hourly)")
    hourly_columns = cursor.fetchall()
    for col in hourly_columns:
        print(f"   {col[1]} ({col[2]})")
    
    print("\n📊 Sample data from tbdb_hourly:")
    cursor.execute("SELECT * FROM timebase_tbdb_hourly LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(f"   {row}")

if __name__ == "__main__":
    check_table_structure()
