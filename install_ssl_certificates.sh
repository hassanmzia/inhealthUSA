#!/bin/bash
###############################################################################
# SSL Certificate Installation Script for InHealth EHR
# This script installs SSL certificates and configures Nginx
###############################################################################

set -e  # Exit on error

echo "========================================================================="
echo "InHealth EHR - SSL Certificate Installation"
echo "========================================================================="
echo ""

# Configuration
SSL_DIR="/etc/ssl/inhealth"
CERT_SOURCE_PATH="/home/zia/test2/inhealth-cert/certificate.crt"
KEY_SOURCE_PATH="/home/zia/test2/inhealth-cert/private.key"
CERT_DEST_PATH="$SSL_DIR/certificate.crt"
KEY_DEST_PATH="$SSL_DIR/private.key"
NGINX_CONF="/etc/nginx/sites-available/inhealth_ssl.conf"
DJANGO_DIR="/home/user/inhealthUSA/django_inhealth"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: This script must be run as root (use sudo)"
    exit 1
fi

echo "Step 1: Checking for certificate files..."
echo "========================================================================="

# Check if source certificate files exist
if [ -f "$CERT_SOURCE_PATH" ]; then
    echo "✓ Certificate file found: $CERT_SOURCE_PATH"
    CERT_EXISTS=true
else
    echo "✗ Certificate file NOT found: $CERT_SOURCE_PATH"
    CERT_EXISTS=false
fi

if [ -f "$KEY_SOURCE_PATH" ]; then
    echo "✓ Private key file found: $KEY_SOURCE_PATH"
    KEY_EXISTS=true
else
    echo "✗ Private key file NOT found: $KEY_SOURCE_PATH"
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
    echo "Option 1: Copy from another server using SCP"
    echo "-------------------------------------------"
    echo "From your local machine or the server where certificates are located, run:"
    echo ""
    echo "  scp /home/zia/test2/inhealth-cert/certificate.crt root@$(hostname -I | awk '{print $1}'):/tmp/"
    echo "  scp /home/zia/test2/inhealth-cert/private.key root@$(hostname -I | awk '{print $1}'):/tmp/"
    echo ""
    echo "Then run this script again with the --from-tmp flag:"
    echo "  sudo bash install_ssl_certificates.sh --from-tmp"
    echo ""
    echo "Option 2: Use SFTP or file upload"
    echo "-----------------------------------"
    echo "Upload certificate.crt and private.key to /tmp/ on this server"
    echo "Then run: sudo bash install_ssl_certificates.sh --from-tmp"
    echo ""
    echo "Option 3: Manual copy"
    echo "---------------------"
    echo "Manually copy the certificate files to:"
    echo "  Certificate: $CERT_DEST_PATH"
    echo "  Private Key: $KEY_DEST_PATH"
    echo ""
    echo "Then run: sudo bash install_ssl_certificates.sh --skip-copy"
    echo ""
    exit 1
fi

echo "Step 2: Creating SSL directory structure..."
echo "========================================================================="
mkdir -p "$SSL_DIR"
echo "✓ Created directory: $SSL_DIR"
echo ""

echo "Step 3: Copying SSL certificate files..."
echo "========================================================================="

# Handle different copy sources based on flags
if [ "$1" = "--from-tmp" ]; then
    echo "Copying from /tmp/ directory..."
    if [ -f "/tmp/certificate.crt" ] && [ -f "/tmp/private.key" ]; then
        cp /tmp/certificate.crt "$CERT_DEST_PATH"
        cp /tmp/private.key "$KEY_DEST_PATH"
        echo "✓ Copied certificate and private key from /tmp/"
        # Clean up temp files
        rm -f /tmp/certificate.crt /tmp/private.key
        echo "✓ Cleaned up temporary files"
    else
        echo "✗ Certificate files not found in /tmp/"
        exit 1
    fi
elif [ "$1" != "--skip-copy" ]; then
    # Copy from source location
    cp "$CERT_SOURCE_PATH" "$CERT_DEST_PATH"
    cp "$KEY_SOURCE_PATH" "$KEY_DEST_PATH"
    echo "✓ Copied certificate: $CERT_SOURCE_PATH → $CERT_DEST_PATH"
    echo "✓ Copied private key: $KEY_SOURCE_PATH → $KEY_DEST_PATH"
fi

echo ""

echo "Step 4: Setting proper permissions..."
echo "========================================================================="
chmod 644 "$CERT_DEST_PATH"
chmod 600 "$KEY_DEST_PATH"
chown root:root "$CERT_DEST_PATH"
chown root:root "$KEY_DEST_PATH"
echo "✓ Certificate permissions: 644 (readable)"
echo "✓ Private key permissions: 600 (secure, root only)"
echo ""

echo "Step 5: Validating certificate..."
echo "========================================================================="
# Check certificate validity
openssl x509 -in "$CERT_DEST_PATH" -noout -text > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Certificate is valid"
    echo ""
    echo "Certificate Details:"
    echo "-------------------"
    openssl x509 -in "$CERT_DEST_PATH" -noout -subject -issuer -dates
    echo ""
else
    echo "✗ Certificate validation failed!"
    exit 1
fi

echo "Step 6: Validating private key..."
echo "========================================================================="
# Check private key validity
openssl rsa -in "$KEY_DEST_PATH" -check -noout > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Private key is valid"
else
    echo "✗ Private key validation failed!"
    exit 1
fi
echo ""

echo "Step 7: Verifying certificate and key match..."
echo "========================================================================="
# Get modulus from certificate and key to ensure they match
CERT_MODULUS=$(openssl x509 -noout -modulus -in "$CERT_DEST_PATH" | openssl md5)
KEY_MODULUS=$(openssl rsa -noout -modulus -in "$KEY_DEST_PATH" | openssl md5)

