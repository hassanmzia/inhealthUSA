"""
IoT Device Data File Management Views for Admin Dashboard
Allows administrators to manage IoT data folders, view files, and upload JSON files
"""
import os
import json
import shutil
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

from .models import Device


def check_admin_permission(user):
    """Check if user has admin permissions"""
    return (
        user.is_superuser or
        user.is_staff or
        (hasattr(user, 'profile') and user.profile.role in ['admin', 'office_admin'])
    )


@login_required
def iot_file_manager(request):
    """
    Main IoT file management dashboard
    Shows inbox and archive directories, allows file upload
    """
    # Check permissions
    if not check_admin_permission(request.user):
        raise PermissionDenied("You don't have permission to access this page")

    # Get directory paths from settings
    inbox_dir = getattr(settings, 'IOT_INBOX_DIR', '/var/iot_data/inbox')
    archive_dir = getattr(settings, 'IOT_ARCHIVE_DIR', '/var/iot_data/archive')

    # Create directories if they don't exist
    Path(inbox_dir).mkdir(parents=True, exist_ok=True)
    Path(archive_dir).mkdir(parents=True, exist_ok=True)

    # Get inbox files
    inbox_files = []
    try:
        for filename in os.listdir(inbox_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(inbox_dir, filename)
                stat = os.stat(filepath)
                inbox_files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'path': filepath,
                })
        inbox_files.sort(key=lambda x: x['modified'], reverse=True)
    except Exception as e:
        messages.error(request, f"Error reading inbox directory: {str(e)}")

    # Get archive directories
    archive_dates = []
    try:
        for dirname in os.listdir(archive_dir):
            dirpath = os.path.join(archive_dir, dirname)
            if os.path.isdir(dirpath):
                # Count files in this directory
                file_count = sum(1 for f in os.listdir(dirpath) if f.endswith('.json'))
                archive_dates.append({
                    'date': dirname,
                    'file_count': file_count,
                    'path': dirpath,
                })
        archive_dates.sort(key=lambda x: x['date'], reverse=True)
    except Exception as e:
        messages.error(request, f"Error reading archive directory: {str(e)}")

    # Get all devices for dropdown
    devices = Device.objects.select_related('patient').all().order_by('-created_at')[:50]

    context = {
        'inbox_files': inbox_files,
        'archive_dates': archive_dates,
        'inbox_dir': inbox_dir,
        'archive_dir': archive_dir,
        'devices': devices,
        'inbox_count': len(inbox_files),
    }

    return render(request, 'healthcare/admin/iot_file_manager.html', context)


@login_required
@require_http_methods(["GET"])
def view_archive_date(request, date):
    """View files for a specific archive date"""
    # Check permissions
    if not check_admin_permission(request.user):
        raise PermissionDenied("You don't have permission to access this page")

    archive_dir = getattr(settings, 'IOT_ARCHIVE_DIR', '/var/iot_data/archive')
    date_dir = os.path.join(archive_dir, date)

    if not os.path.exists(date_dir):
        raise Http404("Archive date not found")

    # Get files for this date
    archive_files = []
    try:
        for filename in os.listdir(date_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(date_dir, filename)
                stat = os.stat(filepath)
                archive_files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'path': filepath,
                })
        archive_files.sort(key=lambda x: x['modified'], reverse=True)
    except Exception as e:
        messages.error(request, f"Error reading archive directory: {str(e)}")

    context = {
        'archive_date': date,
        'archive_files': archive_files,
        'file_count': len(archive_files),
    }

    return render(request, 'healthcare/admin/iot_archive_detail.html', context)


@login_required
@require_http_methods(["GET"])
def view_file_content(request, location, filename):
    """
    View JSON file content
    location: 'inbox' or archive date (YYYY-MM-DD)
    """
    # Check permissions
    if not check_admin_permission(request.user):
        raise PermissionDenied("You don't have permission to access this page")

    # Determine file path
    if location == 'inbox':
        base_dir = getattr(settings, 'IOT_INBOX_DIR', '/var/iot_data/inbox')
    else:
        # Location is a date (YYYY-MM-DD)
        archive_dir = getattr(settings, 'IOT_ARCHIVE_DIR', '/var/iot_data/archive')
        base_dir = os.path.join(archive_dir, location)

    filepath = os.path.join(base_dir, filename)

    # Security check - ensure file is within allowed directory
    if not os.path.abspath(filepath).startswith(os.path.abspath(base_dir)):
        raise PermissionDenied("Invalid file path")

    if not os.path.exists(filepath):
        raise Http404("File not found")

    # Read and parse JSON
    try:
        with open(filepath, 'r') as f:
            content = json.load(f)

        # Pretty print JSON
        content_str = json.dumps(content, indent=2)

        # Get file stats
        stat = os.stat(filepath)

        context = {
            'filename': filename,
            'location': location,
            'content': content,
            'content_str': content_str,
            'file_size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime),
        }

        return render(request, 'healthcare/admin/iot_file_viewer.html', context)

    except json.JSONDecodeError as e:
        messages.error(request, f"Invalid JSON in file: {str(e)}")
        return redirect('iot_file_manager')
    except Exception as e:
        messages.error(request, f"Error reading file: {str(e)}")
        return redirect('iot_file_manager')


