# SSL Certificate Installation Guide - Rocky Linux 9

## Quick Start

This guide will help you install SSL certificates on Rocky Linux 9 for the InHealth EHR application.

---

## Prerequisites

- Root or sudo access to the Rocky Linux 9 server
- SSL certificate files:
  - `certificate.crt` - Your domain certificate
  - `private.key` - Your private key
  - `ca_bundle.crt` (optional) - Certificate chain/bundle

---

## Installation Methods

### Method 1: Copy Certificates from Local Machine (Recommended)

If your certificates are on your local machine at `/home/zia/test2/inhealth-cert/`:

#### Step 1: Copy certificates to the server

From your **local machine**, run:

```bash
# Replace SERVER_IP with your Rocky Linux 9 server IP
SERVER_IP="your.server.ip.address"

scp /home/zia/test2/inhealth-cert/certificate.crt root@$SERVER_IP:/tmp/
scp /home/zia/test2/inhealth-cert/private.key root@$SERVER_IP:/tmp/

# If you have a CA bundle:
scp /home/zia/test2/inhealth-cert/ca_bundle.crt root@$SERVER_IP:/tmp/
```

#### Step 2: Run the installation script on the server

Connect to your Rocky Linux 9 server:

```bash
ssh root@$SERVER_IP
```

Then run:

```bash
cd /home/user/inhealthUSA
chmod +x install_ssl_rocky9.sh
sudo ./install_ssl_rocky9.sh --from-tmp
```

---

### Method 2: Certificates Already on Server

If you've already copied the certificates to `/home/zia/test2/inhealth-cert/` on the server:

```bash
cd /home/user/inhealthUSA
chmod +x install_ssl_rocky9.sh
sudo ./install_ssl_rocky9.sh
```

---

### Method 3: Manual Installation

If you've manually placed certificates in `/etc/ssl/inhealth/`:

```bash
cd /home/user/inhealthUSA
chmod +x install_ssl_rocky9.sh
sudo ./install_ssl_rocky9.sh --skip-copy
```

---

## What the Script Does

The installation script automatically:

1. ✅ **Validates certificate files** - Ensures certificates are valid and match
2. ✅ **Creates SSL directory** - Sets up `/etc/ssl/inhealth/`
3. ✅ **Sets proper permissions** - 644 for certificate, 600 for private key
4. ✅ **Configures SELinux** - Sets correct security contexts for RHEL-based systems
5. ✅ **Creates Nginx configuration** - Sets up HTTPS with modern security
6. ✅ **Configures firewall** - Opens ports 80 and 443 using firewalld
7. ✅ **Tests configuration** - Validates Nginx config before applying
8. ✅ **Restarts Nginx** - Applies the new SSL configuration

---

## After Installation

### Verify HTTPS is Working

```bash
# Test locally
curl -v https://localhost

# Check Nginx status
sudo systemctl status nginx

# View logs
sudo tail -f /var/log/nginx/inhealth_ssl_error.log
```

### Start Django Application

The Nginx configuration expects Django to be running on `127.0.0.1:8000`.

**Option 1: Development Server** (not for production)
```bash
cd /home/user/inhealthUSA/django_inhealth
python manage.py runserver 127.0.0.1:8000
```

**Option 2: Gunicorn** (recommended for production)
```bash
cd /home/user/inhealthUSA/django_inhealth
pip install gunicorn
gunicorn --bind 127.0.0.1:8000 --workers 3 inhealth.wsgi:application
```

**Option 3: Systemd Service** (best for production)
```bash
sudo cp /home/user/inhealthUSA/deployment_configs/inhealth.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable inhealth
sudo systemctl start inhealth
sudo systemctl status inhealth
```

### Test Your Site

1. Update DNS records to point your domain to the server IP
2. Visit your site: `https://yourdomain.com`
3. Test SSL configuration: https://www.ssllabs.com/ssltest/

---

## Troubleshooting

### Issue: Nginx won't start

**Check logs:**
```bash
sudo journalctl -u nginx -n 50
sudo tail -f /var/log/nginx/error.log
```

**Common causes:**
- SELinux blocking Nginx
- Port already in use
- Invalid certificate paths

### Issue: SELinux denials

**Check for denials:**
```bash
sudo ausearch -m avc -ts recent
```

**Allow Nginx network connections:**
```bash
sudo setsebool -P httpd_can_network_connect 1
```

**Fix file contexts:**
```bash
sudo restorecon -Rv /etc/ssl/inhealth
sudo restorecon -Rv /home/user/inhealthUSA/django_inhealth/static
sudo restorecon -Rv /home/user/inhealthUSA/django_inhealth/media
```

### Issue: Firewall blocking connections

**Check firewall status:**
```bash
sudo firewall-cmd --state
sudo firewall-cmd --list-all
```

