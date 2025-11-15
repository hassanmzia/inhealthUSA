"""
IoT Device API Models

Extends the existing Device model with API authentication and data tracking.
Provides JWT token-based authentication for secure device communication.
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
import secrets
import hashlib
from datetime import timedelta
from .models import Device, Patient


class DeviceAPIKey(models.Model):
    """
    API Key for IoT device authentication
    Stores hashed API keys for secure device-to-server communication
    """
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='api_keys')
    key_name = models.CharField(max_length=100, help_text="Friendly name for this API key")
    key_prefix = models.CharField(max_length=8, unique=True, help_text="First 8 chars of key for identification")
    hashed_key = models.CharField(max_length=255, help_text="Hashed API key for security")

    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Optional expiration date")

    is_active = models.BooleanField(default=True)

    # Permissions
    can_write_vitals = models.BooleanField(default=True, help_text="Can POST vital signs data")
    can_read_patient = models.BooleanField(default=False, help_text="Can GET patient information")

    # Rate limiting tracking
    request_count_today = models.IntegerField(default=0)
    last_reset_date = models.DateField(auto_now_add=True)

    # Metadata
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'healthcare_device_api_key'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['key_prefix']),
            models.Index(fields=['device', 'is_active']),
        ]

    def __str__(self):
        return f"{self.device.device_name} - {self.key_name} ({self.key_prefix}...)"

    @staticmethod
    def generate_key():
        """Generate a new API key"""
        # Generate 32-byte (256-bit) random key
        key = secrets.token_urlsafe(32)
        return key

    @classmethod
    def create_key(cls, device, key_name, expires_in_days=None):
        """Create a new API key for a device"""
        key = cls.generate_key()
        key_prefix = key[:8]
        hashed_key = make_password(key)

        expires_at = None
        if expires_in_days:
            expires_at = timezone.now() + timedelta(days=expires_in_days)

        api_key = cls.objects.create(
            device=device,
            key_name=key_name,
            key_prefix=key_prefix,
            hashed_key=hashed_key,
            expires_at=expires_at
        )

        # Return the unhashed key (this is the only time it's available)
        return api_key, key

    def verify_key(self, key):
        """Verify if provided key matches this API key"""
        if not self.is_active:
            return False

        if self.expires_at and timezone.now() > self.expires_at:
            return False

        return check_password(key, self.hashed_key)

    def record_usage(self):
        """Record API key usage"""
        now = timezone.now()

        # Reset counter if it's a new day
        if self.last_reset_date != now.date():
            self.request_count_today = 0
            self.last_reset_date = now.date()

        self.last_used = now
        self.request_count_today += 1
        self.save(update_fields=['last_used', 'request_count_today', 'last_reset_date'])


class DeviceDataReading(models.Model):
    """
    Stores individual data readings from IoT devices
    Generic model for any type of sensor data
    """
    READING_TYPES = [
        ('vital_signs', 'Vital Signs'),
        ('glucose', 'Blood Glucose'),
        ('ecg', 'ECG Data'),
        ('activity', 'Activity/Steps'),
        ('sleep', 'Sleep Data'),
        ('custom', 'Custom Data'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='readings')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='device_readings')

    reading_type = models.CharField(max_length=20, choices=READING_TYPES)
    timestamp = models.DateTimeField(help_text="When the reading was taken")
    received_at = models.DateTimeField(auto_now_add=True, help_text="When server received the data")

    # Data stored as JSON for flexibility
    data = models.JSONField(help_text="Actual sensor data")

    # Quality indicators
    signal_quality = models.IntegerField(null=True, blank=True, help_text="Signal quality 0-100")
    battery_level = models.IntegerField(null=True, blank=True, help_text="Device battery level 0-100")

    # Processing status
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    vital_sign_id = models.IntegerField(null=True, blank=True, help_text="Linked VitalSign record if processed")

    # Metadata
    device_firmware = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'healthcare_device_data_reading'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', 'timestamp']),
            models.Index(fields=['patient', 'timestamp']),
            models.Index(fields=['reading_type', 'processed']),
        ]

    def __str__(self):
        return f"{self.device.device_name} - {self.reading_type} at {self.timestamp}"

    def mark_as_processed(self, vital_sign_id=None):
        """Mark reading as processed"""
        self.processed = True
        self.processed_at = timezone.now()
        if vital_sign_id:
            self.vital_sign_id = vital_sign_id
        self.save()


class DeviceActivityLog(models.Model):
    """
    Logs all API activity for devices for auditing and troubleshooting
    """
    ACTION_TYPES = [
        ('auth', 'Authentication'),
        ('data_post', 'Data Posted'),
        ('data_get', 'Data Retrieved'),
        ('registration', 'Device Registered'),
        ('error', 'Error Occurred'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='activity_logs', null=True, blank=True)
    api_key = models.ForeignKey(DeviceAPIKey, on_delete=models.SET_NULL, null=True, blank=True)

    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Request details
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    endpoint = models.CharField(max_length=255, blank=True, null=True)
    http_method = models.CharField(max_length=10, blank=True, null=True)

    # Response details
    status_code = models.IntegerField(null=True, blank=True)
    response_time_ms = models.IntegerField(null=True, blank=True, help_text="Response time in milliseconds")

    # Additional data
    details = models.JSONField(null=True, blank=True, help_text="Additional log details")
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'healthcare_device_activity_log'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', 'timestamp']),
            models.Index(fields=['action_type', 'timestamp']),
        ]

    def __str__(self):
        device_name = self.device.device_name if self.device else "Unknown"
        return f"{device_name} - {self.action_type} at {self.timestamp}"


class DeviceAlertRule(models.Model):
    """
    Defines alert rules for device data
    Triggers notifications when readings exceed thresholds
    """
    ALERT_LEVELS = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='alert_rules', null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='device_alert_rules', null=True, blank=True)

    rule_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    # Condition
    metric_name = models.CharField(max_length=50, help_text="e.g., heart_rate, blood_pressure_systolic")
    condition = models.CharField(max_length=10, choices=[
        ('gt', 'Greater Than'),
        ('lt', 'Less Than'),
        ('eq', 'Equal To'),
        ('gte', 'Greater Than or Equal'),
        ('lte', 'Less Than or Equal'),
    ])
    threshold_value = models.FloatField()

    # Alert details
    alert_level = models.CharField(max_length=10, choices=ALERT_LEVELS)
    alert_message = models.TextField()

    # Notification settings
    notify_patient = models.BooleanField(default=False)
    notify_provider = models.BooleanField(default=True)
    notification_email = models.EmailField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'healthcare_device_alert_rule'
        ordering = ['patient', 'rule_name']

    def __str__(self):
        return f"{self.rule_name} ({self.patient.full_name if self.patient else 'All Patients'})"

    def check_value(self, value):
        """Check if value triggers this alert rule"""
        if not self.is_active:
            return False

        if self.condition == 'gt':
            return value > self.threshold_value
        elif self.condition == 'lt':
            return value < self.threshold_value
        elif self.condition == 'eq':
            return value == self.threshold_value
        elif self.condition == 'gte':
            return value >= self.threshold_value
        elif self.condition == 'lte':
            return value <= self.threshold_value

        return False
