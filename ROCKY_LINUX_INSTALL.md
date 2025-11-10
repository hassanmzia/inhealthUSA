# InHealth EHR - Rocky Linux 9 Installation Guide

This guide provides detailed instructions for installing the InHealth EHR system on Rocky Linux 9.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Automated Installation](#automated-installation)
- [Manual Installation](#manual-installation)
- [Rocky Linux Specific Configuration](#rocky-linux-specific-configuration)
- [Troubleshooting](#troubleshooting)
- [Security Hardening](#security-hardening)

## Prerequisites

- Rocky Linux 9 (fresh installation recommended)
- At least 2GB RAM
- 20GB free disk space
- Root or sudo access
- Internet connection

## Automated Installation

For a complete automated installation (recommended):

```bash
chmod +x install_rocky9.sh
./install_rocky9.sh
```

This script will:
1. ✅ Install PHP 8.2 from Remi's repository
2. ✅ Install MySQL Server 8.0
3. ✅ Install Composer
4. ✅ Install Node.js 20.x and npm
5. ✅ Install and configure Nginx
6. ✅ Configure firewall (firewalld)
7. ✅ Configure SELinux policies
8. ✅ Create database and user
9. ✅ Import EHR schema
10. ✅ Configure Laravel
11. ✅ Set up Nginx virtual host
12. ✅ Build frontend assets

## Manual Installation

If you prefer to install manually, follow these steps:

### 1. Update System

```bash
sudo dnf update -y
sudo dnf install -y epel-release
```

### 2. Install PHP 8.2

```bash
# Add Remi's repository
sudo dnf install -y https://rpms.remirepo.net/enterprise/remi-release-9.rpm

# Enable PHP 8.2 module
sudo dnf module reset php -y
sudo dnf module enable php:remi-8.2 -y

# Install PHP and extensions
sudo dnf install -y php php-cli php-fpm php-mysqlnd php-mbstring \
    php-xml php-bcmath php-json php-curl php-zip php-gd \
    php-intl php-redis php-soap php-opcache

# Verify installation
php -v
```

### 3. Install Composer

```bash
curl -sS https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer
composer --version
```

### 4. Install MySQL

```bash
# Install MySQL Server
sudo dnf install -y mysql-server

# Start and enable MySQL
sudo systemctl start mysqld
sudo systemctl enable mysqld

# Secure MySQL installation
sudo mysql_secure_installation
```

### 5. Install Node.js

```bash
# Add NodeSource repository
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -

# Install Node.js
sudo dnf install -y nodejs

# Verify installation
node -v
npm -v
```

### 6. Install Nginx

```bash
sudo dnf install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 7. Configure Firewall

```bash
# Allow HTTP and HTTPS
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# Verify
sudo firewall-cmd --list-all
```

### 8. Set Up Database

```bash
# Create database
mysql -u root -p << 'EOF'
CREATE DATABASE ehr_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ehr_user'@'localhost' IDENTIFIED BY 'ehr_password_123';
GRANT ALL PRIVILEGES ON ehr_database.* TO 'ehr_user'@'localhost';
FLUSH PRIVILEGES;
EOF

# Import schema
mysql -u root -p < ehr_schema.sql
```

### 9. Configure Laravel Application

```bash
# Navigate to application directory
cd /path/to/inhealthUSA

# Install PHP dependencies
composer install

# Copy environment file
cp .env.example .env

# Configure database
vi .env
# Set: DB_DATABASE=ehr_database
#      DB_USERNAME=ehr_user
#      DB_PASSWORD=ehr_password_123

# Generate application key
php artisan key:generate

# Install and build frontend
npm install
npm run build
```

### 10. Set Permissions

```bash
# Set ownership
sudo chown -R $USER:nginx .

# Set permissions
sudo chmod -R 775 storage bootstrap/cache
```

### 11. Configure SELinux

**IMPORTANT**: Rocky Linux uses SELinux by default. Configure it properly:

```bash
# Allow Nginx to connect to network and database
sudo setsebool -P httpd_can_network_connect 1
sudo setsebool -P httpd_can_network_connect_db 1
sudo setsebool -P httpd_unified 1

# Set proper contexts for writable directories
sudo semanage fcontext -a -t httpd_sys_rw_content_t "/path/to/inhealthUSA/storage(/.*)?"
sudo semanage fcontext -a -t httpd_sys_rw_content_t "/path/to/inhealthUSA/bootstrap/cache(/.*)?"
sudo restorecon -Rv /path/to/inhealthUSA/storage
sudo restorecon -Rv /path/to/inhealthUSA/bootstrap/cache

# Set context for application directory
sudo chcon -R -t httpd_sys_rw_content_t storage
sudo chcon -R -t httpd_sys_rw_content_t bootstrap/cache
```

### 12. Configure PHP-FPM

```bash
# Edit PHP-FPM configuration
sudo vi /etc/php-fpm.d/www.conf

# Change these lines:
# user = nginx
# group = nginx
# listen.owner = nginx
# listen.group = nginx
# listen.mode = 0660

# Or use sed:
sudo sed -i 's/user = apache/user = nginx/' /etc/php-fpm.d/www.conf
sudo sed -i 's/group = apache/group = nginx/' /etc/php-fpm.d/www.conf
sudo sed -i 's/;listen.owner = nobody/listen.owner = nginx/' /etc/php-fpm.d/www.conf
sudo sed -i 's/;listen.group = nobody/listen.group = nginx/' /etc/php-fpm.d/www.conf

# Start PHP-FPM
sudo systemctl start php-fpm
sudo systemctl enable php-fpm
```

### 13. Configure Nginx

Create `/etc/nginx/conf.d/inhealth.conf`:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name your_domain.com;  # Change this
    root /path/to/inhealthUSA/public;  # Change this

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
        fastcgi_pass unix:/run/php-fpm/www.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
        fastcgi_hide_header X-Powered-By;
    }

    location ~ /\.(?!well-known).* {
        deny all;
    }
}
```

Test and reload Nginx:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

## Rocky Linux Specific Configuration

### SELinux Considerations

Rocky Linux enforces SELinux by default. Here's what you need to know:

#### Check SELinux Status

```bash
sestatus
```

#### Allow Laravel Operations

```bash
# Allow web server to write to storage
sudo setsebool -P httpd_unified 1

# Allow network connections (for external APIs)
sudo setsebool -P httpd_can_network_connect 1

# Allow database connections
sudo setsebool -P httpd_can_network_connect_db 1
```

#### Set File Contexts

```bash
# For application directory
sudo semanage fcontext -a -t httpd_sys_content_t "/path/to/inhealthUSA(/.*)?"
sudo restorecon -Rv /path/to/inhealthUSA

# For writable directories
sudo semanage fcontext -a -t httpd_sys_rw_content_t "/path/to/inhealthUSA/storage(/.*)?"
sudo semanage fcontext -a -t httpd_sys_rw_content_t "/path/to/inhealthUSA/bootstrap/cache(/.*)?"
sudo restorecon -Rv /path/to/inhealthUSA/storage
sudo restorecon -Rv /path/to/inhealthUSA/bootstrap/cache
```

#### Troubleshooting SELinux

If you encounter permission issues:

```bash
# View SELinux denials
sudo ausearch -m avc -ts recent

# Generate custom policy (if needed)
sudo ausearch -m avc -ts recent | audit2allow -M mypolicy
sudo semodule -i mypolicy.pp

# Temporarily disable SELinux (for testing only!)
sudo setenforce 0

# Re-enable SELinux
sudo setenforce 1
```

### Firewall Configuration

Rocky Linux uses firewalld:

```bash
# Check firewall status
sudo firewall-cmd --state

# List all rules
sudo firewall-cmd --list-all

# Add services
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https

# Add custom port (if needed)
sudo firewall-cmd --permanent --add-port=8000/tcp

# Reload firewall
sudo firewall-cmd --reload

# Remove a service
sudo firewall-cmd --permanent --remove-service=http
sudo firewall-cmd --reload
```

## Troubleshooting

### Issue: Permission Denied Errors

**Cause**: SELinux is blocking access

**Solution**:
```bash
# Check SELinux denials
sudo ausearch -m avc -ts recent

# Apply proper contexts
sudo restorecon -Rv /path/to/inhealthUSA
```

### Issue: 502 Bad Gateway

**Cause**: PHP-FPM not running or misconfigured

**Solution**:
```bash
# Check PHP-FPM status
sudo systemctl status php-fpm

# Check PHP-FPM logs
sudo tail -f /var/log/php-fpm/error.log

# Verify socket exists
ls -l /run/php-fpm/www.sock

# Restart PHP-FPM
sudo systemctl restart php-fpm
```

### Issue: Database Connection Failed

**Cause**: MySQL not running or incorrect credentials

**Solution**:
```bash
# Check MySQL status
sudo systemctl status mysqld

# Test connection
mysql -u ehr_user -p ehr_database

# Check MySQL logs
sudo tail -f /var/log/mysqld.log
```

### Issue: Cannot Write to storage Directory

**Cause**: Incorrect permissions or SELinux context

**Solution**:
```bash
# Fix permissions
sudo chown -R $USER:nginx storage bootstrap/cache
sudo chmod -R 775 storage bootstrap/cache

# Fix SELinux context
sudo chcon -R -t httpd_sys_rw_content_t storage
sudo chcon -R -t httpd_sys_rw_content_t bootstrap/cache
```

### Issue: Composer Install Fails

**Cause**: Memory limit or missing dependencies

**Solution**:
```bash
# Increase PHP memory limit
sudo vi /etc/php.ini
# Set: memory_limit = 512M

# Or run with unlimited memory
php -d memory_limit=-1 /usr/local/bin/composer install
```

### Issue: npm Build Fails

**Cause**: Insufficient memory

**Solution**:
```bash
# Increase Node.js memory
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

## Security Hardening

### 1. Secure MySQL

```bash
# Run secure installation
sudo mysql_secure_installation

# Disable remote root access
mysql -u root -p -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"

# Create separate user for application
mysql -u root -p -e "CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'strong_password';"
mysql -u root -p -e "GRANT SELECT, INSERT, UPDATE, DELETE ON ehr_database.* TO 'app_user'@'localhost';"
```

### 2. Configure SSL/TLS

```bash
# Install certbot
sudo dnf install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your_domain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

### 3. Harden PHP Configuration

Edit `/etc/php.ini`:

```ini
expose_php = Off
display_errors = Off
log_errors = On
error_log = /var/log/php_errors.log
max_execution_time = 30
max_input_time = 60
memory_limit = 256M
post_max_size = 20M
upload_max_filesize = 20M
session.cookie_httponly = 1
session.cookie_secure = 1
disable_functions = exec,passthru,shell_exec,system,proc_open,popen
```

### 4. Configure Nginx Security Headers

Add to `/etc/nginx/conf.d/inhealth.conf`:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

### 5. Set Up Automated Backups

```bash
# Create backup script
sudo vi /usr/local/bin/backup-ehr.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backup/ehr"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
mysqldump -u root -p'password' ehr_database | gzip > $BACKUP_DIR/ehr_db_$DATE.sql.gz

# Backup application files
tar -czf $BACKUP_DIR/ehr_files_$DATE.tar.gz /path/to/inhealthUSA

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-ehr.sh

# Add to cron
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-ehr.sh
```

### 6. Configure Fail2ban

```bash
# Install fail2ban
sudo dnf install -y fail2ban

# Configure
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo vi /etc/fail2ban/jail.local

# Enable and start
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## Performance Optimization

### 1. Enable OPcache

Edit `/etc/php.d/10-opcache.ini`:

```ini
opcache.enable=1
opcache.memory_consumption=256
opcache.max_accelerated_files=10000
opcache.revalidate_freq=60
```

### 2. Optimize MySQL

Edit `/etc/my.cnf.d/mysql-server.cnf`:

```ini
[mysqld]
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
max_connections = 200
query_cache_size = 64M
query_cache_type = 1
```

### 3. Laravel Optimizations

```bash
# Cache configuration
php artisan config:cache

# Cache routes
php artisan route:cache

# Cache views
php artisan view:cache

# Optimize autoloader
composer install --optimize-autoloader --no-dev
```

## Service Management

```bash
# View all services
sudo systemctl list-units --type=service

# Start services
sudo systemctl start nginx php-fpm mysqld

# Stop services
sudo systemctl stop nginx php-fpm mysqld

# Restart services
sudo systemctl restart nginx php-fpm mysqld

# Enable on boot
sudo systemctl enable nginx php-fpm mysqld

# Check status
sudo systemctl status nginx php-fpm mysqld
```

## Logs

### View Logs

```bash
# Nginx access log
sudo tail -f /var/log/nginx/access.log

# Nginx error log
sudo tail -f /var/log/nginx/error.log

# PHP-FPM log
sudo tail -f /var/log/php-fpm/error.log

# MySQL log
sudo tail -f /var/log/mysqld.log

# Laravel log
tail -f storage/logs/laravel.log

# System log
sudo journalctl -f
```

## Additional Resources

- [Rocky Linux Documentation](https://docs.rockylinux.org/)
- [SELinux User's Guide](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/using_selinux/)
- [Laravel Deployment](https://laravel.com/docs/10.x/deployment)

## Support

For issues specific to Rocky Linux installation, check:
1. SELinux audit logs: `sudo ausearch -m avc -ts recent`
2. System journal: `sudo journalctl -xe`
3. Service status: `sudo systemctl status <service>`

## License

Copyright © 2025 InTAM Health Inc. All rights reserved.
