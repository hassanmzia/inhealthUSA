#!/bin/bash

#############################################################################
# InHealth Healthcare Application - Rocky Linux 9 Installation Script
# This script installs and configures Laravel, MySQL, and all dependencies
# on Rocky Linux 9
#############################################################################

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}InHealth EHR Installation Script${NC}"
echo -e "${GREEN}Rocky Linux 9${NC}"
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
sudo dnf update -y
sudo dnf install -y epel-release

# Install basic dependencies
print_status "Installing basic dependencies..."
sudo dnf install -y curl wget git unzip tar

# Install Remi's repository for PHP 8.2
print_status "Adding Remi's RPM repository for PHP 8.2..."
sudo dnf install -y https://rpms.remirepo.net/enterprise/remi-release-9.rpm
sudo dnf module reset php -y
sudo dnf module enable php:remi-8.2 -y

# Install PHP 8.2 and required extensions
print_status "Installing PHP 8.2 and extensions..."
sudo dnf install -y php php-cli php-fpm php-mysqlnd php-mbstring \
    php-xml php-bcmath php-json php-curl php-zip php-gd \
    php-intl php-redis php-soap php-opcache

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
sudo dnf install -y mysql-server

# Start and enable MySQL service
print_status "Starting MySQL service..."
sudo systemctl start mysqld
sudo systemctl enable mysqld

# Install Nginx (web server)
print_status "Installing Nginx..."
sudo dnf install -y nginx

# Start and enable Nginx
print_status "Starting Nginx service..."
sudo systemctl start nginx
sudo systemctl enable nginx

# Install Node.js and npm (for frontend assets)
print_status "Installing Node.js and npm..."
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo dnf install -y nodejs

# Verify Node.js installation
print_status "Verifying Node.js installation..."
node -v
npm -v

# Configure firewall
print_status "Configuring firewall..."
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# Configure SELinux for web application
print_status "Configuring SELinux..."
sudo setsebool -P httpd_can_network_connect 1
sudo setsebool -P httpd_can_network_connect_db 1
sudo setsebool -P httpd_unified 1

# Configure MySQL (secure installation)
print_status "Securing MySQL installation..."
print_warning "Please set a strong root password when prompted!"

# Get MySQL root password
read -sp "Enter MySQL root password to set: " MYSQL_ROOT_PASSWORD
echo

sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '$MYSQL_ROOT_PASSWORD';"
sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "DELETE FROM mysql.user WHERE User='';"
sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "DROP DATABASE IF EXISTS test;"
sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"
sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "FLUSH PRIVILEGES;"

# Create database and user
print_status "Creating database and user..."

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
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -f "$SCRIPT_DIR/ehr_schema.sql" ]; then
    mysql -u root -p"$MYSQL_ROOT_PASSWORD" < "$SCRIPT_DIR/ehr_schema.sql"
    print_status "Database schema imported successfully!"
else
    print_warning "ehr_schema.sql not found in $SCRIPT_DIR. Please import it manually later."
fi

# Navigate to application directory
cd "$SCRIPT_DIR"

# Install Laravel dependencies (if not already installed)
if [ ! -f "./composer.json" ]; then
    print_error "composer.json not found. Please ensure you're in the correct directory."
    exit 1
fi

print_status "Installing Laravel dependencies..."
composer install --no-interaction

# Set proper permissions
print_status "Setting file permissions..."
sudo chown -R $USER:nginx .
sudo chmod -R 775 storage bootstrap/cache

# Set SELinux contexts
print_status "Setting SELinux contexts..."
sudo chcon -R -t httpd_sys_rw_content_t storage
sudo chcon -R -t httpd_sys_rw_content_t bootstrap/cache

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

# Configure PHP-FPM
print_status "Configuring PHP-FPM..."
sudo sed -i 's/user = apache/user = nginx/' /etc/php-fpm.d/www.conf
sudo sed -i 's/group = apache/group = nginx/' /etc/php-fpm.d/www.conf
sudo sed -i 's/;listen.owner = nobody/listen.owner = nginx/' /etc/php-fpm.d/www.conf
sudo sed -i 's/;listen.group = nobody/listen.group = nginx/' /etc/php-fpm.d/www.conf
sudo sed -i 's/;listen.mode = 0660/listen.mode = 0660/' /etc/php-fpm.d/www.conf

# Start and enable PHP-FPM
print_status "Starting PHP-FPM..."
sudo systemctl start php-fpm
sudo systemctl enable php-fpm

# Configure Nginx
print_status "Configuring Nginx..."
NGINX_CONF="/etc/nginx/conf.d/inhealth.conf"
sudo tee $NGINX_CONF > /dev/null <<NGINX_CONFIG
server {
    listen 80;
    listen [::]:80;
    server_name localhost;
    root $SCRIPT_DIR/public;

    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";

    index index.php;

    charset utf-8;

    location / {
        try_files \$uri \$uri/ /index.php?\$query_string;
    }

    location = /favicon.ico { access_log off; log_not_found off; }
    location = /robots.txt  { access_log off; log_not_found off; }

    error_page 404 /index.php;

    location ~ \.php$ {
        fastcgi_pass unix:/run/php-fpm/www.sock;
        fastcgi_param SCRIPT_FILENAME \$realpath_root\$fastcgi_script_name;
        include fastcgi_params;
        fastcgi_hide_header X-Powered-By;
    }

    location ~ /\.(?!well-known).* {
        deny all;
    }
}
NGINX_CONFIG

# Test Nginx configuration
print_status "Testing Nginx configuration..."
sudo nginx -t

# Restart Nginx
print_status "Restarting Nginx..."
sudo systemctl restart nginx

# Create storage symlink
print_status "Creating storage symlink..."
php artisan storage:link

# Clear caches
print_status "Clearing Laravel caches..."
php artisan config:clear
php artisan cache:clear
php artisan view:clear
php artisan route:clear

# Set SELinux to allow Nginx to connect to network
print_status "Finalizing SELinux configuration..."
sudo semanage fcontext -a -t httpd_sys_rw_content_t "$SCRIPT_DIR/storage(/.*)?"
sudo semanage fcontext -a -t httpd_sys_rw_content_t "$SCRIPT_DIR/bootstrap/cache(/.*)?"
sudo restorecon -Rv "$SCRIPT_DIR/storage"
sudo restorecon -Rv "$SCRIPT_DIR/bootstrap/cache"

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}Application Details:${NC}"
echo -e "  URL: ${YELLOW}http://localhost${NC} or ${YELLOW}http://$SERVER_IP${NC}"
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
echo -e "  6. Review SELinux policies for your environment"
echo ""
echo -e "${GREEN}Service Status:${NC}"
echo -e "  Nginx: ${YELLOW}systemctl status nginx${NC}"
echo -e "  PHP-FPM: ${YELLOW}systemctl status php-fpm${NC}"
echo -e "  MySQL: ${YELLOW}systemctl status mysqld${NC}"
echo ""
echo -e "${GREEN}To start the development server:${NC}"
echo -e "  ${YELLOW}php artisan serve${NC}"
echo ""
echo -e "${GREEN}To access the application:${NC}"
echo -e "  ${YELLOW}http://localhost${NC} (Nginx)"
echo -e "  ${YELLOW}http://localhost:8000${NC} (Development server)"
echo ""
echo -e "${GREEN}Logs Location:${NC}"
echo -e "  Nginx: ${YELLOW}/var/log/nginx/${NC}"
echo -e "  PHP-FPM: ${YELLOW}/var/log/php-fpm/${NC}"
echo -e "  Laravel: ${YELLOW}$SCRIPT_DIR/storage/logs/${NC}"
echo ""
