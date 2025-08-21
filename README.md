# 🚀 Timebase Database with sqlite3

## 📋 Summary

Timebase database is a simple database for storing time-dependent values. Integer, float, string, decimal and Boolean values can be stored. 

Some mathematical and statistical functions are also implemented.

The database was created to store physical sensor values from SAN switches and then use them to generate long-term evaluations.

## ✅ What We've Accomplished

### 1. **Package Structure Created**
```
timebasedb/
├── timebase/                   # Main app package
│   ├── __init__.py             # Package initialization
│   ├── apps.py                 # App configuration
│   ├── models.py               # Time-series database model
│   └── migrations/             # Database migrations
├── requirements.txt            # Dependencies
├── README.md                   # Documentation
├── LICENSE                     # MIT License
└── generate_temp_data.py       # Generate tempdata for 3 sensors 30 days
```

### 2. **Core Features**
- ✅ **Multi-type measurements**: Integer, Float, String, Boolean, Decimal
- ✅ **Automatic timestamping**: Every measurement gets a timestamp
- ✅ **Your exact syntax**: `x = tbdb('integer', 'temperatur'); x.add(10)`
- ✅ **Statistical functions**: avg, count, min, max, sum
- ✅ **Time-range queries**: Query measurements within date ranges
- ✅ **Raw SQL optimization**: Bypasses Django ORM field mapping issues

### 3. **Usage Examples**

#### **Python API:**
```python
from timebase.models import tbdb

# Create measurements
temp = tbdb('float', 'temperature')
temp.add(23.5)
temp.add(24.0)

# Get statistics
print(f"Average: {tbdb.avg('temperature')}°C")
print(f"Count: {tbdb.count('temperature')}")
```

