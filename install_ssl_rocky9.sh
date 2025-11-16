#!/bin/bash
###############################################################################
# SSL Certificate Installation Script for InHealth EHR - Rocky Linux 9
# This script installs SSL certificates and configures Nginx on Rocky Linux 9
###############################################################################

set -e  # Exit on error

echo "========================================================================="
echo "InHealth EHR - SSL Certificate Installation (Rocky Linux 9)"
echo "========================================================================="
echo ""

# Configuration
SSL_DIR="/etc/ssl/inhealth"
CERT_SOURCE_PATH="/home/zia/test2/inhealth-cert/certificate.crt"
KEY_SOURCE_PATH="/home/zia/test2/inhealth-cert/private.key"
CERT_DEST_PATH="$SSL_DIR/certificate.crt"
KEY_DEST_PATH="$SSL_DIR/private.key"
NGINX_CONF_DIR="/etc/nginx/conf.d"
NGINX_CONF="$NGINX_CONF_DIR/inhealth_ssl.conf"
DJANGO_DIR="/home/user/inhealthUSA/django_inhealth"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}ERROR: This script must be run as root (use sudo)${NC}"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_NAME=$NAME
    OS_VERSION=$VERSION_ID
else
    echo -e "${RED}Cannot detect OS. This script is designed for Rocky Linux 9.${NC}"
    exit 1
fi

echo "Detected OS: $OS_NAME $OS_VERSION"
echo ""

# Verify Rocky Linux 9 (optional - can run on other RHEL-based systems)
if [[ ! "$OS_NAME" =~ "Rocky" ]] && [[ ! "$OS_NAME" =~ "Red Hat" ]] && [[ ! "$OS_NAME" =~ "CentOS" ]] && [[ ! "$OS_NAME" =~ "AlmaLinux" ]]; then
    echo -e "${YELLOW}WARNING: This script is optimized for RHEL-based systems (Rocky/RHEL/AlmaLinux).${NC}"
    echo -e "${YELLOW}You are running: $OS_NAME${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Step 1: Checking for certificate files..."
echo "========================================================================="

# Check if source certificate files exist
if [ -f "$CERT_SOURCE_PATH" ]; then
    echo -e "${GREEN}✓ Certificate file found: $CERT_SOURCE_PATH${NC}"
    CERT_EXISTS=true
else
    echo -e "${RED}✗ Certificate file NOT found: $CERT_SOURCE_PATH${NC}"
    CERT_EXISTS=false
fi

if [ -f "$KEY_SOURCE_PATH" ]; then
    echo -e "${GREEN}✓ Private key file found: $KEY_SOURCE_PATH${NC}"
    KEY_EXISTS=true
else
    echo -e "${RED}✗ Private key file NOT found: $KEY_SOURCE_PATH${NC}"
    KEY_EXISTS=false
fi

echo ""

# If files don't exist locally, provide instructions
if [ "$CERT_EXISTS" = false ] || [ "$KEY_EXISTS" = false ]; then
    echo "========================================================================="
    echo "Certificate files not found on this server!"
    echo "========================================================================="
    echo ""
    echo "You need to copy your SSL certificate files to this server first."
    echo ""
    echo -e "${YELLOW}Option 1: Copy from another server using SCP${NC}"
    echo "-------------------------------------------"
    echo "From your local machine or the server where certificates are located, run:"
    echo ""
    SERVER_IP=$(hostname -I | awk '{print $1}')
    echo "  scp /home/zia/test2/inhealth-cert/certificate.crt root@${SERVER_IP}:/tmp/"
    echo "  scp /home/zia/test2/inhealth-cert/private.key root@${SERVER_IP}:/tmp/"
    echo ""
    echo "Then run this script again with the --from-tmp flag:"
    echo "  sudo bash install_ssl_rocky9.sh --from-tmp"
    echo ""
    echo -e "${YELLOW}Option 2: Use SFTP or file upload${NC}"
    echo "-----------------------------------"
    echo "Upload certificate.crt and private.key to /tmp/ on this server"
    echo "Then run: sudo bash install_ssl_rocky9.sh --from-tmp"
    echo ""
    echo -e "${YELLOW}Option 3: Manual copy${NC}"
    echo "---------------------"
    echo "Manually copy the certificate files to:"
    echo "  Certificate: $CERT_DEST_PATH"
    echo "  Private Key: $KEY_DEST_PATH"
    echo ""
    echo "Then run: sudo bash install_ssl_rocky9.sh --skip-copy"
    echo ""
    exit 1
fi

echo "Step 2: Installing required packages..."
echo "========================================================================="
# Install OpenSSL if not present
if ! command -v openssl &> /dev/null; then
    echo "Installing OpenSSL..."
    dnf install -y openssl
