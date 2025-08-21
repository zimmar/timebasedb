#!/usr/bin/env python
"""
Check Django migrations table
"""
import os
import django
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def check_migrations():
    """Check Django migrations"""
    cursor = connection.cursor()
    
    print("🔍 Checking django_migrations:")
    cursor.execute("SELECT app, name FROM django_migrations WHERE app = 'timebase'")
    
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row[0]}: {row[1]}")

if __name__ == "__main__":
    check_migrations()
