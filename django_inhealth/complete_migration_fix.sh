#!/bin/bash
# Complete Fix for Django Migration Issues
# Handles both migration conflict AND missing django_session table

set -e

echo "============================================================"
echo "Complete Django Migration Fix"
echo "============================================================"
echo ""
echo "This script will:"
echo "  1. Fix the duplicate 0003 migration conflict"
echo "  2. Apply remaining migrations (including sessions)"
echo "  3. Verify all migrations are complete"
echo ""

# Change to project directory
cd /home/zia/django_inhealth || {
    echo "Error: Cannot find /home/zia/django_inhealth"
    echo "Please update the path in this script"
    exit 1
}

# Activate virtual environment
echo "Step 1: Activating virtual environment..."
source venv/bin/activate || {
    echo "Error: Cannot activate virtual environment"
    exit 1
}

echo ""
echo "Step 2: Checking PostgreSQL is running..."
sudo systemctl status postgresql >/dev/null 2>&1 || {
    echo "PostgreSQL is not running. Starting it..."
    sudo systemctl start postgresql
    sleep 2
}
echo "✓ PostgreSQL is running"

echo ""
echo "Step 3: Checking current migration status..."
echo "------------------------------------------------------------"
python manage.py showmigrations 2>&1 | head -30

echo ""
echo "Step 4: Fixing the migration conflict..."
echo "------------------------------------------------------------"
echo "The duplicate 0003 migration needs to be marked as 'fake' applied."
echo "This tells Django it's already done without running the SQL."
echo ""

# Fake the conflicting migration
python manage.py migrate healthcare 0003 --fake 2>&1 || {
    echo "Note: Migration may already be faked. Continuing..."
}

echo ""
echo "Step 5: Applying ALL remaining migrations..."
echo "------------------------------------------------------------"
echo "This will create the django_session table and any other missing tables."
echo ""

# Now run full migrate to apply sessions and any other pending migrations
python manage.py migrate

echo ""
echo "Step 6: Verifying all migrations are complete..."
echo "------------------------------------------------------------"
python manage.py showmigrations

echo ""
echo "Step 7: Checking that critical tables exist..."
echo "------------------------------------------------------------"
sudo -u postgres psql -d inhealth_db -c "
SELECT
    CASE
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='django_session')
        THEN '✓ django_session exists'
        ELSE '✗ django_session MISSING'
    END as session_table,
    CASE
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='billings')
        THEN '✓ billings exists'
        ELSE '✗ billings MISSING'
    END as billings_table,
    CASE
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='auth_user')
        THEN '✓ auth_user exists'
        ELSE '✗ auth_user MISSING'
    END as auth_table;
" 2>&1

echo ""
echo "============================================================"
echo "✓ Migration Fix Complete!"
echo "============================================================"
echo ""
echo "Your Django application should now work correctly."
echo ""
echo "To test:"
echo "  1. Start the server: python manage.py runserver 0.0.0.0:8000"
echo "  2. Visit: http://172.168.1.125:8000/"
echo "  3. Visit admin: http://172.168.1.125:8000/admin/"
echo ""
echo "If you still see errors, please share the output above."
echo ""
