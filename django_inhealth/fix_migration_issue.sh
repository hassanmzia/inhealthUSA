#!/bin/bash

# Fix for duplicate table migration issue
# This script resolves the "relation 'billings' already exists" error
# by marking the problematic migration as applied without running it

set -e

echo "========================================="
echo "Fixing Migration State Issue"
echo "========================================="
echo ""

# Change to the django_inhealth directory
cd "$(dirname "$0")"

echo "Step 1: Checking current migration status..."
python manage.py showmigrations healthcare

echo ""
echo "Step 2: Checking if billings table exists in database..."
sudo -u postgres psql -d inhealth_db -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'billings');" 2>&1

echo ""
echo "Step 3: Faking migration 0003 to mark it as applied..."
echo "This tells Django the migration has been applied without actually running it."
python manage.py migrate healthcare 0003 --fake

echo ""
echo "Step 4: Verifying migration status..."
python manage.py showmigrations healthcare

echo ""
echo "========================================="
echo "Migration Fix Complete!"
echo "========================================="
echo ""
echo "You should now be able to access the admin panel without errors."
echo "To test, start the development server:"
echo "  python manage.py runserver 0.0.0.0:8000"
echo ""
