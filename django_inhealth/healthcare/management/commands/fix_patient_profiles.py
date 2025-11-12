"""
Management command to create Patient records for users with patient role
who don't have a corresponding Patient record
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from healthcare.models import UserProfile, Patient, Provider


class Command(BaseCommand):
    help = 'Creates Patient/Provider records for users who have the appropriate role but no corresponding profile'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating records',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No records will be created'))

        # Find users with patient role but no Patient record
        patient_profiles = UserProfile.objects.filter(role='patient').select_related('user')
        patients_created = 0
        patients_skipped = 0

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Checking Patient Profiles'))
        self.stdout.write('='*60)

        for profile in patient_profiles:
            user = profile.user

            # Check if Patient record exists
            try:
                patient = user.patient_profile
                self.stdout.write(f'✓ User {user.username} ({user.id}) already has Patient record (ID: {patient.patient_id})')
                patients_skipped += 1
            except (Patient.DoesNotExist, AttributeError):
                # Patient record doesn't exist, create it
                if not dry_run:
                    patient = Patient.objects.create(
                        user=user,
                        first_name=user.first_name or 'Unknown',
                        last_name=user.last_name or 'Unknown',
                        date_of_birth=profile.date_of_birth or '2000-01-01',
                        gender='Other',
                        email=user.email,
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Created Patient record (ID: {patient.patient_id}) for user {user.username} ({user.id})'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ Would create Patient record for user {user.username} ({user.id})'
                        )
                    )
                patients_created += 1

        # Find users with doctor role but no Provider record
        doctor_profiles = UserProfile.objects.filter(role='doctor').select_related('user')
        providers_created = 0
        providers_skipped = 0

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Checking Provider Profiles'))
        self.stdout.write('='*60)

        for profile in doctor_profiles:
            user = profile.user

            # Check if Provider record exists
            try:
                provider = user.provider_profile
                self.stdout.write(f'✓ User {user.username} ({user.id}) already has Provider record (ID: {provider.provider_id})')
                providers_skipped += 1
            except (Provider.DoesNotExist, AttributeError):
                # Provider record doesn't exist, create it
                if not dry_run:
                    provider = Provider.objects.create(
                        user=user,
                        first_name=user.first_name or 'Unknown',
                        last_name=user.last_name or 'Unknown',
                        npi=f'TEMP{user.id:010d}',  # Temporary NPI - admin should update
                        email=user.email,
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Created Provider record (ID: {provider.provider_id}) for user {user.username} ({user.id})'
                        )
                    )
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠ Provider has temporary NPI: {provider.npi} - Please update with real NPI'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ Would create Provider record for user {user.username} ({user.id})'
                        )
                    )
                providers_created += 1

        # Print summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write('='*60)
        self.stdout.write(f'Patient records:')
        self.stdout.write(f'  - Created: {patients_created}')
        self.stdout.write(f'  - Already exist: {patients_skipped}')
        self.stdout.write(f'Provider records:')
        self.stdout.write(f'  - Created: {providers_created}')
        self.stdout.write(f'  - Already exist: {providers_skipped}')

        if dry_run:
            self.stdout.write('\n' + self.style.WARNING('DRY RUN COMPLETE - Run without --dry-run to create records'))
        else:
            self.stdout.write('\n' + self.style.SUCCESS('COMPLETE'))
