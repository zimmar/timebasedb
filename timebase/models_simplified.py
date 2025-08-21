from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta


class BaseTimeSeriesModel(models.Model):
    """Base class for time series data with common functionality"""
    
    timestamp = models.DateTimeField(default=timezone.now)
    measurement_name = models.CharField(max_length=100)
    measurement_type = models.CharField(max_length=20, choices=[
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('string', 'String'),
        ('boolean', 'Boolean'),
        ('decimal', 'Decimal'),
    ])
    value = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.__class__.__name__}(name='{self.measurement_name}', type={self.measurement_type}, data={self.data}, time={self.timestamp})"
    
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
        elif self.measurement_type == 'decimal':
            from decimal import Decimal
            return Decimal(self.value)
        return self.value

    @classmethod
    def get_measurements(cls, name=None, measurement_type=None):
        """Get measurements using Django ORM"""
        queryset = cls.objects.all()
        
        if name:
            queryset = queryset.filter(measurement_name=name)
        if measurement_type:
            queryset = queryset.filter(measurement_type=measurement_type)
            
        return queryset.order_by('-timestamp')

    @classmethod
    def avg(cls, name=None):
        """Calculate average for numeric measurements"""
        queryset = cls.objects.filter(
            measurement_type__in=['integer', 'float', 'decimal']
        )
        if name:
            queryset = queryset.filter(measurement_name=name)
        
        values = []
        for obj in queryset:
            try:
                values.append(float(obj.value))
            except (ValueError, TypeError):
                continue
        
        return sum(values) / len(values) if values else None

    @classmethod
    def count(cls, name=None):
        """Count measurements"""
        queryset = cls.objects.all()
        if name:
            queryset = queryset.filter(measurement_name=name)
        return queryset.count()

    @classmethod
    def sum(cls, name=None):
        """Sum numeric measurements"""
        queryset = cls.objects.filter(
            measurement_type__in=['integer', 'float', 'decimal']
        )
        if name:
            queryset = queryset.filter(measurement_name=name)
        
        total = 0
        for obj in queryset:
            try:
                total += float(obj.value)
            except (ValueError, TypeError):
                continue
        return total

    @classmethod
    def min_value(cls, name=None):
        """Get minimum value for numeric measurements"""
        queryset = cls.objects.filter(
            measurement_type__in=['integer', 'float', 'decimal']
        )
        if name:
            queryset = queryset.filter(measurement_name=name)
        
        values = []
        for obj in queryset:
            try:
                values.append(float(obj.value))
            except (ValueError, TypeError):
                continue
        return min(values) if values else None

    @classmethod
    def max_value(cls, name=None):
        """Get maximum value for numeric measurements"""
        queryset = cls.objects.filter(
            measurement_type__in=['integer', 'float', 'decimal']
        )
        if name:
            queryset = queryset.filter(measurement_name=name)
        
        values = []
        for obj in queryset:
            try:
                values.append(float(obj.value))
            except (ValueError, TypeError):
                continue
        return max(values) if values else None

    @classmethod
    def latest(cls, name=None):
        """Get the latest measurement"""
        queryset = cls.objects.all()
        if name:
            queryset = queryset.filter(measurement_name=name)
        return queryset.order_by('-timestamp').first()

    @classmethod
    def all_values(cls, name=None):
        """Get all data values ordered by timestamp"""
        measurements = cls.get_measurements(name=name)
        return [m.data for m in measurements]

    @classmethod
    def bulk_delete(cls, names):
        """Delete multiple measurements by name"""
        if names:
            return cls.objects.filter(measurement_name__in=names).delete()[0]
        return 0

    @classmethod
    def get_measurements_between_dates(cls, start_date, end_date, name=None):
        """Get measurements between two dates"""
        queryset = cls.objects.filter(timestamp__range=[start_date, end_date])
        if name:
            queryset = queryset.filter(measurement_name=name)
        return queryset.order_by('-timestamp')


