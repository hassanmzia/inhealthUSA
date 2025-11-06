# InHealth EHR - Installation Guide

This guide will walk you through installing and setting up the InHealth Electronic Health Record system on Ubuntu Linux.

## Prerequisites

- Ubuntu Linux 20.04/22.04/24.04 LTS
- At least 2GB RAM
- 20GB free disk space
- Root or sudo access

## Quick Installation

For a complete automated installation (recommended for production):

```bash
chmod +x install_ubuntu.sh
./install_ubuntu.sh
```

This script will:
1. Install PHP 8.2 and all required extensions
2. Install MySQL Server
3. Install Composer (PHP dependency manager)
4. Install Node.js and npm
5. Install Nginx web server
6. Create the database and user
7. Import the EHR schema
8. Configure Laravel
9. Set up Nginx virtual host

## Development Setup

For a quicker development setup (assumes you already have PHP, MySQL, and Composer):

```bash
chmod +x quick_setup.sh
./quick_setup.sh
```

## Manual Installation

If you prefer to install manually, follow these steps:

### 1. Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install PHP 8.2
sudo add-apt-repository ppa:ondrej/php -y
sudo apt update
sudo apt install -y php8.2 php8.2-cli php8.2-fpm php8.2-mysql php8.2-mbstring \
    php8.2-xml php8.2-bcmath php8.2-curl php8.2-zip php8.2-gd

# Install MySQL
sudo apt install -y mysql-server

# Install Composer
curl -sS https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### 2. Set Up MySQL Database

```bash
# Secure MySQL installation
sudo mysql_secure_installation

# Create database and user
mysql -u root -p << 'EOF'
CREATE DATABASE ehr_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ehr_user'@'localhost' IDENTIFIED BY 'ehr_password_123';
GRANT ALL PRIVILEGES ON ehr_database.* TO 'ehr_user'@'localhost';
FLUSH PRIVILEGES;
EOF

# Import the schema
mysql -u root -p < ehr_schema.sql
```

### 3. Configure Laravel

```bash
# Install PHP dependencies
composer install

# Copy environment file
cp .env.example .env

# Configure database in .env
sed -i "s/DB_DATABASE=.*/DB_DATABASE=ehr_database/" .env
sed -i "s/DB_USERNAME=.*/DB_USERNAME=ehr_user/" .env
sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=ehr_password_123/" .env

# Generate application key
php artisan key:generate

# Set permissions
sudo chown -R $USER:www-data .
sudo chmod -R 775 storage bootstrap/cache
```

### 4. Install Frontend Dependencies

```bash
# Install npm packages
npm install

# Build assets
npm run build
```

### 5. Set Up Web Server

#### Using Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/inhealth

# Add the following configuration:
server {
    listen 80;
    listen [::]:80;
    server_name localhost;
    root /path/to/inhealthUSA/public;

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

# Enable site
sudo ln -s /etc/nginx/sites-available/inhealth /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx
```

### 6. Start the Application

For development:
```bash
php artisan serve
```

Access the application at: http://localhost:8000

For production (using Nginx):
Access the application at: http://localhost

## Database Configuration

The application connects to the MySQL database using the credentials in the `.env` file:

```env
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=ehr_database
DB_USERNAME=ehr_user
DB_PASSWORD=ehr_password_123
```

**IMPORTANT:** Change these credentials in production!

## Features

The InHealth EHR system includes:

- **Patient Management**: Complete patient demographics, insurance, and contact information
- **Encounter Management**: Track patient visits and appointments
- **Clinical Documentation**: Chief complaints, vital signs, physical examinations
- **Diagnoses**: ICD-10/ICD-11 coded diagnoses
- **Prescriptions**: E-prescribing with pharmacy information
- **Allergies**: Track and alert on patient allergies
- **Medical History**: Past medical, surgical, family, and social history
- **Laboratory and Imaging**: Track test orders and results
- **Billing**: CPT codes and billing information
- **API**: RESTful API for integration with other systems

## Default Routes

- `/` - Dashboard
- `/patients` - Patient list
- `/patients/{id}` - Patient details
- `/encounters` - Encounter list
- `/encounters/{id}` - Encounter details
- `/prescriptions` - Prescription list

## API Endpoints

API endpoints are available at `/api/v1/`:

- `GET /api/v1/patients` - List patients
- `GET /api/v1/patients/{id}` - Get patient details
- `GET /api/v1/encounters` - List encounters
- `GET /api/v1/encounters/{id}` - Get encounter details
- `GET /api/v1/providers` - List providers
- `GET /api/v1/departments` - List departments
- `GET /api/v1/prescriptions` - List prescriptions

## Troubleshooting

### Database Connection Error

If you get a database connection error:

1. Verify MySQL is running: `sudo systemctl status mysql`
2. Check database credentials in `.env`
3. Test connection: `mysql -u ehr_user -p ehr_database`

### Permission Errors

If you get permission errors:

```bash
sudo chown -R $USER:www-data storage bootstrap/cache
sudo chmod -R 775 storage bootstrap/cache
```

### Composer Errors

If composer fails:

```bash
composer install --no-scripts
php artisan key:generate
composer install
```

## Security Considerations

Before deploying to production:

1. **Change Database Password**: Update the `ehr_user` password
2. **Set APP_DEBUG=false**: In `.env` file
3. **Configure APP_URL**: Set to your domain
4. **Enable HTTPS**: Use Let's Encrypt or another SSL certificate
5. **Set Up Firewall**: Configure UFW or iptables
6. **Regular Backups**: Set up automated database backups
7. **Keep Updated**: Regularly update packages and dependencies

## Support

For issues or questions:
- Check the documentation in `EHR_SCHEMA_DOCUMENTATION.md`
- Review the database schema in `ehr_schema.sql`
- Contact: InTAM Health Inc

## License

Copyright InTAM Health Inc. All rights reserved.