@login_required
@require_http_methods(["POST"])
@csrf_protect
def upload_file(request):
    """Upload a JSON file to the inbox"""
    # Check permissions
    if not check_admin_permission(request.user):
        raise PermissionDenied("You don't have permission to upload files")

    if 'file' not in request.FILES:
        messages.error(request, "No file provided")
        return redirect('iot_file_manager')

    uploaded_file = request.FILES['file']

    # Validate file extension
    if not uploaded_file.name.endswith('.json'):
        messages.error(request, "Only JSON files are allowed")
        return redirect('iot_file_manager')

    # Validate file size (max 1MB)
    if uploaded_file.size > 1024 * 1024:
        messages.error(request, "File size must be less than 1MB")
        return redirect('iot_file_manager')

    # Validate JSON content
    try:
        content = uploaded_file.read()
        json_data = json.loads(content)

        # Validate required fields
        if 'device_id' not in json_data:
            messages.error(request, "JSON file must contain 'device_id' field")
            return redirect('iot_file_manager')

        if 'timestamp' not in json_data:
            messages.error(request, "JSON file must contain 'timestamp' field")
            return redirect('iot_file_manager')

    except json.JSONDecodeError as e:
        messages.error(request, f"Invalid JSON file: {str(e)}")
        return redirect('iot_file_manager')
    except Exception as e:
        messages.error(request, f"Error validating file: {str(e)}")
        return redirect('iot_file_manager')

    # Save file to inbox
    inbox_dir = getattr(settings, 'IOT_INBOX_DIR', '/var/iot_data/inbox')
    Path(inbox_dir).mkdir(parents=True, exist_ok=True)

    # Generate unique filename if file already exists
    filename = uploaded_file.name
    filepath = os.path.join(inbox_dir, filename)
    counter = 1
    while os.path.exists(filepath):
        name, ext = os.path.splitext(uploaded_file.name)
        filename = f"{name}_{counter}{ext}"
        filepath = os.path.join(inbox_dir, filename)
        counter += 1

    try:
        with open(filepath, 'wb') as f:
            f.write(content)

        messages.success(request, f"File '{filename}' uploaded successfully to inbox")
    except Exception as e:
        messages.error(request, f"Error saving file: {str(e)}")

    return redirect('iot_file_manager')


@login_required
@require_http_methods(["POST"])
@csrf_protect
def delete_file(request, location, filename):
    """Delete a file from inbox or archive"""
    # Check permissions
    if not check_admin_permission(request.user):
        raise PermissionDenied("You don't have permission to delete files")

    # Determine file path
    if location == 'inbox':
        base_dir = getattr(settings, 'IOT_INBOX_DIR', '/var/iot_data/inbox')
    else:
        # Location is a date (YYYY-MM-DD)
        archive_dir = getattr(settings, 'IOT_ARCHIVE_DIR', '/var/iot_data/archive')
        base_dir = os.path.join(archive_dir, location)

    filepath = os.path.join(base_dir, filename)

    # Security check
    if not os.path.abspath(filepath).startswith(os.path.abspath(base_dir)):
        raise PermissionDenied("Invalid file path")

    if not os.path.exists(filepath):
        messages.error(request, "File not found")
        return redirect('iot_file_manager')

    try:
        os.remove(filepath)
        messages.success(request, f"File '{filename}' deleted successfully")
    except Exception as e:
        messages.error(request, f"Error deleting file: {str(e)}")

    # Redirect based on location
    if location == 'inbox':
        return redirect('iot_file_manager')
    else:
        return redirect('iot_archive_date', date=location)


@login_required
@require_http_methods(["GET"])
def download_file(request, location, filename):
    """Download a file"""
    # Check permissions
    if not check_admin_permission(request.user):
        raise PermissionDenied("You don't have permission to download files")

    # Determine file path
    if location == 'inbox':
        base_dir = getattr(settings, 'IOT_INBOX_DIR', '/var/iot_data/inbox')
    else:
        archive_dir = getattr(settings, 'IOT_ARCHIVE_DIR', '/var/iot_data/archive')
        base_dir = os.path.join(archive_dir, location)

    filepath = os.path.join(base_dir, filename)

    # Security check
    if not os.path.abspath(filepath).startswith(os.path.abspath(base_dir)):
        raise PermissionDenied("Invalid file path")

    if not os.path.exists(filepath):
        raise Http404("File not found")

    try:
        response = FileResponse(open(filepath, 'rb'), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        messages.error(request, f"Error downloading file: {str(e)}")
        return redirect('iot_file_manager')


@login_required
@require_http_methods(["GET"])
def get_folder_stats(request):
    """API endpoint to get folder statistics"""
    # Check permissions
    if not check_admin_permission(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    inbox_dir = getattr(settings, 'IOT_INBOX_DIR', '/var/iot_data/inbox')
    archive_dir = getattr(settings, 'IOT_ARCHIVE_DIR', '/var/iot_data/archive')

    # Count inbox files
    inbox_count = 0
    try:
        inbox_count = sum(1 for f in os.listdir(inbox_dir) if f.endswith('.json'))
    except:
        pass

    # Count archive files
    archive_count = 0
    archive_dates = 0
    try:
        for dirname in os.listdir(archive_dir):
            dirpath = os.path.join(archive_dir, dirname)
            if os.path.isdir(dirpath):
                archive_dates += 1
                archive_count += sum(1 for f in os.listdir(dirpath) if f.endswith('.json'))
    except:
        pass

    return JsonResponse({
        'inbox_count': inbox_count,
        'archive_count': archive_count,
        'archive_dates': archive_dates,
    })
