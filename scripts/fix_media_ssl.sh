#!/bin/bash

# Script to fix common media file SSL issues
# This script fixes permissions and configuration for media files with SSL

set -e

echo "========================================="
echo "Media Files SSL Fix Script"
echo "========================================="
echo ""

# Get the script directory and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DJANGO_ROOT="$PROJECT_ROOT/django_inhealth"

echo "Project Root: $PROJECT_ROOT"
echo "Django Root: $DJANGO_ROOT"
echo ""

# Detect nginx user
NGINX_USER=""
if command -v nginx &> /dev/null; then
    NGINX_USER=$(ps aux | grep nginx | grep -v grep | grep worker | awk '{print $1}' | head -1)
fi

if [ -z "$NGINX_USER" ]; then
    # Try common nginx users
    if id -u www-data &> /dev/null; then
        NGINX_USER="www-data"
    elif id -u nginx &> /dev/null; then
        NGINX_USER="nginx"
    else
        echo "⚠ Warning: Could not detect nginx user"
        echo "Defaulting to www-data"
        NGINX_USER="www-data"
    fi
fi

echo "Nginx user detected: $NGINX_USER"
echo ""

# Fix 1: Create media directories
echo "=== Fix 1: Creating Media Directories ==="
mkdir -p "$DJANGO_ROOT/media/profile_pictures"
echo "✓ Media directories created"
echo ""

# Fix 2: Set ownership
echo "=== Fix 2: Setting Ownership ==="
CURRENT_USER=$(whoami)
echo "Setting owner to: $CURRENT_USER:$NGINX_USER"

if id -u "$NGINX_USER" &> /dev/null; then
    sudo chown -R "$CURRENT_USER:$NGINX_USER" "$DJANGO_ROOT/media"
    echo "✓ Ownership set"
else
    echo "⚠ Warning: Nginx user '$NGINX_USER' does not exist"
    echo "Setting owner to: $CURRENT_USER:$CURRENT_USER"
    sudo chown -R "$CURRENT_USER:$CURRENT_USER" "$DJANGO_ROOT/media"
    echo "✓ Ownership set (without nginx group)"
fi
echo ""

# Fix 3: Set permissions
echo "=== Fix 3: Setting Permissions ==="
# Directories: 755 (rwxr-xr-x)
# Files: 644 (rw-r--r--)
find "$DJANGO_ROOT/media" -type d -exec chmod 755 {} \;
find "$DJANGO_ROOT/media" -type f -exec chmod 644 {} \;
echo "✓ Permissions set (directories: 755, files: 644)"
echo ""

# Fix 4: Verify Django settings
echo "=== Fix 4: Verifying Django Settings ==="
if grep -q "SECURE_PROXY_SSL_HEADER" "$DJANGO_ROOT/inhealth/settings.py"; then
    echo "✓ SECURE_PROXY_SSL_HEADER is configured"
else
    echo "⚠ Warning: SECURE_PROXY_SSL_HEADER not found in settings.py"
    echo "You may need to add:"
    echo "  SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')"
fi

if grep -q "MEDIA_URL.*=.*'/media/'" "$DJANGO_ROOT/inhealth/settings.py"; then
    echo "✓ MEDIA_URL is set correctly"
else
    echo "⚠ Warning: MEDIA_URL may not be set correctly"
fi
echo ""

# Fix 5: Test file creation
echo "=== Fix 5: Testing File Creation ==="
TEST_FILE="$DJANGO_ROOT/media/profile_pictures/.test"
echo "test" > "$TEST_FILE"
if [ -f "$TEST_FILE" ]; then
    echo "✓ Can create files in media directory"
    rm -f "$TEST_FILE"
else
    echo "✗ Error: Cannot create files in media directory"
fi
echo ""

# Fix 6: Check nginx configuration
echo "=== Fix 6: Checking Nginx Configuration ==="
if [ -f "/etc/nginx/sites-enabled/inhealth" ]; then
    if grep -q "location /media/" /etc/nginx/sites-enabled/inhealth; then
        echo "✓ Nginx media location configured"

        # Check if path is correct
        NGINX_MEDIA_PATH=$(grep -A 2 "location /media/" /etc/nginx/sites-enabled/inhealth | grep alias | awk '{print $2}' | tr -d ';')
        if [ -n "$NGINX_MEDIA_PATH" ]; then
            echo "  Nginx media path: $NGINX_MEDIA_PATH"
            echo "  Actual media path: $DJANGO_ROOT/media/"

            if [ "$NGINX_MEDIA_PATH" != "$DJANGO_ROOT/media/" ]; then
                echo "⚠ Warning: Paths don't match!"
                echo "Update nginx configuration to use: $DJANGO_ROOT/media/"
            else
                echo "✓ Media paths match"
            fi
        fi
    else
        echo "⚠ Warning: Nginx media location not configured"
        echo "Add this to your nginx configuration:"
        echo ""
        echo "location /media/ {"
        echo "    alias $DJANGO_ROOT/media/;"
        echo "    expires 7d;"
        echo "    add_header Cache-Control \"public\";"
        echo "}"
    fi

    if grep -q "X-Forwarded-Proto" /etc/nginx/sites-enabled/inhealth; then
        echo "✓ X-Forwarded-Proto header configured"
    else
        echo "⚠ Warning: X-Forwarded-Proto header not found"
        echo "Add to your nginx proxy location:"
        echo "  proxy_set_header X-Forwarded-Proto \$scheme;"
    fi
else
    echo "⚠ Warning: Nginx configuration not found at /etc/nginx/sites-enabled/inhealth"
fi
echo ""

# Summary
echo "========================================="
echo "Fix Summary"
echo "========================================="
echo ""
echo "Actions completed:"
echo "✓ Created media directories"
echo "✓ Set proper ownership"
echo "✓ Set proper permissions"
echo ""
echo "Next steps:"
echo "1. If nginx configuration needs updates, edit /etc/nginx/sites-enabled/inhealth"
echo "2. Test nginx configuration: sudo nginx -t"
echo "3. Reload nginx: sudo systemctl reload nginx"
echo "4. Test in browser or with: curl https://yourdomain.com/media/test.txt"
echo "5. Check browser console (F12) for any remaining errors"
echo ""
echo "If issues persist, run: $SCRIPT_DIR/diagnose_media_ssl.sh"
echo "See also: django_inhealth/TROUBLESHOOTING.md section 7"
echo ""
