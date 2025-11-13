#!/bin/bash

# Script to fix migration errors for duplicate tables and columns
# Errors: relation "nurses" already exists, relation "office_administrators" already exists, column "glucose" already exists

echo "=========================================="
echo "Fixing Migration Errors"
echo "=========================================="
echo ""

# Navigate to the project directory
cd /home/zia/django_inhealth || { echo "Error: Project directory not found"; exit 1; }

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || { echo "Error: Could not activate virtual environment"; exit 1; }

echo "Virtual environment activated successfully!"
echo ""

# Show current migration status
echo "Current migration status:"
python manage.py showmigrations healthcare
echo ""

# Fake the problematic migrations
echo "Faking migration 0004_alter_userprofile_role_nurse..."
python manage.py migrate healthcare 0004_alter_userprofile_role_nurse --fake

if [ $? -eq 0 ]; then
    echo "✓ Successfully faked migration 0004_alter_userprofile_role_nurse"
    echo ""
else
    echo "✗ Error faking migration 0004. Please check the error message above."
    exit 1
fi

echo "Faking migration 0005_officeadministrator..."
python manage.py migrate healthcare 0005_officeadministrator --fake

if [ $? -eq 0 ]; then
    echo "✓ Successfully faked migration 0005_officeadministrator"
    echo ""
else
    echo "✗ Error faking migration 0005. Please check the error message above."
    exit 1
fi

echo "Faking migration 0006_vitalsign_glucose..."
python manage.py migrate healthcare 0006_vitalsign_glucose --fake

if [ $? -eq 0 ]; then
    echo "✓ Successfully faked migration 0006_vitalsign_glucose"
    echo ""
else
    echo "✗ Error faking migration 0006. Please check the error message above."
    exit 1
fi

echo "Faking migration 0007_vitalsign_data_source_vitalsign_device_and_more..."
python manage.py migrate healthcare 0007_vitalsign_data_source_vitalsign_device_and_more --fake

if [ $? -eq 0 ]; then
    echo "✓ Successfully faked migration 0007_vitalsign_data_source_vitalsign_device_and_more"
    echo ""
else
    echo "✗ Error faking migration 0007. Please check the error message above."
    exit 1
fi

# Run remaining migrations
echo "Running remaining migrations..."
python manage.py migrate

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ All migrations completed successfully!"
    echo "=========================================="
    echo ""
    echo "Final migration status:"
    python manage.py showmigrations healthcare
else
    echo ""
    echo "✗ Error running migrations. Please check the error message above."
    exit 1
fi

echo ""
echo "Migration fix complete!"
