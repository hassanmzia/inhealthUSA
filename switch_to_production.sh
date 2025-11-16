#!/bin/bash
# Quick script to switch Django to production mode
# This assumes nginx and SSL are already configured

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Switching InHealth EHR to Production Mode${NC}"
echo ""

# Check if .env.production exists
if [ ! -f "/home/user/inhealthUSA/.env.production" ]; then
    echo -e "${RED}Error: .env.production file not found${NC}"
    echo -e "Please create it first or run the full deployment script"
    exit 1
fi

# Backup current settings if they exist
if [ -f "/home/user/inhealthUSA/django_inhealth/.env" ]; then
    echo -e "${YELLOW}Backing up current .env to .env.backup${NC}"
    cp /home/user/inhealthUSA/django_inhealth/.env /home/user/inhealthUSA/django_inhealth/.env.backup
fi

# Copy production environment file
echo -e "${GREEN}Copying production environment configuration...${NC}"
cp /home/user/inhealthUSA/.env.production /home/user/inhealthUSA/django_inhealth/.env

# Update Django settings.py to use DEBUG=False
echo -e "${GREEN}Updating Django settings for production...${NC}"
cd /home/user/inhealthUSA/django_inhealth

# Create or update .env file with production settings
cat > .env << 'EOF'
# Production Environment
DEBUG=False
SECRET_KEY=django-insecure-change-this-in-production-2024-inhealth-ehr
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com,www.yourdomain.com

# Database
DB_NAME=inhealth_db
DB_USER=inhealth_user
DB_PASSWORD=inhealth_password
DB_HOST=localhost
DB_PORT=5432

# Session Security
SESSION_COOKIE_AGE=1800
SESSION_INACTIVITY_TIMEOUT=1800
SESSION_RENEWAL_THRESHOLD=300
EOF

# Collect static files
echo -e "${GREEN}Collecting static files...${NC}"
if [ -d "../venv" ]; then
    source ../venv/bin/activate
    python manage.py collectstatic --noinput
    deactivate
else
    echo -e "${YELLOW}Warning: Virtual environment not found, skipping collectstatic${NC}"
fi

# Set proper permissions
echo -e "${GREEN}Setting permissions...${NC}"
if [ "$EUID" -eq 0 ]; then
    chown -R www-data:www-data /home/user/inhealthUSA/django_inhealth/staticfiles
    chown -R www-data:www-data /home/user/inhealthUSA/django_inhealth/media
    chmod -R 755 /home/user/inhealthUSA/django_inhealth/staticfiles
    chmod -R 755 /home/user/inhealthUSA/django_inhealth/media
else
    echo -e "${YELLOW}Not running as root, skipping permission changes${NC}"
    echo -e "Run the following commands as root:"
    echo -e "  sudo chown -R www-data:www-data /home/user/inhealthUSA/django_inhealth/staticfiles"
    echo -e "  sudo chown -R www-data:www-data /home/user/inhealthUSA/django_inhealth/media"
fi

# Restart services if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${GREEN}Restarting services...${NC}"
    systemctl restart inhealth 2>/dev/null || echo -e "${YELLOW}Gunicorn service not found, skip restarting${NC}"
    systemctl restart nginx 2>/dev/null || echo -e "${YELLOW}Nginx not found, skip restarting${NC}"
else
    echo -e "${YELLOW}Not running as root, skipping service restart${NC}"
    echo -e "Run the following commands as root:"
    echo -e "  sudo systemctl restart inhealth"
    echo -e "  sudo systemctl restart nginx"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Production Mode Activated!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Important:${NC}"
echo -e "1. Update SECRET_KEY in .env with a secure random key"
echo -e "2. Update ALLOWED_HOSTS with your actual domain"
echo -e "3. Update database credentials"
echo -e "4. Configure email settings for password reset"
echo ""
echo -e "${YELLOW}To switch back to development mode:${NC}"
echo -e "  cp .env.backup .env (if backup exists)"
echo -e "  or manually edit .env and set DEBUG=True"
echo ""
