"""
Django signals for automatic profile creation and management
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile, Patient, Provider


@receiver(post_save, sender=UserProfile)
def create_profile_records(sender, instance, created, **kwargs):
    """
    Automatically create Patient or Provider records when a UserProfile is created
    with the appropriate role
    """
    # Only process for newly created profiles or when role changes
    if created or 'role' in kwargs.get('update_fields', []):
        user = instance.user

        # Create Patient record for patient role
        if instance.role == 'patient':
            # Check if patient record already exists
            if not hasattr(user, 'patient_profile') or user.patient_profile is None:
                try:
                    Patient.objects.get_or_create(
                        user=user,
                        defaults={
                            'first_name': user.first_name or 'Unknown',
                            'last_name': user.last_name or 'Unknown',
                            'date_of_birth': instance.date_of_birth or '2000-01-01',
                            'gender': 'Other',
                            'email': user.email,
                        }
                    )
                except Exception as e:
                    # Log the error but don't prevent profile creation
                    print(f"Error creating Patient record for user {user.id}: {e}")

        # Create Provider record for doctor role
        elif instance.role == 'doctor':
            # Check if provider record already exists
            if not hasattr(user, 'provider_profile') or user.provider_profile is None:
                try:
                    # Note: Provider requires NPI which must be unique
                    # We'll create a temporary NPI based on user ID
                    # Admin should update this with real NPI
                    Provider.objects.get_or_create(
                        user=user,
                        defaults={
                            'first_name': user.first_name or 'Unknown',
                            'last_name': user.last_name or 'Unknown',
                            'npi': f'TEMP{user.id:010d}',  # Temporary NPI
                            'email': user.email,
                        }
                    )
                except Exception as e:
                    # Log the error but don't prevent profile creation
                    print(f"Error creating Provider record for user {user.id}: {e}")