class tbdb(BaseTimeSeriesModel):
    """Main timebase database for high-frequency measurements"""
    
    class Meta:
        verbose_name = "Timebase Database"
        verbose_name_plural = "Timebase Databases"
        ordering = ['-timestamp']

    @classmethod
    def compress_to_hourly(cls, start_date=None, end_date=None):
        """
        Compress data to hourly averages for numeric measurements.
        Simplified version using Django ORM and bulk operations.
        """
        # Get distinct measurement names and types
        measurements_info = cls.objects.values('measurement_name', 'measurement_type').distinct()
        
        # Filter by date range if provided
        base_queryset = cls.objects.all()
        if start_date:
            base_queryset = base_queryset.filter(timestamp__gte=start_date)
        if end_date:
            base_queryset = base_queryset.filter(timestamp__lte=end_date)
        
        compression_results = []
        
        for info in measurements_info:
            measurement_name = info['measurement_name']
            measurement_type = info['measurement_type']
            
            # Only compress numeric measurements
            if measurement_type not in ['integer', 'float', 'decimal']:
                continue
                
            # Get data for this measurement
            measurement_data = base_queryset.filter(
                measurement_name=measurement_name,
                measurement_type=measurement_type
            ).order_by('timestamp')
            
            if not measurement_data:
                continue
            
            # Group by hour and calculate averages
            hourly_data = {}
            for record in measurement_data:
                # Round down to hour
                hour_timestamp = record.timestamp.replace(minute=0, second=0, microsecond=0)
                
                if hour_timestamp not in hourly_data:
                    hourly_data[hour_timestamp] = []
                
                try:
                    hourly_data[hour_timestamp].append(float(record.value))
                except (ValueError, TypeError):
                    continue
            
            # Create hourly records
            for hour_timestamp, values in hourly_data.items():
                if not values:
                    continue
                
                avg_value = sum(values) / len(values)
                
                # Check if this hourly record already exists
                existing = tbdb_hourly.objects.filter(
                    measurement_name=measurement_name,
                    timestamp=hour_timestamp
                ).first()
                
                if not existing:
                    # Create new hourly record with timezone-aware timestamp
                    if hour_timestamp.tzinfo is None:
                        hour_timestamp = timezone.make_aware(hour_timestamp)
                    
                    hourly_record = tbdb_hourly.objects.create(
                        measurement_name=measurement_name,
                        measurement_type=measurement_type,
                        timestamp=hour_timestamp,
                        value=str(avg_value)
                    )
                    
                    compression_results.append({
                        'measurement_name': measurement_name,
                        'timestamp': hour_timestamp,
                        'average_value': avg_value
                    })
        
        return compression_results


class tbdb_hourly(BaseTimeSeriesModel):
    """
    Hourly compressed version of tbdb containing hourly averages.
    Inherits all functionality from BaseTimeSeriesModel.
    """
    
    class Meta:
        verbose_name = "Timebase Database (Hourly)"
        verbose_name_plural = "Timebase Databases (Hourly)"
        ordering = ['-timestamp']
        db_table = 'timebase_tbdb_hourly'

    @classmethod
    def compress_from_main(cls, start_date=None, end_date=None):
        """
        Convenience method to compress data from main tbdb table to hourly table.
        """
        return tbdb.compress_to_hourly(start_date, end_date)

    @classmethod 
    def get_hourly_statistics(cls, measurement_name=None, start_date=None, end_date=None):
        """
        Get statistics for hourly compressed data using Django ORM.
        """
        queryset = cls.objects.filter(
            measurement_type__in=['integer', 'float', 'decimal']
        )
        
        if measurement_name:
            queryset = queryset.filter(measurement_name=measurement_name)
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        values = []
        for obj in queryset:
            try:
                values.append(float(obj.value))
            except (ValueError, TypeError):
                continue
        
        if not values:
            return {
                'count': 0,
                'avg': None,
                'min': None,
                'max': None,
                'sum': None
            }
        
        return {
            'count': len(values),
            'avg': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'sum': sum(values)
        }
