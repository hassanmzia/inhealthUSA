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

### 2. "relation 'billings' already exists" Error

**Error Message:**
```
django.db.utils.ProgrammingError: relation "billings" already exists
```

**Full Error Context:**
```
Applying healthcare.0003_billing_alter_userprofile_role_payment_and_more...
Traceback (most recent call last):
  ...
psycopg2.errors.DuplicateTable: relation "billings" already exists
```

**Cause:**
This error occurs when the database tables already exist but Django's migration tracking system doesn't know they've been applied. This typically happens when:
- Tables were created manually in the database
- A previous migration partially failed
- The `django_migrations` table is out of sync with the actual database state

**Solution:**

Use the provided fix script or follow these manual steps:

**Option 1: Using the Fix Script (Recommended)**
```bash
cd /home/zia/django_inhealth
chmod +x fix_migration_issue.sh
./fix_migration_issue.sh
```

**Option 2: Manual Fix**
```bash
cd /home/zia/django_inhealth
source venv/bin/activate  # if using virtual environment

# Fake the migration using FULL migration name (not just "0003")
python manage.py migrate healthcare 0003_billing_alter_userprofile_role_payment_and_more --fake

# Apply remaining migrations
python manage.py migrate

# Verify the fix
python manage.py showmigrations healthcare
```

**IMPORTANT:** You must use the **full migration name**. Using just "0003" will cause an error: "More than one migration matches '0003'".

**What does `--fake` do?**
The `--fake` flag tells Django to mark the migration as applied in the `django_migrations` table without actually executing the SQL commands. This is useful when the database changes have already been made but Django doesn't know about them.

**Verification:**
After running the fix, all migrations should show as applied:
```bash
python manage.py showmigrations
```

You should see:
```
healthcare
 [X] 0001_initial
 [X] 0002_familyhistory
 [X] 0003_billing_alter_userprofile_role_payment_and_more
```

### 3. Database Connection Refused

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

### 4. Authentication Failed for User

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

### 5. Static Files Not Found

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

### 6. Permission Denied on Staticfiles Directory

**Error Message:**
```
PermissionError: [Errno 13] Permission denied: '/path/to/staticfiles/admin/css/autocomplete.css'
```

**Full Error Context:**
```
File "/path/to/django/contrib/staticfiles/management/commands/collectstatic.py", line 270, in clear_dir
    self.storage.delete(fpath)
File "/path/to/django/core/files/storage/filesystem.py", line 158, in delete
    os.remove(name)
PermissionError: [Errno 13] Permission denied: '/path/to/staticfiles/admin/css/autocomplete.css'
```

**Cause:**
This error occurs when the `staticfiles` directory exists but is owned by a different user (e.g., root or another user). This typically happens when:
- Static files were previously collected with sudo or by a different user
- The directory was created with incorrect ownership
- A deployment process created files with different permissions

**Solution:**

**Option 1: Using the Fix Script (Recommended - Removes and Recreates)**
```bash
cd scripts
./fix_staticfiles_permissions.sh
```

This script will:
1. Remove the existing staticfiles directory (using sudo if needed)
2. Create a fresh staticfiles directory with proper permissions
3. Set correct permissions (755)

**Option 2: Using the Ownership Fix Script (Preserves Existing Files)**
```bash
cd scripts
./fix_staticfiles_ownership.sh
```

This script will:
1. Change ownership of the staticfiles directory to the current user
2. Set proper permissions (755)
3. Preserve all existing static files

**Option 3: Manual Fix (Remove and Recreate)**
```bash
cd django_inhealth

# Remove existing directory (may need sudo)
sudo rm -rf staticfiles

# Create fresh directory
mkdir -p staticfiles
chmod 755 staticfiles

# Collect static files
python manage.py collectstatic --noinput
```

**Option 4: Manual Fix (Change Ownership)**
```bash
cd django_inhealth

# Change ownership to current user
sudo chown -R $(whoami):$(whoami) staticfiles
sudo chmod -R 755 staticfiles

# Collect static files
python manage.py collectstatic --noinput
```

**After Fixing Permissions:**

Once permissions are fixed, collect static files:
```bash
python manage.py collectstatic --noinput
```

**Prevention:**
- Always run `python manage.py collectstatic` as the same user that runs the Django application
- Avoid using `sudo` when running Django management commands unless absolutely necessary
- In production, ensure the web server user has write access to the staticfiles directory

### 7. User Profile Pictures Blocked After Enabling SSL

**Symptoms:**
- Profile pictures don't load after enabling HTTPS/SSL
- Browser console shows "Mixed Content" errors
- Images worked fine with HTTP but fail with HTTPS

**Cause:**
This issue occurs when browsers block "mixed content" - when an HTTPS page tries to load resources over HTTP. Common causes include:
- Django not detecting that requests came over HTTPS
- Nginx not forwarding the protocol information correctly
- Incorrect nginx media file configuration
- File permission issues preventing nginx from serving media files

**Solution:**

