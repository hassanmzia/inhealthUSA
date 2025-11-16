# Django HTTPS/SSL Configuration - InHealth EHR

## Overview

Django has been configured to work with SSL/TLS certificates for secure HTTPS communication. This document explains how Django integrates with the SSL certificates installed on Rocky Linux 9.

---

## Important: How SSL Works with Django

**Django does NOT directly use SSL certificates**. Here's how it works:

```
Client (Browser)
    ↓ HTTPS Request (port 443)
Nginx (SSL/TLS Termination)
    ↓ Decrypts HTTPS
    ↓ HTTP Request (localhost:8000)
Django/Gunicorn (Application Server)
    ↓ Processes request
    ↓ HTTP Response
Nginx
    ↓ Encrypts with SSL
Client receives HTTPS Response
```

### What This Means

1. **Nginx** handles SSL/TLS encryption/decryption using the certificates
2. **Django** receives plain HTTP requests from Nginx on localhost:8000
3. **Django** needs to be configured to understand it's behind an HTTPS proxy
4. **Django** generates HTTPS URLs and enforces secure cookies

---

## Django HTTPS Settings Configured

The following settings have been added to `django_inhealth/inhealth/settings.py`:

### 1. HTTPS Redirect

```python
SECURE_SSL_REDIRECT = not DEBUG
```

**Purpose**: In production (DEBUG=False), Django will automatically redirect all HTTP requests to HTTPS.

**Example**: If someone visits `http://yourdomain.com`, Django redirects to `https://yourdomain.com`

### 2. Proxy SSL Header

```python
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

**Purpose**: Tells Django to trust the `X-Forwarded-Proto` header from Nginx to determine if the original request was HTTPS.

**Why needed**: Since Nginx decrypts HTTPS and sends HTTP to Django, Django needs to know the original protocol.

### 3. HTTP Strict Transport Security (HSTS)

```python
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

