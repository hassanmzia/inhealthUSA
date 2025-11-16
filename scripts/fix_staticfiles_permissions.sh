#!/bin/bash

# Script to fix staticfiles permissions
# This script removes the staticfiles directory and recreates it with proper permissions

set -e  # Exit on error

echo "Fixing staticfiles permissions..."

# Navigate to Django project directory
cd "$(dirname "$0")/../django_inhealth"

# Check if staticfiles directory exists
if [ -d "staticfiles" ]; then
    echo "Removing existing staticfiles directory..."
    # Try to remove with current user first
    rm -rf staticfiles 2>/dev/null || {
        echo "Need sudo permissions to remove staticfiles directory..."
        sudo rm -rf staticfiles
    }
    echo "Staticfiles directory removed."
fi

# Create fresh staticfiles directory with proper permissions
echo "Creating new staticfiles directory..."
mkdir -p staticfiles
chmod 755 staticfiles

echo "Staticfiles directory is ready!"
echo ""
echo "Now you can run: python manage.py collectstatic --noinput"
