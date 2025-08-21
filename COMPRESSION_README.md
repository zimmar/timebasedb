# TimebaseDB Compression Feature

This document describes the database compression functionality that compresses time-dependent data from high-frequency measurements to hourly averages.

## Overview

The `tbdb` database contains time-dependent values with high frequency (e.g., every 5 minutes). To optimize storage and improve query performance, you can compress this data into hourly averages stored in the `tbdb_hourly` table.

## Example

**Original data (every 5 minutes):**
```
2025-07-22 18:00:00 - temp1: 20.5°C
2025-07-22 18:05:00 - temp1: 21.2°C
2025-07-22 18:10:00 - temp1: 20.8°C
2025-07-22 18:15:00 - temp1: 21.5°C
... (more measurements every 5 minutes)
2025-07-22 18:55:00 - temp1: 20.9°C
```

**Compressed data (hourly average):**
```
2025-07-22 18:00:00 - temp1: 21.0°C (average of all measurements in that hour)
```

## Models

### `tbdb` (Original table)
- Stores high-frequency time-dependent measurements
- Contains all original functionality and methods

### `tbdb_hourly` (Compressed table)
- Stores hourly compressed averages
- **Inherits all functionality from `tbdb`**
- Same API, same methods, same data access patterns
- Provides faster queries for historical data analysis

## Usage

### 1. Compress Data from tbdb to tbdb_hourly

```python
from timebase.models import tbdb, tbdb_hourly
from datetime import datetime, timedelta

# Compress all data
results = tbdb.compress_to_hourly()

# Compress data for specific date range
end_date = datetime.now()
start_date = end_date - timedelta(days=7)  # Last 7 days
results = tbdb.compress_to_hourly(start_date, end_date)

# Alternative: Use tbdb_hourly convenience method
results = tbdb_hourly.compress_from_main(start_date, end_date)
```

### 2. Use tbdb_hourly exactly like tbdb

```python
# All tbdb methods work exactly the same on tbdb_hourly

# Get measurements
hourly_measurements = tbdb_hourly.get_measurements('temp1')

# Calculate statistics
avg_temp = tbdb_hourly.avg('temp1')
min_temp = tbdb_hourly.min_value('temp1')
max_temp = tbdb_hourly.max_value('temp1')
count = tbdb_hourly.count('temp1')

# Get latest measurement
latest = tbdb_hourly.latest('temp1')

# Get measurements between dates
from datetime import datetime, timedelta
yesterday = datetime.now() - timedelta(days=1)
today = datetime.now()
recent_data = tbdb_hourly.get_measurements_between_dates(yesterday, today, 'temp1')

# Get hourly statistics for a period
stats = tbdb_hourly.get_hourly_statistics('temp1', yesterday, today)
```

### 3. Adding new data to tbdb_hourly

```python
# Create new hourly record (same as tbdb)
hourly_record = tbdb_hourly(measurement_type='float', measurement_name='temp1')
hourly_record.add(25.5)  # Temperature value

# Or create and save directly
hourly_record = tbdb_hourly(
    measurement_name='temp1',
    measurement_type='float'
)
hourly_record.timestamp = datetime(2025, 8, 21, 15, 0, 0)  # 3 PM
hourly_record.value = '25.5'
hourly_record.save()
```

## Compression Process

The compression function:

1. **Identifies numeric measurements**: Only compresses `integer`, `float`, and `decimal` type measurements
2. **Groups by hour**: Rounds timestamps down to the nearest hour
3. **Calculates averages**: Uses SQL AVG() for accurate numerical averaging
4. **Avoids duplicates**: Checks for existing hourly records before creating new ones
5. **Preserves metadata**: Maintains measurement names and types

## Benefits

- **Reduced Storage Space**: Compresses ~12 measurements per hour into 1 record
- **Faster Queries**: Hourly data enables faster analysis of historical trends
- **Preserved Functionality**: All original `tbdb` methods work identically on `tbdb_hourly`
- **Maintained Accuracy**: Uses precise SQL averaging, not approximations

## Example Results

In the demonstration:
- **Original data**: 26,424 high-frequency records
- **Compressed data**: 504 hourly records  
- **Compression ratio**: ~52:1 reduction in record count
- **Data preserved**: All trends and patterns maintained in hourly averages

## Files

- `timebase/models.py` - Contains both `tbdb` and `tbdb_hourly` models with compression functionality
- `compress_demo.py` - Demonstration script showing compression in action
- `timebase/migrations/0003_tbdb_hourly.py` - Database migration to create the hourly table

## Running the Demo

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run the compression demonstration
python compress_demo.py
```

This will show the compression process, statistics, and verify that all `tbdb` functionality works on `tbdb_hourly`.
