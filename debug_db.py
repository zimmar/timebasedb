#!/usr/bin/env python
"""
Check actual database schema and content
"""
import os
import django
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def check_database():
    """Check the actual database content"""
    cursor = connection.cursor()
    
    print("🔍 Checking actual tbdb data:")
    cursor.execute("SELECT * FROM timebase_tbdb LIMIT 5")
    columns = [desc[0] for desc in cursor.description]
    print(f"Columns: {columns}")
    
    rows = cursor.fetchall()
    for i, row in enumerate(rows):
        print(f"Row {i+1}: {dict(zip(columns, row))}")

if __name__ == "__main__":
    check_database()