fi

# Install policycoreutils-python-utils for SELinux management
if ! command -v semanage &> /dev/null; then
    echo "Installing SELinux tools..."
    dnf install -y policycoreutils-python-utils
fi

echo -e "${GREEN}✓ Required packages installed${NC}"
echo ""

echo "Step 3: Creating SSL directory structure..."
echo "========================================================================="
mkdir -p "$SSL_DIR"
mkdir -p "$NGINX_CONF_DIR"
echo -e "${GREEN}✓ Created directory: $SSL_DIR${NC}"
echo -e "${GREEN}✓ Verified Nginx config directory: $NGINX_CONF_DIR${NC}"
echo ""

echo "Step 4: Copying SSL certificate files..."
echo "========================================================================="

# Handle different copy sources based on flags
if [ "$1" = "--from-tmp" ]; then
    echo "Copying from /tmp/ directory..."
    if [ -f "/tmp/certificate.crt" ] && [ -f "/tmp/private.key" ]; then
        cp /tmp/certificate.crt "$CERT_DEST_PATH"
        cp /tmp/private.key "$KEY_DEST_PATH"
        echo -e "${GREEN}✓ Copied certificate and private key from /tmp/${NC}"
        # Clean up temp files
        rm -f /tmp/certificate.crt /tmp/private.key
        echo -e "${GREEN}✓ Cleaned up temporary files${NC}"
    else
        echo -e "${RED}✗ Certificate files not found in /tmp/${NC}"
        exit 1
    fi
elif [ "$1" != "--skip-copy" ]; then
    # Copy from source location
    cp "$CERT_SOURCE_PATH" "$CERT_DEST_PATH"
    cp "$KEY_SOURCE_PATH" "$KEY_DEST_PATH"
    echo -e "${GREEN}✓ Copied certificate: $CERT_SOURCE_PATH → $CERT_DEST_PATH${NC}"
    echo -e "${GREEN}✓ Copied private key: $KEY_SOURCE_PATH → $KEY_DEST_PATH${NC}"
fi

echo ""

echo "Step 5: Setting proper permissions..."
echo "========================================================================="
chmod 644 "$CERT_DEST_PATH"
chmod 600 "$KEY_DEST_PATH"
chown root:root "$CERT_DEST_PATH"
chown root:root "$KEY_DEST_PATH"
echo -e "${GREEN}✓ Certificate permissions: 644 (readable)${NC}"
echo -e "${GREEN}✓ Private key permissions: 600 (secure, root only)${NC}"
echo ""

echo "Step 6: Configuring SELinux contexts..."
echo "========================================================================="
# Check if SELinux is enabled
if command -v getenforce &> /dev/null; then
    SELINUX_STATUS=$(getenforce)
    echo "SELinux status: $SELINUX_STATUS"

    if [ "$SELINUX_STATUS" != "Disabled" ]; then
        # Set correct SELinux context for SSL certificates
        chcon -t cert_t "$CERT_DEST_PATH" 2>/dev/null || semanage fcontext -a -t cert_t "$CERT_DEST_PATH"
        chcon -t cert_t "$KEY_DEST_PATH" 2>/dev/null || semanage fcontext -a -t cert_t "$KEY_DEST_PATH"

        # Make contexts persistent
        restorecon -v "$CERT_DEST_PATH"
        restorecon -v "$KEY_DEST_PATH"

        echo -e "${GREEN}✓ SELinux contexts configured for SSL certificates${NC}"

        # Allow Nginx to make network connections (needed for proxy)
        setsebool -P httpd_can_network_connect 1
        echo -e "${GREEN}✓ Enabled httpd_can_network_connect for Nginx proxy${NC}"
    else
        echo -e "${YELLOW}⚠ SELinux is disabled${NC}"
    fi
else
    echo -e "${YELLOW}⚠ SELinux tools not found${NC}"
fi
echo ""

echo "Step 7: Validating certificate..."
echo "========================================================================="
# Check certificate validity
if openssl x509 -in "$CERT_DEST_PATH" -noout -text > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Certificate is valid${NC}"
    echo ""
    echo "Certificate Details:"
    echo "-------------------"
    openssl x509 -in "$CERT_DEST_PATH" -noout -subject -issuer -dates
    echo ""
else
    echo -e "${RED}✗ Certificate validation failed!${NC}"
    exit 1
fi

echo "Step 8: Validating private key..."
echo "========================================================================="
# Check private key validity
if openssl rsa -in "$KEY_DEST_PATH" -check -noout > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Private key is valid${NC}"
else
    echo -e "${RED}✗ Private key validation failed!${NC}"
    exit 1
fi
echo ""

