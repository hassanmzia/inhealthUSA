#!/bin/bash
###############################################################################
# InHealth EHR - Production Server Start Script
# Starts Django with Gunicorn behind Nginx SSL/HTTPS
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================================================="
echo "InHealth EHR - Production Server Startup"
echo "========================================================================="
echo ""

# Configuration
DJANGO_DIR="/home/user/inhealthUSA/django_inhealth"
WORKERS=3  # Number of Gunicorn workers (2-4 x NUM_CORES)
BIND_ADDRESS="127.0.0.1:8000"  # Nginx will proxy to this
TIMEOUT=120  # Request timeout in seconds
LOG_LEVEL="info"  # debug, info, warning, error, critical

cd "$DJANGO_DIR"

# Check if in production mode
if python -c "from inhealth.settings import DEBUG; import sys; sys.exit(0 if not DEBUG else 1)" 2>/dev/null; then
    echo -e "${GREEN}✓ Running in PRODUCTION mode (DEBUG=False)${NC}"
else
    echo -e "${RED}ERROR: DEBUG is still set to True in settings.py${NC}"
    echo ""
    echo "For production, you must set DEBUG=False in settings.py or use environment variable:"
    echo "  export DJANGO_DEBUG=False"
    echo ""
    read -p "Continue anyway with DEBUG=True? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check SSL certificates are installed
if [ ! -f "/etc/ssl/inhealth/certificate.crt" ]; then
    echo -e "${YELLOW}WARNING: SSL certificates not found in /etc/ssl/inhealth/${NC}"
    echo "Run: sudo /home/user/inhealthUSA/install_ssl_rocky9.sh"
    echo ""
fi

# Check Nginx is running
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx is running${NC}"
else
    echo -e "${YELLOW}⚠ Nginx is not running${NC}"
    echo "Start Nginx: sudo systemctl start nginx"
    echo ""
fi

# Check if Gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo -e "${YELLOW}Gunicorn not found. Installing...${NC}"
    pip install gunicorn
fi

echo -e "${GREEN}✓ Gunicorn installed${NC}"
echo ""

# Run Django checks
echo "Running Django system checks..."
echo "========================================================================="
python manage.py check --deploy
echo ""

# Collect static files
echo "Collecting static files..."
echo "========================================================================="
python manage.py collectstatic --noinput --clear
echo ""

# Run migrations
echo "Checking for database migrations..."
echo "========================================================================="
python manage.py migrate --noinput
echo ""

echo "Starting Gunicorn application server..."
echo "========================================================================="
echo ""
echo "Configuration:"
echo "  Workers: $WORKERS"
echo "  Bind: $BIND_ADDRESS"
echo "  Timeout: ${TIMEOUT}s"
echo "  Log level: $LOG_LEVEL"
echo ""
echo -e "${GREEN}Gunicorn will serve Django on $BIND_ADDRESS${NC}"
echo -e "${GREEN}Nginx will handle HTTPS and proxy to Gunicorn${NC}"
echo ""
echo "Access your application at:"
echo "  https://your-domain.com"
echo "  https://$(hostname -I | awk '{print $1}')"
echo ""
echo "Logs:"
echo "  Application: /home/user/inhealthUSA/django_inhealth/logs/gunicorn.log"
echo "  Nginx access: /var/log/nginx/inhealth_ssl_access.log"
echo "  Nginx error: /var/log/nginx/inhealth_ssl_error.log"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "========================================================================="
echo ""

# Create logs directory
mkdir -p logs

# Start Gunicorn
exec gunicorn inhealth.wsgi:application \
    --workers $WORKERS \
    --bind $BIND_ADDRESS \
    --timeout $TIMEOUT \
    --log-level $LOG_LEVEL \
    --access-logfile logs/gunicorn-access.log \
    --error-logfile logs/gunicorn-error.log \
    --capture-output \
    --enable-stdio-inheritance
