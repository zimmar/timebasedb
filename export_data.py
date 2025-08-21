#!/usr/bin/env python
"""
Export all data to JSON for backup
"""
import os
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

def export_data():
    """Export all data to JSON"""
    cursor = connection.cursor()
    
    # Export tbdb data
    cursor.execute("SELECT * FROM timebase_tbdb")
    columns = [desc[0] for desc in cursor.description]
    tbdb_data = []
    
    for row in cursor.fetchall():
        row_dict = dict(zip(columns, row))
        # Convert datetime to string
        if 'timestamp' in row_dict and row_dict['timestamp']:
            row_dict['timestamp'] = row_dict['timestamp'].isoformat()
        tbdb_data.append(row_dict)
    
    # Export tbdb_hourly data
    cursor.execute("SELECT * FROM timebase_tbdb_hourly")
    hourly_columns = [desc[0] for desc in cursor.description]
    hourly_data = []
    
    for row in cursor.fetchall():
        row_dict = dict(zip(hourly_columns, row))
        # Convert datetime to string
        if 'timestamp' in row_dict and row_dict['timestamp']:
            row_dict['timestamp'] = row_dict['timestamp'].isoformat()
        hourly_data.append(row_dict)
    
    # Save to JSON
    backup_data = {
        'tbdb': tbdb_data,
        'tbdb_hourly': hourly_data,
        'export_time': datetime.now().isoformat()
    }
    
    with open('data_backup.json', 'w') as f:
        json.dump(backup_data, f, indent=2)
    
    print(f"✅ Exported {len(tbdb_data)} tbdb records and {len(hourly_data)} hourly records")
    print("📁 Saved to data_backup.json")

if __name__ == "__main__":
    export_data()
