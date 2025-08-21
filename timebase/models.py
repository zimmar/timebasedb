from django.db import models, connection
from django.utils import timezone

class tbdb(models.Model):
    # Define your model fields here
    timestamp = models.DateTimeField(default=timezone.now)
    measurement_name = models.CharField(max_length=100)
    measurement_type = models.CharField(max_length=20, 
    choices=[
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('string', 'String'),
        ('boolean', 'Boolean'),
        ('decimal', 'Decimal'),
    ])
    value = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Timebase Database"
        verbose_name_plural = "Timebase Databases"
        ordering = ['-timestamp']

    def __str__(self):
        return f"tbdb(name='{self.measurement_name}', type={self.measurement_type}, data={self.data}, time={self.timestamp})"
 
    def __init__(self, measurement_type=None, measurement_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if measurement_type and measurement_name and not self.pk:
            self.measurement_type = measurement_type
            self.measurement_name = measurement_name

    def save(self, *args, **kwargs):
        # Always create a new entry with the current timestamp when adding data
        if hasattr(self, '_force_new') or (self.value is not None and self.pk):
            self.pk = None
        self.timestamp = timezone.now()
        super().save(*args, **kwargs)

    def add(self, data_value):
        """Add new data value and save as new entry with new timestamp"""
        # Validate and convert value based on measurement type
        if self.measurement_type == 'integer':
            data_value = int(data_value)
        elif self.measurement_type == 'float':
            data_value = float(data_value)
        elif self.measurement_type == 'boolean':
            if isinstance(data_value, str):
                data_value = data_value.lower() in ('true', '1', 'yes', 'on')
            else:
                data_value = bool(data_value)
        elif self.measurement_type == 'string':
            data_value = str(data_value)
        elif self.measurement_type == 'decimal':
            from decimal import Decimal
            data_value = Decimal(str(data_value))
        
        self.value = str(data_value)
        self._force_new = True  # Flag to force new record
        self.save()
        return self

    @property
    def data(self):
        """Get the data value converted to appropriate type"""
        if self.value is None:
            return None

        if self.measurement_type == 'integer':
            return int(self.value)
        elif self.measurement_type == 'float':
            return float(self.value)
        elif self.measurement_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.measurement_type == 'string':
            return self.value

        return self.value

    @classmethod
    def get_measurements(cls, name=None, measurement_type=None):
        """Get measurements using raw SQL to avoid field mapping issues"""
        cursor = connection.cursor()
        
        # Get the correct table name from Django's meta
        table_name = cls._meta.db_table
        sql = f"SELECT measurement_name, measurement_type, value, timestamp FROM {table_name} WHERE 1=1"
        params = []
        
        if name:
            sql += " AND measurement_name = %s"
            params.append(name)
        if measurement_type:
            sql += " AND measurement_type = %s"
            params.append(measurement_type)
            
        sql += " ORDER BY timestamp DESC"
        
        cursor.execute(sql, params)
        results = []
        for row in cursor.fetchall():
            # Create a temporary object with correct values
            obj = cls()
            obj.measurement_name = row[0]
            obj.measurement_type = row[1]
            obj.value = row[2]
            obj.timestamp = row[3]
            results.append(obj)
        return results  

    @classmethod
    def avg(cls, name=None):
        """Calculate average for numeric measurements"""
        measurements = cls.get_measurements(name=name)
        numeric_measurements = [m for m in measurements if m.measurement_type in ['integer', 'float', 'decimal']]
        if not numeric_measurements:
            return None
        
        total = sum(measurement.data for measurement in numeric_measurements)
        return total / len(numeric_measurements)

    @classmethod
    def count(cls, name=None):
        """Count measurements"""
        return len(cls.get_measurements(name=name))

    @classmethod
    def sum(cls, name=None):
        """Sum numeric measurements"""
        measurements = cls.get_measurements(name=name)
        numeric_measurements = [m for m in measurements if m.measurement_type in ['integer', 'float', 'decimal']]
        return sum(measurement.data for measurement in numeric_measurements)

    @classmethod
    def min_value(cls, name=None):
        """Get minimum value for numeric measurements"""
        measurements = cls.get_measurements(name=name)
        numeric_measurements = [m for m in measurements if m.measurement_type in ['integer', 'float', 'decimal']]
        if not numeric_measurements:
            return None
        return min(measurement.data for measurement in numeric_measurements)

    @classmethod
    def max_value(cls, name=None):
        """Get maximum value for numeric measurements"""
        measurements = cls.get_measurements(name=name)
        numeric_measurements = [m for m in measurements if m.measurement_type in ['integer', 'float', 'decimal']]
        if not numeric_measurements:
            return None
        return max(measurement.data for measurement in numeric_measurements)

    @classmethod
    def latest(cls, name=None):
        """Get the latest measurement"""
        measurements = cls.get_measurements(name=name)
        return measurements[0] if measurements else None

    @classmethod
    def all_values(cls, name=None):
        """Get all data values ordered by timestamp"""
        return [m.data for m in cls.get_measurements(name=name)]      

    @classmethod
    def bulk_delete(cls, names):
        """Delete multiple measurements by name"""
        cursor = connection.cursor()
        table_name = cls._meta.db_table
        sql = f"DELETE FROM {table_name} WHERE 1=1"
        params = []

        if names:
            sql += " AND measurement_name IN %s"
            params.append(tuple(names))

        cursor.execute(sql, params)
        return cursor.rowcount  # Return number of deleted rows

    @classmethod
    def get_measurements_between_dates(cls, start_date, end_date, name=None):
        """Get measurements between two dates"""
        cursor = connection.cursor()
        table_name = cls._meta.db_table
        sql = f"SELECT measurement_name, measurement_type, value, timestamp FROM {table_name} WHERE 1=1"
        params = []

        if name:
            sql += " AND measurement_name = %s"
            params.append(name)
        sql += " AND timestamp BETWEEN %s AND %s"
        params.extend([start_date, end_date])

        cursor.execute(sql, params)
        results = []
        for row in cursor.fetchall():
            obj = cls()
            obj.measurement_name = row[0]
            obj.measurement_type = row[1]
            obj.value = row[2]
            obj.timestamp = row[3]
            results.append(obj)
        return results
