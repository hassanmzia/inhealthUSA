#!/bin/bash
# Script to completely reset the InHealth database

set -e

echo "========================================="
echo "InHealth Database Reset Script"
echo "========================================="
echo ""
echo "WARNING: This will delete ALL data in the database!"
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

cd "$(dirname "$0")"

# Get database connection info from .env if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

DB_NAME=${DB_NAME:-inhealth_db}
DB_USER=${DB_USER:-inhealth_user}
DB_PASSWORD=${DB_PASSWORD:-inhealth_password}

echo ""
echo "Step 1: Dropping existing database..."

# Drop database using sudo postgres user
sudo -u postgres psql << EOF
-- Terminate all connections
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '$DB_NAME'
  AND pid <> pg_backend_pid();

-- Drop database
DROP DATABASE IF EXISTS $DB_NAME;

-- Drop and recreate user
DROP USER IF EXISTS $DB_USER;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Create fresh database
CREATE DATABASE $DB_NAME OWNER $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Connect and set permissions
\c $DB_NAME
GRANT ALL ON SCHEMA public TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;
EOF

echo ""
echo "Step 2: Clearing Django migration history..."

# Remove migrations from django_migrations table (it doesn't exist yet, but just in case)
# This ensures migrations run fresh

echo ""
echo "Step 3: Running migrations..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run migrations
python manage.py migrate

echo ""
echo "========================================="
echo "Database reset completed successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Create a superuser: python manage.py createsuperuser"
echo "  2. Run the server: python manage.py runserver"
echo ""