echo "Step 9: Verifying certificate and key match..."
echo "========================================================================="
# Get modulus from certificate and key to ensure they match
CERT_MODULUS=$(openssl x509 -noout -modulus -in "$CERT_DEST_PATH" | openssl md5)
KEY_MODULUS=$(openssl rsa -noout -modulus -in "$KEY_DEST_PATH" | openssl md5)

if [ "$CERT_MODULUS" = "$KEY_MODULUS" ]; then
    echo -e "${GREEN}✓ Certificate and private key match!${NC}"
else
    echo -e "${RED}✗ ERROR: Certificate and private key DO NOT match!${NC}"
    exit 1
fi
echo ""

echo "Step 10: Checking for intermediate/chain certificates..."
echo "========================================================================="
# Check if there's a chain/bundle file
if [ -f "/home/zia/test2/inhealth-cert/ca_bundle.crt" ]; then
    cp /home/zia/test2/inhealth-cert/ca_bundle.crt "$SSL_DIR/ca_bundle.crt"
    chmod 644 "$SSL_DIR/ca_bundle.crt"
    chcon -t cert_t "$SSL_DIR/ca_bundle.crt" 2>/dev/null || true
    restorecon -v "$SSL_DIR/ca_bundle.crt" 2>/dev/null || true
    echo -e "${GREEN}✓ CA bundle copied and configured${NC}"
    USE_CA_BUNDLE=true
elif [ -f "/tmp/ca_bundle.crt" ] && [ "$1" = "--from-tmp" ]; then
    cp /tmp/ca_bundle.crt "$SSL_DIR/ca_bundle.crt"
    chmod 644 "$SSL_DIR/ca_bundle.crt"
    chcon -t cert_t "$SSL_DIR/ca_bundle.crt" 2>/dev/null || true
    restorecon -v "$SSL_DIR/ca_bundle.crt" 2>/dev/null || true
    rm -f /tmp/ca_bundle.crt
    echo -e "${GREEN}✓ CA bundle copied from /tmp and configured${NC}"
    USE_CA_BUNDLE=true
else
    echo -e "${YELLOW}⚠ No CA bundle found (may be okay if included in certificate)${NC}"
    USE_CA_BUNDLE=false
fi
echo ""

echo "Step 11: Creating Nginx SSL configuration..."
echo "========================================================================="

# Detect server IP and hostname
SERVER_IP=$(hostname -I | awk '{print $1}')
SERVER_HOSTNAME=$(hostname -f 2>/dev/null || hostname)

# Create Nginx SSL configuration for Rocky Linux 9
cat > "$NGINX_CONF" << EOF
# InHealth EHR - HTTPS Configuration
# Generated on $(date)

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name $SERVER_HOSTNAME $SERVER_IP _;

    # Redirect all HTTP to HTTPS
    return 301 https://\$host\$request_uri;
}

# HTTPS Server Block
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $SERVER_HOSTNAME $SERVER_IP _;

    # SSL Certificate Configuration
    ssl_certificate $CERT_DEST_PATH;
    ssl_certificate_key $KEY_DEST_PATH;
EOF

# Add CA bundle if exists
if [ "$USE_CA_BUNDLE" = true ]; then
    echo "    ssl_trusted_certificate $SSL_DIR/ca_bundle.crt;" >> "$NGINX_CONF"
fi

