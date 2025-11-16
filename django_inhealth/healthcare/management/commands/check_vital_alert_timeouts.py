"""
Management command to check for timed-out vital sign alert responses
and auto-escalate them to providers.

This should be run as a cron job or scheduled task every 1-5 minutes.

Usage:
    python manage.py check_vital_alert_timeouts

    # In cron (every 5 minutes):
    */5 * * * * cd /path/to/project && python manage.py check_vital_alert_timeouts
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from healthcare.models import VitalSignAlertResponse


class Command(BaseCommand):
    help = 'Check for timed-out vital sign alert responses and auto-escalate them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be escalated without actually doing it',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']

        if verbose or dry_run:
            self.stdout.write(self.style.WARNING('='*70))
            self.stdout.write(self.style.WARNING('Checking for timed-out vital sign alerts...'))
            self.stdout.write(self.style.WARNING(f'Time: {timezone.now()}'))
            self.stdout.write(self.style.WARNING('='*70))

        # Get all pending alerts
        pending_alerts = VitalSignAlertResponse.objects.filter(
            patient_response_status='pending',
            auto_escalated=False
        )

        if verbose:
            self.stdout.write(f'Found {pending_alerts.count()} pending alerts')

        # Check each alert for timeout
        escalated_count = 0
        for alert in pending_alerts:
            if alert.should_auto_escalate():
                escalated_count += 1

                patient_name = alert.patient.full_name
                alert_id = alert.alert_id
                minutes_elapsed = (timezone.now() - alert.created_at).total_seconds() / 60

                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(
                            f'[DRY RUN] Would escalate Alert #{alert_id} for {patient_name} '
                            f'(elapsed: {minutes_elapsed:.1f} min, timeout: {alert.timeout_minutes} min)'
                        )
                    )
                else:
                    if verbose:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Escalating Alert #{alert_id} for {patient_name} '
                                f'(elapsed: {minutes_elapsed:.1f} min, timeout: {alert.timeout_minutes} min)'
                            )
                        )

                    # Auto-escalate the alert
                    try:
                        alert.auto_escalate()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Alert #{alert_id} auto-escalated successfully'
                            )
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'✗ Error escalating Alert #{alert_id}: {str(e)}'
                            )
                        )

        # Summary
        if verbose or dry_run or escalated_count > 0:
            self.stdout.write(self.style.WARNING('='*70))
            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'[DRY RUN] Would have escalated {escalated_count} alert(s)'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully escalated {escalated_count} alert(s)'
                    )
                )
            self.stdout.write(self.style.WARNING('='*70))
