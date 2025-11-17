#!/bin/bash
#
# Wrapper script for processing IoT device data via cron
# This script ensures the proper Django environment is loaded
#
# Usage in crontab:
# * * * * * /path/to/django_inhealth/scripts/process_iot_data_cron.sh >> /var/log/iot_processing.log 2>&1
#

# Set the project directory
PROJECT_DIR="/home/zia/ihealth/inhealthUSA/django_inhealth"

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Load environment variables if .env file exists
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

# Alternatively, you can explicitly set environment variables here:
# export DJANGO_SETTINGS_MODULE="inhealth.settings"
# export EMAIL_HOST="smtp.gmail.com"
# export EMAIL_PORT="587"
# export EMAIL_HOST_USER="your-email@gmail.com"
# export EMAIL_HOST_PASSWORD="your-app-password"
# export EMAIL_USE_TLS="True"

# Activate virtual environment if it exists
if [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
    source "$PROJECT_DIR/venv/bin/activate"
fi

# Run the Django management command
python manage.py process_iot_data

# Exit with the same status as the Python command
exit $?