if [ "$CERT_MODULUS" = "$KEY_MODULUS" ]; then
    echo "✓ Certificate and private key match!"
else
    echo "✗ ERROR: Certificate and private key DO NOT match!"
    exit 1
fi
echo ""

echo "Step 8: Checking for intermediate/chain certificates..."
echo "========================================================================="
# Check if there's a chain/bundle file
if [ -f "/home/zia/test2/inhealth-cert/ca_bundle.crt" ] || [ -f "$SSL_DIR/ca_bundle.crt" ]; then
    echo "✓ CA bundle/chain certificate found"
    if [ -f "/home/zia/test2/inhealth-cert/ca_bundle.crt" ]; then
        cp /home/zia/test2/inhealth-cert/ca_bundle.crt "$SSL_DIR/ca_bundle.crt"
        chmod 644 "$SSL_DIR/ca_bundle.crt"
    fi
else
    echo "⚠ No CA bundle found (may be okay if included in certificate)"
fi
echo ""

echo "Step 9: Updating Nginx configuration..."
echo "========================================================================="

# Check if Nginx config already exists
if [ -f "/home/user/inhealthUSA/deployment_configs/nginx_ssl.conf" ]; then
    echo "✓ Found existing Nginx SSL configuration template"

    # Copy and update the configuration
    cp /home/user/inhealthUSA/deployment_configs/nginx_ssl.conf "$NGINX_CONF"

    # Update certificate paths in the config
    sed -i "s|/etc/ssl/inhealth/yourdomain.crt|$CERT_DEST_PATH|g" "$NGINX_CONF"
    sed -i "s|/etc/ssl/inhealth/yourdomain.key|$KEY_DEST_PATH|g" "$NGINX_CONF"

    echo "✓ Updated Nginx configuration with certificate paths"
else
    echo "Creating new Nginx SSL configuration..."

    # Create basic SSL configuration
    cat > "$NGINX_CONF" << EOF
server {
    listen 80;
    server_name _;

    # Redirect HTTP to HTTPS
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name _;

    # SSL Certificate Configuration
    ssl_certificate $CERT_DEST_PATH;
    ssl_certificate_key $KEY_DEST_PATH;

    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Django Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Static files
    location /static/ {
        alias $DJANGO_DIR/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias $DJANGO_DIR/media/;
        expires 7d;
    }
}
EOF
    echo "✓ Created new Nginx SSL configuration"
fi
echo ""

echo "Step 10: Testing Nginx configuration..."
echo "========================================================================="
nginx -t
if [ $? -eq 0 ]; then
    echo "✓ Nginx configuration is valid"
else
    echo "✗ Nginx configuration test failed!"
    exit 1
fi
echo ""

echo "Step 11: Enabling site configuration..."
echo "========================================================================="
# Enable the site
if [ ! -f "/etc/nginx/sites-enabled/inhealth_ssl.conf" ]; then
    ln -s "$NGINX_CONF" /etc/nginx/sites-enabled/inhealth_ssl.conf
    echo "✓ Enabled Nginx SSL configuration"
else
    echo "✓ Configuration already enabled"
fi

# Disable default site if exists
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    rm -f /etc/nginx/sites-enabled/default
    echo "✓ Disabled default Nginx site"
fi
echo ""

echo "Step 12: Updating Django settings for HTTPS..."
echo "========================================================================="
if [ -f "$DJANGO_DIR/inhealth/settings.py" ]; then
    # Backup settings
    cp "$DJANGO_DIR/inhealth/settings.py" "$DJANGO_DIR/inhealth/settings.py.bak.$(date +%Y%m%d_%H%M%S)"

    # Check if HTTPS settings already exist
    if grep -q "SECURE_SSL_REDIRECT" "$DJANGO_DIR/inhealth/settings.py"; then
        echo "✓ Django HTTPS settings already configured"
    else
        echo "⚠ Django HTTPS settings not found in settings.py"
        echo "  Please ensure the following settings are in your settings.py:"
        echo "  - SECURE_SSL_REDIRECT = True"
        echo "  - SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')"
        echo "  - SESSION_COOKIE_SECURE = True"
        echo "  - CSRF_COOKIE_SECURE = True"
    fi
else
    echo "⚠ Django settings.py not found at expected location"
fi
echo ""

echo "Step 13: Reloading Nginx..."
echo "========================================================================="
systemctl reload nginx
if [ $? -eq 0 ]; then
    echo "✓ Nginx reloaded successfully"
else
    echo "✗ Failed to reload Nginx"
    exit 1
fi
echo ""

echo "========================================================================="
echo "✓ SSL Certificate Installation Complete!"
echo "========================================================================="
echo ""
echo "Summary:"
echo "--------"
echo "Certificate: $CERT_DEST_PATH"
echo "Private Key: $KEY_DEST_PATH"
echo "Nginx Config: $NGINX_CONF"
echo ""
echo "Certificate Information:"
openssl x509 -in "$CERT_DEST_PATH" -noout -subject -issuer -dates
echo ""
echo "Next Steps:"
echo "-----------"
echo "1. Update your domain DNS to point to this server"
echo "2. Test HTTPS: https://your-domain.com"
echo "3. Check SSL rating: https://www.ssllabs.com/ssltest/"
echo "4. Monitor logs: sudo tail -f /var/log/nginx/error.log"
echo ""
echo "To restart Nginx: sudo systemctl restart nginx"
echo "To check Nginx status: sudo systemctl status nginx"
echo ""
echo "========================================================================="
