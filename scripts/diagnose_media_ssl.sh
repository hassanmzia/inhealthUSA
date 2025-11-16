#!/bin/bash

# Script to diagnose media file issues with SSL
# This script helps identify why profile pictures are blocked after enabling SSL

set -e

echo "========================================="
echo "Media Files SSL Diagnostic Tool"
echo "========================================="
echo ""

# Get the script directory and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DJANGO_ROOT="$PROJECT_ROOT/django_inhealth"

echo "Project Root: $PROJECT_ROOT"
echo "Django Root: $DJANGO_ROOT"
echo ""

# Check 1: Media directory exists and permissions
echo "=== Check 1: Media Directory ==="
if [ -d "$DJANGO_ROOT/media" ]; then
    echo "✓ Media directory exists"
    ls -lah "$DJANGO_ROOT/media" | head -10
    echo ""

    if [ -d "$DJANGO_ROOT/media/profile_pictures" ]; then
        echo "✓ Profile pictures directory exists"
        echo "Files:"
        ls -lah "$DJANGO_ROOT/media/profile_pictures" | head -10
    else
        echo "⚠ Profile pictures directory does not exist"
        echo "Creating directory..."
        mkdir -p "$DJANGO_ROOT/media/profile_pictures"
        chmod 755 "$DJANGO_ROOT/media/profile_pictures"
        echo "✓ Directory created"
    fi
else
    echo "✗ Media directory does not exist!"
    echo "Creating directory..."
    mkdir -p "$DJANGO_ROOT/media/profile_pictures"
    chmod 755 "$DJANGO_ROOT/media"
    chmod 755 "$DJANGO_ROOT/media/profile_pictures"
    echo "✓ Directories created"
fi
echo ""

# Check 2: Nginx user
echo "=== Check 2: Nginx User ==="
if command -v nginx &> /dev/null; then
    echo "✓ Nginx is installed"
    NGINX_USER=$(ps aux | grep nginx | grep -v grep | grep worker | awk '{print $1}' | head -1)
    if [ -n "$NGINX_USER" ]; then
        echo "Nginx worker user: $NGINX_USER"
    else
        echo "⚠ Nginx is not running or user could not be determined"
        echo "Common nginx users: www-data, nginx"
    fi
else
    echo "⚠ Nginx is not installed or not in PATH"
fi
echo ""

# Check 3: Media directory permissions for nginx user
echo "=== Check 3: Permission Test ==="
CURRENT_USER=$(whoami)
echo "Current user: $CURRENT_USER"

if [ -n "$NGINX_USER" ] && [ -d "$DJANGO_ROOT/media" ]; then
    echo "Testing if nginx user can read media directory..."

    # Create a test file
    TEST_FILE="$DJANGO_ROOT/media/test_permission.txt"
    echo "test" > "$TEST_FILE"
    chmod 644 "$TEST_FILE"

    # Try to read as nginx user
    if sudo -u "$NGINX_USER" cat "$TEST_FILE" &> /dev/null; then
        echo "✓ Nginx user can read media files"
    else
        echo "✗ Nginx user CANNOT read media files"
        echo "Fix: Run the following commands:"
        echo "  sudo chown -R $CURRENT_USER:$NGINX_USER $DJANGO_ROOT/media/"
        echo "  sudo chmod -R 755 $DJANGO_ROOT/media/"
    fi

    # Clean up test file
    rm -f "$TEST_FILE"
else
    echo "⚠ Skipping nginx user permission test"
fi
echo ""

# Check 4: Nginx configuration
echo "=== Check 4: Nginx Configuration ==="
if [ -f "/etc/nginx/sites-enabled/inhealth" ]; then
    echo "✓ Nginx site configuration found"

    # Check for media location
    if grep -q "location /media/" /etc/nginx/sites-enabled/inhealth; then
        echo "✓ Media location block found"
        echo ""
        echo "Media configuration:"
        grep -A 8 "location /media/" /etc/nginx/sites-enabled/inhealth
    else
        echo "✗ Media location block NOT found!"
        echo "Add this to your nginx configuration:"
        echo ""
        echo "location /media/ {"
        echo "    alias $DJANGO_ROOT/media/;"
        echo "    expires 7d;"
        echo "    add_header Cache-Control \"public\";"
        echo "}"
    fi
    echo ""

    # Check for X-Forwarded-Proto header
    if grep -q "X-Forwarded-Proto" /etc/nginx/sites-enabled/inhealth; then
        echo "✓ X-Forwarded-Proto header is set"
    else
        echo "✗ X-Forwarded-Proto header NOT found!"
        echo "Add this to your proxy location block:"
        echo "  proxy_set_header X-Forwarded-Proto \$scheme;"
    fi
else
    echo "⚠ Nginx site configuration not found at /etc/nginx/sites-enabled/inhealth"
    echo "Check your nginx configuration path"
fi
echo ""

# Check 5: Django settings
echo "=== Check 5: Django Settings ==="
if [ -f "$DJANGO_ROOT/inhealth/settings.py" ]; then
    echo "✓ Django settings found"

    # Check MEDIA_URL
    if grep -q "MEDIA_URL.*=.*'/media/'" "$DJANGO_ROOT/inhealth/settings.py"; then
        echo "✓ MEDIA_URL is set to '/media/'"
    else
        echo "⚠ MEDIA_URL setting check failed"
        echo "Ensure MEDIA_URL = '/media/'"
    fi

    # Check SECURE_PROXY_SSL_HEADER
    if grep -q "SECURE_PROXY_SSL_HEADER" "$DJANGO_ROOT/inhealth/settings.py"; then
        echo "✓ SECURE_PROXY_SSL_HEADER is configured"
    else
        echo "✗ SECURE_PROXY_SSL_HEADER NOT found!"
        echo "Add to settings.py:"
        echo "  SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')"
    fi
else
    echo "✗ Django settings.py not found!"
fi
echo ""

# Check 6: Test media file creation
echo "=== Check 6: Test File Creation ==="
TEST_IMG="$DJANGO_ROOT/media/profile_pictures/test.txt"
if mkdir -p "$DJANGO_ROOT/media/profile_pictures" 2>/dev/null; then
    echo "test" > "$TEST_IMG"
    if [ -f "$TEST_IMG" ]; then
        echo "✓ Can create files in media/profile_pictures"
        rm -f "$TEST_IMG"
    else
        echo "✗ Cannot create files in media/profile_pictures"
    fi
else
    echo "✗ Cannot create profile_pictures directory"
fi
echo ""

# Summary
echo "========================================="
echo "Diagnostic Summary"
echo "========================================="
echo ""
echo "Next Steps:"
echo "1. Review any errors (✗) or warnings (⚠) above"
echo "2. Check nginx error logs: sudo tail -50 /var/log/nginx/error.log"
echo "3. Check browser console (F12) for mixed content errors"
echo "4. Verify nginx is serving media files:"
echo "   curl https://yourdomain.com/media/test.txt"
echo "5. See TROUBLESHOOTING.md section 7 for detailed solutions"
echo ""
