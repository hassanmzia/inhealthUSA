#!/bin/bash

# Script to configure nginx for serving Django media files
# This script helps diagnose and fix media file serving issues in production

set -e

echo "========================================="
echo "Nginx Media Configuration Helper"
echo "========================================="
echo ""

# Get the script directory and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DJANGO_ROOT="$PROJECT_ROOT/django_inhealth"

echo "Project Root: $PROJECT_ROOT"
echo "Django Root: $DJANGO_ROOT"
echo ""

# Detect nginx site config location
NGINX_CONFIG=""
if [ -f "/etc/nginx/sites-enabled/inhealth" ]; then
    NGINX_CONFIG="/etc/nginx/sites-enabled/inhealth"
elif [ -f "/etc/nginx/conf.d/inhealth.conf" ]; then
    NGINX_CONFIG="/etc/nginx/conf.d/inhealth.conf"
elif [ -f "/etc/nginx/nginx.conf" ]; then
    NGINX_CONFIG="/etc/nginx/nginx.conf"
fi

echo "=== Step 1: Detect Configuration ==="
if [ -n "$NGINX_CONFIG" ]; then
    echo "✓ Found nginx config: $NGINX_CONFIG"
else
    echo "⚠ Warning: Could not find nginx configuration"
    echo "Common locations:"
    echo "  - /etc/nginx/sites-enabled/inhealth"
    echo "  - /etc/nginx/conf.d/inhealth.conf"
    echo "  - /etc/nginx/nginx.conf"
fi
echo ""

# Check if media location block exists
echo "=== Step 2: Check Media Configuration ==="
if [ -n "$NGINX_CONFIG" ] && [ -f "$NGINX_CONFIG" ]; then
    if grep -q "location /media/" "$NGINX_CONFIG"; then
        echo "✓ Media location block found in nginx config"
        echo ""
        echo "Current configuration:"
        grep -A 8 "location /media/" "$NGINX_CONFIG" || true
        echo ""

        # Check if path is correct
        CONFIGURED_PATH=$(grep -A 3 "location /media/" "$NGINX_CONFIG" | grep "alias" | awk '{print $2}' | tr -d ';' | head -1)
        EXPECTED_PATH="$DJANGO_ROOT/media/"

        if [ -n "$CONFIGURED_PATH" ]; then
            echo "Configured path: $CONFIGURED_PATH"
            echo "Expected path:   $EXPECTED_PATH"

            if [ "$CONFIGURED_PATH" = "$EXPECTED_PATH" ]; then
                echo "✓ Paths match!"
            else
                echo "✗ PATH MISMATCH!"
                echo "This is likely causing your 404 errors."
            fi
        fi
    else
        echo "✗ Media location block NOT found in nginx config"
        echo ""
        echo "You need to add media configuration to nginx."
        echo "See the configuration template below."
    fi
else
    echo "⚠ Skipping nginx config check (file not found)"
fi
echo ""

# Check media directory
echo "=== Step 3: Check Media Directory ==="
if [ -d "$DJANGO_ROOT/media" ]; then
    echo "✓ Media directory exists"
    echo "Files in media/profile_pictures:"
    ls -lh "$DJANGO_ROOT/media/profile_pictures/" 2>/dev/null | tail -5 || echo "  (directory empty or doesn't exist)"
else
    echo "✗ Media directory does not exist at: $DJANGO_ROOT/media"
    echo "Creating it now..."
    mkdir -p "$DJANGO_ROOT/media/profile_pictures"
    chmod 755 "$DJANGO_ROOT/media"
    chmod 755 "$DJANGO_ROOT/media/profile_pictures"
    echo "✓ Created media directory"
fi
echo ""

# Check permissions
echo "=== Step 4: Check Permissions ==="
MEDIA_PERMS=$(stat -c '%a' "$DJANGO_ROOT/media" 2>/dev/null || echo "unknown")
echo "Media directory permissions: $MEDIA_PERMS (should be 755)"

if [ "$MEDIA_PERMS" = "755" ]; then
    echo "✓ Permissions are correct"
else
    echo "⚠ Permissions should be 755"
    echo "Fix with: chmod 755 $DJANGO_ROOT/media"
fi
echo ""

# Nginx configuration template
echo "========================================="
echo "Nginx Configuration Template"
echo "========================================="
echo ""
echo "Add this to your nginx server block:"
echo ""
cat << 'EOF'
# Django Media Files (User uploads)
location /media/ {
    alias /path/to/django_inhealth/media/;  # UPDATE THIS PATH!
    expires 7d;
    add_header Cache-Control "public";

    # Security: Prevent execution of uploaded scripts
    location ~* \.(php|py|pl|sh|cgi|exe)$ {
        deny all;
    }
}
EOF
echo ""
echo "Replace '/path/to/django_inhealth/media/' with:"
echo "  $DJANGO_ROOT/media/"
echo ""

# Test instructions
echo "========================================="
echo "How to Apply Changes"
echo "========================================="
echo ""
echo "1. Edit your nginx configuration:"
echo "   sudo nano $NGINX_CONFIG"
echo ""
echo "2. Add or update the media location block (see template above)"
echo ""
echo "3. Test nginx configuration:"
echo "   sudo nginx -t"
echo ""
echo "4. Reload nginx:"
echo "   sudo systemctl reload nginx"
echo ""
echo "5. Test media file access:"
echo "   # Create a test file"
echo "   echo 'test' > $DJANGO_ROOT/media/test.txt"
echo "   "
echo "   # Access via curl (replace with your domain)"
echo "   curl http://yourdomain.com/media/test.txt"
echo "   # Should return: test"
echo ""
echo "6. Check for errors:"
echo "   sudo tail -50 /var/log/nginx/error.log"
echo ""

# Summary
echo "========================================="
echo "Summary"
echo "========================================="
echo ""
echo "Quick diagnosis:"
echo "• DEBUG=True shows pictures  → Django is serving them"
echo "• DEBUG=False shows 404      → Nginx is NOT serving them"
echo ""
echo "Solution: Configure nginx to serve media files (see template above)"
echo ""
echo "After configuring nginx, your media files will work in production!"
echo ""