cat >> "$NGINX_CONF" << EOF

    # SSL Security Settings (Modern Configuration)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Logging
    access_log /var/log/nginx/inhealth_ssl_access.log;
    error_log /var/log/nginx/inhealth_ssl_error.log;

    # Client Body Size (for file uploads)
    client_max_body_size 10M;

    # Django Application (Proxy to Gunicorn/uWSGI)
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files
    location /static/ {
        alias /home/user/inhealthUSA/django_inhealth/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Media files (protected - should require authentication in production)
    location /media/ {
        alias /home/user/inhealthUSA/django_inhealth/media/;
        expires 7d;
        add_header Cache-Control "private";
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

echo -e "${GREEN}✓ Created Nginx SSL configuration: $NGINX_CONF${NC}"
echo ""

echo "Step 12: Configuring SELinux for Nginx static/media files..."
echo "========================================================================="
if [ "$SELINUX_STATUS" != "Disabled" ]; then
    # Set correct context for static/media directories
    if [ -d "/home/user/inhealthUSA/django_inhealth/static" ]; then
        semanage fcontext -a -t httpd_sys_content_t "/home/user/inhealthUSA/django_inhealth/static(/.*)?" 2>/dev/null || true
        restorecon -Rv /home/user/inhealthUSA/django_inhealth/static 2>/dev/null || true
        echo -e "${GREEN}✓ Configured SELinux for static files${NC}"
    fi

    if [ -d "/home/user/inhealthUSA/django_inhealth/media" ]; then
        semanage fcontext -a -t httpd_sys_rw_content_t "/home/user/inhealthUSA/django_inhealth/media(/.*)?" 2>/dev/null || true
        restorecon -Rv /home/user/inhealthUSA/django_inhealth/media 2>/dev/null || true
        echo -e "${GREEN}✓ Configured SELinux for media files${NC}"
    fi
fi
echo ""

echo "Step 13: Testing Nginx configuration..."
echo "========================================================================="
if nginx -t 2>&1; then
    echo -e "${GREEN}✓ Nginx configuration is valid${NC}"
else
    echo -e "${RED}✗ Nginx configuration test failed!${NC}"
    echo ""
    echo "Please check the error messages above."
    exit 1
fi
echo ""

echo "Step 14: Configuring firewall (firewalld)..."
echo "========================================================================="
if command -v firewall-cmd &> /dev/null; then
    FIREWALLD_RUNNING=$(firewall-cmd --state 2>/dev/null || echo "not running")

    if [ "$FIREWALLD_RUNNING" = "running" ]; then
        # Add HTTP and HTTPS services
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --reload
        echo -e "${GREEN}✓ Firewall configured to allow HTTP (80) and HTTPS (443)${NC}"
    else
        echo -e "${YELLOW}⚠ Firewalld is not running${NC}"
        echo "  To enable firewall, run: systemctl enable --now firewalld"
    fi
else
    echo -e "${YELLOW}⚠ Firewalld not found${NC}"
fi
echo ""

echo "Step 15: Enabling and restarting Nginx..."
echo "========================================================================="
# Enable Nginx to start on boot
systemctl enable nginx

# Restart Nginx to apply configuration
if systemctl restart nginx; then
    echo -e "${GREEN}✓ Nginx restarted successfully${NC}"
    sleep 2

    # Check if Nginx is running
    if systemctl is-active --quiet nginx; then
        echo -e "${GREEN}✓ Nginx is running${NC}"
    else
        echo -e "${RED}✗ Nginx failed to start${NC}"
        echo ""
        echo "Check logs with: sudo journalctl -u nginx -n 50"
        exit 1
    fi
else
    echo -e "${RED}✗ Failed to restart Nginx${NC}"
    exit 1
fi
echo ""

echo "Step 16: Verifying HTTPS is working..."
echo "========================================================================="
sleep 2
if curl -k -s -o /dev/null -w "%{http_code}" https://localhost | grep -q "200\|301\|302"; then
    echo -e "${GREEN}✓ HTTPS is responding${NC}"
else
    echo -e "${YELLOW}⚠ Could not verify HTTPS response (this may be normal if Django isn't running)${NC}"
fi
echo ""

echo "========================================================================="
echo -e "${GREEN}✓ SSL Certificate Installation Complete!${NC}"
echo "========================================================================="
echo ""
echo "Summary:"
echo "--------"
echo "Certificate: $CERT_DEST_PATH"
echo "Private Key: $KEY_DEST_PATH"
if [ "$USE_CA_BUNDLE" = true ]; then
    echo "CA Bundle: $SSL_DIR/ca_bundle.crt"
fi
echo "Nginx Config: $NGINX_CONF"
echo "SELinux: $(getenforce 2>/dev/null || echo 'Not available')"
echo ""
echo "Certificate Information:"
openssl x509 -in "$CERT_DEST_PATH" -noout -subject -issuer -dates
echo ""
echo "Nginx Status:"
systemctl status nginx --no-pager -l | head -10
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "-----------"
echo "1. Ensure Django application is running: cd /home/user/inhealthUSA/django_inhealth && python manage.py runserver"
echo "2. Or use Gunicorn: gunicorn --bind 127.0.0.1:8000 inhealth.wsgi:application"
echo "3. Update your domain DNS to point to this server: $SERVER_IP"
echo "4. Test HTTPS: https://$SERVER_HOSTNAME or https://$SERVER_IP"
echo "5. Check SSL rating: https://www.ssllabs.com/ssltest/"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "-----------------"
echo "Check Nginx status: sudo systemctl status nginx"
echo "Restart Nginx: sudo systemctl restart nginx"
echo "View Nginx logs: sudo tail -f /var/log/nginx/inhealth_ssl_error.log"
echo "View Nginx access: sudo tail -f /var/log/nginx/inhealth_ssl_access.log"
echo "Test SSL locally: curl -v https://localhost"
echo "Check firewall: sudo firewall-cmd --list-all"
echo "Check SELinux: sudo ausearch -m avc -ts recent"
echo ""
echo "========================================================================="
