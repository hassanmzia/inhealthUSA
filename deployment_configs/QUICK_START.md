# SSL Setup Quick Start Guide

## Prerequisites Checklist

- [ ] Domain name registered and pointing to your server
- [ ] Server has public IP address
- [ ] Ports 80 and 443 are open in firewall
- [ ] Django application working on HTTP
- [ ] Root/sudo access to server

## Option 1: Automated Setup (Recommended)

### Step 1: Edit Configuration
Edit the setup script with your domain:
```bash
nano /home/user/inhealthUSA/deployment_configs/setup_ssl.sh
```

Change these lines:
```bash
DOMAIN="yourdomain.com"          # Your domain
WWW_DOMAIN="www.yourdomain.com"  # Your www subdomain
EMAIL="admin@yourdomain.com"     # Your email for SSL notifications
```

### Step 2: Run Setup Script
```bash
cd /home/user/inhealthUSA/deployment_configs
sudo bash setup_ssl.sh
```

That's it! The script will:
- Install Nginx and Certbot
- Obtain SSL certificate
- Configure Nginx with SSL
- Set up Gunicorn systemd service
- Configure firewall

## Option 2: Manual Setup

### Step 1: Install Dependencies
```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx
```

### Step 2: Install Gunicorn
```bash
source /home/user/inhealthUSA/venv/bin/activate
pip install gunicorn
deactivate
```

### Step 3: Collect Static Files
```bash
cd /home/user/inhealthUSA/django_inhealth
source /home/user/inhealthUSA/venv/bin/activate
python manage.py collectstatic --noinput
deactivate
```

### Step 4: Configure Nginx

**Edit the template:**
```bash
nano /home/user/inhealthUSA/deployment_configs/nginx_ssl.conf
```

**Replace these placeholders:**
- `yourdomain.com` → Your actual domain
- `www.yourdomain.com` → Your www subdomain

**Copy to Nginx:**
```bash
sudo cp /home/user/inhealthUSA/deployment_configs/nginx_ssl.conf /etc/nginx/sites-available/inhealth
sudo ln -s /etc/nginx/sites-available/inhealth /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default  # Remove default site
sudo nginx -t  # Test configuration
```

### Step 5: Obtain SSL Certificate
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Follow the prompts:
- Enter your email address
- Agree to terms of service
- Choose whether to redirect HTTP to HTTPS (choose yes/2)

### Step 6: Set Up Systemd Service
```bash
sudo cp /home/user/inhealthUSA/deployment_configs/inhealth.service /etc/systemd/system/
sudo mkdir -p /var/log/inhealth
sudo chown www-data:www-data /var/log/inhealth
sudo systemctl daemon-reload
sudo systemctl enable inhealth
sudo systemctl start inhealth
```

### Step 7: Update Django Settings

Add to `django_inhealth/inhealth/settings.py`:
```python
# Add your domain to ALLOWED_HOSTS
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# HTTPS Settings (add these)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

See full settings in: `deployment_configs/django_https_settings.py`

### Step 8: Restart Services
```bash
sudo systemctl restart inhealth
sudo systemctl reload nginx
```

## Testing Your Setup

### 1. Check Services Status
```bash
sudo systemctl status nginx
sudo systemctl status inhealth
```

### 2. Test SSL Certificate
```bash
sudo certbot certificates
```

### 3. Visit Your Site
```
https://yourdomain.com
```

### 4. Check SSL Grade
Visit: https://www.ssllabs.com/ssltest/analyze.html?d=yourdomain.com

## Common Commands

### View Logs
```bash
# Application logs
sudo tail -f /var/log/inhealth/error.log

# Nginx error logs
sudo tail -f /var/log/nginx/inhealth_error.log

# Nginx access logs
sudo tail -f /var/log/nginx/inhealth_access.log

# Systemd service logs
sudo journalctl -u inhealth -f
```

### Restart Services
```bash
# Restart Django application
sudo systemctl restart inhealth

# Reload Nginx (without dropping connections)
sudo systemctl reload nginx

# Restart Nginx
sudo systemctl restart nginx
```

### SSL Certificate Management
```bash
# Check certificate status
sudo certbot certificates

# Renew certificates manually
sudo certbot renew

# Test renewal (dry run)
sudo certbot renew --dry-run

