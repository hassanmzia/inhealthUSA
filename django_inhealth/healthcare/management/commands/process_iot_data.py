"""
Django Management Command to Process IoT Device Data
Run this command periodically (e.g., via cron) to process pending IoT data files

Usage:
    python manage.py process_iot_data
    python manage.py process_iot_data --cleanup  # Also cleanup old archives
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from healthcare.iot_data_processor import IoTDataProcessor
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process pending IoT device data files from inbox directory'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Cleanup old archived files (older than 90 days)',
        )
        parser.add_argument(
            '--cleanup-days',
            type=int,
            default=90,
            help='Number of days to keep archived files (default: 90)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== IoT Data Processor ==='))
        self.stdout.write(f'Started at: {logger.name}')

        # Initialize processor
        processor = IoTDataProcessor()

        self.stdout.write(f'Inbox directory: {processor.inbox_dir}')
        self.stdout.write(f'Archive directory: {processor.archive_dir}')

        # Process all pending files
        self.stdout.write('\nProcessing pending files...')
        stats = processor.process_all_pending_files()

        # Display results
        self.stdout.write(self.style.SUCCESS('\n=== Processing Results ==='))
        self.stdout.write(f'Total files found: {stats["total_files"]}')
        self.stdout.write(self.style.SUCCESS(f'Successfully processed: {stats["processed"]}'))
        self.stdout.write(self.style.ERROR(f'Failed: {stats["failed"]}'))
        self.stdout.write(f'Vital signs created: {stats["vitals_created"]}')
        self.stdout.write(f'Alerts triggered: {stats["alerts_triggered"]}')

        # Show errors if any
        if stats['errors']:
            self.stdout.write(self.style.WARNING('\n=== Errors ==='))
            for error in stats['errors']:
                self.stdout.write(self.style.ERROR(f"File: {error['file']}"))
                self.stdout.write(self.style.ERROR(f"Error: {error['error']}\n"))

        # Cleanup old archives if requested
        if options['cleanup']:
            self.stdout.write(self.style.WARNING('\n=== Cleanup Old Archives ==='))
            days = options['cleanup_days']
            self.stdout.write(f'Deleting files older than {days} days...')

            deleted_count = processor.cleanup_old_archives(days=days)
            self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_count} old archived files'))

        self.stdout.write(self.style.SUCCESS('\n=== Complete ==='))
