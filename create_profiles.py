#!/usr/bin/env python
"""
Script to create Patient and Provider profiles for existing users
Run this with: python manage.py shell < create_profiles.py
Or: python create_profiles.py (if Django is in PYTHONPATH)
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/home/user/inhealthUSA/django_inhealth')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inhealth.settings')
django.setup()

from django.contrib.auth.models import User
from healthcare.models import UserProfile, Patient, Provider

def create_profiles():
    """Create Patient/Provider profiles for users who don't have them"""

    print("="*70)
    print("Creating Patient and Provider Profiles")
    print("="*70)

    # Get all user profiles
    profiles = UserProfile.objects.all().select_related('user')

    patients_created = 0
    providers_created = 0
    patients_skipped = 0
    providers_skipped = 0

    for profile in profiles:
        user = profile.user

        if profile.role == 'patient':
            # Check if Patient record exists
            try:
                patient = user.patient_profile
                print(f"✓ User {user.username} ({user.id}) already has Patient record (ID: {patient.patient_id})")
                patients_skipped += 1
            except (Patient.DoesNotExist, AttributeError):
                # Create Patient record
                patient = Patient.objects.create(
                    user=user,
                    first_name=user.first_name or 'Unknown',
                    last_name=user.last_name or 'Unknown',
                    date_of_birth=profile.date_of_birth or '2000-01-01',
                    gender='Other',
                    email=user.email,
                )
                print(f"✓ Created Patient record (ID: {patient.patient_id}) for user {user.username} ({user.id})")
                patients_created += 1

        elif profile.role == 'doctor':
            # Check if Provider record exists
            try:
                provider = user.provider_profile
                print(f"✓ User {user.username} ({user.id}) already has Provider record (ID: {provider.provider_id})")
                providers_skipped += 1
            except (Provider.DoesNotExist, AttributeError):
                # Create Provider record
                provider = Provider.objects.create(
                    user=user,
                    first_name=user.first_name or 'Unknown',
                    last_name=user.last_name or 'Unknown',
                    npi=f'TEMP{user.id:010d}',  # Temporary NPI
                    email=user.email,
                )
                print(f"✓ Created Provider record (ID: {provider.provider_id}) for user {user.username} ({user.id})")
                print(f"  ⚠ Provider has temporary NPI: {provider.npi} - Please update with real NPI")
                providers_created += 1

    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Patient records:")
    print(f"  - Created: {patients_created}")
    print(f"  - Already exist: {patients_skipped}")
    print(f"Provider records:")
    print(f"  - Created: {providers_created}")
    print(f"  - Already exist: {providers_skipped}")
    print("="*70)
    print("\nDone!")

if __name__ == '__main__':
    create_profiles()
