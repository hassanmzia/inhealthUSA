#!/bin/bash

#############################################################################
# InHealth Healthcare Application - Ubuntu Installation Script
# This script installs and configures Laravel, MySQL, and all dependencies
# on Ubuntu Linux (20.04/22.04/24.04)
#############################################################################

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}InHealth EHR Installation Script${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
   echo -e "${RED}Please do not run this script as root${NC}"
   exit 1
fi

# Function to print status messages
print_status() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_error() {
    echo -e "${RED}[!]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[*]${NC} $1"
}

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install basic dependencies
print_status "Installing basic dependencies..."
sudo apt install -y software-properties-common curl wget git unzip

# Add PHP repository
print_status "Adding PHP repository..."
sudo add-apt-repository ppa:ondrej/php -y
sudo apt update

# Install PHP 8.2 and required extensions
print_status "Installing PHP 8.2 and extensions..."
sudo apt install -y php8.2 \
    php8.2-cli \
    php8.2-fpm \
    php8.2-mysql \
    php8.2-mbstring \
    php8.2-xml \
    php8.2-bcmath \
    php8.2-curl \
    php8.2-zip \
    php8.2-gd \
    php8.2-intl \
    php8.2-redis \
    php8.2-soap

# Verify PHP installation
print_status "Verifying PHP installation..."
php -v

# Install Composer
print_status "Installing Composer..."
cd ~
curl -sS https://getcomposer.org/installer -o composer-setup.php
HASH=$(curl -sS https://composer.github.io/installer.sig)
php -r "if (hash_file('SHA384', 'composer-setup.php') === '$HASH') { echo 'Installer verified'; } else { echo 'Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;"
sudo php composer-setup.php --install-dir=/usr/local/bin --filename=composer
rm composer-setup.php

# Verify Composer installation
print_status "Verifying Composer installation..."
composer --version

# Install MySQL Server
print_status "Installing MySQL Server..."
sudo apt install -y mysql-server mysql-client

# Start and enable MySQL service
print_status "Starting MySQL service..."
sudo systemctl start mysql
sudo systemctl enable mysql

# Install Nginx (web server)
print_status "Installing Nginx..."
sudo apt install -y nginx

# Start and enable Nginx
print_status "Starting Nginx service..."
sudo systemctl start nginx
sudo systemctl enable nginx

# Configure firewall
print_status "Configuring firewall (UFW)..."
sudo ufw --force enable
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw allow 8000/tcp comment 'Laravel Development Server'
sudo ufw reload
print_status "Firewall rules configured."

# Install Node.js and npm (for frontend assets)
print_status "Installing Node.js and npm..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify Node.js installation
print_status "Verifying Node.js installation..."
node -v
npm -v

# Configure MySQL (secure installation)
print_status "Securing MySQL installation..."
print_warning "Please set a strong root password when prompted!"
sudo mysql_secure_installation

# Create database and user
print_status "Creating database and user..."
print_warning "Please enter the MySQL root password you just set:"
read -s MYSQL_ROOT_PASSWORD

mysql -u root -p"$MYSQL_ROOT_PASSWORD" <<MYSQL_SCRIPT
-- Create database
CREATE DATABASE IF NOT EXISTS ehr_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create application user
CREATE USER IF NOT EXISTS 'ehr_user'@'localhost' IDENTIFIED BY 'ehr_password_123';

-- Grant privileges
GRANT ALL PRIVILEGES ON ehr_database.* TO 'ehr_user'@'localhost';
FLUSH PRIVILEGES;

SELECT 'Database and user created successfully!' AS message;
MYSQL_SCRIPT

# Import the EHR schema
print_status "Importing EHR database schema..."
if [ -f "./ehr_schema.sql" ]; then
    mysql -u root -p"$MYSQL_ROOT_PASSWORD" < ./ehr_schema.sql
    print_status "Database schema imported successfully!"
else
    print_warning "ehr_schema.sql not found. Please import it manually later."
fi

# Create required directories
print_status "Creating Laravel directory structure..."
mkdir -p storage/{app,framework,logs}
mkdir -p storage/framework/{cache,sessions,testing,views}
mkdir -p storage/app/public
mkdir -p bootstrap/cache

# Set proper permissions before composer install
print_status "Setting file permissions..."
sudo chown -R $USER:www-data .
sudo chmod -R 775 storage bootstrap/cache

# Install Laravel (if not already in the directory)
if [ ! -f "./composer.json" ]; then
    print_status "Installing Laravel..."
    composer create-project laravel/laravel . --prefer-dist
else
    print_status "Laravel already exists. Running composer install..."
    composer install
fi

# Create .env file
print_status "Configuring .env file..."
if [ ! -f ".env" ]; then
    cp .env.example .env
fi

# Configure database in .env
sed -i "s/DB_CONNECTION=.*/DB_CONNECTION=mysql/" .env
sed -i "s/DB_HOST=.*/DB_HOST=127.0.0.1/" .env
sed -i "s/DB_PORT=.*/DB_PORT=3306/" .env
sed -i "s/DB_DATABASE=.*/DB_DATABASE=ehr_database/" .env
sed -i "s/DB_USERNAME=.*/DB_USERNAME=ehr_user/" .env
sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=ehr_password_123/" .env

# Set APP_NAME
sed -i "s/APP_NAME=.*/APP_NAME=\"InHealth EHR\"/" .env

# Generate application key
print_status "Generating application key..."
php artisan key:generate

# Install frontend dependencies
print_status "Installing frontend dependencies..."
npm install

# Build frontend assets
print_status "Building frontend assets..."
npm run build

# Configure Nginx
print_status "Configuring Nginx..."
NGINX_CONF="/etc/nginx/sites-available/inhealth"
sudo tee $NGINX_CONF > /dev/null <<'NGINX_CONFIG'
server {
    listen 80;
    listen [::]:80;
    server_name localhost;
    root /home/$USER/inhealthUSA/public;

    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";

    index index.php;

    charset utf-8;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location = /favicon.ico { access_log off; log_not_found off; }
    location = /robots.txt  { access_log off; log_not_found off; }

    error_page 404 /index.php;

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.(?!well-known).* {
        deny all;
    }
}
NGINX_CONFIG

# Replace $USER with actual username
sudo sed -i "s/\$USER/$USER/g" $NGINX_CONF

# Enable the site
sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
print_status "Testing Nginx configuration..."
sudo nginx -t

# Restart Nginx
print_status "Restarting Nginx..."
sudo systemctl restart nginx

# Configure PHP-FPM
print_status "Configuring PHP-FPM..."
sudo sed -i 's/;cgi.fix_pathinfo=1/cgi.fix_pathinfo=0/' /etc/php/8.2/fpm/php.ini
sudo systemctl restart php8.2-fpm

# Create storage symlink
print_status "Creating storage symlink..."
php artisan storage:link

# Clear caches
print_status "Clearing Laravel caches..."
php artisan config:clear
php artisan cache:clear
php artisan view:clear

# Install Laravel Breeze for authentication (optional)
print_status "Installing Laravel Breeze for authentication..."
composer require laravel/breeze --dev
php artisan breeze:install blade
npm install
npm run build

# Run migrations
print_status "Running database migrations..."
php artisan migrate

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}Application Details:${NC}"
echo -e "  URL: ${YELLOW}http://localhost${NC}"
echo -e "  Database: ${YELLOW}ehr_database${NC}"
echo -e "  DB User: ${YELLOW}ehr_user${NC}"
echo -e "  DB Password: ${YELLOW}ehr_password_123${NC}"
echo ""
echo -e "${YELLOW}IMPORTANT SECURITY NOTES:${NC}"
echo -e "  1. Change the database password in production!"
echo -e "  2. Update the APP_KEY in .env"
echo -e "  3. Set APP_DEBUG=false in production"
echo -e "  4. Configure proper firewall rules"
echo -e "  5. Set up SSL/TLS certificates for HTTPS"
echo ""
echo -e "${GREEN}To start the development server:${NC}"
echo -e "  ${YELLOW}php artisan serve${NC}"
echo ""
echo -e "${GREEN}To access the application:${NC}"
echo -e "  ${YELLOW}http://localhost${NC} (Nginx)"
echo -e "  ${YELLOW}http://localhost:8000${NC} (Development server)"
echo ""
