# InHealth EHR - Production Deployment Guide

This guide will help you deploy InHealth EHR in production mode with Nginx on port 443 (HTTPS/SSL).

## Overview

The production setup includes:
- **Nginx** running on port 443 with SSL/TLS encryption
- **Django** in production mode (DEBUG=False)
- **Gunicorn** as the WSGI application server
- **SSL certificates** (Let's Encrypt or self-signed)
- **Security headers** for HIPAA compliance
- **Automatic HTTPS redirect** from port 80

## Quick Start

### Option 1: Full Automated Deployment

Run the automated deployment script as root:

```bash
sudo ./deploy_production.sh
```

This will:
1. Install Nginx
2. Set up SSL certificates (Let's Encrypt or self-signed)
3. Configure Nginx on port 443
4. Create Gunicorn systemd service
5. Set up all necessary directories and permissions

### Option 2: Manual Step-by-Step Deployment

#### Step 1: Install Nginx

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx
```

**Rocky Linux/RHEL:**
```bash
sudo dnf install -y nginx certbot python3-certbot-nginx
```

#### Step 2: Configure Production Environment

Copy the production environment template:
```bash
cp .env.production django_inhealth/.env
```

Edit `django_inhealth/.env` and update:
- `DOMAIN_NAME`: Your actual domain (e.g., example.com)
- `SECRET_KEY`: Generate with: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
- `DB_PASSWORD`: Your database password
- `EMAIL_*`: Your email settings
- `RECAPTCHA_*`: Your reCAPTCHA keys

#### Step 3: Set Up SSL Certificate

**Option A: Let's Encrypt (Recommended for Production)**
```bash
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com
```

**Option B: Self-Signed Certificate (For Testing)**
```bash
sudo mkdir -p /etc/ssl/inhealth
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/inhealth/private.key \
    -out /etc/ssl/inhealth/certificate.crt \
    -subj "/C=US/ST=State/L=City/O=InHealth/OU=IT/CN=yourdomain.com"
sudo chmod 600 /etc/ssl/inhealth/private.key
sudo chmod 644 /etc/ssl/inhealth/certificate.crt
```

#### Step 4: Configure Nginx

Copy the SSL configuration template:
```bash
sudo cp deployment_configs/nginx_ssl.conf /etc/nginx/sites-available/inhealth
```

Edit the file and update:
- `server_name`: Your domain
- `ssl_certificate`: Path to your SSL certificate
- `ssl_certificate_key`: Path to your SSL private key

Create symlink and test:
```bash
sudo ln -sf /etc/nginx/sites-available/inhealth /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx
```

#### Step 5: Set Up Gunicorn Service

Copy the systemd service file:
```bash
sudo cp deployment_configs/inhealth.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable inhealth
```

#### Step 6: Prepare Django Application

Activate virtual environment and install dependencies:
```bash
cd /home/user/inhealthUSA
source venv/bin/activate
pip install gunicorn psycopg2-binary
```

Collect static files:
```bash
cd django_inhealth
python manage.py collectstatic --noinput
python manage.py migrate
```

Create superuser (if needed):
```bash
python manage.py createsuperuser
```

Set permissions:
```bash
sudo chown -R www-data:www-data /home/user/inhealthUSA/django_inhealth/staticfiles
sudo chown -R www-data:www-data /home/user/inhealthUSA/django_inhealth/media
sudo mkdir -p /var/log/inhealth
sudo chown -R www-data:www-data /var/log/inhealth
```

#### Step 7: Start Services

Start Gunicorn:
```bash
sudo systemctl start inhealth
sudo systemctl status inhealth
```

Verify Nginx is running:
```bash
sudo systemctl status nginx
```

## Verification

### Check Services

```bash
# Check Gunicorn is running
sudo systemctl status inhealth

# Check Nginx is running
sudo systemctl status nginx

# Check port 443 is listening
sudo ss -tlnp | grep :443

# Check port 80 is listening
sudo ss -tlnp | grep :80
```

### Test SSL Certificate

```bash
# Test SSL certificate
curl -I https://yourdomain.com

# Check SSL rating (if publicly accessible)
# Visit: https://www.ssllabs.com/ssltest/
```

### View Logs

```bash
# Django/Gunicorn logs
sudo journalctl -u inhealth -f

# Nginx access logs
sudo tail -f /var/log/nginx/inhealth_access.log

# Nginx error logs
sudo tail -f /var/log/nginx/inhealth_error.log
```

## Security Checklist

- [ ] DEBUG is set to False
- [ ] SECRET_KEY is changed from default
- [ ] ALLOWED_HOSTS is configured with your domain
- [ ] SSL certificate is valid and properly configured
- [ ] Port 443 (HTTPS) is accessible
- [ ] Port 80 redirects to 443
- [ ] Static and media files are served correctly
- [ ] Database credentials are secure
- [ ] File permissions are set correctly (www-data:www-data)
- [ ] Firewall allows ports 80 and 443
- [ ] Session timeout is configured (default: 30 minutes)
- [ ] Failed login protection is enabled (Django Axes)

## Firewall Configuration

### Ubuntu/Debian (UFW)
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Rocky Linux/RHEL (firewalld)
```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## SSL Certificate Auto-Renewal

If using Let's Encrypt, the certificate will auto-renew. Test renewal:

```bash
sudo certbot renew --dry-run
```

Auto-renewal is configured via systemd timer:
```bash
sudo systemctl status certbot.timer
```

## Troubleshooting

### Nginx won't start
```bash
# Check configuration
sudo nginx -t

# View error logs
sudo tail -f /var/log/nginx/error.log
```

### Gunicorn won't start
```bash
# Check service status
sudo systemctl status inhealth

# View logs
sudo journalctl -u inhealth -n 50

# Check if port 8000 is in use
sudo ss -tlnp | grep :8000
```

### 502 Bad Gateway
- Check if Gunicorn is running: `sudo systemctl status inhealth`
- Check if Gunicorn is listening on port 8000: `sudo ss -tlnp | grep :8000`
- Check Gunicorn logs: `sudo journalctl -u inhealth -f`

### Static files not loading
```bash
# Collect static files
cd /home/user/inhealthUSA/django_inhealth
source ../venv/bin/activate
python manage.py collectstatic --noinput

# Check permissions
sudo chown -R www-data:www-data staticfiles/
sudo chmod -R 755 staticfiles/
```

### SSL certificate errors
```bash
# Check certificate expiry
sudo certbot certificates

# Renew manually
sudo certbot renew

# Check SSL configuration
sudo nginx -t
```

## Performance Tuning

### Gunicorn Workers

Edit `/etc/systemd/system/inhealth.service` and adjust workers:
```ini
--workers 4  # Recommended: (2 × CPU cores) + 1
```

Restart after changes:
```bash
sudo systemctl daemon-reload
sudo systemctl restart inhealth
```

### Nginx Caching

Add to Nginx configuration for better performance:
```nginx
# Browser caching
location /static/ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

## Maintenance

### Update Application

```bash
cd /home/user/inhealthUSA
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
cd django_inhealth
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart inhealth
```

### Backup Database

```bash
# PostgreSQL backup
sudo -u postgres pg_dump inhealth_db > backup_$(date +%Y%m%d).sql

# Restore
sudo -u postgres psql inhealth_db < backup_20241116.sql
```

### View Running Processes

```bash
# Gunicorn workers
ps aux | grep gunicorn

# Nginx workers
ps aux | grep nginx
```

## Quick Commands Reference

```bash
# Start services
sudo systemctl start inhealth
sudo systemctl start nginx

# Stop services
sudo systemctl stop inhealth
sudo systemctl stop nginx

# Restart services
sudo systemctl restart inhealth
sudo systemctl restart nginx

# Enable on boot
sudo systemctl enable inhealth
sudo systemctl enable nginx

# View logs
sudo journalctl -u inhealth -f
sudo tail -f /var/log/nginx/inhealth_error.log

# Test configurations
sudo nginx -t
python manage.py check --deploy

# Switch to production mode
./switch_to_production.sh
```

## Support

For issues or questions:
1. Check the logs first
2. Review this documentation
3. Check Django deployment checklist: `python manage.py check --deploy`
4. Review Nginx error logs: `sudo tail -f /var/log/nginx/error.log`

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Nginx SSL Configuration](https://nginx.org/en/docs/http/configuring_https_servers.html)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Gunicorn Deployment](https://docs.gunicorn.org/en/stable/deploy.html)
