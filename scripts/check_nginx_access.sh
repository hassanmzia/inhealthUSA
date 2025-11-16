#!/bin/bash

# Script to check nginx configuration and port access
# Helps identify how to access your Django application through nginx

echo "========================================="
echo "Nginx Access Configuration Checker"
echo "========================================="
echo ""

# Check if nginx is installed
echo "=== Step 1: Check Nginx Installation ==="
if command -v nginx &> /dev/null; then
    echo "✓ Nginx is installed"
    nginx -v
else
    echo "✗ Nginx is not installed"
    exit 1
fi
echo ""

# Check if nginx is running
echo "=== Step 2: Check Nginx Status ==="
if systemctl is-active --quiet nginx; then
    echo "✓ Nginx is running"
    systemctl status nginx --no-pager | head -5
else
    echo "✗ Nginx is NOT running"
    echo "Start it with: sudo systemctl start nginx"
fi
echo ""

# Check what ports nginx is listening on
echo "=== Step 3: Ports Nginx is Listening On ==="
echo "Checking active nginx processes and ports..."
NGINX_PORTS=$(sudo netstat -tlnp 2>/dev/null | grep nginx || sudo ss -tlnp 2>/dev/null | grep nginx)

if [ -n "$NGINX_PORTS" ]; then
    echo "$NGINX_PORTS"
    echo ""

    # Parse and display in friendly format
    if echo "$NGINX_PORTS" | grep -q ":80 "; then
        echo "✓ HTTP  - Port 80  is open (http://)"
    fi

    if echo "$NGINX_PORTS" | grep -q ":443 "; then
        echo "✓ HTTPS - Port 443 is open (https://)"
    fi

    # Check for custom ports
    CUSTOM_PORTS=$(echo "$NGINX_PORTS" | grep -v ":80 " | grep -v ":443 " | awk '{print $4}' | cut -d: -f2)
    if [ -n "$CUSTOM_PORTS" ]; then
        echo "⚠ Custom ports detected: $CUSTOM_PORTS"
    fi
else
    echo "⚠ No nginx ports detected. Nginx might not be running."
fi
echo ""

# Find nginx configuration files
echo "=== Step 4: Nginx Configuration Files ==="
NGINX_CONFIGS=""

if [ -f "/etc/nginx/sites-enabled/inhealth" ]; then
    NGINX_CONFIGS="/etc/nginx/sites-enabled/inhealth"
    echo "✓ Found: /etc/nginx/sites-enabled/inhealth"
elif [ -f "/etc/nginx/conf.d/inhealth.conf" ]; then
    NGINX_CONFIGS="/etc/nginx/conf.d/inhealth.conf"
    echo "✓ Found: /etc/nginx/conf.d/inhealth.conf"
elif [ -f "/etc/nginx/nginx.conf" ]; then
    NGINX_CONFIGS="/etc/nginx/nginx.conf"
    echo "✓ Found: /etc/nginx/nginx.conf (main config)"
fi

if [ -n "$NGINX_CONFIGS" ]; then
    echo ""
    echo "Checking 'listen' directives in config:"
    sudo grep -n "listen" "$NGINX_CONFIGS" | head -10
fi
echo ""

# Get server IP addresses
echo "=== Step 5: Server IP Addresses ==="
echo "Your server can be accessed at these IPs:"
ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1'
echo ""

# Check if server is accessible
echo "=== Step 6: Testing Access ==="
SERVER_IP=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -1)

if [ -n "$SERVER_IP" ]; then
    echo "Testing HTTP (port 80) access..."
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost" | grep -q "200\|301\|302"; then
        echo "✓ HTTP is working on localhost"
        echo "  Access via: http://$SERVER_IP"
    else
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost")
        echo "⚠ HTTP returned code: $HTTP_CODE"
    fi
    echo ""

    echo "Testing HTTPS (port 443) access..."
    if curl -s -k -o /dev/null -w "%{http_code}" "https://localhost" | grep -q "200\|301\|302"; then
        echo "✓ HTTPS is working on localhost"
        echo "  Access via: https://$SERVER_IP"
    else
        HTTPS_CODE=$(curl -s -k -o /dev/null -w "%{http_code}" "https://localhost" 2>/dev/null || echo "Failed")
        if [ "$HTTPS_CODE" = "Failed" ] || [ "$HTTPS_CODE" = "000" ]; then
            echo "⚠ HTTPS not configured or not responding"
        else
            echo "⚠ HTTPS returned code: $HTTPS_CODE"
        fi
    fi
fi
echo ""

# Check firewall
echo "=== Step 7: Firewall Status ==="
if command -v firewall-cmd &> /dev/null; then
    echo "Firewall (firewalld) status:"
    if sudo firewall-cmd --state 2>/dev/null | grep -q "running"; then
        echo "✓ Firewall is running"
        echo ""
        echo "Open ports:"
        sudo firewall-cmd --list-ports 2>/dev/null || echo "No ports explicitly opened"
        echo ""
        echo "Allowed services:"
        sudo firewall-cmd --list-services 2>/dev/null

        if ! sudo firewall-cmd --list-services | grep -q "http"; then
            echo ""
            echo "⚠ HTTP service not allowed in firewall"
            echo "  Allow it with: sudo firewall-cmd --permanent --add-service=http"
        fi

        if ! sudo firewall-cmd --list-services | grep -q "https"; then
            echo "⚠ HTTPS service not allowed in firewall"
            echo "  Allow it with: sudo firewall-cmd --permanent --add-service=https"
        fi
    else
        echo "Firewall is not running"
    fi
elif command -v ufw &> /dev/null; then
    echo "Firewall (ufw) status:"
    sudo ufw status
else
    echo "No firewall detected (firewalld or ufw)"
fi
echo ""

# Summary
echo "========================================="
echo "Access Summary"
echo "========================================="
echo ""
echo "Based on the checks above, you should access your Django app at:"
echo ""

if echo "$NGINX_PORTS" | grep -q ":80 "; then
    echo "HTTP:  http://$SERVER_IP"
    echo "       (or http://yourdomain.com if you have a domain)"
fi

if echo "$NGINX_PORTS" | grep -q ":443 "; then
    echo "HTTPS: https://$SERVER_IP"
    echo "       (or https://yourdomain.com if you have a domain)"
fi

echo ""
echo "To access from your browser:"
echo "1. If on the same network: http://$SERVER_IP"
echo "2. If remote: Use your public IP or domain name"
echo "3. If localhost: http://localhost or http://127.0.0.1"
echo ""
echo "Note: If you see errors, check nginx error logs:"
echo "  sudo tail -50 /var/log/nginx/error.log"
echo ""
