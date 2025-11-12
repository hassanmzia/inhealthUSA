# Troubleshooting Guide

## Common Issues and Solutions

### 1. "relation 'django_session' does not exist" Error

**Error Message:**
```
ProgrammingError at /admin/
relation "django_session" does not exist
LINE 1: ...ession_data", "django_session"."expire_date" FROM "django_se...
```

**Cause:**
This error occurs when Django migrations have not been run on the database. The `django_session` table (and potentially other Django tables) haven't been created yet.

**Solution:**

1. **Check if PostgreSQL is running:**
   ```bash
   sudo systemctl status postgresql
   # or
   sudo service postgresql status
   ```

   If not running, start it:
   ```bash
   sudo systemctl start postgresql
   # or
   sudo service postgresql start
   ```

2. **Verify database exists:**
   ```bash
   sudo -u postgres psql -c "\l" | grep inhealth_db
   ```

   If the database doesn't exist, create it:
   ```bash
   sudo -u postgres psql << EOF
   CREATE DATABASE inhealth_db;
   CREATE USER inhealth_user WITH PASSWORD 'inhealth_password';
   GRANT ALL PRIVILEGES ON DATABASE inhealth_db TO inhealth_user;
   \c inhealth_db
   GRANT ALL ON SCHEMA public TO inhealth_user;
   EOF
   ```

3. **Activate virtual environment (if using one):**
   ```bash
   cd django_inhealth
   source venv/bin/activate
   ```

4. **Run Django migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Verify tables were created:**
   ```bash
   sudo -u postgres psql -d inhealth_db -c "\dt"
   ```

   You should see tables including:
   - `django_session`
   - `django_migrations`
   - `auth_user`
   - `healthcare_patient`
   - etc.

### 2. Database Connection Refused

**Error Message:**
```
django.db.utils.OperationalError: connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused
```

**Solutions:**

1. **Start PostgreSQL service:**
   ```bash
   sudo systemctl start postgresql
   sudo systemctl enable postgresql  # Enable auto-start on boot
   ```

2. **Check PostgreSQL is listening on the correct port:**
   ```bash
   sudo netstat -plnt | grep 5432
   ```

3. **Verify database credentials in settings.py or .env file**

### 3. Authentication Failed for User

**Error Message:**
```
FATAL: Peer authentication failed for user "postgres"
```

**Solution:**

Edit PostgreSQL authentication configuration:
```bash
sudo nano /etc/postgresql/16/main/pg_hba.conf
```

Change the line:
```
local   all             postgres                                peer
```

To:
```
local   all             postgres                                trust
```

Then reload PostgreSQL:
```bash
sudo systemctl reload postgresql
```

### 4. Static Files Not Found

**Error Message:**
```
?: (staticfiles.W004) The directory '/path/to/static' in the STATICFILES_DIRS setting does not exist.
```

**Solution:**

Create the static directory and collect static files:
```bash
mkdir -p static
python manage.py collectstatic --noinput
```

### 5. Permission Denied on SSL Certificate

**Error Message:**
```
FATAL: private key file "/etc/ssl/private/ssl-cert-snakeoil.key" has group or world access
```

**Solution:**

Fix SSL certificate permissions:
```bash
sudo chmod 640 /etc/ssl/private/ssl-cert-snakeoil.key
sudo chown root:ssl-cert /etc/ssl/private/ssl-cert-snakeoil.key
sudo usermod -a -G ssl-cert postgres
sudo systemctl restart postgresql
```

Or disable SSL in development (not recommended for production):
```bash
sudo nano /etc/postgresql/16/main/postgresql.conf
```

Change:
```
ssl = on
```

To:
```
ssl = off
```

Then restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## Quick Start Checklist

If you're experiencing issues, run through this checklist:

- [ ] PostgreSQL service is running
- [ ] Database `inhealth_db` exists
- [ ] Database user `inhealth_user` exists with correct password
- [ ] User has proper permissions on the database and schema
- [ ] Virtual environment is activated (if using one)
- [ ] Django dependencies are installed (`pip install -r requirements.txt`)
- [ ] Migrations have been run (`python manage.py migrate`)
- [ ] Static files collected (`python manage.py collectstatic`)
- [ ] Firewall allows traffic on required ports
- [ ] Environment variables are set correctly (.env file or exports)

## Running the Full Setup

If you haven't run the installation script yet, it's the easiest way to set everything up:

**Ubuntu 24.04:**
```bash
cd django_inhealth
chmod +x install_ubuntu24.sh
sudo ./install_ubuntu24.sh
```

**Rocky Linux 9:**
```bash
cd django_inhealth
chmod +x install_rocky9.sh
sudo ./install_rocky9.sh
```

## Getting Help

If you continue to experience issues:

1. Check the Django logs for detailed error messages
2. Verify PostgreSQL logs: `/var/log/postgresql/postgresql-16-main.log`
3. Run `python manage.py check` to identify configuration issues
4. Contact your development team with:
   - Complete error message
   - Django version (`python manage.py --version`)
   - PostgreSQL version (`psql --version`)
   - Operating system and version
   - Steps to reproduce the issue
