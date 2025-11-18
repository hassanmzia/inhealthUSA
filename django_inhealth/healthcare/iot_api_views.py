"""
IoT Device REST API Views
Endpoints for IoT devices to submit vital signs data
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models_iot import DeviceAPIKey, DeviceDataReading, DeviceActivityLog
from .models import Device
from .iot_data_processor import IoTDataProcessor
from datetime import datetime
import time

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def authenticate_device(request):
    """
    Authenticate IoT device using API key

    Args:
        request: Django request object

    Returns:
        tuple: (is_authenticated, device_api_key, error_message)
    """
    # Get API key from Authorization header
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')

    if not auth_header.startswith('Bearer '):
        return False, None, "Missing or invalid Authorization header"

    api_key = auth_header.replace('Bearer ', '').strip()

    if not api_key:
        return False, None, "Empty API key"

    # Extract key prefix (first 8 chars)
    if len(api_key) < 8:
        return False, None, "Invalid API key format"

    key_prefix = api_key[:8]

    # Find API key by prefix
    try:
        device_api_key = DeviceAPIKey.objects.select_related('device').get(
            key_prefix=key_prefix,
            is_active=True
        )
    except DeviceAPIKey.DoesNotExist:
        return False, None, "Invalid API key"

    # Verify full key
    if not device_api_key.verify_key(api_key):
        return False, None, "Invalid API key"

    # Check if device has write permissions
    if not device_api_key.can_write_vitals:
        return False, None, "API key does not have permission to write vitals"

    # Record usage
    device_api_key.record_usage()

    return True, device_api_key, None


def log_api_activity(device, api_key, action_type, request, status_code, response_time_ms=None, error_message=None):
    """Log API activity for auditing"""
    try:
        DeviceActivityLog.objects.create(
            device=device,
            api_key=api_key,
            action_type=action_type,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            endpoint=request.path,
            http_method=request.method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            error_message=error_message
        )
    except Exception as e:
        logger.error(f"Failed to log API activity: {str(e)}")


@csrf_exempt
@require_http_methods(["POST"])
def submit_vitals(request):
    """
    API endpoint for IoT devices to submit vital signs data

    Request:
        POST /api/iot/vitals/
        Headers:
            Authorization: Bearer <api_key>
            Content-Type: application/json
        Body:
            {
                "device_id": "DEV001",  // Device unique ID (string) or device_id (integer)
                "timestamp": "2025-11-17T10:30:00Z",
                "heart_rate": 75,
                "blood_pressure_systolic": 120,
                "blood_pressure_diastolic": 80,
                "temperature": 98.6,
                "temperature_unit": "F",
                "respiratory_rate": 16,
                "oxygen_saturation": 98.0,
                "glucose": 95.0,
                "weight": 150.0,
                "weight_unit": "lbs",
                "notes": "Optional notes",
                "signal_quality": 95,
                "battery_level": 80
            }

    Response:
        {
            "success": true,
            "message": "Vital signs received successfully",
            "vital_sign_id": 123,
            "alerts_triggered": 1
        }
    """
    start_time = time.time()
    device = None
    api_key = None

    try:
        # Authenticate device
        is_authenticated, device_api_key, error_message = authenticate_device(request)

        if not is_authenticated:
            log_api_activity(None, None, 'auth', request, 401, error_message=error_message)
            return JsonResponse({
                'success': False,
                'error': error_message
            }, status=401)

        api_key = device_api_key
        device = device_api_key.device

        # Parse request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            error_msg = "Invalid JSON in request body"
            log_api_activity(device, api_key, 'error', request, 400, error_message=error_msg)
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=400)

        # Validate device_id matches authenticated device
        # Accept both device_unique_id (string) and device_id (integer)
        payload_device_id = data.get('device_id')
        if payload_device_id != device.device_unique_id and payload_device_id != device.device_id:
            error_msg = f"device_id in payload ('{payload_device_id}') does not match authenticated device (expected: '{device.device_unique_id}' or {device.device_id})"
            log_api_activity(device, api_key, 'error', request, 403, error_message=error_msg)
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=403)

        # Process the data using IoT data processor
        processor = IoTDataProcessor()

        # Add timestamp if not provided
        if 'timestamp' not in data:
            data['timestamp'] = timezone.now().isoformat()

        # Validate data
        if not processor.validate_data(data):
            error_msg = "Invalid vital signs data format"
            log_api_activity(device, api_key, 'error', request, 400, error_message=error_msg)
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=400)

        # Create vital sign record
        vital_sign, alerts_triggered = processor.create_vital_sign_from_data(data)

        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)

        # Log successful activity
        log_api_activity(device, api_key, 'data_post', request, 200, response_time_ms)

        return JsonResponse({
            'success': True,
            'message': 'Vital signs received successfully',
            'vital_sign_id': vital_sign.vital_signs_id,
            'alerts_triggered': alerts_triggered,
            'timestamp': vital_sign.recorded_at.isoformat()
        }, status=200)

    except ValidationError as e:
        error_msg = str(e)
        log_api_activity(device, api_key, 'error', request, 400, error_message=error_msg)
        return JsonResponse({
            'success': False,
            'error': error_msg
        }, status=400)

    except Exception as e:
        logger.exception("Error processing IoT vital signs submission")
        error_msg = f"Internal server error: {str(e)}"
        log_api_activity(device, api_key, 'error', request, 500, error_message=error_msg)
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def device_status(request):
    """
    API endpoint for IoT devices to check their status

    Request:
        GET /api/iot/status/
        Headers:
            Authorization: Bearer <api_key>

    Response:
        {
            "success": true,
            "device_id": "DEV001",
            "device_name": "Smart BP Monitor",
            "is_active": true,
            "patient_assigned": true,
            "patient_id": "P123",
            "api_key_valid": true,
            "last_reading": "2025-11-17T10:30:00Z"
        }
    """
    try:
        # Authenticate device
        is_authenticated, device_api_key, error_message = authenticate_device(request)

        if not is_authenticated:
            log_api_activity(None, None, 'auth', request, 401, error_message=error_message)
            return JsonResponse({
                'success': False,
                'error': error_message
            }, status=401)

        device = device_api_key.device

        # Get last reading
        last_reading = device.vitals_recorded.order_by('-recorded_at').first()

        # Log activity
        log_api_activity(device, device_api_key, 'data_get', request, 200)

        return JsonResponse({
            'success': True,
            'device_id': device.device_id,
            'device_name': device.device_name,
            'device_type': device.device_type,
            'is_active': device.is_active,
            'patient_assigned': device.patient is not None,
            'patient_id': device.patient.patient_id if device.patient else None,
            'api_key_valid': True,
            'last_reading': last_reading.recorded_at.isoformat() if last_reading else None
        }, status=200)

    except Exception as e:
        logger.exception("Error checking device status")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def submit_vitals_batch(request):
    """
    API endpoint for IoT devices to submit multiple vital sign readings at once

    Request:
        POST /api/iot/vitals/batch/
        Headers:
            Authorization: Bearer <api_key>
            Content-Type: application/json
        Body:
            {
                "device_id": "DEV001",
                "readings": [
                    {
                        "timestamp": "2025-11-17T10:30:00Z",
                        "heart_rate": 75,
                        ...
                    },
                    {
                        "timestamp": "2025-11-17T11:30:00Z",
                        "heart_rate": 78,
                        ...
                    }
                ]
            }

    Response:
        {
            "success": true,
            "message": "Batch submitted successfully",
            "total_readings": 2,
            "processed": 2,
            "failed": 0,
            "vitals_created": [123, 124],
            "alerts_triggered": 1
        }
    """
    start_time = time.time()

    try:
        # Authenticate device
        is_authenticated, device_api_key, error_message = authenticate_device(request)

        if not is_authenticated:
            return JsonResponse({
                'success': False,
                'error': error_message
            }, status=401)

        device = device_api_key.device

        # Parse request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON in request body'
            }, status=400)

        readings = data.get('readings', [])

        if not readings or not isinstance(readings, list):
            return JsonResponse({
                'success': False,
                'error': 'No readings provided or invalid format'
            }, status=400)

        # Process each reading
        processor = IoTDataProcessor()
        results = {
            'total_readings': len(readings),
            'processed': 0,
            'failed': 0,
            'vitals_created': [],
            'alerts_triggered': 0,
            'errors': []
        }

        for reading in readings:
            # Add device_id to each reading
            reading['device_id'] = device.device_id

            try:
                vital_sign, alerts = processor.create_vital_sign_from_data(reading)
                results['processed'] += 1
                results['vitals_created'].append(vital_sign.vital_signs_id)
                results['alerts_triggered'] += alerts
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(str(e))
                logger.error(f"Error processing reading in batch: {str(e)}")

        # Log activity
        response_time_ms = int((time.time() - start_time) * 1000)
        log_api_activity(device, device_api_key, 'data_post', request, 200, response_time_ms)

        return JsonResponse({
            'success': True,
            'message': 'Batch submitted successfully',
            **results
        }, status=200)

    except Exception as e:
        logger.exception("Error processing batch vital signs submission")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)
