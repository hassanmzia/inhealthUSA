"""
IoT Device REST API Views

Handles device authentication and data submission endpoints.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.utils import timezone
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging

from .models import Device, Patient, VitalSign
from .models_iot import DeviceAPIKey, DeviceDataReading, DeviceActivityLog
from .serializers import (
    VitalSignsDataSerializer, BulkVitalSignsSerializer,
    DeviceAuthSerializer, DeviceRegistrationSerializer,
    GlucoseDataSerializer, ECGDataSerializer,
    ActivityDataSerializer, SleepDataSerializer,
    DeviceStatusSerializer, APIResponseSerializer,
    DeviceSerializer
)

logger = logging.getLogger(__name__)


class DeviceAPIKeyAuthentication:
    """
    Custom authentication class for IoT devices using API keys
    """
    def authenticate(self, request):
        """Authenticate device using API key from Authorization header"""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return None

        api_key = auth_header.replace('Bearer ', '').strip()

        if not api_key:
            return None

        # Extract key prefix
        key_prefix = api_key[:8]

        try:
            api_key_obj = DeviceAPIKey.objects.select_related('device', 'device__patient').get(
                key_prefix=key_prefix,
                is_active=True
            )

            # Verify the full key
            if not api_key_obj.verify_key(api_key):
                return None

            # Record usage
            api_key_obj.record_usage()

            # Return device and api_key_obj as authentication
            return (api_key_obj.device, api_key_obj)

        except DeviceAPIKey.DoesNotExist:
            return None

    def authenticate_header(self, request):
        """Return authentication header to include in 401 responses"""
        return 'Bearer'


class DeviceAPIView(APIView):
    """
    Base API view for device endpoints
    Includes common authentication and logging
    """
    authentication_classes = []  # No standard authentication
    permission_classes = [AllowAny]  # Will check API key manually

    def get_device_from_api_key(self, request):
        """Extract and validate device from API key"""
        auth = DeviceAPIKeyAuthentication()
        result = auth.authenticate(request)

        if result is None:
            return None, None

        device, api_key_obj = result
        return device, api_key_obj

    def log_activity(self, request, device, api_key, action_type, status_code, details=None, error_message=None):
        """Log device API activity"""
        try:
            DeviceActivityLog.objects.create(
                device=device,
                api_key=api_key,
                action_type=action_type,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                endpoint=request.path,
                http_method=request.method,
                status_code=status_code,
                details=details,
                error_message=error_message
            )
        except Exception as e:
            logger.error(f"Error logging device activity: {str(e)}")

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def standard_response(self, success, message, data=None, errors=None, http_status=status.HTTP_200_OK):
        """Return standardized API response"""
        response_data = {
            'success': success,
            'message': message,
            'timestamp': timezone.now().isoformat()
        }

        if data is not None:
            response_data['data'] = data

        if errors is not None:
            response_data['errors'] = errors

        return Response(response_data, status=http_status)


@method_decorator(csrf_exempt, name='dispatch')
class DeviceAuthView(DeviceAPIView):
    """
    POST /api/v1/device/auth
    Authenticate device and return JWT token (simplified - returns API key validation)
    """

    def post(self, request):
        serializer = DeviceAuthSerializer(data=request.data)

        if not serializer.is_valid():
            return self.standard_response(
                False,
                "Invalid request data",
                errors=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST
            )

        device_unique_id = serializer.validated_data['device_unique_id']
        api_key = serializer.validated_data['api_key']

        try:
            device = Device.objects.get(device_unique_id=device_unique_id)

            # Verify API key
            key_prefix = api_key[:8]
            api_key_obj = DeviceAPIKey.objects.get(
                device=device,
                key_prefix=key_prefix,
                is_active=True
            )

            if not api_key_obj.verify_key(api_key):
                self.log_activity(request, device, None, 'auth', status.HTTP_401_UNAUTHORIZED,
                                error_message="Invalid API key")
                return self.standard_response(
                    False,
                    "Invalid API key",
                    http_status=status.HTTP_401_UNAUTHORIZED
                )

            api_key_obj.record_usage()

            self.log_activity(request, device, api_key_obj, 'auth', status.HTTP_200_OK)

            return self.standard_response(
                True,
                "Authentication successful",
                data={
                    'device_id': device.device_id,
                    'device_name': device.device_name,
                    'patient_id': device.patient.patient_id,
                    'permissions': {
                        'can_write_vitals': api_key_obj.can_write_vitals,
                        'can_read_patient': api_key_obj.can_read_patient
                    }
                }
            )

        except Device.DoesNotExist:
            return self.standard_response(
                False,
                "Device not found",
                http_status=status.HTTP_404_NOT_FOUND
            )
        except DeviceAPIKey.DoesNotExist:
            return self.standard_response(
                False,
                "Invalid API key",
                http_status=status.HTTP_401_UNAUTHORIZED
            )


@method_decorator(csrf_exempt, name='dispatch')
class PostVitalSignsView(DeviceAPIView):
    """
    POST /api/v1/device/vitals
    Submit vital signs data from IoT device
    """

    @transaction.atomic
    def post(self, request):
        # Authenticate device
        device, api_key_obj = self.get_device_from_api_key(request)

        if device is None:
            return self.standard_response(
                False,
                "Unauthorized: Invalid or missing API key",
                http_status=status.HTTP_401_UNAUTHORIZED
            )

        # Check permissions
        if not api_key_obj.can_write_vitals:
            self.log_activity(request, device, api_key_obj, 'data_post', status.HTTP_403_FORBIDDEN,
                            error_message="No permission to write vitals")
            return self.standard_response(
                False,
                "Permission denied: Cannot write vital signs",
                http_status=status.HTTP_403_FORBIDDEN
            )

        # Validate data
        serializer = VitalSignsDataSerializer(data=request.data)

        if not serializer.is_valid():
            self.log_activity(request, device, api_key_obj, 'data_post', status.HTTP_400_BAD_REQUEST,
                            error_message="Validation failed", details={'errors': serializer.errors})
            return self.standard_response(
                False,
                "Validation failed",
                errors=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data

        # Create VitalSign record
        vital_sign = VitalSign.objects.create(
            patient=device.patient,
            recorded_date=validated_data['timestamp'],
            blood_pressure_systolic=validated_data.get('blood_pressure_systolic'),
            blood_pressure_diastolic=validated_data.get('blood_pressure_diastolic'),
            heart_rate=validated_data.get('heart_rate'),
            temperature=validated_data.get('temperature'),
            respiratory_rate=validated_data.get('respiratory_rate'),
            oxygen_saturation=validated_data.get('oxygen_saturation'),
            weight=validated_data.get('weight'),
            height=validated_data.get('height')
        )

        # Store raw device data
        device_reading = DeviceDataReading.objects.create(
            device=device,
            patient=device.patient,
            reading_type='vital_signs',
            timestamp=validated_data['timestamp'],
            data=request.data,
            signal_quality=validated_data.get('signal_quality'),
            battery_level=validated_data.get('battery_level'),
            device_firmware=validated_data.get('firmware_version'),
            processed=True,
            processed_at=timezone.now(),
            vital_sign_id=vital_sign.vital_signs_id
        )

        # Update device status
        if validated_data.get('battery_level') is not None:
            device.battery_level = validated_data['battery_level']
        device.last_sync = timezone.now()
        device.save(update_fields=['battery_level', 'last_sync'])

        # Log activity
        self.log_activity(request, device, api_key_obj, 'data_post', status.HTTP_201_CREATED,
                        details={'vital_sign_id': vital_sign.vital_signs_id})

        return self.standard_response(
            True,
            "Vital signs recorded successfully",
            data={
                'vital_sign_id': vital_sign.vital_signs_id,
                'reading_id': device_reading.id,
                'timestamp': vital_sign.recorded_date.isoformat()
            },
            http_status=status.HTTP_201_CREATED
        )


@method_decorator(csrf_exempt, name='dispatch')
class BulkPostVitalSignsView(DeviceAPIView):
    """
    POST /api/v1/device/vitals/bulk
    Submit multiple vital signs readings at once
    """

    @transaction.atomic
    def post(self, request):
        # Authenticate device
        device, api_key_obj = self.get_device_from_api_key(request)

        if device is None:
            return self.standard_response(
                False,
                "Unauthorized: Invalid or missing API key",
                http_status=status.HTTP_401_UNAUTHORIZED
            )

        if not api_key_obj.can_write_vitals:
            return self.standard_response(
                False,
                "Permission denied: Cannot write vital signs",
                http_status=status.HTTP_403_FORBIDDEN
            )

        # Validate bulk data
        serializer = BulkVitalSignsSerializer(data=request.data)

        if not serializer.is_valid():
            return self.standard_response(
                False,
                "Validation failed",
                errors=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST
            )

        readings = serializer.validated_data['readings']
        created_records = []

        # Process each reading
        for reading_data in readings:
            vital_sign = VitalSign.objects.create(
                patient=device.patient,
                recorded_date=reading_data['timestamp'],
                blood_pressure_systolic=reading_data.get('blood_pressure_systolic'),
                blood_pressure_diastolic=reading_data.get('blood_pressure_diastolic'),
                heart_rate=reading_data.get('heart_rate'),
                temperature=reading_data.get('temperature'),
                respiratory_rate=reading_data.get('respiratory_rate'),
                oxygen_saturation=reading_data.get('oxygen_saturation'),
                weight=reading_data.get('weight'),
                height=reading_data.get('height')
            )

            created_records.append({
                'vital_sign_id': vital_sign.vital_signs_id,
                'timestamp': vital_sign.recorded_date.isoformat()
            })

        # Update device
        device.last_sync = timezone.now()
        device.save(update_fields=['last_sync'])

        # Log activity
        self.log_activity(request, device, api_key_obj, 'data_post', status.HTTP_201_CREATED,
                        details={'count': len(created_records)})

        return self.standard_response(
            True,
            f"Successfully recorded {len(created_records)} vital signs readings",
            data={'records': created_records, 'count': len(created_records)},
            http_status=status.HTTP_201_CREATED
        )


@method_decorator(csrf_exempt, name='dispatch')
class PostGlucoseDataView(DeviceAPIView):
    """
    POST /api/v1/device/glucose
    Submit blood glucose data
    """

    @transaction.atomic
    def post(self, request):
        device, api_key_obj = self.get_device_from_api_key(request)

        if device is None or not api_key_obj.can_write_vitals:
            return self.standard_response(
                False,
                "Unauthorized",
                http_status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = GlucoseDataSerializer(data=request.data)
        if not serializer.is_valid():
            return self.standard_response(
                False,
                "Validation failed",
                errors=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data

        # Store as device reading
        device_reading = DeviceDataReading.objects.create(
            device=device,
            patient=device.patient,
            reading_type='glucose',
            timestamp=validated_data['timestamp'],
            data=validated_data
        )

        return self.standard_response(
            True,
            "Glucose data recorded",
            data={'reading_id': device_reading.id},
            http_status=status.HTTP_201_CREATED
        )


@method_decorator(csrf_exempt, name='dispatch')
class UpdateDeviceStatusView(DeviceAPIView):
    """
    PUT /api/v1/device/status
    Update device status (battery, firmware, etc.)
    """

    def put(self, request):
        device, api_key_obj = self.get_device_from_api_key(request)

        if device is None:
            return self.standard_response(
                False,
                "Unauthorized",
                http_status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = DeviceStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return self.standard_response(
                False,
                "Validation failed",
                errors=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data

        # Update device fields
        if 'battery_level' in validated_data and validated_data['battery_level'] is not None:
            device.battery_level = validated_data['battery_level']

        if 'firmware_version' in validated_data and validated_data['firmware_version']:
            device.firmware_version = validated_data['firmware_version']

        if 'status' in validated_data and validated_data['status']:
            device.status = validated_data['status']

        device.last_sync = timezone.now()
        device.save()

        return self.standard_response(
            True,
            "Device status updated",
            data=DeviceSerializer(device).data
        )


@method_decorator(csrf_exempt, name='dispatch')
class DeviceInfoView(DeviceAPIView):
    """
    GET /api/v1/device/info
    Get device information
    """

    def get(self, request):
        device, api_key_obj = self.get_device_from_api_key(request)

        if device is None:
            return self.standard_response(
                False,
                "Unauthorized",
                http_status=status.HTTP_401_UNAUTHORIZED
            )

        return self.standard_response(
            True,
            "Device information",
            data=DeviceSerializer(device).data
        )
