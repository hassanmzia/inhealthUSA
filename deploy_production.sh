#!/bin/bash
# InHealth EHR - Production Deployment Script with Nginx SSL on Port 443
# This script sets up nginx with SSL and configures Django for production mode

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}InHealth EHR - Production Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
    exit 1
fi

# Prompt for domain name
read -p "Enter your domain name (e.g., example.com): " DOMAIN_NAME
if [ -z "$DOMAIN_NAME" ]; then
    echo -e "${RED}Error: Domain name is required${NC}"
    exit 1
fi

read -p "Enter your email for SSL certificate (for Let's Encrypt): " SSL_EMAIL
if [ -z "$SSL_EMAIL" ]; then
    echo -e "${YELLOW}Warning: Email not provided, will use self-signed certificate${NC}"
    USE_SELFSIGNED=true
else
    USE_SELFSIGNED=false
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo -e "${RED}Cannot detect OS${NC}"
    exit 1
fi

echo -e "${GREEN}Detected OS: $OS${NC}"

# Step 1: Install Nginx
echo -e "\n${GREEN}Step 1: Installing Nginx...${NC}"
if [ "$OS" == "ubuntu" ] || [ "$OS" == "debian" ]; then
    apt-get update
    apt-get install -y nginx certbot python3-certbot-nginx
elif [ "$OS" == "rocky" ] || [ "$OS" == "rhel" ] || [ "$OS" == "centos" ]; then
    dnf install -y nginx certbot python3-certbot-nginx
    dnf install -y python3-certbot-dns-cloudflare || true
else
    echo -e "${RED}Unsupported OS: $OS${NC}"
    exit 1
fi

# Step 2: Create necessary directories
echo -e "\n${GREEN}Step 2: Creating directories...${NC}"
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled
mkdir -p /var/log/inhealth
mkdir -p /home/user/inhealthUSA/django_inhealth/staticfiles
mkdir -p /home/user/inhealthUSA/django_inhealth/media
mkdir -p /home/user/inhealthUSA/django_inhealth/logs

# Set permissions
chown -R www-data:www-data /var/log/inhealth
chown -R www-data:www-data /home/user/inhealthUSA/django_inhealth/staticfiles
chown -R www-data:www-data /home/user/inhealthUSA/django_inhealth/media
chmod -R 755 /home/user/inhealthUSA/django_inhealth/staticfiles
chmod -R 755 /home/user/inhealthUSA/django_inhealth/media

# Step 3: Create Nginx configuration
echo -e "\n${GREEN}Step 3: Creating Nginx configuration...${NC}"

# First, create HTTP-only config for Let's Encrypt verification
cat > /etc/nginx/sites-available/inhealth << EOF
# InHealth EHR - Initial HTTP Configuration
# This will be updated with HTTPS after SSL certificate is obtained