# Revoke certificate
sudo certbot revoke --cert-path /etc/letsencrypt/live/yourdomain.com/cert.pem
```

### Update Django Code
```bash
cd /home/user/inhealthUSA/django_inhealth
source /home/user/inhealthUSA/venv/bin/activate

# Pull latest code
git pull

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart application
sudo systemctl restart inhealth
```

## Troubleshooting

### Issue: Certificate Not Found
```bash
# Check if certificate was created
sudo ls -la /etc/letsencrypt/live/yourdomain.com/

# Check Nginx error log
sudo tail -50 /var/log/nginx/error.log
```

### Issue: 502 Bad Gateway
```bash
# Check if Gunicorn is running
sudo systemctl status inhealth

# Check Gunicorn logs
sudo tail -50 /var/log/inhealth/error.log

# Restart Gunicorn
sudo systemctl restart inhealth
```

### Issue: Static Files Not Loading
```bash
# Collect static files again
cd /home/user/inhealthUSA/django_inhealth
source /home/user/inhealthUSA/venv/bin/activate
python manage.py collectstatic --noinput

# Check permissions
sudo chown -R www-data:www-data /home/user/inhealthUSA/django_inhealth/staticfiles/
```

### Issue: Database Connection Error
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check database settings in settings.py
# Verify DATABASES configuration
```

### Issue: Permission Denied
```bash
# Fix ownership
sudo chown -R www-data:www-data /home/user/inhealthUSA/django_inhealth

# Fix log directory
sudo mkdir -p /var/log/inhealth
sudo chown www-data:www-data /var/log/inhealth
```

## Security Checklist

After setup, verify these security settings:

```bash
# Run Django security check
cd /home/user/inhealthUSA/django_inhealth
source /home/user/inhealthUSA/venv/bin/activate
python manage.py check --deploy
```

- [ ] SSL certificate installed and valid
- [ ] HTTP redirects to HTTPS
- [ ] HSTS header enabled
- [ ] Security headers configured
- [ ] Firewall configured (only ports 22, 80, 443 open)
- [ ] Database uses strong password
- [ ] Django SECRET_KEY is secret and random
- [ ] DEBUG = False in production
- [ ] ALLOWED_HOSTS properly configured
- [ ] Static files served with cache headers
- [ ] Regular backups configured

## Monitoring

### Set Up Monitoring Script
Create a simple monitoring script:

```bash
cat > /home/user/check_services.sh << 'EOF'
#!/bin/bash
echo "=== Service Status ==="
systemctl is-active nginx && echo "Nginx: ✓" || echo "Nginx: ✗"
systemctl is-active inhealth && echo "InHealth: ✓" || echo "InHealth: ✗"
systemctl is-active postgresql && echo "PostgreSQL: ✓" || echo "PostgreSQL: ✗"

echo -e "\n=== SSL Certificate ==="
sudo certbot certificates | grep "Expiry Date"

echo -e "\n=== Disk Usage ==="
df -h / | tail -1

echo -e "\n=== Memory Usage ==="
free -h | grep Mem
EOF

chmod +x /home/user/check_services.sh
```

Run with: `bash /home/user/check_services.sh`

## Auto-Renewal Verification

Let's Encrypt certificates expire every 90 days but auto-renew.

### Check Renewal Timer
```bash
sudo systemctl status certbot.timer
```

### Test Renewal
```bash
sudo certbot renew --dry-run
```

### Manual Renewal
```bash
sudo certbot renew
sudo systemctl reload nginx
```

## Next Steps

1. **Set up monitoring**: Consider using tools like:
   - UptimeRobot (uptime monitoring)
   - Sentry (error tracking)
   - New Relic or DataDog (performance monitoring)

2. **Enable backups**:
   - Database backups (pg_dump)
   - Media files backup
   - Configuration backup

3. **Configure email**:
   - Set up SMTP for password resets
   - Configure error notification emails

4. **Performance optimization**:
   - Enable caching (Redis)
   - Configure CDN for static files
   - Database query optimization

## Support Resources

- **Let's Encrypt**: https://letsencrypt.org/docs/
- **Nginx Docs**: https://nginx.org/en/docs/
- **Django Deployment**: https://docs.djangoproject.com/en/stable/howto/deployment/
- **Gunicorn**: https://docs.gunicorn.org/

## Need Help?

Check the detailed guide: `/home/user/inhealthUSA/SSL_SETUP_GUIDE.md`
