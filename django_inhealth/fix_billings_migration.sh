#!/bin/bash
# Quick Fix for "relation 'billings' already exists" Error
# Run this on your production server at /home/zia/django_inhealth

set -e

echo "=================================================="
echo "Fixing Django Migration State for Billings Table"
echo "=================================================="
echo ""

# Ensure we're in the right directory
cd /home/zia/django_inhealth || {
    echo "Error: Directory /home/zia/django_inhealth not found!"
    echo "Please run this script from the correct location."
    exit 1
}

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || {
    echo "Error: Could not activate virtual environment"
    echo "Make sure venv exists at /home/zia/django_inhealth/venv"
    exit 1
}

echo ""
echo "Step 1: Checking current migration status..."
python manage.py showmigrations healthcare

echo ""
echo "Step 2: Checking database for existing billings table..."
sudo -u postgres psql -d inhealth_db -c "\dt billings" 2>&1 | grep -q "billings" && {
    echo "✓ Confirmed: billings table exists in database"
} || {
    echo "✗ Warning: billings table not found in database"
}

echo ""
echo "Step 3: Faking migration 0003 to sync Django's state with database..."
echo "This marks the migration as applied WITHOUT running the SQL commands."
echo ""
python manage.py migrate healthcare 0003 --fake

echo ""
echo "Step 4: Verifying all migrations are now marked as applied..."
python manage.py showmigrations healthcare

echo ""
echo "=================================================="
echo "✓ Migration Fix Complete!"
echo "=================================================="
echo ""
echo "All healthcare migrations should now show [X] (applied)."
echo ""
echo "You can now:"
echo "  1. Access the admin panel at: http://172.168.1.125:8000/admin/"
echo "  2. Run the development server: python manage.py runserver 0.0.0.0:8000"
echo ""
echo "If you see any errors, check:"
echo "  - PostgreSQL is running: sudo systemctl status postgresql"
echo "  - Database exists: sudo -u postgres psql -l | grep inhealth_db"
echo ""
