from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Patient, Doctor, Nurse, OfficeAdmin
"""
Django signals for automatic profile creation and management
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile, Patient, Provider


@receiver(post_save, sender=UserProfile)
def create_profile_records(sender, instance, created, **kwargs):
    """
    Automatically create role-specific profile records when a UserProfile is saved.
    Creates Patient, Doctor, Nurse, or OfficeAdmin records based on the user's role.
    """
    # Safety check: ensure instance and role exist
    if not instance or not instance.role:
        return

    # Get or check if role is valid
    role = instance.role
    if not role or role not in dict(UserProfile.ROLE_CHOICES):
        return

    user = instance.user

    # Create role-specific profile based on the user's role
    if role == 'patient':
        # Create or get Patient profile
        if not hasattr(user, 'patient_profile'):
            Patient.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'email': user.email or '',
                    'phone': instance.phone or '',
                    'date_of_birth': instance.date_of_birth,
                }
            )

    elif role == 'doctor':
        # Create or get Doctor profile
        if not hasattr(user, 'doctor_profile'):
            Doctor.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'email': user.email or '',
                    'phone': instance.phone or '',
                }
            )

    elif role == 'nurse':
        # Create or get Nurse profile
        if not hasattr(user, 'nurse_profile'):
            Nurse.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'email': user.email or '',
                    'phone': instance.phone or '',
                }
            )

    elif role == 'office_admin':
        # Create or get OfficeAdmin profile
        if not hasattr(user, 'officeadmin_profile'):
            OfficeAdmin.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'email': user.email or '',
                    'phone': instance.phone or '',
                }
            )


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile when a new User is created.
    By default, all new users are assigned the 'patient' role.
    """
    if created:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={'role': 'patient'}
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the UserProfile whenever the User is saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
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