**Open HTTP/HTTPS:**
```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### Issue: Certificate/Key mismatch

**Verify certificate and key match:**
```bash
openssl x509 -noout -modulus -in /etc/ssl/inhealth/certificate.crt | openssl md5
openssl rsa -noout -modulus -in /etc/ssl/inhealth/private.key | openssl md5
```

The MD5 hashes should match.

### Issue: Django not accessible

**Check if Django is running:**
```bash
ps aux | grep python
```

**Test Django directly:**
```bash
curl http://127.0.0.1:8000
```

**Check Django logs:**
```bash
cd /home/user/inhealthUSA/django_inhealth
python manage.py check --deploy
```

---

## Security Hardening

### Update Django Settings for Production

Edit `/home/user/inhealthUSA/django_inhealth/inhealth/settings.py`:

```python
# HTTPS Settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Security Headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Production Settings
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', 'server-ip']
```

### Restrict Admin Access

Update Nginx configuration to restrict admin panel:

```nginx
# Add to /etc/nginx/conf.d/inhealth_ssl.conf
location /admin/ {
    # Restrict to specific IPs
    allow 203.0.113.0/24;  # Your office IP
    deny all;

    proxy_pass http://127.0.0.1:8000;
    # ... other proxy settings
}
```

---

## Certificate Renewal

### Auto-renewal with Let's Encrypt (if using certbot)

```bash
# Install certbot
sudo dnf install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test renewal
sudo certbot renew --dry-run

# Certbot will auto-renew via systemd timer
sudo systemctl status certbot-renew.timer
```

### Manual Renewal (if using commercial certificate)

1. Obtain new certificate from your CA
2. Copy new certificates to server
3. Run the installation script again:

```bash
cd /home/user/inhealthUSA
sudo ./install_ssl_rocky9.sh --from-tmp
```

---

## Useful Commands

### Nginx Management
```bash
sudo systemctl start nginx        # Start Nginx
sudo systemctl stop nginx         # Stop Nginx
sudo systemctl restart nginx      # Restart Nginx
sudo systemctl reload nginx       # Reload config without downtime
sudo systemctl status nginx       # Check status
sudo nginx -t                     # Test configuration
```

### View Logs
```bash
sudo tail -f /var/log/nginx/inhealth_ssl_access.log
sudo tail -f /var/log/nginx/inhealth_ssl_error.log
sudo journalctl -u nginx -f
```

### SELinux Management
```bash
getenforce                        # Check SELinux mode
sudo setenforce 0                 # Temporarily disable (for testing)
sudo setenforce 1                 # Re-enable
sudo ausearch -m avc -ts recent   # Check recent denials
```

### Firewall Management
```bash
sudo firewall-cmd --state
sudo firewall-cmd --list-all
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=8000/tcp  # If needed
sudo firewall-cmd --reload
```

### Certificate Information
```bash
# View certificate details
openssl x509 -in /etc/ssl/inhealth/certificate.crt -noout -text

# Check expiration date
openssl x509 -in /etc/ssl/inhealth/certificate.crt -noout -dates

# Verify certificate chain
openssl verify -CAfile /etc/ssl/inhealth/ca_bundle.crt /etc/ssl/inhealth/certificate.crt

# Test SSL connection
openssl s_client -connect localhost:443 -servername yourdomain.com
```

---

## File Locations

```
/etc/ssl/inhealth/
├── certificate.crt           # Your SSL certificate
├── private.key              # Your private key (600 permissions)
└── ca_bundle.crt           # Certificate chain (if applicable)

/etc/nginx/conf.d/
└── inhealth_ssl.conf       # Nginx HTTPS configuration

/var/log/nginx/
├── inhealth_ssl_access.log # HTTPS access log
└── inhealth_ssl_error.log  # HTTPS error log

/home/user/inhealthUSA/
├── django_inhealth/        # Django application
│   ├── static/            # Static files (CSS, JS, images)
│   └── media/             # User uploads
└── install_ssl_rocky9.sh  # Installation script
```

---

## Support

For issues or questions:

1. Check the logs (see commands above)
2. Review the security guide: `/home/user/inhealthUSA/SECURITY_IMPLEMENTATION_GUIDE.md`
3. Test your SSL configuration: https://www.ssllabs.com/ssltest/

---

## Additional Resources

- **Nginx Documentation**: https://nginx.org/en/docs/
- **Rocky Linux Documentation**: https://docs.rockylinux.org/
- **SELinux Guide**: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/using_selinux/
- **SSL Labs Test**: https://www.ssllabs.com/ssltest/
- **Mozilla SSL Configuration Generator**: https://ssl-config.mozilla.org/

---

**Installation Script**: `install_ssl_rocky9.sh`
**Last Updated**: 2025-11-16
**Compatible with**: Rocky Linux 9, RHEL 9, AlmaLinux 9, CentOS Stream 9
