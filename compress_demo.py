#!/usr/bin/env python
"""
Demonstration script for database compression functionality.
This script shows how to compress time-dependent data from tbdb to tbdb_hourly.
"""
import os
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Now import the Django models
from timebase.models import tbdb, tbdb_hourly

def demonstrate_compression():
    """Demonstrate the compression functionality"""
    
    print("🔄 Database Compression Demonstration")
    print("=" * 50)
    
    # Check if we have any data in the main table
    total_records = tbdb.objects.count()
    print(f"\n📊 Current data in tbdb: {total_records:,} records")
    
    if total_records == 0:
        print("❌ No data found in tbdb table.")
        print("💡 Run 'python generate_temp_data.py' first to create sample data.")
        return
    
    # Show some example data before compression
    print("\n🔍 Sample data from tbdb (before compression):")
    # Use working methods instead of model instances
    temp1_values = tbdb.all_values('temp1')[:5]
    for i, value in enumerate(temp1_values):
        print(f"   {i+1}.  {value:5.1f}°C")
    
    # Check current hourly table state
    hourly_count = tbdb_hourly.objects.count()
    print(f"\n📊 Current data in tbdb_hourly: {hourly_count:,} records")
    
    # Perform compression
    print(f"\n🗜️  Starting compression process...")
    
    # Get date range for compression (e.g., last 7 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"📅 Compressing data from {start_date.strftime('%Y-%m-%d %H:%M')} to {end_date.strftime('%Y-%m-%d %H:%M')}")
    
    # Perform the compression
    compression_results = tbdb.compress_to_hourly(start_date, end_date)
    
    print(f"\n✅ Compression complete!")
    print(f"📈 Created {len(compression_results):,} hourly records")
    
    if compression_results:
        print(f"\n🔍 Sample of compressed data:")
        for i, result in enumerate(compression_results[:5]):
            print(f"   {i+1}. {result['measurement_name']}: {result['average_value']:.1f} at {result['timestamp'].strftime('%Y-%m-%d %H:%M')}")
    
    # Show statistics comparison
    print(f"\n📊 Compression Statistics:")
    print(f"   • Original tbdb records: {total_records:,}")
    print(f"   • Compressed tbdb_hourly records: {tbdb_hourly.objects.count():,}")
    
    # Demonstrate that all tbdb functions work on tbdb_hourly
    print(f"\n🧪 Testing tbdb_hourly functionality:")
    
    for sensor_name in ['temp1', 'temp2', 'temp3']:
        try:
            count = tbdb_hourly.count(sensor_name)
            if count > 0:
                avg_temp = tbdb_hourly.avg(sensor_name)
                min_temp = tbdb_hourly.min_value(sensor_name)
                max_temp = tbdb_hourly.max_value(sensor_name)
                latest = tbdb_hourly.latest(sensor_name)
                
                print(f"   🌡️  {sensor_name} (hourly compressed):")
                print(f"      • Count: {count:,} hourly records")
                print(f"      • Average: {avg_temp:.1f}°C")
                print(f"      • Range: {min_temp:.1f}°C to {max_temp:.1f}°C")
                if latest:
                    # Use the latest method result differently since .data may not work
                    latest_values = tbdb_hourly.all_values(sensor_name)
                    if latest_values:
                        print(f"      • Latest: {latest_values[0]:.1f}°C")
        except Exception as e:
            print(f"   ❌ Error with {sensor_name}: {e}")
    
    # Show some example queries
    print(f"\n🔍 Example queries on compressed data:")
    
    # Get hourly statistics for a specific period
    try:
        yesterday = datetime.now() - timedelta(days=1)
        today = datetime.now()
        
        stats = tbdb_hourly.get_hourly_statistics('temp1', yesterday, today)
        print(f"   📈 temp1 statistics for last 24 hours:")
        print(f"      • Hourly records: {stats['count']}")
        if stats['avg']:
            print(f"      • Average: {stats['avg']:.1f}°C")
            print(f"      • Min: {stats['min']:.1f}°C")
            print(f"      • Max: {stats['max']:.1f}°C")
    except Exception as e:
        print(f"   ❌ Error getting statistics: {e}")
    
    print(f"\n🎉 Demonstration complete!")
    print(f"\n💡 Key benefits of compression:")
    print(f"   • Reduced storage space")
    print(f"   • Faster queries on large datasets")
    print(f"   • Preserved data trends and patterns")
    print(f"   • All original tbdb functions work on tbdb_hourly")

def show_compression_example():
    """Show a specific example of how compression works"""
    print(f"\n📚 Compression Example:")
    print(f"=" * 30)
    print(f"Original data (every 5 minutes):")
    print(f"   2025-07-22 18:00:00 - temp1: 20.5°C")
    print(f"   2025-07-22 18:05:00 - temp1: 21.2°C") 
    print(f"   2025-07-22 18:10:00 - temp1: 20.8°C")
    print(f"   2025-07-22 18:15:00 - temp1: 21.5°C")
    print(f"   ... (more measurements)")
    print(f"   2025-07-22 18:55:00 - temp1: 20.9°C")
    print(f"")
    print(f"Compressed data (hourly average):")
    print(f"   2025-07-22 18:00:00 - temp1: 21.0°C (average of all measurements in that hour)")

if __name__ == "__main__":
    show_compression_example()
    demonstrate_compression()
