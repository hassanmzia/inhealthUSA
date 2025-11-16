#!/bin/bash

# Script to fix staticfiles ownership (alternative to removing directory)
# This script changes ownership of the staticfiles directory to the current user

set -e  # Exit on error

echo "Fixing staticfiles ownership..."

# Navigate to Django project directory
cd "$(dirname "$0")/../django_inhealth"

# Check if staticfiles directory exists
if [ -d "staticfiles" ]; then
    echo "Changing ownership of staticfiles directory to current user..."
    CURRENT_USER=$(whoami)

    # Change ownership - may require sudo
    sudo chown -R $CURRENT_USER:$CURRENT_USER staticfiles
    sudo chmod -R 755 staticfiles

    echo "Ownership changed to: $CURRENT_USER"
    echo "Permissions set to: 755"
else
    echo "Staticfiles directory does not exist. Creating it..."
    mkdir -p staticfiles
    chmod 755 staticfiles
    echo "Staticfiles directory created."
fi

echo ""
echo "Staticfiles directory is ready!"
echo "Now you can run: python manage.py collectstatic --noinput"
