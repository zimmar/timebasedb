#!/usr/bin/env python
"""
Generate fake temperature data for 3 sensors over 30 days with 5-minute intervals
"""
import os
import django
import random
import math
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Now import the Django models
from timebase.models import tbdb
from django.db import connection



def generate_realistic_temperature(base_temp, time_offset_hours, day_of_year, noise_level=2.0):
    """
    Generate realistic temperature data with daily cycles and seasonal variation
    
    Args:
        base_temp: Base temperature for this sensor location
        time_offset_hours: Hours since midnight (0-24)
        day_of_year: Day of the year (1-365) for seasonal variation
        noise_level: Random noise amplitude
    """
    # Daily temperature cycle (cooler at night, warmer during day)
    daily_variation = 8 * math.sin((time_offset_hours - 6) * math.pi / 12)
    
    # Seasonal variation (assuming Northern hemisphere)
    seasonal_variation = 15 * math.sin((day_of_year - 81) * 2 * math.pi / 365)
    
    # Random noise
    noise = random.uniform(-noise_level, noise_level)
    
    # Weather pattern (occasional temperature drops/spikes)
    weather_event = 0
    if random.random() < 0.05:  # 5% chance of weather event
        weather_event = random.uniform(-8, 8)
    
    return base_temp + daily_variation + seasonal_variation + noise + weather_event

def bulk_insert_measurements(measurements):
    """Efficiently insert many measurements using raw SQL"""
    table_name = tbdb._meta.db_table
    cursor = connection.cursor()
    
    # Insert in batches for better performance
    batch_size = 1000
    for i in range(0, len(measurements), batch_size):
        batch = measurements[i:i + batch_size]
        
        values = []
        params = []
        for timestamp, name, measurement_type, value in batch:
            values.append("(%s, %s, %s, %s)")
            params.extend([timestamp, name, measurement_type, str(value)])
        
        sql = f"""
        INSERT INTO {table_name} (timestamp, measurement_name, measurement_type, value)
        VALUES {', '.join(values)}
        """
        
        cursor.execute(sql, params)
        print(f"✅ Inserted batch {i//batch_size + 1}: {len(batch)} measurements")

def generate_fake_data():
    """Generate 30 days of temperature data for 3 sensors"""
    table_name = tbdb._meta.db_table
    print("🌡️  Generating fake temperature data...")
    print("=" * 50)
    
    # Configuration
    sensors = {
        'temp1': {'base_temp': 20.0, 'location': 'Indoor Office'},
        'temp2': {'base_temp': 18.5, 'location': 'Outdoor Garden'}, 
        'temp3': {'base_temp': 22.0, 'location': 'Server Room'}
    }
    
    # Time configuration
    start_date = datetime.now() - timedelta(days=30)
    interval_minutes = 5
    total_days = 30
    
    # Calculate total measurements
    measurements_per_day = (24 * 60) // interval_minutes  # 288 measurements per day
    total_measurements = total_days * measurements_per_day * len(sensors)
    
    print(f"📊 Configuration:")
    print(f"   • Sensors: {len(sensors)} ({', '.join(sensors.keys())})")
    print(f"   • Duration: {total_days} days")
    print(f"   • Interval: {interval_minutes} minutes")
    print(f"   • Measurements per sensor per day: {measurements_per_day}")
    print(f"   • Total measurements to generate: {total_measurements:,}")
    print(f"   • Start date: {start_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Clear existing data for these sensors
    print(f"\n🗑️  Clearing existing data...")
    cursor = connection.cursor()
    for sensor_name in sensors.keys():
        cursor.execute(f"DELETE FROM {table_name} WHERE measurement_name = %s", [sensor_name])
    
    # Generate all measurements
    print(f"\n🔄 Generating measurements...")
    all_measurements = []
    
    current_time = start_date
    
    for day in range(total_days):
        day_of_year = current_time.timetuple().tm_yday
        
        for measurement_of_day in range(measurements_per_day):
            time_offset_hours = (measurement_of_day * interval_minutes) / 60.0
            
            for sensor_name, config in sensors.items():
                # Generate realistic temperature
                temperature = generate_realistic_temperature(
                    base_temp=config['base_temp'],
                    time_offset_hours=time_offset_hours,
                    day_of_year=day_of_year
                )
                
                # Round to 1 decimal place
                temperature = round(temperature, 1)
                
                # Add to batch
                all_measurements.append((
                    current_time,
                    sensor_name,
                    'float',
                    temperature
                ))
            
            # Move to next measurement time
            current_time += timedelta(minutes=interval_minutes)
        
        # Progress update
        if (day + 1) % 5 == 0:
            print(f"   📅 Generated day {day + 1}/{total_days}")
    
    print(f"\n💾 Inserting {len(all_measurements):,} measurements into database...")
    bulk_insert_measurements(all_measurements)
    
    # Verify the data
    print(f"\n✅ Data generation complete!")
    print(f"\n📈 Statistics:")
    
    for sensor_name in sensors.keys():
        count = tbdb.count(sensor_name)
        avg_temp = tbdb.avg(sensor_name)
        min_temp = tbdb.min_value(sensor_name)
        max_temp = tbdb.max_value(sensor_name)
        latest = tbdb.latest(sensor_name)
        
        print(f"   🌡️  {sensor_name}:")
        print(f"      • Count: {count:,} measurements")
        print(f"      • Average: {avg_temp:.1f}°C")
        print(f"      • Range: {min_temp:.1f}°C to {max_temp:.1f}°C")
        print(f"      • Latest: {latest.data}°C at {latest.timestamp}")
    
    # Sample recent data
    print(f"\n🔍 Sample of recent temp1 data:")
    recent_measurements = tbdb.get_measurements(name='temp1')[:10]
    for i, measurement in enumerate(recent_measurements):
        print(f"   {i+1:2d}. {measurement.data:5.1f}°C at {measurement.timestamp}")
    
    print(f"\n🎉 Successfully generated {total_measurements:,} temperature measurements!")
    print(f"💡 Use tbdb.get_measurements('temp1') to access the data")

if __name__ == "__main__":
    generate_fake_data()