**Purpose**: Tells browsers to ALWAYS use HTTPS for your site (even if user types http://).

**Duration**: 1 year (31536000 seconds)

**Subdomains**: Also applies to all subdomains

**Preload**: Makes your site eligible for browser HSTS preload lists

### 4. Secure Cookies

```python
SESSION_COOKIE_SECURE = not DEBUG  # HTTPS only
CSRF_COOKIE_SECURE = not DEBUG     # HTTPS only
SESSION_COOKIE_HTTPONLY = True     # No JavaScript access
CSRF_COOKIE_SAMESITE = 'Strict'    # CSRF protection
```

**Purpose**:
- Cookies only sent over HTTPS (prevents theft over HTTP)
- JavaScript cannot access session cookies (XSS protection)
- Cookies not sent in cross-site requests (CSRF protection)

### 5. Content Security

```python
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
```

**Purpose**:
- Prevent MIME type sniffing
- Enable browser XSS protection
- Prevent clickjacking
- Control referrer information leakage

---

## SSL Certificate Locations (Reference)

Django doesn't directly access these files, but Nginx does:

```
/etc/ssl/inhealth/
├── certificate.crt       # SSL certificate
├── private.key          # Private key (600 permissions)
└── ca_bundle.crt       # Certificate chain (if applicable)
```

Nginx configuration:
```
/etc/nginx/conf.d/inhealth_ssl.conf
```

---

## Running Django with HTTPS

### Production (Recommended)

Use Gunicorn behind Nginx:

```bash
cd /home/user/inhealthUSA/django_inhealth
chmod +x production_start.sh
./production_start.sh
```

This will:
1. ✅ Check Django configuration
2. ✅ Collect static files
3. ✅ Run database migrations
4. ✅ Start Gunicorn on localhost:8000
5. ✅ Nginx proxies HTTPS → Gunicorn

**Access your site:**
- `https://yourdomain.com` (after DNS setup)
- `https://your-server-ip`

### Development with HTTPS (Testing)

For testing HTTPS locally:

```bash
cd /home/user/inhealthUSA/django_inhealth
chmod +x run_dev_https.sh
sudo ./run_dev_https.sh  # Requires root to access /etc/ssl/inhealth/
```

This uses Django's development server with SSL:
- Runs on port 8443
- Uses the installed SSL certificates
- **ONLY for testing - NOT for production**

**Access:**
- `https://localhost:8443`

---

## Production Deployment with Systemd

For automatic startup and management:

### 1. Create systemd service

```bash
sudo nano /etc/systemd/system/inhealth.service
```

```ini
[Unit]
Description=InHealth EHR Django Application
After=network.target postgresql.service

[Service]
Type=notify
User=inhealthuser
Group=inhealthuser
WorkingDirectory=/home/user/inhealthUSA/django_inhealth
Environment="DJANGO_DEBUG=False"
Environment="DJANGO_SECRET_KEY=your-secret-key-here"
Environment="DB_NAME=inhealth_db"
Environment="DB_USER=inhealth_user"
Environment="DB_PASSWORD=your-db-password"
Environment="DB_HOST=localhost"
Environment="DB_PORT=5432"
ExecStart=/usr/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    --access-logfile /var/log/inhealth/gunicorn-access.log \
    --error-logfile /var/log/inhealth/gunicorn-error.log \
    inhealth.wsgi:application
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### 2. Enable and start

```bash
# Create user (if needed)
sudo useradd -r -s /bin/false inhealthuser

# Create log directory
sudo mkdir -p /var/log/inhealth
sudo chown inhealthuser:inhealthuser /var/log/inhealth

# Set permissions
sudo chown -R inhealthuser:inhealthuser /home/user/inhealthUSA/django_inhealth

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable inhealth
sudo systemctl start inhealth

# Check status
sudo systemctl status inhealth

# View logs
sudo journalctl -u inhealth -f
```

---

## Environment Variables for Production

Create a `.env` file or use systemd environment variables:

```bash
# Required
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-secret-key-here-minimum-50-characters
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,server-ip

# Database
DB_NAME=inhealth_db
DB_USER=inhealth_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

# Email (for password reset, notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=InHealth EHR <noreply@yourdomain.com>

# Session Security
SESSION_COOKIE_AGE=1800  # 30 minutes
SESSION_INACTIVITY_TIMEOUT=1800
```

**Load environment variables:**

```bash
# In your shell startup or systemd service
export $(cat .env | xargs)
```

---

## Verifying HTTPS Configuration

### 1. Check Django Settings

```bash
cd /home/user/inhealthUSA/django_inhealth
python manage.py shell
```

```python
from django.conf import settings

# Check HTTPS settings
print("SECURE_SSL_REDIRECT:", settings.SECURE_SSL_REDIRECT)
print("SECURE_PROXY_SSL_HEADER:", settings.SECURE_PROXY_SSL_HEADER)
print("SECURE_HSTS_SECONDS:", settings.SECURE_HSTS_SECONDS)
print("SESSION_COOKIE_SECURE:", settings.SESSION_COOKIE_SECURE)
print("CSRF_COOKIE_SECURE:", settings.CSRF_COOKIE_SECURE)
```

### 2. Run Django Deployment Check

```bash
python manage.py check --deploy
```

This will warn you about any security issues.

### 3. Test HTTPS Redirect

```bash
# Should redirect to HTTPS
curl -I http://yourdomain.com

# Should return 301 and Location: https://...
```

### 4. Test SSL/TLS

```bash
# Test SSL locally
curl -v https://localhost

# Test with OpenSSL
openssl s_client -connect localhost:443 -servername yourdomain.com

# Check certificate expiration
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com 2>/dev/null | openssl x509 -noout -dates
```

### 5. Test Security Headers

```bash
curl -I https://yourdomain.com
```

Should see:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
```

### 6. SSL Labs Test

Visit: https://www.ssllabs.com/ssltest/

Enter your domain and get a security grade (aim for A or A+)

---

## Troubleshooting

### Issue: Redirect loop (too many redirects)

**Cause**: `SECURE_SSL_REDIRECT` is True but Nginx isn't setting `X-Forwarded-Proto` header

**Solution**: Check Nginx config has:
```nginx
proxy_set_header X-Forwarded-Proto $scheme;
```

### Issue: Mixed content warnings

**Cause**: Some resources loaded over HTTP instead of HTTPS

**Solution**:
1. Check all static/media URLs use `//` or `https://`
2. Update `STATIC_URL` and `MEDIA_URL` in settings.py
3. Use `{{ request.scheme }}` in templates

### Issue: Session/CSRF cookies not working

**Cause**: Cookie security settings incompatible with setup

**Solution**: Temporarily set in development:
```python
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
```

Then re-enable for production.

### Issue: Cannot access via HTTPS

**Cause**: Firewall blocking port 443

**Solution**:
```bash
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### Issue: SSL certificate errors

**Cause**: Certificate not trusted or expired

**Solution**:
```bash
# Check certificate
openssl x509 -in /etc/ssl/inhealth/certificate.crt -noout -text

# Check expiration
openssl x509 -in /etc/ssl/inhealth/certificate.crt -noout -dates

# Test certificate chain
openssl verify -CAfile /etc/ssl/inhealth/ca_bundle.crt /etc/ssl/inhealth/certificate.crt
```

---

## Security Best Practices

### 1. Production Settings

Always set for production:

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 2. Keep DEBUG = False

Never set `DEBUG = True` in production:
- Exposes sensitive information
- Shows detailed error pages
- Serves static files inefficiently

### 3. Use Environment Variables

Never hardcode secrets in settings.py:
```python
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
```

### 4. Regular Updates

```bash
# Update SSL certificates before expiration
# Update Django and dependencies
pip install --upgrade django
pip install --upgrade -r requirements.txt
```

### 5. Monitor Logs

```bash
# Watch for errors
tail -f /var/log/nginx/inhealth_ssl_error.log
tail -f /home/user/inhealthUSA/django_inhealth/logs/gunicorn-error.log

# Watch for suspicious activity
tail -f /var/log/nginx/inhealth_ssl_access.log | grep -E "40[0-9]|50[0-9]"
```

---

## Summary

Your Django application is now configured to work with SSL/TLS certificates:

✅ **HTTPS enforcement** - All traffic uses HTTPS
✅ **HSTS enabled** - Browsers always use HTTPS
✅ **Secure cookies** - Session/CSRF cookies only over HTTPS
✅ **Security headers** - XSS, clickjacking protection
✅ **Proxy awareness** - Works behind Nginx reverse proxy

**SSL Certificate Flow:**
1. Nginx receives HTTPS on port 443
2. Nginx decrypts using certificates in /etc/ssl/inhealth/
3. Nginx proxies HTTP to Django on localhost:8000
4. Django generates HTTPS URLs and sets secure cookies
5. Nginx encrypts response and sends HTTPS to client

**For Production:**
- Use `./production_start.sh` to start Gunicorn
- Or use systemd service for automatic management
- Nginx handles SSL/TLS
- Django enforces HTTPS policies

**Certificate installed at:**
- `/etc/ssl/inhealth/certificate.crt`
- `/etc/ssl/inhealth/private.key`

**Nginx config:**
- `/etc/nginx/conf.d/inhealth_ssl.conf`

---

## Additional Resources

- Django Security Documentation: https://docs.djangoproject.com/en/stable/topics/security/
- Django Deployment Checklist: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/
- Gunicorn Documentation: https://docs.gunicorn.org/
- SSL Labs Test: https://www.ssllabs.com/ssltest/

---

**Last Updated**: 2025-11-16
**Django Version**: 5.x
**Compatible with**: Rocky Linux 9, RHEL 9, AlmaLinux 9
