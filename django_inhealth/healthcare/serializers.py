"""
REST API Serializers for IoT Device Data

Handles serialization/deserialization of device data for the REST API.
"""

from rest_framework import serializers
from django.utils import timezone
from .models import Device, Patient, VitalSign
from .models_iot import DeviceAPIKey, DeviceDataReading, DeviceActivityLog, DeviceAlertRule


class DeviceSerializer(serializers.ModelSerializer):
    """Serializer for Device model"""

    class Meta:
        model = Device
        fields = [
            'device_id', 'device_unique_id', 'device_type', 'device_name',
            'manufacturer', 'model_number', 'firmware_version',
            'status', 'battery_level', 'last_sync', 'registration_date'
        ]
        read_only_fields = ['device_id', 'registration_date']


class VitalSignsDataSerializer(serializers.Serializer):
    """
    Serializer for vital signs data posted by IoT devices
    Validates incoming sensor data
    """
    # Timestamp when reading was taken
    timestamp = serializers.DateTimeField(required=True)

    # Vital sign measurements
    blood_pressure_systolic = serializers.IntegerField(required=False, allow_null=True, min_value=50, max_value=300)
    blood_pressure_diastolic = serializers.IntegerField(required=False, allow_null=True, min_value=30, max_value=200)
    heart_rate = serializers.IntegerField(required=False, allow_null=True, min_value=20, max_value=300)
    temperature = serializers.FloatField(required=False, allow_null=True, min_value=90.0, max_value=110.0)
    respiratory_rate = serializers.IntegerField(required=False, allow_null=True, min_value=5, max_value=60)
    oxygen_saturation = serializers.IntegerField(required=False, allow_null=True, min_value=50, max_value=100)
    weight = serializers.FloatField(required=False, allow_null=True, min_value=0, max_value=1000)
    height = serializers.FloatField(required=False, allow_null=True, min_value=0, max_value=300)

    # Device metadata
    battery_level = serializers.IntegerField(required=False, allow_null=True, min_value=0, max_value=100)
    signal_quality = serializers.IntegerField(required=False, allow_null=True, min_value=0, max_value=100)
    firmware_version = serializers.CharField(required=False, allow_null=True, max_length=50)

    def validate_timestamp(self, value):
        """Ensure timestamp is not in the future"""
        if value > timezone.now():
            raise serializers.ValidationError("Timestamp cannot be in the future")
        return value

    def validate(self, data):
        """Ensure at least one vital sign is provided"""
        vital_fields = [
            'blood_pressure_systolic', 'blood_pressure_diastolic',
            'heart_rate', 'temperature', 'respiratory_rate',
            'oxygen_saturation', 'weight', 'height'
        ]

        if not any(data.get(field) is not None for field in vital_fields):
            raise serializers.ValidationError(
                "At least one vital sign measurement must be provided"
            )

        # If one blood pressure value is provided, both should be provided
        bp_systolic = data.get('blood_pressure_systolic')
        bp_diastolic = data.get('blood_pressure_diastolic')

        if (bp_systolic is not None and bp_diastolic is None) or \
           (bp_diastolic is not None and bp_systolic is None):
            raise serializers.ValidationError(
                "Both systolic and diastolic blood pressure values must be provided together"
            )

        return data


class DeviceDataReadingSerializer(serializers.ModelSerializer):
    """Serializer for DeviceDataReading model"""

    device_name = serializers.CharField(source='device.device_name', read_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)

    class Meta:
        model = DeviceDataReading
        fields = [
            'id', 'device', 'device_name', 'patient', 'patient_name',
            'reading_type', 'timestamp', 'received_at', 'data',
            'signal_quality', 'battery_level', 'processed',
            'device_firmware'
        ]
        read_only_fields = ['id', 'received_at', 'processed']


class BulkVitalSignsSerializer(serializers.Serializer):
    """
    Serializer for bulk vital signs data
    Allows devices to send multiple readings at once
    """
    readings = serializers.ListField(
        child=VitalSignsDataSerializer(),
        min_length=1,
        max_length=100,  # Limit bulk uploads to 100 readings
        help_text="Array of vital signs readings"
    )

    def validate_readings(self, value):
        """Ensure readings are in chronological order"""
        if len(value) > 1:
            timestamps = [r['timestamp'] for r in value]
            if timestamps != sorted(timestamps):
                raise serializers.ValidationError(
                    "Readings must be in chronological order"
                )
        return value


