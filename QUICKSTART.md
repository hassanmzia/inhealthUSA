# InHealth EHR - Quick Start Guide

## Prerequisites

Before you begin, ensure you have:
- PHP 8.1 or higher
- MySQL 5.7 or higher
- Composer
- Node.js & npm (for frontend assets)

## Quick Installation

### Option 1: Automated Installation (Ubuntu)

For a complete automated setup on Ubuntu:

```bash
chmod +x install_ubuntu.sh
./install_ubuntu.sh
```

This will install all dependencies (PHP, MySQL, Nginx, Composer, Node.js) and set up the application.

### Option 2: Manual Installation

If you already have PHP, MySQL, and Composer installed:

#### Step 1: Install Dependencies

```bash
# Install PHP dependencies
composer install

# Install Node.js dependencies
npm install
```

#### Step 2: Configure Environment

```bash
# Copy environment file
cp .env.example .env

# Generate application key
php artisan key:generate
```

#### Step 3: Configure Database

Edit `.env` file and set your database credentials:

```env
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=ehr_database
DB_USERNAME=ehr_user
DB_PASSWORD=your_password_here
```

#### Step 4: Create Database

```bash
# Log into MySQL
mysql -u root -p

# Create database and user
CREATE DATABASE ehr_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ehr_user'@'localhost' IDENTIFIED BY 'your_password_here';
GRANT ALL PRIVILEGES ON ehr_database.* TO 'ehr_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Import the EHR schema
mysql -u root -p < ehr_schema.sql
```

#### Step 5: Build Frontend Assets

```bash
# Development
npm run dev

# Production
npm run build
```

#### Step 6: Set Permissions

```bash
chmod -R 775 storage bootstrap/cache
```

#### Step 7: Start Development Server

```bash
php artisan serve
```

Visit: http://localhost:8000

## Common Issues & Solutions

### Error: "Application::configure does not exist"

**Solution**: This has been fixed. Make sure you pull the latest changes:
```bash
git pull origin claude/laravel-mysql-healthcare-setup-011CUsSGtsAFjf4hpmWXYsCk
```

### Error: "Class 'App\Http\Kernel' not found"

**Solution**: Run composer install to generate the autoloader:
```bash
composer install
composer dump-autoload
```

### Error: "No application encryption key has been specified"

**Solution**: Generate a new application key:
```bash
php artisan key:generate
```

### Error: Database connection refused

**Solution**:
1. Make sure MySQL is running: `sudo systemctl status mysql`
2. Check your `.env` database credentials
3. Test connection: `mysql -u ehr_user -p ehr_database`

### Error: Permission denied on storage directory

**Solution**: Set proper permissions:
```bash
sudo chown -R $USER:www-data storage bootstrap/cache
sudo chmod -R 775 storage bootstrap/cache
```

## Project Structure

```
inhealthUSA/
├── app/                    # Application code
│   ├── Http/
│   │   ├── Controllers/   # 6 controllers
│   │   ├── Middleware/    # Request middleware
│   │   └── Kernel.php     # HTTP kernel
│   ├── Models/            # 11 Eloquent models
│   ├── Providers/         # Service providers
│   ├── Console/           # Console commands
│   └── Exceptions/        # Exception handler
├── bootstrap/             # Bootstrap files
├── config/                # Configuration files
├── database/              # Database files
├── public/                # Public web files
├── resources/             # Views, CSS, JS
│   ├── views/            # Blade templates
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript
├── routes/                # Route definitions
│   ├── web.php           # Web routes
│   ├── api.php           # API routes
│   ├── console.php       # Console routes
│   └── channels.php      # Broadcast channels
├── storage/               # Application storage
├── vendor/                # Composer dependencies (after install)
├── .env.example           # Environment template
├── composer.json          # PHP dependencies
├── package.json           # Node dependencies
└── ehr_schema.sql         # Database schema
```

## Available Routes

### Web Interface

- `GET /` - Dashboard (overview, statistics)
- `GET /patients` - Patient list
- `GET /patients/{id}` - Patient details
- `GET /patients/create` - Create new patient
- `GET /encounters` - Encounter list
- `GET /encounters/{id}` - Encounter details
- `GET /prescriptions` - Prescription list

### API Endpoints

All API endpoints are prefixed with `/api/v1/`:

- `GET /api/v1/patients` - List all patients
- `GET /api/v1/patients/{id}` - Get patient details
- `GET /api/v1/encounters` - List all encounters
- `GET /api/v1/encounters/{id}` - Get encounter details
- `GET /api/v1/providers` - List all providers
- `GET /api/v1/departments` - List all departments
- `GET /api/v1/prescriptions` - List all prescriptions
- `GET /api/v1/patients/search/{query}` - Search patients

## Development

### Running Tests

```bash
php artisan test
```

### Code Formatting

```bash
./vendor/bin/pint
```

### Clearing Caches

```bash
php artisan config:clear
php artisan cache:clear
php artisan view:clear
php artisan route:clear
```

### Database Operations

```bash
# Run migrations (if you have migration files)
php artisan migrate

# Seed database with sample data
php artisan db:seed
```

## Production Deployment

For production deployment:

1. Set environment variables in `.env`:
   ```env
   APP_ENV=production
   APP_DEBUG=false
   APP_URL=https://yourdomain.com
   ```

2. Optimize for production:
   ```bash
   composer install --optimize-autoloader --no-dev
   php artisan config:cache
   php artisan route:cache
   php artisan view:cache
   npm run build
   ```

3. Set proper permissions:
   ```bash
   chmod -R 755 storage bootstrap/cache
   ```

4. Configure web server (Nginx or Apache)

5. Set up SSL/HTTPS

6. Configure automated backups

## Need Help?

- **Installation Guide**: See `INSTALLATION_GUIDE.md` for detailed setup instructions
- **Project Summary**: See `PROJECT_SUMMARY.md` for project overview
- **Database Documentation**: See `EHR_SCHEMA_DOCUMENTATION.md` for database details

## Security Checklist

Before going to production:

- [ ] Change all default passwords
- [ ] Set `APP_DEBUG=false`
- [ ] Set secure `APP_KEY`
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall
- [ ] Set up regular backups
- [ ] Implement authentication
- [ ] Review file permissions
- [ ] Enable error logging
- [ ] Set up monitoring

## License

Copyright © 2025 InTAM Health Inc. All rights reserved.
