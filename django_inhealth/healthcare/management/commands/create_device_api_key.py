"""
Django management command to create API keys for IoT devices

Usage:
    python manage.py create_device_api_key --device-id=123 --key-name="Primary API Key"
    python manage.py create_device_api_key --device-unique-id="MAC:00:11:22:33:44:55" --key-name="Backup Key" --expires=90
"""

from django.core.management.base import BaseCommand, CommandError
from healthcare.models import Device
from healthcare.models_iot import DeviceAPIKey


class Command(BaseCommand):
    help = 'Create an API key for an IoT device'

    def add_arguments(self, parser):
        parser.add_argument(
            '--device-id',
            type=int,
            help='Device ID in database',
        )
        parser.add_argument(
            '--device-unique-id',
            type=str,
            help='Device unique ID (alternative to device-id)',
        )
        parser.add_argument(
            '--key-name',
            type=str,
            required=True,
            help='Friendly name for this API key',
        )
        parser.add_argument(
            '--expires',
            type=int,
            default=None,
            help='Expiration in days (optional, default: never expires)',
        )
        parser.add_argument(
            '--no-write-vitals',
            action='store_true',
            help='Do not allow writing vital signs data',
        )
        parser.add_argument(
            '--allow-read-patient',
            action='store_true',
            help='Allow reading patient information',
        )

    def handle(self, *args, **options):
        # Get device
        device = None

        if options['device_id']:
            try:
                device = Device.objects.get(device_id=options['device_id'])
            except Device.DoesNotExist:
                raise CommandError(f'Device with ID {options["device_id"]} does not exist')

        elif options['device_unique_id']:
            try:
                device = Device.objects.get(device_unique_id=options['device_unique_id'])
            except Device.DoesNotExist:
                raise CommandError(f'Device with unique ID {options["device_unique_id"]} does not exist')

        else:
            raise CommandError('Either --device-id or --device-unique-id must be provided')

        # Create API key
        api_key_obj, api_key = DeviceAPIKey.create_key(
            device=device,
            key_name=options['key_name'],
            expires_in_days=options['expires']
        )

        # Set permissions
        api_key_obj.can_write_vitals = not options['no_write_vitals']
        api_key_obj.can_read_patient = options['allow_read_patient']
        api_key_obj.save()

        # Output results
        self.stdout.write(self.style.SUCCESS('\n=== API Key Created Successfully ===\n'))
        self.stdout.write(f'Device: {device.device_name} ({device.device_unique_id})')
        self.stdout.write(f'Patient: {device.patient.full_name}')
        self.stdout.write(f'Key Name: {options["key_name"]}')
        self.stdout.write(f'Key Prefix: {api_key_obj.key_prefix}')

        if options['expires']:
            self.stdout.write(f'Expires: {api_key_obj.expires_at.strftime("%Y-%m-%d %H:%M:%S")}')
        else:
            self.stdout.write('Expires: Never')

        self.stdout.write(f'\nPermissions:')
        self.stdout.write(f'  - Can Write Vitals: {api_key_obj.can_write_vitals}')
        self.stdout.write(f'  - Can Read Patient: {api_key_obj.can_read_patient}')

        self.stdout.write(self.style.WARNING('\n=== API KEY (Save this - it will not be shown again!) ===\n'))
        self.stdout.write(self.style.WARNING(api_key))
        self.stdout.write(self.style.WARNING('\n' + '=' * 70 + '\n'))

        self.stdout.write(self.style.SUCCESS('\nAPI key created and ready to use!'))
        self.stdout.write('\nUsage in device code:')
        self.stdout.write('  Authorization: Bearer ' + api_key)