class DeviceAuthSerializer(serializers.Serializer):
    """Serializer for device authentication"""
    device_unique_id = serializers.CharField(max_length=255, help_text="Unique device identifier")
    api_key = serializers.CharField(max_length=255, help_text="Device API key")


class DeviceRegistrationSerializer(serializers.Serializer):
    """Serializer for new device registration"""
    device_unique_id = serializers.CharField(max_length=255, help_text="Unique device identifier (e.g., MAC address, IMEI)")
    device_type = serializers.ChoiceField(choices=Device.DEVICE_TYPES, help_text="Type of device")
    device_name = serializers.CharField(max_length=200, help_text="Human-readable device name")
    manufacturer = serializers.CharField(max_length=200, required=False, allow_blank=True)
    model_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    firmware_version = serializers.CharField(max_length=50, required=False, allow_blank=True)
    patient_id = serializers.IntegerField(help_text="Patient ID this device belongs to")

    def validate_device_unique_id(self, value):
        """Check if device is already registered"""
        if Device.objects.filter(device_unique_id=value).exists():
            raise serializers.ValidationError("Device with this unique ID is already registered")
        return value

    def validate_patient_id(self, value):
        """Check if patient exists"""
        if not Patient.objects.filter(patient_id=value).exists():
            raise serializers.ValidationError("Patient with this ID does not exist")
        return value


class GlucoseDataSerializer(serializers.Serializer):
    """Serializer for blood glucose data"""
    timestamp = serializers.DateTimeField(required=True)
    glucose_level = serializers.FloatField(required=True, min_value=0, max_value=600, help_text="mg/dL")
    meal_context = serializers.ChoiceField(
        choices=['fasting', 'before_meal', 'after_meal', 'bedtime', 'random'],
        required=False,
        allow_null=True
    )
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)


class ECGDataSerializer(serializers.Serializer):
    """Serializer for ECG data"""
    timestamp = serializers.DateTimeField(required=True)
    duration_seconds = serializers.IntegerField(required=True, min_value=1, max_value=300)
    sample_rate = serializers.IntegerField(required=True, help_text="Samples per second (Hz)")
    ecg_data = serializers.ListField(
        child=serializers.FloatField(),
        help_text="Array of ECG voltage values"
    )
    heart_rate_bpm = serializers.IntegerField(required=False, allow_null=True)
    rhythm = serializers.CharField(required=False, allow_blank=True, max_length=50)


class ActivityDataSerializer(serializers.Serializer):
    """Serializer for activity/step data"""
    date = serializers.DateField(required=True)
    steps = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    distance_meters = serializers.FloatField(required=False, allow_null=True, min_value=0)
    calories_burned = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    active_minutes = serializers.IntegerField(required=False, allow_null=True, min_value=0, max_value=1440)
    floors_climbed = serializers.IntegerField(required=False, allow_null=True, min_value=0)


class SleepDataSerializer(serializers.Serializer):
    """Serializer for sleep data"""
    sleep_date = serializers.DateField(required=True)
    sleep_start = serializers.DateTimeField(required=True)
    sleep_end = serializers.DateTimeField(required=True)
    total_sleep_minutes = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    deep_sleep_minutes = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    light_sleep_minutes = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    rem_sleep_minutes = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    awake_minutes = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    sleep_quality_score = serializers.IntegerField(required=False, allow_null=True, min_value=0, max_value=100)


class DeviceStatusSerializer(serializers.Serializer):
    """Serializer for device status updates"""
    battery_level = serializers.IntegerField(required=False, allow_null=True, min_value=0, max_value=100)
    firmware_version = serializers.CharField(required=False, allow_blank=True, max_length=50)
    status = serializers.ChoiceField(choices=Device.STATUS_CHOICES, required=False)
    last_sync = serializers.DateTimeField(required=False, allow_null=True)


class APIResponseSerializer(serializers.Serializer):
    """Standard API response format"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField(required=False, allow_null=True)
    errors = serializers.DictField(required=False, allow_null=True)
    timestamp = serializers.DateTimeField()
