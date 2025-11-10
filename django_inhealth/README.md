# InHealth EHR - Django/PostgreSQL Version

A comprehensive Electronic Health Records (EHR) system built with Django and PostgreSQL, designed for healthcare providers to manage patient information, appointments, prescriptions, and medical records.

## Features

- **Patient Management**: Complete patient demographic information, medical history, and social history
- **Physician Management**: Provider profiles with specialties and credentials
- **Appointment Scheduling**: Track encounters/appointments with various types and statuses
- **Vital Signs Recording**: Comprehensive vital signs tracking (BP, HR, temperature, O2 saturation, weight, height, BMI)
- **Diagnosis Management**: ICD-10/ICD-11 coded diagnoses with status tracking
- **E-Prescribing**: Electronic prescription management with pharmacy information
- **Allergy Tracking**: Patient allergy documentation with severity levels
- **Medical History**: Complete medical history with conditions and status

## Technology Stack

- **Backend**: Django 5.0.1
- **Database**: PostgreSQL 15+
- **Frontend**: Django Templates with Tailwind CSS
- **Python**: 3.10+

## Installation

### Prerequisites

- Ubuntu 24.04 or Rocky Linux 9
- Root or sudo access
- Internet connection

### Ubuntu 24.04 Installation

```bash
cd django_inhealth
chmod +x install_ubuntu24.sh
sudo ./install_ubuntu24.sh
```

### Rocky Linux 9 Installation

```bash
cd django_inhealth
chmod +x install_rocky9.sh
sudo ./install_rocky9.sh
```

## Manual Installation

If you prefer to install manually:

### 1. Install System Dependencies

**Ubuntu:**
```bash
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib python3 python3-pip python3-venv libpq-dev
```

**Rocky Linux:**
```bash
sudo dnf install -y postgresql15-server postgresql15-contrib python3 python3-pip postgresql15-devel
```

### 2. Configure PostgreSQL

```sql
CREATE DATABASE inhealth_db;
CREATE USER inhealth_user WITH PASSWORD 'inhealth_password';
GRANT ALL PRIVILEGES ON DATABASE inhealth_db TO inhealth_user;
```

### 3. Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```env
DB_NAME=inhealth_db
DB_USER=inhealth_user
DB_PASSWORD=inhealth_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Collect Static Files

```bash
python manage.py collectstatic
```

### 8. Run Development Server

```bash
python manage.py runserver 0.0.0.0:8000
```

## Usage

### Access the Application

- **Main Application**: http://your-server-ip:8000/
- **Admin Panel**: http://your-server-ip:8000/admin/

### Default Database Credentials

- **Database**: inhealth_db
- **Username**: inhealth_user
- **Password**: inhealth_password

**IMPORTANT**: Change these credentials in production!

## Project Structure

```
django_inhealth/
├── inhealth/               # Main Django project
│   ├── settings.py        # Project settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── healthcare/            # Healthcare application
│   ├── models.py         # Data models
│   ├── views.py          # View functions
│   ├── urls.py           # URL routes
│   ├── admin.py          # Admin configuration
│   └── templates/        # HTML templates
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── install_ubuntu24.sh    # Ubuntu installation script
└── install_rocky9.sh      # Rocky Linux installation script
```

## Database Models

- **Patient**: Patient demographic and contact information
- **Provider**: Physician/provider information
- **Department**: Healthcare departments
- **Encounter**: Patient appointments/encounters
- **VitalSign**: Vital signs measurements
- **Diagnosis**: Patient diagnoses with ICD codes
- **Prescription**: Medication prescriptions
- **Allergy**: Patient allergies
- **MedicalHistory**: Patient medical history
- **SocialHistory**: Patient social history

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Starting Development Server

```bash
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in settings
2. Change `SECRET_KEY` to a secure random value
3. Update `ALLOWED_HOSTS` with your domain
4. Use a production WSGI server (Gunicorn)
5. Set up Nginx as a reverse proxy
6. Configure SSL/TLS certificates
7. Use strong database passwords
8. Enable PostgreSQL authentication
9. Configure proper firewall rules
10. Set up regular backups

## Security Considerations

- Change default database passwords
- Use environment variables for sensitive data
- Enable HTTPS in production
- Keep Django and dependencies updated
- Use Django's built-in security features
- Implement proper user authentication
- Regular security audits
- HIPAA compliance considerations for healthcare data

## Firewall Configuration

The installation scripts configure the following ports:

- **22**: SSH
- **80**: HTTP
- **443**: HTTPS
- **8000**: Django Development Server
- **5432**: PostgreSQL

## Support and Documentation

- Django Documentation: https://docs.djangoproject.com/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Project Issues: Report issues to your development team

## License

Proprietary - All rights reserved

## Contributing

Contact your development team for contribution guidelines.

## Changelog

### Version 1.0.0 (2024)
- Initial release
- Complete patient management system
- Appointment scheduling
- Prescription management
- Vital signs tracking
- Diagnosis management
- PostgreSQL database support
- Ubuntu 24 and Rocky Linux 9 support
