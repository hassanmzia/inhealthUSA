#!/bin/bash

# Script to fix the nurse migration error
# Error: relation "nurses" already exists

echo "=========================================="
echo "Fixing Nurse Migration Error"
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

# Fake the problematic migration
echo "Faking migration 0004_alter_userprofile_role_nurse..."
python manage.py migrate healthcare 0004_alter_userprofile_role_nurse --fake

if [ $? -eq 0 ]; then
    echo "✓ Successfully faked migration 0004_alter_userprofile_role_nurse"
    echo ""
else
    echo "✗ Error faking migration. Please check the error message above."
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
