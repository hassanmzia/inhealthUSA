#!/bin/bash
###############################################################################
# Django Development Server with SSL - InHealth EHR
# This script runs Django's development server with HTTPS using the installed
# SSL certificates for testing purposes.
#
# IMPORTANT: This is for DEVELOPMENT/TESTING ONLY
# For production, use Gunicorn with Nginx (see production_start.sh)
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================================================="
echo "InHealth EHR - Django Development Server with SSL"
echo "========================================================================="
echo ""

# Configuration
DJANGO_DIR="/home/user/inhealthUSA/django_inhealth"
SSL_CERT="/etc/ssl/inhealth/certificate.crt"
SSL_KEY="/etc/ssl/inhealth/private.key"
HOST="0.0.0.0"
PORT="8443"  # Use 8443 for development HTTPS (443 requires root)

# Check if running in Django directory
if [ ! -f "$DJANGO_DIR/manage.py" ]; then
    echo -e "${RED}ERROR: manage.py not found in $DJANGO_DIR${NC}"
    exit 1
fi

cd "$DJANGO_DIR"

# Check if SSL certificates exist
if [ ! -f "$SSL_CERT" ]; then
    echo -e "${YELLOW}WARNING: SSL certificate not found: $SSL_CERT${NC}"
    echo ""
    echo "Please install SSL certificates first:"
    echo "  cd /home/user/inhealthUSA"
    echo "  sudo ./install_ssl_rocky9.sh"
    echo ""
    exit 1
fi

if [ ! -f "$SSL_KEY" ]; then
    echo -e "${YELLOW}WARNING: SSL private key not found: $SSL_KEY${NC}"
    echo ""
    echo "Please install SSL certificates first:"
    echo "  cd /home/user/inhealthUSA"
    echo "  sudo ./install_ssl_rocky9.sh"
    echo ""
    exit 1
fi

# Check if django-extensions is installed (provides runserver_plus with SSL)
echo "Checking for django-extensions..."
if ! python -c "import django_extensions" 2>/dev/null; then
    echo -e "${YELLOW}django-extensions not installed. Installing...${NC}"
    pip install django-extensions Werkzeug pyOpenSSL

    # Add to INSTALLED_APPS if not already there
    if ! grep -q "django_extensions" "$DJANGO_DIR/inhealth/settings.py"; then
        echo ""
        echo -e "${YELLOW}NOTE: Add 'django_extensions' to INSTALLED_APPS in settings.py${NC}"
        echo ""
    fi
fi

echo -e "${GREEN}✓ SSL certificates found${NC}"
echo -e "${GREEN}✓ django-extensions installed${NC}"
echo ""

# Display certificate info
echo "Certificate Information:"
echo "------------------------"
openssl x509 -in "$SSL_CERT" -noout -subject -issuer -dates
echo ""

# Check if port is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}ERROR: Port $PORT is already in use${NC}"
    echo ""
    echo "Stop the service using port $PORT or use a different port:"
    echo "  sudo lsof -i :$PORT"
    echo "  sudo kill <PID>"
    exit 1
fi

echo "Starting Django development server with SSL..."
echo "========================================================================="
echo ""
echo -e "${GREEN}Access your application at:${NC}"
echo "  https://localhost:$PORT"
echo "  https://$(hostname -I | awk '{print $1}'):$PORT"
echo ""
echo -e "${YELLOW}IMPORTANT: This is for DEVELOPMENT/TESTING ONLY${NC}"
echo -e "${YELLOW}For production, use Gunicorn with Nginx${NC}"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run Django development server with SSL using django-extensions
# This requires django-extensions package
python manage.py runserver_plus \
    --cert-file "$SSL_CERT" \
    --key-file "$SSL_KEY" \
    "$HOST:$PORT"