server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN_NAME} www.${DOMAIN_NAME};

    # Let's Encrypt challenge location
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Temporary proxy to Django for initial setup
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$http_host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Static files
    location /static/ {
        alias /home/user/inhealthUSA/django_inhealth/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /home/user/inhealthUSA/django_inhealth/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/inhealth /etc/nginx/sites-enabled/

# Test nginx configuration
nginx -t

# Start nginx
systemctl enable nginx
systemctl restart nginx

# Step 4: Set up SSL Certificate
echo -e "\n${GREEN}Step 4: Setting up SSL certificate...${NC}"

if [ "$USE_SELFSIGNED" = true ]; then
    echo -e "${YELLOW}Creating self-signed SSL certificate...${NC}"

    # Create SSL directory
    mkdir -p /etc/ssl/inhealth

    # Generate self-signed certificate
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/ssl/inhealth/private.key \
        -out /etc/ssl/inhealth/certificate.crt \
        -subj "/C=US/ST=State/L=City/O=InHealth/OU=IT/CN=${DOMAIN_NAME}"

    # Set permissions
    chmod 600 /etc/ssl/inhealth/private.key
    chmod 644 /etc/ssl/inhealth/certificate.crt

    SSL_CERT_PATH="/etc/ssl/inhealth/certificate.crt"
    SSL_KEY_PATH="/etc/ssl/inhealth/private.key"
    SSL_CHAIN_PATH="/etc/ssl/inhealth/certificate.crt"

    echo -e "${GREEN}Self-signed certificate created${NC}"
else
    echo -e "${YELLOW}Obtaining Let's Encrypt SSL certificate...${NC}"

    # Stop nginx temporarily for standalone mode
    systemctl stop nginx

    # Get certificate using certbot standalone
    certbot certonly --standalone \
        --agree-tos \
        --email "${SSL_EMAIL}" \
        --non-interactive \
        -d "${DOMAIN_NAME}" \
        -d "www.${DOMAIN_NAME}" || {
            echo -e "${YELLOW}Let's Encrypt failed, falling back to self-signed certificate${NC}"
            USE_SELFSIGNED=true

            # Create self-signed as fallback
            mkdir -p /etc/ssl/inhealth
            openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                -keyout /etc/ssl/inhealth/private.key \
                -out /etc/ssl/inhealth/certificate.crt \
                -subj "/C=US/ST=State/L=City/O=InHealth/OU=IT/CN=${DOMAIN_NAME}"
            chmod 600 /etc/ssl/inhealth/private.key
            chmod 644 /etc/ssl/inhealth/certificate.crt
            SSL_CERT_PATH="/etc/ssl/inhealth/certificate.crt"
            SSL_KEY_PATH="/etc/ssl/inhealth/private.key"
            SSL_CHAIN_PATH="/etc/ssl/inhealth/certificate.crt"
        }

    if [ "$USE_SELFSIGNED" = false ]; then
        SSL_CERT_PATH="/etc/letsencrypt/live/${DOMAIN_NAME}/fullchain.pem"
        SSL_KEY_PATH="/etc/letsencrypt/live/${DOMAIN_NAME}/privkey.pem"
        SSL_CHAIN_PATH="/etc/letsencrypt/live/${DOMAIN_NAME}/chain.pem"

        # Set up auto-renewal
        systemctl enable certbot.timer || true
        systemctl start certbot.timer || true

        echo -e "${GREEN}Let's Encrypt certificate obtained${NC}"
    fi
fi

# Generate DH parameters for stronger security
echo -e "${YELLOW}Generating DH parameters (this may take a few minutes)...${NC}"
if [ ! -f /etc/nginx/dhparam.pem ]; then
    openssl dhparam -out /etc/nginx/dhparam.pem 2048
fi

# Step 5: Create HTTPS Nginx configuration
echo -e "\n${GREEN}Step 5: Creating HTTPS Nginx configuration...${NC}"

cat > /etc/nginx/sites-available/inhealth << EOF
# InHealth EHR - Production Nginx Configuration with SSL on Port 443

# HTTP - Redirect all traffic to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN_NAME} www.${DOMAIN_NAME};

    # Let's Encrypt challenge location
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirect all other HTTP requests to HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS - Main application server on Port 443
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${DOMAIN_NAME} www.${DOMAIN_NAME};

    # SSL Certificate Configuration
    ssl_certificate ${SSL_CERT_PATH};
    ssl_certificate_key ${SSL_KEY_PATH};
    ssl_trusted_certificate ${SSL_CHAIN_PATH};

    # SSL Configuration - Modern, Secure Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';

    # SSL Session Optimization
    ssl_session_cache shared:SSL:50m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;

    # DH parameters
    ssl_dhparam /etc/nginx/dhparam.pem;

    # Security Headers - HIPAA Compliance
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

    # Max upload size
    client_max_body_size 100M;
    client_body_timeout 120s;

    # Buffer sizes
    client_body_buffer_size 128k;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 16k;

    # Django Static Files
    location /static/ {
        alias /home/user/inhealthUSA/django_inhealth/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Django Media Files
    location /media/ {
        alias /home/user/inhealthUSA/django_inhealth/media/;
        expires 7d;
        add_header Cache-Control "public";

        # Security: Prevent execution of uploaded scripts
        location ~* \.(php|py|pl|sh|cgi|exe)$ {
            deny all;
        }
    }

    # Favicon
    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }

    # Robots.txt
    location = /robots.txt {
        access_log off;
        log_not_found off;
    }

    # Main Django Application Proxy
    location / {
        # Proxy to Gunicorn on port 8000
        proxy_pass http://127.0.0.1:8000;

        # Proxy headers
        proxy_set_header Host \$http_host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$server_name;

        # Proxy settings
        proxy_redirect off;
        proxy_buffering off;
        proxy_connect_timeout 90;
        proxy_send_timeout 90;
        proxy_read_timeout 90;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check endpoint
    location /health/ {
        access_log off;
        proxy_pass http://127.0.0.1:8000/health/;
        proxy_set_header Host \$http_host;
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Logging
    access_log /var/log/nginx/inhealth_access.log;
    error_log /var/log/nginx/inhealth_error.log warn;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/rss+xml font/truetype font/opentype application/vnd.ms-fontobject image/svg+xml;
    gzip_disable "MSIE [1-6]\.";
}
EOF

# Test nginx configuration
nginx -t

# Restart nginx
systemctl restart nginx

# Step 6: Update Django settings for production
echo -e "\n${GREEN}Step 6: Updating Django settings for production...${NC}"

# Create production settings file
cat > /home/user/inhealthUSA/django_inhealth/inhealth/production_settings.py << 'EOFPYTHON'
# Production settings overrides
import os
from .settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Update allowed hosts
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',') if os.environ.get('ALLOWED_HOSTS') else ['*']

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static and media files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
EOFPYTHON

# Step 7: Install Gunicorn and create systemd service
echo -e "\n${GREEN}Step 7: Setting up Gunicorn service...${NC}"

# Install gunicorn in virtual environment
cd /home/user/inhealthUSA
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install gunicorn
    deactivate
else
    echo -e "${YELLOW}Warning: Virtual environment not found. Please install gunicorn manually.${NC}"
fi

# Copy systemd service file
cp /home/user/inhealthUSA/deployment_configs/inhealth.service /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable and start the service
systemctl enable inhealth.service

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Update ${GREEN}/home/user/inhealthUSA/.env.production${NC} with your actual values"
echo -e "2. Copy to .env: ${GREEN}cp .env.production django_inhealth/.env${NC}"
echo -e "3. Collect static files: ${GREEN}cd django_inhealth && python manage.py collectstatic --noinput${NC}"
echo -e "4. Run migrations: ${GREEN}python manage.py migrate${NC}"
echo -e "5. Start the service: ${GREEN}sudo systemctl start inhealth${NC}"
echo -e "6. Check service status: ${GREEN}sudo systemctl status inhealth${NC}"
echo ""
echo -e "${YELLOW}SSL Certificate:${NC}"
if [ "$USE_SELFSIGNED" = true ]; then
    echo -e "  Self-signed certificate created at: ${GREEN}/etc/ssl/inhealth/${NC}"
    echo -e "  ${RED}WARNING: Browsers will show security warnings for self-signed certificates${NC}"
    echo -e "  For production, use Let's Encrypt by providing an email address"
else
    echo -e "  Let's Encrypt certificate obtained for: ${GREEN}${DOMAIN_NAME}${NC}"
    echo -e "  Auto-renewal is configured"
fi
echo ""
echo -e "${YELLOW}Nginx Configuration:${NC}"
echo -e "  HTTP (port 80): Redirects to HTTPS"
echo -e "  HTTPS (port 443): ${GREEN}Active with SSL${NC}"
echo -e "  Config file: ${GREEN}/etc/nginx/sites-available/inhealth${NC}"
echo ""
echo -e "${YELLOW}Access your application at:${NC}"
echo -e "  ${GREEN}https://${DOMAIN_NAME}${NC}"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo -e "  Restart nginx: ${GREEN}sudo systemctl restart nginx${NC}"
echo -e "  Restart app: ${GREEN}sudo systemctl restart inhealth${NC}"
echo -e "  View logs: ${GREEN}sudo journalctl -u inhealth -f${NC}"
echo -e "  Nginx logs: ${GREEN}sudo tail -f /var/log/nginx/inhealth_error.log${NC}"
echo ""
