#!/bin/bash
# Complete database reset and setup script for InHealth

set -e

echo "========================================="
echo "InHealth Complete Database Reset"
echo "========================================="
echo ""
echo "WARNING: This will DELETE ALL DATA in the database!"
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

cd "$(dirname "$0")"

# Get database connection info
DB_NAME=${DB_NAME:-inhealth_db}
DB_USER=${DB_USER:-inhealth_user}
DB_PASSWORD=${DB_PASSWORD:-inhealth_password}

echo ""
echo "Step 1: Stopping any running Django processes..."
pkill -f "python manage.py runserver" || true
sleep 2

echo ""
echo "Step 2: Dropping and recreating database..."

# Drop and recreate database
sudo -u postgres psql << EOF
-- Terminate all connections to the database
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '$DB_NAME'
  AND pid <> pg_backend_pid();

-- Drop everything
DROP DATABASE IF EXISTS $DB_NAME;
DROP USER IF EXISTS $DB_USER;

-- Recreate fresh
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE $DB_NAME OWNER $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Connect and grant schema permissions
\c $DB_NAME
GRANT ALL ON SCHEMA public TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to drop/recreate database. Do you have sudo access?"
    echo "Please ask your system administrator to run:"
    echo ""
    echo "sudo -u postgres psql << 'EOF'"
    echo "DROP DATABASE IF EXISTS $DB_NAME CASCADE;"
    echo "DROP USER IF EXISTS $DB_USER;"
    echo "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    echo "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
    echo "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    echo "\c $DB_NAME"
    echo "GRANT ALL ON SCHEMA public TO $DB_USER;"
    echo "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;"
    echo "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;"
    echo "EOF"
    echo ""
    exit 1
fi

echo ""
echo "Step 3: Activating virtual environment and installing packages..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "ERROR: Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install/upgrade packages
echo "Installing required packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Step 4: Running migrations on clean database..."

# Run migrations
python manage.py migrate

echo ""
echo "Step 5: Creating static directory if it doesn't exist..."
mkdir -p static
python manage.py collectstatic --noinput || true

echo ""
echo "========================================="
echo "Database reset completed successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Create a superuser:"
echo "     python manage.py createsuperuser"
echo ""
echo "  2. Start the server:"
echo "     python manage.py runserver 0.0.0.0:8899"
echo ""
echo "If you encounter any 'column does not exist' errors,"
echo "the issue is with the model definitions, not the database."
echo "========================================="
