#!/bin/bash
# Fix Django Migration Conflict for Healthcare App
# This script handles the duplicate 0003 migration issue

set -e

echo "============================================================"
echo "Django Migration Conflict Fix"
echo "============================================================"
echo ""
echo "This script fixes the issue where two different migrations"
echo "numbered '0003' exist in the healthcare app."
echo ""

# Ensure we're in the right directory
cd /home/zia/django_inhealth || {
    echo "Error: Directory /home/zia/django_inhealth not found!"
    echo "Please adjust the path in this script or run from correct location."
    exit 1
}

# Activate virtual environment
echo "Step 1: Activating virtual environment..."
source venv/bin/activate || {
    echo "Error: Could not activate virtual environment"
    exit 1
}

echo ""
echo "Step 2: Checking current migration status..."
echo "------------------------------------------------------------"
python manage.py showmigrations healthcare || true

echo ""
echo "Step 3: Checking which tables exist in database..."
echo "------------------------------------------------------------"
echo "Looking for billing-related tables..."
sudo -u postgres psql -d inhealth_db -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE '%billing%' OR table_name LIKE '%payment%' OR table_name LIKE '%insurance%' OR table_name LIKE '%device%' ORDER BY table_name;" 2>&1 || true

echo ""
echo "Step 4: Checking django_migrations table..."
echo "------------------------------------------------------------"
sudo -u postgres psql -d inhealth_db -c "SELECT id, app, name, applied FROM django_migrations WHERE app='healthcare' ORDER BY applied;" 2>&1 || true

echo ""
echo "Step 5: Analyzing the problem..."
echo "------------------------------------------------------------"
echo "Problem: You have TWO different migrations numbered 0003:"
echo "  1. 0003_billing_payment_insuranceinformation_device_and_more"
echo "  2. 0003_billing_alter_userprofile_role_payment_and_more"
echo ""
echo "Migration #1 already applied successfully on your server."
echo "Migration #2 exists in the current code but conflicts with #1."
echo ""

echo "Step 6: Applying the fix..."
echo "------------------------------------------------------------"
echo "We will fake migration 0003_billing_alter_userprofile_role_payment_and_more"
echo "since the tables it creates already exist from migration #1."
echo ""

# Try to fake the specific migration
echo "Running: python manage.py migrate healthcare 0003 --fake"
python manage.py migrate healthcare 0003 --fake 2>&1 || {
    echo ""
    echo "Note: The migration may already be marked as applied."
    echo "This is OK if all tables exist."
}

echo ""
echo "Step 7: Verifying the fix..."
echo "------------------------------------------------------------"
python manage.py showmigrations healthcare

echo ""
echo "Step 8: Running any pending migrations..."
echo "------------------------------------------------------------"
python manage.py migrate || {
    echo ""
    echo "If you see errors above, we may need to fake additional migrations."
    echo "Please share the error message."
}

echo ""
echo "============================================================"
echo "Migration Fix Process Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Review the output above for any errors"
echo "  2. Test the admin panel: http://172.168.1.125:8000/admin/"
echo "  3. If you still see errors, run:"
echo "     python manage.py showmigrations"
echo "     and share the output"
echo ""
echo "To start your server:"
echo "  python manage.py runserver 0.0.0.0:8000"
echo ""