**Step 1: Verify Nginx Configuration**

Ensure your nginx configuration includes the X-Forwarded-Proto header:

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;  # CRITICAL - Tells Django if HTTPS
    proxy_set_header X-Forwarded-Host $server_name;
}
```

**Step 2: Verify Django Settings**

Ensure these settings are in your `settings.py`:

```python
# Trust the X-Forwarded-Proto header from Nginx
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Use relative URL (not absolute with http://)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**Step 3: Check Media Directory Permissions**

The nginx user (usually `www-data` or `nginx`) needs read access to media files:

```bash
cd django_inhealth

# Check current permissions
ls -la media/

# Fix permissions if needed
sudo chown -R $USER:www-data media/
sudo chmod -R 755 media/

# Ensure uploaded files have correct permissions
sudo chmod -R 755 media/profile_pictures/
```

**Step 4: Verify Nginx Media Configuration**

Ensure nginx is configured to serve media files. In your nginx site configuration:

```nginx
# Django Media Files (User uploads)
location /media/ {
    alias /path/to/django_inhealth/media/;  # Update this path
    expires 7d;
    add_header Cache-Control "public";

    # Security: Prevent execution of uploaded scripts
    location ~* \.(php|py|pl|sh|cgi|exe)$ {
        deny all;
    }
}
```

**Step 5: Test Media File Access**

Test if nginx can serve media files directly:

```bash
# Create a test file
echo "test" > django_inhealth/media/test.txt

# Try accessing via browser or curl
curl https://yourdomain.com/media/test.txt
# Should return "test"

# If it fails, check nginx error logs
sudo tail -f /var/log/nginx/error.log
```

**Step 6: Restart Services**

After making changes, restart nginx:

```bash
# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Or restart nginx
sudo systemctl restart nginx
```

**Step 7: Check Browser Console**

Open your browser's developer console (F12) and look for errors:
- **Mixed Content errors**: Django is generating HTTP URLs instead of HTTPS
  - Solution: Ensure `SECURE_PROXY_SSL_HEADER` is set correctly
- **404 errors**: Nginx can't find the media files
  - Solution: Check the media path in nginx config
- **403 errors**: Permission denied
  - Solution: Fix file permissions (see Step 3)

**Debugging Commands:**

```bash
# Check if media directory exists and has files
ls -la /path/to/django_inhealth/media/profile_pictures/

# Check nginx user
ps aux | grep nginx

# Test file permissions as nginx user
sudo -u www-data cat /path/to/django_inhealth/media/profile_pictures/some_image.jpg

# Check nginx error logs
sudo tail -50 /var/log/nginx/error.log

# Check if X-Forwarded-Proto header is being received by Django
# Add this to a Django view temporarily:
# print(request.META.get('HTTP_X_FORWARDED_PROTO'))
```

**Prevention:**
- Always use relative URLs for MEDIA_URL and STATIC_URL
- Ensure proper permissions on media directory before going to production
- Test HTTPS thoroughly before deploying
- Use `SECURE_PROXY_SSL_HEADER` when behind a reverse proxy

### 8. Permission Denied on SSL Certificate

**Error Message:**
```
FATAL: private key file "/etc/ssl/private/ssl-cert-snakeoil.key" has group or world access
```

**Note:** SSL is currently disabled in the development environment to simplify setup. For production deployments, you should enable SSL with proper certificates.

**Development Solution (Current Configuration):**

SSL has been disabled in the development configuration. If you need to verify this:
```bash
grep "^ssl" /etc/postgresql/16/main/postgresql.conf
```

You should see:
```
ssl = off
```

**Production Solution (Re-enabling SSL):**

For production environments, re-enable SSL with proper certificate configuration:

**Option 1: Copy certificates to PostgreSQL data directory**
```bash
sudo cp /etc/ssl/certs/ssl-cert-snakeoil.pem /var/lib/postgresql/16/main/server.crt
sudo cp /etc/ssl/private/ssl-cert-snakeoil.key /var/lib/postgresql/16/main/server.key
sudo chown postgres:postgres /var/lib/postgresql/16/main/server.*
sudo chmod 600 /var/lib/postgresql/16/main/server.key
sudo chmod 644 /var/lib/postgresql/16/main/server.crt
```

Then update `/etc/postgresql/16/main/postgresql.conf`:
```
ssl = on
ssl_cert_file = '/var/lib/postgresql/16/main/server.crt'
ssl_key_file = '/var/lib/postgresql/16/main/server.key'
```

**Option 2: Fix permissions on system certificates**
```bash
sudo chmod 640 /etc/ssl/private/ssl-cert-snakeoil.key
sudo chown root:ssl-cert /etc/ssl/private/ssl-cert-snakeoil.key
sudo usermod -a -G ssl-cert postgres
sudo systemctl restart postgresql
```

**Important:** For production, use proper SSL certificates from a trusted Certificate Authority (CA) rather than self-signed certificates.

After enabling SSL, restart PostgreSQL:
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
