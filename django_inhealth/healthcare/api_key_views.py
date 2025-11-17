"""
API Key Management Views
System administrators can create, view, edit, and manage REST API keys
"""
import secrets
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import APIKey
from .decorators import require_role


@login_required
@require_role('admin')
def api_key_list(request):
    """List all API keys with search and filter"""
    # Get search query
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()

    # Base queryset
    api_keys = APIKey.objects.select_related('created_by').all()

    # Apply search filter
    if search_query:
        api_keys = api_keys.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(key__icontains=search_query)
        )

    # Apply status filter
    if status_filter:
        api_keys = api_keys.filter(status=status_filter)

    # Get statistics
    stats = {
        'total_keys': APIKey.objects.count(),
        'active_keys': APIKey.objects.filter(status='active').count(),
        'inactive_keys': APIKey.objects.filter(status='inactive').count(),
        'revoked_keys': APIKey.objects.filter(status='revoked').count(),
        'expired_keys': APIKey.objects.filter(
            expires_at__lt=timezone.now(),
            status='active'
        ).count(),
    }

    context = {
        'api_keys': api_keys,
        'stats': stats,
        'search_query': search_query,
        'status_filter': status_filter,
    }

    return render(request, 'healthcare/system_admin/api_keys/list.html', context)


@login_required
@require_role('admin')
def api_key_create(request):
    """Create a new API key"""
    if request.method == 'POST':
        # Generate API key and secret
        api_key = APIKey.generate_key()
        api_secret = secrets.token_urlsafe(48)

        # Create the API key object
        new_key = APIKey.objects.create(
            name=request.POST.get('name', '').strip(),
            description=request.POST.get('description', '').strip(),
            key=api_key,
            secret=APIKey.hash_secret(api_secret),
            rate_limit=int(request.POST.get('rate_limit', 1000)),
            ip_whitelist=request.POST.get('ip_whitelist', '').strip(),
            status=request.POST.get('status', 'active'),
            created_by=request.user,
        )

        # Parse expiration date
        expires_at = request.POST.get('expires_at', '').strip()
        if expires_at:
            from datetime import datetime
            try:
                new_key.expires_at = datetime.strptime(expires_at, '%Y-%m-%d')
                new_key.save()
            except ValueError:
                pass

        # Parse permissions
        permissions = []
        if request.POST.get('perm_vitals'):
            permissions.append('vitals')
        if request.POST.get('perm_patients'):
            permissions.append('patients')
        if request.POST.get('perm_devices'):
            permissions.append('devices')
        if request.POST.get('perm_encounters'):
            permissions.append('encounters')

        new_key.permissions = permissions
        new_key.save()

        # Store the plain secret in session temporarily for display
        request.session['new_api_secret'] = api_secret
        request.session['new_api_key_id'] = new_key.api_key_id

        messages.success(
            request,
            f'API Key "{new_key.name}" created successfully! '
            'Make sure to copy the secret - it will only be shown once.'
        )

        return redirect('api_key_detail', key_id=new_key.api_key_id)

    context = {
        'default_permissions': ['vitals', 'patients', 'devices', 'encounters'],
    }

    return render(request, 'healthcare/system_admin/api_keys/create.html', context)


@login_required
@require_role('admin')
def api_key_detail(request, key_id):
    """View API key details"""
    api_key = get_object_or_404(APIKey, api_key_id=key_id)

    # Check if we have a newly generated secret in session
    new_secret = None
    if request.session.get('new_api_key_id') == key_id:
        new_secret = request.session.pop('new_api_secret', None)
        request.session.pop('new_api_key_id', None)

    context = {
        'api_key': api_key,
        'new_secret': new_secret,
        'is_expired': api_key.is_expired(),
        'is_active': api_key.is_active(),
    }

    return render(request, 'healthcare/system_admin/api_keys/detail.html', context)


@login_required
@require_role('admin')
def api_key_edit(request, key_id):
    """Edit an existing API key"""
    api_key = get_object_or_404(APIKey, api_key_id=key_id)

    if request.method == 'POST':
        # Update basic information
        api_key.name = request.POST.get('name', api_key.name).strip()
        api_key.description = request.POST.get('description', '').strip()
        api_key.rate_limit = int(request.POST.get('rate_limit', api_key.rate_limit))
        api_key.ip_whitelist = request.POST.get('ip_whitelist', '').strip()
        api_key.status = request.POST.get('status', api_key.status)

        # Parse expiration date
        expires_at = request.POST.get('expires_at', '').strip()
        if expires_at:
            from datetime import datetime
            try:
                api_key.expires_at = datetime.strptime(expires_at, '%Y-%m-%d')
            except ValueError:
                pass
        else:
            api_key.expires_at = None

        # Parse permissions
        permissions = []
        if request.POST.get('perm_vitals'):
            permissions.append('vitals')
        if request.POST.get('perm_patients'):
            permissions.append('patients')
        if request.POST.get('perm_devices'):
            permissions.append('devices')
        if request.POST.get('perm_encounters'):
            permissions.append('encounters')

        api_key.permissions = permissions
        api_key.save()

        messages.success(request, f'API Key "{api_key.name}" updated successfully!')
        return redirect('api_key_detail', key_id=api_key.api_key_id)

    context = {
        'api_key': api_key,
        'available_permissions': ['vitals', 'patients', 'devices', 'encounters'],
    }

    return render(request, 'healthcare/system_admin/api_keys/edit.html', context)


@login_required
@require_role('admin')
def api_key_revoke(request, key_id):
    """Revoke an API key"""
    api_key = get_object_or_404(APIKey, api_key_id=key_id)

    if request.method == 'POST':
        api_key.revoke()
        messages.success(request, f'API Key "{api_key.name}" has been revoked.')
        return redirect('api_key_list')

    context = {
        'api_key': api_key,
    }

    return render(request, 'healthcare/system_admin/api_keys/revoke_confirm.html', context)


@login_required
@require_role('admin')
def api_key_delete(request, key_id):
    """Delete an API key"""
    api_key = get_object_or_404(APIKey, api_key_id=key_id)

    if request.method == 'POST':
        name = api_key.name
        api_key.delete()
        messages.success(request, f'API Key "{name}" has been permanently deleted.')
        return redirect('api_key_list')

    context = {
        'api_key': api_key,
    }

    return render(request, 'healthcare/system_admin/api_keys/delete_confirm.html', context)


@login_required
@require_role('admin')
def api_key_regenerate_secret(request, key_id):
    """Regenerate API secret for an existing key"""
    api_key = get_object_or_404(APIKey, api_key_id=key_id)

    if request.method == 'POST':
        # Generate new secret
        new_secret = secrets.token_urlsafe(48)
        api_key.secret = APIKey.hash_secret(new_secret)
        api_key.save()

        # Store the plain secret in session temporarily for display
        request.session['new_api_secret'] = new_secret
        request.session['new_api_key_id'] = api_key.api_key_id

        messages.success(
            request,
            f'API Secret for "{api_key.name}" has been regenerated! '
            'Make sure to copy it - it will only be shown once.'
        )

        return redirect('api_key_detail', key_id=api_key.api_key_id)

    context = {
        'api_key': api_key,
    }

    return render(request, 'healthcare/system_admin/api_keys/regenerate_confirm.html', context)
