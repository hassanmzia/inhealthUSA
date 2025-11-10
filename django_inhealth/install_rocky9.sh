#!/bin/bash

# InHealth EHR Django/PostgreSQL Installation Script for Rocky Linux 9
# This script installs and configures PostgreSQL, Python 3, Django, and the InHealth EHR application

set -e  # Exit on any error

echo "========================================="
echo "InHealth EHR Installation for Rocky Linux 9"
echo "========================================="

# Update system packages
echo "Updating system packages..."
sudo dnf update -y

# Install EPEL repository
echo "Installing EPEL repository..."
sudo dnf install -y epel-release

# Install PostgreSQL 15
echo "Installing PostgreSQL 15..."
sudo dnf install -y postgresql15-server postgresql15-contrib postgresql15-devel

# Initialize PostgreSQL database
echo "Initializing PostgreSQL database..."
sudo postgresql-15-setup initdb

# Start and enable PostgreSQL
echo "Starting PostgreSQL service..."
sudo systemctl start postgresql-15
sudo systemctl enable postgresql-15

# Install Python 3 and pip
echo "Installing Python 3 and dependencies..."
sudo dnf install -y python3 python3-pip python3-devel

# Install system dependencies
echo "Installing system dependencies..."
sudo dnf install -y gcc make git curl

# Configure PostgreSQL authentication
echo "Configuring PostgreSQL authentication..."
sudo sed -i 's/ident/md5/g' /var/lib/pgsql/15/data/pg_hba.conf
sudo sed -i 's/peer/md5/g' /var/lib/pgsql/15/data/pg_hba.conf

# Restart PostgreSQL to apply changes
echo "Restarting PostgreSQL service..."
sudo systemctl restart postgresql-15

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to start..."
sleep 5

# Configure PostgreSQL database and user
echo "Configuring PostgreSQL database..."
sudo -u postgres psql << EOF
-- Create database
DROP DATABASE IF EXISTS inhealth_db;
CREATE DATABASE inhealth_db;

-- Create user
DROP USER IF EXISTS inhealth_user;
CREATE USER inhealth_user WITH PASSWORD 'inhealth_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE inhealth_db TO inhealth_user;

-- Grant schema permissions
\c inhealth_db
GRANT ALL ON SCHEMA public TO inhealth_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO inhealth_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO inhealth_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO inhealth_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO inhealth_user;

-- Exit
\q
EOF

echo "PostgreSQL database 'inhealth_db' and user 'inhealth_user' created successfully."

# Create Python virtual environment
echo "Creating Python virtual environment..."
cd "$(dirname "$0")"
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Set environment variables
export DB_NAME="inhealth_db"
export DB_USER="inhealth_user"
export DB_PASSWORD="inhealth_password"
export DB_HOST="localhost"
export DB_PORT="5432"

# Create .env file for environment variables
echo "Creating .env file..."
cat > .env << EOF
DB_NAME=inhealth_db
DB_USER=inhealth_user
DB_PASSWORD=inhealth_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=django-insecure-change-this-in-production-2024-inhealth-ehr
DEBUG=True
EOF

# Run Django migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create Django superuser (optional - commented out for non-interactive install)
# echo "Creating Django superuser..."
# python manage.py createsuperuser

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Configure SELinux to allow httpd network connections (if needed)
echo "Configuring SELinux..."
sudo setsebool -P httpd_can_network_connect 1
sudo setsebool -P httpd_can_network_connect_db 1

# Configure firewall
echo "Configuring firewall..."
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-service=postgresql
sudo firewall-cmd --reload

echo ""
echo "========================================="
echo "Installation completed successfully!"
echo "========================================="
echo ""
echo "Database Information:"
echo "  Database Name: inhealth_db"
echo "  Database User: inhealth_user"
echo "  Database Password: inhealth_password"
echo "  Database Host: localhost"
echo "  Database Port: 5432"
echo ""
echo "To start the Django development server:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Create a superuser: python manage.py createsuperuser"
echo "  3. Run the server: python manage.py runserver 0.0.0.0:8000"
echo ""
echo "Access the application at: http://your-server-ip:8000"
echo "Access the admin panel at: http://your-server-ip:8000/admin"
echo ""
echo "IMPORTANT: Change the SECRET_KEY and database password in production!"
echo "========================================="
