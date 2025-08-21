#!/usr/bin/env python
"""
Drop the tbdb_hourly table and recreate it properly
"""
import os
import django
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def drop_hourly_table():
    """Drop the tbdb_hourly table"""
    cursor = connection.cursor()
    
    try:
        cursor.execute("DROP TABLE IF EXISTS timebase_tbdb_hourly")
        print("✅ Dropped timebase_tbdb_hourly table")
    except Exception as e:
        print(f"❌ Error dropping table: {e}")

if __name__ == "__main__":
    drop_hourly_table()
