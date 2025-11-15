# SSL Certificate Setup Guide for InHealth EHR

This guide covers multiple approaches to setting up SSL/TLS certificates for your Django application.

## Table of Contents
1. [Production Setup with Let's Encrypt (Recommended)](#production-setup-with-lets-encrypt)
2. [Using Nginx as Reverse Proxy with SSL](#nginx-reverse-proxy-setup)
3. [Development Setup with Self-Signed Certificates](#development-self-signed-certificates)
4. [Django HTTPS Configuration](#django-https-configuration)
5. [AWS/Cloud Provider SSL](#cloud-provider-ssl)

---

## Production Setup with Let's Encrypt (Recommended)

Let's Encrypt provides free, automated SSL certificates that auto-renew.

### Prerequisites
- A registered domain name pointing to your server
- Root or sudo access to your server
- Nginx or Apache web server installed
- Ports 80 and 443 open in your firewall

### Step 1: Install Certbot

**For Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

**For CentOS/RHEL:**
```bash
sudo yum install certbot python3-certbot-nginx
```

**For macOS:**
```bash
brew install certbot
```

### Step 2: Obtain SSL Certificate

**For Nginx (Automatic Configuration):**
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**For Apache:**
```bash
sudo certbot --apache -d yourdomain.com -d www.yourdomain.com
```

**Standalone (if web server is stopped):**
```bash
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

### Step 3: Verify Auto-Renewal

Certbot automatically sets up renewal. Test it with:
```bash
sudo certbot renew --dry-run
```

### Step 4: Certificate Locations

After successful installation, certificates are stored at:
- Certificate: `/etc/letsencrypt/live/yourdomain.com/fullchain.pem`
- Private Key: `/etc/letsencrypt/live/yourdomain.com/privkey.pem`

---

## Nginx Reverse Proxy Setup

### Step 1: Install Nginx

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Step 2: Create Nginx Configuration

Create a new configuration file:
```bash
sudo nano /etc/nginx/sites-available/inhealth
```

Add the following configuration:

```nginx
# HTTP - Redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect all HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS - Main configuration
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Certificate files (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL Configuration - Strong security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Max upload size (adjust as needed)
    client_max_body_size 100M;

    # Django static files
    location /static/ {
        alias /home/user/inhealthUSA/django_inhealth/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Django media files
    location /media/ {
        alias /home/user/inhealthUSA/django_inhealth/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Proxy to Django application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Logging
    access_log /var/log/nginx/inhealth_access.log;
    error_log /var/log/nginx/inhealth_error.log;
}
```

### Step 3: Enable the Configuration

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/inhealth /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Step 4: Configure Firewall

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable

# CentOS/RHEL (Firewalld)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

---

## Development Self-Signed Certificates

For local development and testing only (not for production).

### Step 1: Generate Self-Signed Certificate

```bash
# Create directory for certificates
mkdir -p /home/user/inhealthUSA/ssl

# Generate certificate and key
cd /home/user/inhealthUSA/ssl
openssl req -x509 -newkey rsa:4096 -nodes \
    -keyout key.pem \
    -out cert.pem \
    -days 365 \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

### Step 2: Run Django with SSL

```bash
# Install django-extensions
pip install django-extensions pyOpenSSL

# Add to INSTALLED_APPS in settings.py
# INSTALLED_APPS = [
#     ...
#     'django_extensions',
# ]

# Run server with SSL
python manage.py runserver_plus --cert-file ssl/cert.pem --key-file ssl/key.pem
```

Access your site at: `https://localhost:8000`

**Note:** Browsers will show a security warning for self-signed certificates. This is normal for development.

---

## Django HTTPS Configuration

Update your Django settings for HTTPS:

### Add to settings.py

```python
# HTTPS Settings
if not DEBUG:
    # Force HTTPS
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HSTS Settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Other security settings
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

    # Trust proxy headers
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allowed hosts - Update with your domain
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', '172.168.1.125']
```

### Update CORS Settings (if using CORS)

```python
# If using django-cors-headers
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

---

## Cloud Provider SSL

### AWS (Using Application Load Balancer)

1. **Request Certificate in AWS Certificate Manager (ACM):**
   - Go to AWS Certificate Manager
   - Request a public certificate
   - Add your domain names
   - Validate via DNS or Email

2. **Attach to Load Balancer:**
   - Create/Configure Application Load Balancer
   - Add HTTPS listener on port 443
   - Select your ACM certificate
   - Forward traffic to your Django target group

3. **Django Settings:**
```python
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### DigitalOcean

1. **Add Domain to DigitalOcean:**
   - Go to Networking → Domains
   - Add your domain

2. **Create Load Balancer:**
   - Enable SSL/TLS
   - Let's Encrypt certificate auto-generates
   - Or upload custom certificate

### Heroku

```bash
# Heroku automatically provides SSL for custom domains
heroku certs:auto:enable
```

---

## Running Django in Production

### Option 1: Using Gunicorn (Recommended)

```bash
# Install Gunicorn
pip install gunicorn

# Run Gunicorn
gunicorn --bind 127.0.0.1:8000 \
         --workers 4 \
         --timeout 120 \
         inhealth.wsgi:application
```

### Option 2: Create Systemd Service

Create `/etc/systemd/system/inhealth.service`:

```ini
[Unit]
Description=InHealth Django Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
RuntimeDirectory=gunicorn
WorkingDirectory=/home/user/inhealthUSA/django_inhealth
Environment="PATH=/home/user/inhealthUSA/venv/bin"
ExecStart=/home/user/inhealthUSA/venv/bin/gunicorn \
          --workers 4 \
          --bind 127.0.0.1:8000 \
          --timeout 120 \
          --access-logfile /var/log/inhealth/access.log \
          --error-logfile /var/log/inhealth/error.log \
          inhealth.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable inhealth
sudo systemctl start inhealth
sudo systemctl status inhealth
```

---

## Testing SSL Configuration

### 1. Test SSL Certificate

```bash
# Check certificate details
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Check certificate expiry
echo | openssl s_client -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

### 2. Online SSL Tests

- **SSL Labs:** https://www.ssllabs.com/ssltest/
- **Security Headers:** https://securityheaders.com/

### 3. Test HTTPS Redirect

```bash
curl -I http://yourdomain.com
# Should return 301 redirect to https://
```

---

## Troubleshooting

### Certificate Not Found Error

```bash
# Check if certificate exists
sudo ls -la /etc/letsencrypt/live/yourdomain.com/

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Permission Denied Errors

```bash
# Give Nginx access to certificates
sudo chmod 755 /etc/letsencrypt/live/
sudo chmod 755 /etc/letsencrypt/archive/
```

### Django Still Serving HTTP

```python
# Verify settings.py has:
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### Renewal Failed

```bash
# Check renewal timer
sudo systemctl status certbot.timer

# Manually renew
sudo certbot renew --force-renewal
```

---

## Security Best Practices

1. **Keep Software Updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Enable Firewall:**
   ```bash
   sudo ufw enable
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

3. **Regular Backups:**
   - Database backups
   - Certificate backups
   - Application backups

4. **Monitor Certificate Expiry:**
   - Let's Encrypt certs expire in 90 days
   - Auto-renewal should handle this
   - Set up monitoring/alerts

5. **Use Strong SSL Ciphers:**
   - TLS 1.2 and 1.3 only
   - Disable weak ciphers
   - Enable HSTS

---

## Quick Start Checklist

- [ ] Domain name pointing to your server
- [ ] Nginx installed
- [ ] Certbot installed
- [ ] SSL certificate obtained
- [ ] Nginx configured with SSL
- [ ] Django settings updated for HTTPS
- [ ] Firewall configured (ports 80, 443)
- [ ] Gunicorn or production server running
- [ ] Static files collected
- [ ] Test SSL configuration
- [ ] Verify auto-renewal works

---

## Next Steps

After SSL is configured:
1. Test all application functionality over HTTPS
2. Update any hardcoded HTTP URLs to HTTPS
3. Configure monitoring and alerting
4. Set up automated backups
5. Consider adding a CDN for static files

## Support

For HIPAA compliance (healthcare applications):
- Ensure end-to-end encryption
- Use TLS 1.2 or higher only
- Enable perfect forward secrecy
- Maintain audit logs of SSL/TLS connections
- Regular security audits

---

**Need Help?** Check the official documentation:
- Let's Encrypt: https://letsencrypt.org/docs/
- Nginx: https://nginx.org/en/docs/
- Django Security: https://docs.djangoproject.com/en/stable/topics/security/
