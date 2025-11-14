"""
Permission helpers and decorators for role-based access control
"""
from functools import wraps
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Patient, Provider, UserProfile


def get_user_role(user):
    """Get the role of a user"""
    if not user.is_authenticated:
        return None

    try:
        return user.profile.role
    except (UserProfile.DoesNotExist, AttributeError):
        return None


def is_patient(user):
    """Check if user is a patient"""
    return get_user_role(user) == 'patient'


def is_doctor(user):
    """Check if user is a doctor"""
    return get_user_role(user) == 'doctor'


def is_office_admin(user):
    """Check if user is an office admin"""
    return get_user_role(user) == 'office_admin'


def is_nurse(user):
    """Check if user is a nurse"""
    return get_user_role(user) == 'nurse'


def is_admin(user):
    """Check if user is a system administrator"""
    return get_user_role(user) == 'admin'


def get_patient_for_user(user):
    """Get the Patient object for a user if they are a patient"""
    if not is_patient(user):
        return None

    try:
        return user.patient_profile
    except (Patient.DoesNotExist, AttributeError):
        return None


def get_provider_for_user(user):
    """Get the Provider object for a user if they are a doctor"""
    if not is_doctor(user):
        return None

    try:
        return user.provider_profile
    except (Provider.DoesNotExist, AttributeError):
        return None


def can_view_patient(user, patient):
    """Check if user can view a specific patient's information"""
    # System admins, office admins, doctors, and nurses can view all patients
    if is_admin(user) or is_office_admin(user) or is_doctor(user) or is_nurse(user):
        return True

    # Patients can only view their own information
    if is_patient(user):
        user_patient = get_patient_for_user(user)
        return user_patient and user_patient.patient_id == patient.patient_id

    return False


def can_edit_patient(user, patient):
    """Check if user can edit a specific patient's information"""
    # System admins, office admins, and doctors can edit patient information
    return is_admin(user) or is_office_admin(user) or is_doctor(user)


def require_role(*allowed_roles):
    """
    Decorator to require specific role(s) to access a view
    Usage: @require_role('doctor', 'office_admin')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user_role = get_user_role(request.user)

            if user_role not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('index')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_patient_access(view_func):
    """
    Decorator to check if user can access a specific patient's information
    Expects patient_id in URL kwargs
    """
    @wraps(view_func)
    def wrapper(request, patient_id, *args, **kwargs):
        patient = get_object_or_404(Patient, patient_id=patient_id)

        if not can_view_patient(request.user, patient):
            messages.error(request, 'You do not have permission to view this patient information.')

            # If user is a patient, redirect them to their own profile
            if is_patient(request.user):
                user_patient = get_patient_for_user(request.user)
                if user_patient:
                    return redirect('patient_detail', patient_id=user_patient.patient_id)

            return redirect('index')

        return view_func(request, patient_id, *args, **kwargs)
    return wrapper


def require_patient_edit(view_func):
    """
    Decorator to check if user can edit a specific patient's information
    Expects patient_id in URL kwargs
    """
    @wraps(view_func)
    def wrapper(request, patient_id, *args, **kwargs):
        patient = get_object_or_404(Patient, patient_id=patient_id)

        if not can_edit_patient(request.user, patient):
            messages.error(request, 'You do not have permission to edit patient information.')
            return redirect('patient_detail', patient_id=patient_id)

        return view_func(request, patient_id, *args, **kwargs)
    return wrapper


# Vital-specific permissions

def can_edit_vitals(user, patient):
    """Check if user can edit vital information for a patient"""
    # System admins, office admins, doctors, and nurses can edit vital information
    return is_admin(user) or is_office_admin(user) or is_doctor(user) or is_nurse(user)


def require_vital_edit(view_func):
    """
    Decorator to check if user can edit vital information
    Expects patient_id in URL kwargs
    """
    @wraps(view_func)
    def wrapper(request, patient_id, *args, **kwargs):
        patient = get_object_or_404(Patient, patient_id=patient_id)

        if not can_edit_vitals(request.user, patient):
            messages.error(request, 'You do not have permission to edit vital information.')
            return redirect('patient_detail', patient_id=patient_id)

        return view_func(request, patient_id, *args, **kwargs)
    return wrapper


# Provider-specific permissions

def can_view_provider(user, provider):
    """Check if user can view a specific provider's information"""
    # System admins, office admins, and nurses can view all providers
    if is_admin(user) or is_office_admin(user) or is_nurse(user):
        return True

    # Doctors can only view their own information
    if is_doctor(user):
        user_provider = get_provider_for_user(user)
        return user_provider and user_provider.provider_id == provider.provider_id

    # Patients cannot view provider details
    return False


def can_edit_provider(user, provider):
    """Check if user can edit a specific provider's information"""
    # System admins and office admins can edit provider information
    return is_admin(user) or is_office_admin(user)


def require_provider_access(view_func):
    """
    Decorator to check if user can access a specific provider's information
    Expects provider_id in URL kwargs
    """
    @wraps(view_func)
    def wrapper(request, provider_id, *args, **kwargs):
        provider = get_object_or_404(Provider, provider_id=provider_id)

        if not can_view_provider(request.user, provider):
            messages.error(request, 'You do not have permission to view this provider information.')

            # If user is a doctor, redirect them to their own profile
            if is_doctor(request.user):
                user_provider = get_provider_for_user(request.user)
                if user_provider:
                    return redirect('physician_detail', provider_id=user_provider.provider_id)

            return redirect('index')

        return view_func(request, provider_id, *args, **kwargs)
    return wrapper


def require_provider_edit(view_func):
    """
    Decorator to check if user can edit a specific provider's information
    Expects provider_id in URL kwargs
    """
    @wraps(view_func)
    def wrapper(request, provider_id, *args, **kwargs):
        provider = get_object_or_404(Provider, provider_id=provider_id)

        if not can_edit_provider(request.user, provider):
            messages.error(request, 'You do not have permission to edit provider information.')
            return redirect('physician_detail', provider_id=provider_id)

        return view_func(request, provider_id, *args, **kwargs)
    return wrapper
