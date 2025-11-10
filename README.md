# InHealth EHR - Electronic Health Record System

A complete, production-ready Electronic Health Record (EHR) system built with Laravel (PHP) and MySQL, designed for healthcare facilities to manage patient records, encounters, prescriptions, and clinical documentation.

## 🚀 Quick Start

### Ubuntu 20.04/22.04/24.04

```bash
chmod +x install_ubuntu.sh
./install_ubuntu.sh
```

### Rocky Linux 9

```bash
chmod +x install_rocky9.sh
./install_rocky9.sh
```

### Manual Installation

```bash
composer install
cp .env.example .env
php artisan key:generate
npm install && npm run build
php artisan serve
```

Visit: http://localhost:8000

## 📋 Features

### Patient Management
- Complete patient demographics and insurance
- Emergency contact management
- Patient search functionality
- Medical history (past, surgical, family, social)
- Allergy tracking with severity alerts

### Clinical Documentation
- Patient encounters and visits
- Vital signs recording (BP, temp, heart rate, etc.)
- Physical examinations
- Chief complaints and HPI
- Clinical impressions and assessments
- Treatment plans

### Prescriptions & Medications
- E-prescribing with pharmacy integration
- Dosage, frequency, and duration tracking
- Refill management
- Active/discontinued status

### Diagnoses
- ICD-10 and ICD-11 code support
- Primary, secondary, and differential diagnoses
- Active/resolved status tracking

### Dashboard & Analytics
- Real-time statistics
- Recent encounters listing
- Critical allergy alerts
- Today's appointments overview

### RESTful API
- Complete API for system integration
- Patient, encounter, and prescription endpoints
- Provider and department listings

## 🛠️ Technology Stack

- **Backend**: Laravel 10.x (PHP 8.1+)
- **Database**: MySQL 8.0+ with 40+ table schema
- **Frontend**: Blade templates + Tailwind CSS
- **Build Tools**: Vite, npm
- **Web Server**: Nginx or Apache

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Quick installation guide
- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - Detailed Ubuntu installation
- **[ROCKY_LINUX_INSTALL.md](ROCKY_LINUX_INSTALL.md)** - Rocky Linux 9 installation
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete project overview
- **[EHR_SCHEMA_DOCUMENTATION.md](EHR_SCHEMA_DOCUMENTATION.md)** - Database documentation

## 🗂️ Project Structure

```
inhealthUSA/
├── app/
│   ├── Http/Controllers/     # 6 controllers
│   ├── Models/               # 11 Eloquent models
│   ├── Providers/           # Service providers
│   └── Middleware/          # Request middleware
├── resources/
│   ├── views/               # Blade templates
│   ├── css/                 # Tailwind CSS
│   └── js/                  # JavaScript
├── routes/
│   ├── web.php              # Web routes
│   └── api.php              # API routes
├── database/
│   └── ehr_schema.sql       # MySQL schema (40+ tables)
├── install_ubuntu.sh        # Ubuntu installer
├── install_rocky9.sh        # Rocky Linux installer
└── quick_setup.sh           # Quick dev setup
```

## 🔌 API Endpoints

All API endpoints are prefixed with `/api/v1/`:

- `GET /api/v1/patients` - List patients
- `GET /api/v1/patients/{id}` - Get patient details
- `GET /api/v1/encounters` - List encounters
- `GET /api/v1/encounters/{id}` - Get encounter details
- `GET /api/v1/providers` - List providers
- `GET /api/v1/departments` - List departments
- `GET /api/v1/prescriptions` - List prescriptions
- `GET /api/v1/patients/search/{query}` - Search patients

## 🗄️ Database Schema

The application uses a comprehensive 40+ table MySQL schema covering:

1. **Patient Demographics** - patients, emergency_contacts, insurance_information
2. **Providers & Staff** - providers, departments
3. **Encounters** - encounters
4. **Clinical Documentation** - chief_complaints, vital_signs, physical_examinations
5. **Patient History** - past_medical_history, surgical_history, family_history, social_history, allergies
6. **Orders & Procedures** - physician_orders, medications, procedures_tests
7. **Laboratory & Imaging** - laboratory_tests, imaging_studies
8. **Diagnoses & Assessment** - diagnoses, clinical_impressions
9. **Treatment & Prescriptions** - treatment_plans, prescriptions
10. **Billing** - billing with CPT codes
11. **System & Audit** - audit_log, provider_signatures

