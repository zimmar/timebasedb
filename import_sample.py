#!/usr/bin/env python
"""
Import sample data from backup to test simplified models
"""
import os
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from timebase.models import tbdb
from django.utils import timezone

def import_sample_data():
    """Import first 1000 records for testing"""
    with open('data_backup.json', 'r') as f:
        backup_data = json.load(f)
    
    sample_records = backup_data['tbdb'][:1000]  # Import first 1000 records
    
    print(f"📥 Importing {len(sample_records)} sample records...")
    
    for i, record in enumerate(sample_records):
        try:
            # Parse timestamp
            timestamp = datetime.fromisoformat(record['timestamp'])
            if timestamp.tzinfo is None:
                timestamp = timezone.make_aware(timestamp)
            
            # Create record
            tbdb.objects.create(
                timestamp=timestamp,
                measurement_name=record['measurement_name'],
                measurement_type=record['measurement_type'],
                value=record['value']
            )
            
            if (i + 1) % 100 == 0:
                print(f"   📦 Imported {i + 1} records...")
                
        except Exception as e:
            print(f"❌ Error importing record {i}: {e}")
            continue
    
    print(f"✅ Import complete! Total records in tbdb: {tbdb.objects.count()}")
    
    # Test a few operations
    print("\n🧪 Testing simplified models:")
    print(f"   Count for temp1: {tbdb.count('temp1')}")
    print(f"   Average for temp1: {tbdb.avg('temp1'):.2f}")
    print(f"   Latest temp1: {tbdb.latest('temp1').data}")

if __name__ == "__main__":
    import_sample_data()
