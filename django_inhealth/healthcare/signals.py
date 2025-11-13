from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Patient, Doctor, Nurse, OfficeAdmin


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
