"""
Management command to link User accounts with Patient and Provider records
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from healthcare.models import Patient, Provider, UserProfile


class Command(BaseCommand):
    help = 'Link User accounts with Patient and Provider records by email or create UserProfiles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be linked without actually making changes',
        )
        parser.add_argument(
            '--create-profiles',
            action='store_true',
            help='Create UserProfile for users that don\'t have one',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        create_profiles = options['create_profiles']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        # Step 1: Create UserProfiles for users without one
        if create_profiles:
            self.stdout.write('\n' + '='*60)
            self.stdout.write('Step 1: Creating UserProfiles for users without profiles')
            self.stdout.write('='*60)

            users_without_profile = User.objects.filter(profile__isnull=True)
            profile_count = users_without_profile.count()

            if profile_count == 0:
                self.stdout.write(self.style.SUCCESS('✓ All users already have profiles'))
            else:
                self.stdout.write(f'Found {profile_count} users without profiles')

                if not dry_run:
                    with transaction.atomic():
                        for user in users_without_profile:
                            UserProfile.objects.create(
                                user=user,
                                role='patient'  # Default role
                            )
                            self.stdout.write(f'  Created profile for: {user.username} (default role: patient)')
                    self.stdout.write(self.style.SUCCESS(f'✓ Created {profile_count} UserProfiles'))
                else:
                    for user in users_without_profile:
                        self.stdout.write(f'  Would create profile for: {user.username}')

        # Step 2: Link Patients to Users by email
        self.stdout.write('\n' + '='*60)
        self.stdout.write('Step 2: Linking Patient records to User accounts by email')
        self.stdout.write('='*60)

        patients_without_user = Patient.objects.filter(user__isnull=True).exclude(email__isnull=True).exclude(email='')
        patient_link_count = 0
        patient_no_match_count = 0

        for patient in patients_without_user:
            try:
                user = User.objects.get(email__iexact=patient.email)

                # Update user profile to patient role if needed
                try:
                    profile = user.profile
                    if profile.role != 'patient':
                        self.stdout.write(f'  ⚠ Warning: User {user.username} has role "{profile.role}" but will be linked to patient')
                except UserProfile.DoesNotExist:
                    if not dry_run and create_profiles:
                        UserProfile.objects.create(user=user, role='patient')
                        self.stdout.write(f'  Created patient profile for: {user.username}')

                if not dry_run:
                    patient.user = user
                    patient.save()
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Linked patient "{patient.full_name}" to user "{user.username}"'))
                else:
                    self.stdout.write(f'  Would link patient "{patient.full_name}" to user "{user.username}"')

                patient_link_count += 1

            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ✗ No user found with email: {patient.email} (Patient: {patient.full_name})'))
                patient_no_match_count += 1
            except User.MultipleObjectsReturned:
                self.stdout.write(self.style.ERROR(f'  ✗ Multiple users found with email: {patient.email}'))
                patient_no_match_count += 1

        if patient_link_count > 0:
            self.stdout.write(self.style.SUCCESS(f'✓ Linked {patient_link_count} patients to users'))
        if patient_no_match_count > 0:
            self.stdout.write(self.style.WARNING(f'⚠ {patient_no_match_count} patients could not be linked'))
        if patient_link_count == 0 and patient_no_match_count == 0:
            self.stdout.write(self.style.SUCCESS('✓ All patients are already linked or have no email'))

        # Step 3: Link Providers to Users by email
        self.stdout.write('\n' + '='*60)
        self.stdout.write('Step 3: Linking Provider records to User accounts by email')
        self.stdout.write('='*60)

        providers_without_user = Provider.objects.filter(user__isnull=True).exclude(email__isnull=True).exclude(email='')
        provider_link_count = 0
        provider_no_match_count = 0

        for provider in providers_without_user:
            try:
                user = User.objects.get(email__iexact=provider.email)

                # Update user profile to doctor role if needed
                try:
                    profile = user.profile
                    if profile.role not in ['doctor', 'office_admin']:
                        if not dry_run:
                            profile.role = 'doctor'
                            profile.save()
                            self.stdout.write(f'  Updated user {user.username} role to "doctor"')
                        else:
                            self.stdout.write(f'  Would update user {user.username} role to "doctor"')
                except UserProfile.DoesNotExist:
                    if not dry_run and create_profiles:
                        UserProfile.objects.create(user=user, role='doctor')
                        self.stdout.write(f'  Created doctor profile for: {user.username}')

                if not dry_run:
                    provider.user = user
                    provider.save()
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Linked provider "Dr. {provider.full_name}" to user "{user.username}"'))
                else:
                    self.stdout.write(f'  Would link provider "Dr. {provider.full_name}" to user "{user.username}"')

                provider_link_count += 1

            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ✗ No user found with email: {provider.email} (Provider: Dr. {provider.full_name})'))
                provider_no_match_count += 1
            except User.MultipleObjectsReturned:
                self.stdout.write(self.style.ERROR(f'  ✗ Multiple users found with email: {provider.email}'))
                provider_no_match_count += 1

        if provider_link_count > 0:
            self.stdout.write(self.style.SUCCESS(f'✓ Linked {provider_link_count} providers to users'))
        if provider_no_match_count > 0:
            self.stdout.write(self.style.WARNING(f'⚠ {provider_no_match_count} providers could not be linked'))
        if provider_link_count == 0 and provider_no_match_count == 0:
            self.stdout.write(self.style.SUCCESS('✓ All providers are already linked or have no email'))

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SUMMARY')
        self.stdout.write('='*60)

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes were made'))
            self.stdout.write('Run without --dry-run to apply these changes')
        else:
            self.stdout.write(self.style.SUCCESS('All linking operations completed!'))

        if create_profiles:
            self.stdout.write(f'UserProfiles created: {profile_count if not dry_run else "N/A (dry run)"}')
        self.stdout.write(f'Patients linked: {patient_link_count}')
        self.stdout.write(f'Providers linked: {provider_link_count}')
        self.stdout.write(f'Total linked: {patient_link_count + provider_link_count}')

        if patient_no_match_count + provider_no_match_count > 0:
            self.stdout.write(self.style.WARNING(f'\nNote: {patient_no_match_count + provider_no_match_count} records could not be linked automatically'))
            self.stdout.write('You can link these manually in the Django admin panel')
