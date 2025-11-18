"""
Device API Key Management Views
System administrators can create, view, edit, and manage IoT Device API keys
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from .models import Device, Patient
from .models_iot import DeviceAPIKey
from .permissions import require_role
from datetime import timedelta


@login_required
@require_role('admin')
def device_api_key_list(request):
    """List all Device API keys with search and filter"""
    # Get search query
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    device_filter = request.GET.get('device', '').strip()

    # Base queryset
    api_keys = DeviceAPIKey.objects.select_related('device', 'device__patient').all()

    # Apply search filter
    if search_query:
        api_keys = api_keys.filter(
            Q(key_name__icontains=search_query) |
            Q(device__device_name__icontains=search_query) |
            Q(device__device_unique_id__icontains=search_query) |
            Q(key_prefix__icontains=search_query)
        )

    # Apply status filter
    if status_filter == 'active':
        api_keys = api_keys.filter(is_active=True, expires_at__gt=timezone.now())
    elif status_filter == 'inactive':
        api_keys = api_keys.filter(is_active=False)
    elif status_filter == 'expired':
        api_keys = api_keys.filter(expires_at__lte=timezone.now())

    # Apply device filter
    if device_filter:
        api_keys = api_keys.filter(device_id=device_filter)

    # Get statistics
    total_keys = DeviceAPIKey.objects.count()
    active_keys = DeviceAPIKey.objects.filter(is_active=True).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    ).count()
    inactive_keys = DeviceAPIKey.objects.filter(is_active=False).count()
    expired_keys = DeviceAPIKey.objects.filter(
        expires_at__lte=timezone.now(),
        is_active=True
    ).count()

    # Get device list for filter dropdown
    devices = Device.objects.filter(status='Active').order_by('device_name')

    stats = {
        'total_keys': total_keys,
        'active_keys': active_keys,
        'inactive_keys': inactive_keys,
        'expired_keys': expired_keys,
    }

    context = {
        'api_keys': api_keys,
        'stats': stats,
        'search_query': search_query,
        'status_filter': status_filter,
        'device_filter': device_filter,
        'devices': devices,
    }

    return render(request, 'healthcare/system_admin/device_api_keys/list.html', context)


@login_required
@require_role('admin')
def device_api_key_create(request):
    """Create a new Device API key"""
    if request.method == 'POST':
        device_id = request.POST.get('device_id')
        key_name = request.POST.get('key_name', '').strip()
        expires_in_days = request.POST.get('expires_in_days', '').strip()
        can_write_vitals = request.POST.get('can_write_vitals') == '1'
        can_read_patient = request.POST.get('can_read_patient') == '1'
        notes = request.POST.get('notes', '').strip()

        # Validate device
        device = get_object_or_404(Device, device_id=device_id)

        # Create API key
        try:
            expires_days = int(expires_in_days) if expires_in_days else None
            api_key_obj, plain_key = DeviceAPIKey.create_key(
                device=device,
                key_name=key_name,
                expires_in_days=expires_days
            )

            # Update permissions
            api_key_obj.can_write_vitals = can_write_vitals
            api_key_obj.can_read_patient = can_read_patient
            api_key_obj.notes = notes
            api_key_obj.save()

            # Store the plain key in session temporarily for display
            request.session['new_device_api_key'] = plain_key
            request.session['new_device_api_key_id'] = api_key_obj.id

            messages.success(
                request,
                f'Device API Key "{key_name}" created successfully! '
                'Make sure to copy the key - it will only be shown once.'
            )

            return redirect('device_api_key_detail', key_id=api_key_obj.id)

        except Exception as e:
            messages.error(request, f'Error creating API key: {str(e)}')

    # Get list of active devices
    devices = Device.objects.filter(status='Active').select_related('patient').order_by('device_name')

    context = {
        'devices': devices,
    }

    return render(request, 'healthcare/system_admin/device_api_keys/create.html', context)


@login_required
@require_role('admin')
def device_api_key_detail(request, key_id):
    """View Device API key details"""
    api_key = get_object_or_404(
        DeviceAPIKey.objects.select_related('device', 'device__patient'),
        id=key_id
    )

    # Check if we have a newly generated key in session
    new_key = None
    if request.session.get('new_device_api_key_id') == key_id:
        new_key = request.session.pop('new_device_api_key', None)
        request.session.pop('new_device_api_key_id', None)

    # Check if expired
    is_expired = api_key.expires_at and timezone.now() > api_key.expires_at
    is_active = api_key.is_active and not is_expired

    context = {
        'api_key': api_key,
        'new_key': new_key,
        'is_expired': is_expired,
        'is_active': is_active,
    }

    return render(request, 'healthcare/system_admin/device_api_keys/detail.html', context)


@login_required
@require_role('admin')
def device_api_key_edit(request, key_id):
    """Edit an existing Device API key"""
    api_key = get_object_or_404(DeviceAPIKey, id=key_id)

    if request.method == 'POST':
        # Update basic information
        api_key.key_name = request.POST.get('key_name', api_key.key_name).strip()
        api_key.notes = request.POST.get('notes', '').strip()
        api_key.is_active = request.POST.get('is_active') == '1'
        api_key.can_write_vitals = request.POST.get('can_write_vitals') == '1'
        api_key.can_read_patient = request.POST.get('can_read_patient') == '1'

        # Parse expiration date
        expires_in_days = request.POST.get('expires_in_days', '').strip()
        if expires_in_days:
            try:
                days = int(expires_in_days)
                api_key.expires_at = timezone.now() + timedelta(days=days)
            except ValueError:
                pass
        else:
            api_key.expires_at = None

        api_key.save()

        messages.success(request, f'Device API Key "{api_key.key_name}" updated successfully!')
        return redirect('device_api_key_detail', key_id=api_key.id)

    # Calculate days until expiration
    days_until_expiration = None
    if api_key.expires_at:
        delta = api_key.expires_at - timezone.now()
        days_until_expiration = max(0, delta.days)

    context = {
        'api_key': api_key,
        'days_until_expiration': days_until_expiration,
    }

    return render(request, 'healthcare/system_admin/device_api_keys/edit.html', context)


@login_required
@require_role('admin')
def device_api_key_revoke(request, key_id):
    """Revoke a Device API key"""
    api_key = get_object_or_404(DeviceAPIKey, id=key_id)

    if request.method == 'POST':
        api_key.is_active = False
        api_key.save()
        messages.success(request, f'Device API Key "{api_key.key_name}" has been revoked.')
        return redirect('device_api_key_list')

    context = {
        'api_key': api_key,
    }

    return render(request, 'healthcare/system_admin/device_api_keys/revoke_confirm.html', context)


@login_required
@require_role('admin')
def device_api_key_delete(request, key_id):
    """Delete a Device API key"""
    api_key = get_object_or_404(DeviceAPIKey, id=key_id)

    if request.method == 'POST':
        key_name = api_key.key_name
        device_name = api_key.device.device_name
        api_key.delete()
        messages.success(request, f'Device API Key "{key_name}" for {device_name} has been permanently deleted.')
        return redirect('device_api_key_list')

    context = {
        'api_key': api_key,
    }

    return render(request, 'healthcare/system_admin/device_api_keys/delete_confirm.html', context)


@login_required
@require_role('admin')
def device_api_key_regenerate(request, key_id):
    """Regenerate a Device API key"""
    old_api_key = get_object_or_404(DeviceAPIKey, id=key_id)

    if request.method == 'POST':
        # Create new API key with same settings
        new_api_key_obj, plain_key = DeviceAPIKey.create_key(
            device=old_api_key.device,
            key_name=old_api_key.key_name,
            expires_in_days=None
        )

        # Copy settings from old key
        if old_api_key.expires_at:
            delta = old_api_key.expires_at - timezone.now()
            if delta.days > 0:
                new_api_key_obj.expires_at = timezone.now() + delta

        new_api_key_obj.can_write_vitals = old_api_key.can_write_vitals
        new_api_key_obj.can_read_patient = old_api_key.can_read_patient
        new_api_key_obj.notes = old_api_key.notes
        new_api_key_obj.save()

        # Deactivate old key
        old_api_key.is_active = False
        old_api_key.save()

        # Store the plain key in session temporarily for display
        request.session['new_device_api_key'] = plain_key
        request.session['new_device_api_key_id'] = new_api_key_obj.id

        messages.success(
            request,
            f'Device API Key "{new_api_key_obj.key_name}" has been regenerated! '
            'The old key has been deactivated. Make sure to copy the new key.'
        )

        return redirect('device_api_key_detail', key_id=new_api_key_obj.id)

    context = {
        'api_key': old_api_key,
    }

    return render(request, 'healthcare/system_admin/device_api_keys/regenerate_confirm.html', context)