## 🔒 Security Features

- Parameterized queries via Eloquent ORM
- CSRF protection
- Input validation
- Audit trail logging
- HIPAA compliance ready
- SELinux support (Rocky Linux)

## 🚀 Supported Platforms

### Ubuntu
- Ubuntu 20.04 LTS
- Ubuntu 22.04 LTS
- Ubuntu 24.04 LTS

### Rocky Linux
- Rocky Linux 9
- RHEL 9 compatible
- AlmaLinux 9 compatible

## 📦 Installation Options

### Option 1: Automated Installation (Ubuntu)
Full production setup with all dependencies
```bash
./install_ubuntu.sh
```

### Option 2: Automated Installation (Rocky Linux 9)
Full production setup with SELinux configuration
```bash
./install_rocky9.sh
```

### Option 3: Quick Setup (Development)
Assumes PHP, MySQL, and Composer are installed
```bash
./quick_setup.sh
```

### Option 4: Manual Installation
Follow detailed instructions in `INSTALLATION_GUIDE.md` or `ROCKY_LINUX_INSTALL.md`

## 🔧 Configuration

### Environment Variables (.env)

```env
APP_NAME="InHealth EHR"
APP_ENV=local
APP_DEBUG=true
APP_URL=http://localhost

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=ehr_database
DB_USERNAME=ehr_user
DB_PASSWORD=ehr_password_123
```

**Note**: Change these credentials in production!

## 🧪 Development

```bash
# Install dependencies
composer install
npm install

# Run development server
php artisan serve

# Build assets (development)
npm run dev

# Build assets (production)
npm run build

# Run tests
php artisan test
```

## 📊 Key Routes

- `/` - Dashboard
- `/patients` - Patient list
- `/patients/{id}` - Patient details
- `/encounters` - Encounter list
- `/encounters/{id}` - Encounter details
- `/prescriptions` - Prescription list

## 🔍 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check MySQL is running
sudo systemctl status mysql    # Ubuntu
sudo systemctl status mysqld   # Rocky Linux

# Test connection
mysql -u ehr_user -p ehr_database
```

**Permission Errors**
```bash
# Ubuntu
sudo chown -R $USER:www-data storage bootstrap/cache
sudo chmod -R 775 storage bootstrap/cache

# Rocky Linux (with SELinux)
sudo chown -R $USER:nginx storage bootstrap/cache
sudo chmod -R 775 storage bootstrap/cache
sudo chcon -R -t httpd_sys_rw_content_t storage bootstrap/cache
```

**SELinux Issues (Rocky Linux)**
```bash
# Check denials
sudo ausearch -m avc -ts recent

# Apply proper contexts
sudo restorecon -Rv storage bootstrap/cache
```

See `QUICKSTART.md` and `ROCKY_LINUX_INSTALL.md` for detailed troubleshooting.

## 📈 Performance

- Database indexes on foreign keys and common queries
- Eager loading to prevent N+1 queries
- Laravel cache system configured
- OPcache support
- Query optimization with database views

## 🔮 Future Enhancements

- Authentication & role-based access control
- Appointment scheduling
- Document management (PDF reports)
- E-signature for providers
- Patient portal
- Telemedicine integration
- HL7/FHIR API for interoperability
- Mobile applications

## 📄 License

Copyright © 2025 InTAM Health Inc. All rights reserved.

## 🆘 Support

For installation issues:
- Check the relevant installation guide for your OS
- Review logs in `storage/logs/laravel.log`
- Check web server logs (`/var/log/nginx/` or `/var/log/httpd/`)

## 👥 Contributing

This is a proprietary project for InTAM Health Inc.

## 🔗 Resources

- [Laravel Documentation](https://laravel.com/docs/10.x)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Rocky Linux Documentation](https://docs.rockylinux.org/)
- [Tailwind CSS](https://tailwindcss.com/docs)
