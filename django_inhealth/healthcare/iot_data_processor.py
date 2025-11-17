"""
IoT Device Data Processor
Handles processing of IoT device vital signs data from JSON files
Integrates with existing vital signs and alert systems
"""
import json
import os
import shutil
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Device, Patient, Encounter, VitalSign, Provider
from .vital_alerts import process_vital_alerts
import logging

logger = logging.getLogger(__name__)


class IoTDataProcessor:
    """Process IoT device data from JSON files"""

    def __init__(self, inbox_dir=None, archive_dir=None):
        """
        Initialize the IoT data processor

        Args:
            inbox_dir: Directory where IoT devices upload JSON files
            archive_dir: Directory where processed files are archived
        """
        from django.conf import settings

        self.inbox_dir = inbox_dir or getattr(settings, 'IOT_INBOX_DIR', '/var/iot_data/inbox')
        self.archive_dir = archive_dir or getattr(settings, 'IOT_ARCHIVE_DIR', '/var/iot_data/archive')

        # Create directories if they don't exist
        os.makedirs(self.inbox_dir, exist_ok=True)
        os.makedirs(self.archive_dir, exist_ok=True)

    def process_all_pending_files(self):
        """
        Process all JSON files in the inbox directory

        Returns:
            dict: Processing statistics
        """
        stats = {
            'total_files': 0,
            'processed': 0,
            'failed': 0,
            'vitals_created': 0,
            'alerts_triggered': 0,
            'errors': []
        }

        # Get all JSON files in inbox
        json_files = [f for f in os.listdir(self.inbox_dir) if f.endswith('.json')]
        stats['total_files'] = len(json_files)

        logger.info(f"Processing {stats['total_files']} IoT data files...")

        for filename in json_files:
            filepath = os.path.join(self.inbox_dir, filename)

            try:
                result = self.process_file(filepath)

                if result['success']:
                    stats['processed'] += 1
                    stats['vitals_created'] += result.get('vitals_created', 0)
                    stats['alerts_triggered'] += result.get('alerts_triggered', 0)

                    # Archive the file
                    self.archive_file(filepath)
                else:
                    stats['failed'] += 1
                    stats['errors'].append({
                        'file': filename,
                        'error': result.get('error', 'Unknown error')
                    })

            except Exception as e:
                logger.error(f"Error processing file {filename}: {str(e)}")
                stats['failed'] += 1
                stats['errors'].append({
                    'file': filename,
                    'error': str(e)
                })

        logger.info(f"Processing complete: {stats['processed']} successful, {stats['failed']} failed")
        return stats

    def process_file(self, filepath):
        """
        Process a single IoT data JSON file

        Args:
            filepath: Path to JSON file

        Returns:
            dict: Processing result
        """
        result = {
            'success': False,
            'vitals_created': 0,
            'alerts_triggered': 0,
            'error': None
        }

        try:
            # Read JSON file
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Validate required fields
            if not self.validate_data(data):
                result['error'] = "Invalid data format"
                return result

            # Process the data
            vital_sign, alerts_triggered = self.create_vital_sign_from_data(data)

            if vital_sign:
                result['success'] = True
                result['vitals_created'] = 1
                result['alerts_triggered'] = alerts_triggered
                logger.info(f"Created vital sign {vital_sign.vital_signs_id} from IoT device")
            else:
                result['error'] = "Failed to create vital sign"

        except json.JSONDecodeError as e:
            result['error'] = f"Invalid JSON: {str(e)}"
        except Exception as e:
            result['error'] = str(e)
            logger.exception(f"Error processing file {filepath}")

        return result

    def validate_data(self, data):
        """
        Validate IoT data has required fields

        Args:
            data: Parsed JSON data

        Returns:
            bool: True if valid
        """
        required_fields = ['device_id', 'timestamp']

        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return False

        # Must have at least one vital sign measurement
        vital_fields = [
            'heart_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'temperature', 'respiratory_rate', 'oxygen_saturation', 'glucose'
        ]

        if not any(field in data for field in vital_fields):
            logger.error("No vital sign measurements found in data")
            return False

        return True

    @transaction.atomic
    def create_vital_sign_from_data(self, data):
        """
        Create VitalSign record from IoT device data

        Args:
            data: Parsed JSON data from IoT device

        Returns:
            tuple: (VitalSign object, alerts_triggered_count)
        """
        # Get or validate device
        try:
            device = Device.objects.get(device_unique_id=data['device_id'])
        except Device.DoesNotExist:
            logger.error(f"Device not found: {data['device_id']}")
            raise ValidationError(f"Device {data['device_id']} not found in system")

        # Get patient associated with device
        patient = device.patient
        if not patient:
            logger.error(f"Device {device.device_id} not assigned to any patient")
            raise ValidationError(f"Device {device.device_id} not assigned to a patient")

        # Create or get encounter for device data
        encounter = self.get_or_create_device_encounter(patient, device)

        # Parse timestamp
        try:
            if isinstance(data['timestamp'], str):
                timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            else:
                timestamp = timezone.now()
        except (ValueError, KeyError):
            timestamp = timezone.now()

        # Create vital sign record
        vital_sign = VitalSign.objects.create(
            encounter=encounter,
            data_source='device',
            device=device,
            recorded_at=timestamp,

            # Vital signs data
            heart_rate=data.get('heart_rate'),
            blood_pressure_systolic=data.get('blood_pressure_systolic'),
            blood_pressure_diastolic=data.get('blood_pressure_diastolic'),
            temperature_value=data.get('temperature'),
            temperature_unit=data.get('temperature_unit', 'F'),
            respiratory_rate=data.get('respiratory_rate'),
            oxygen_saturation=data.get('oxygen_saturation'),
            glucose=data.get('glucose'),
            weight_value=data.get('weight'),
            weight_unit=data.get('weight_unit', 'lbs'),

            # Metadata
            notes=data.get('notes', f"Automated reading from {device.device_name}")
        )

        # Trigger alerts using existing alert system
        alerts_triggered = self.trigger_alerts(vital_sign, patient, device)

        logger.info(f"Created vital sign {vital_sign.vital_signs_id} for patient {patient.full_name}")

        return vital_sign, alerts_triggered

    def get_or_create_device_encounter(self, patient, device):
        """
        Get or create an encounter for device data
        Creates a virtual encounter for device readings

        Args:
            patient: Patient object
            device: Device object

        Returns:
            Encounter object
        """
        # Look for recent device encounter (within last 24 hours)
        recent_encounter = Encounter.objects.filter(
            patient=patient,
            encounter_type='Remote Monitoring',
            encounter_date__gte=timezone.now() - timedelta(hours=24)
        ).first()

        if recent_encounter:
            return recent_encounter

        # Create new remote monitoring encounter
        encounter = Encounter.objects.create(
            patient=patient,
            provider=patient.primary_doctor,  # Use patient's primary doctor
            encounter_date=timezone.now(),
            encounter_type='Remote Monitoring',
            chief_complaint=f'Automated vital signs monitoring via {device.device_name}',
            status='In Progress',
            notes=f'Automated encounter for IoT device data collection from {device.device_name}'
        )

        logger.info(f"Created remote monitoring encounter {encounter.encounter_id} for patient {patient.full_name}")

        return encounter

    def trigger_alerts(self, vital_sign, patient, device):
        """
        Trigger alerts for critical vital signs using existing alert system

        Args:
            vital_sign: VitalSign object
            patient: Patient object
            device: Device object

        Returns:
            int: Number of alerts triggered
        """
        alerts_triggered = 0

        try:
            # Use the existing vital_alerts.process_vital_alerts function
            # This function handles the two-stage alert system (patient consent then provider notification)
            alert_response = process_vital_alerts(vital_sign)

            if alert_response:
                alerts_triggered = 1
                logger.info(f"Alert triggered for vital sign {vital_sign.vital_signs_id}")

        except Exception as e:
            logger.error(f"Error triggering alert for vital sign {vital_sign.vital_signs_id}: {str(e)}")

        return alerts_triggered

    def archive_file(self, filepath):
        """
        Archive processed file with timestamp

        Args:
            filepath: Path to file to archive
        """
        filename = os.path.basename(filepath)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Create dated archive subfolder
        date_folder = datetime.now().strftime('%Y-%m-%d')
        archive_subdir = os.path.join(self.archive_dir, date_folder)
        os.makedirs(archive_subdir, exist_ok=True)

        # Create archived filename with timestamp
        name, ext = os.path.splitext(filename)
        archived_filename = f"{name}_{timestamp}{ext}"
        archived_filepath = os.path.join(archive_subdir, archived_filename)

        # Move file to archive
        shutil.move(filepath, archived_filepath)
        logger.info(f"Archived file: {archived_filename}")

    def cleanup_old_archives(self, days=90):
        """
        Clean up archived files older than specified days

        Args:
            days: Number of days to keep archived files
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0

        for root, dirs, files in os.walk(self.archive_dir):
            for filename in files:
                filepath = os.path.join(root, filename)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))

                if file_mtime < cutoff_date:
                    os.remove(filepath)
                    deleted_count += 1
                    logger.info(f"Deleted old archive: {filename}")

        logger.info(f"Cleanup complete: {deleted_count} files deleted")
        return deleted_count
