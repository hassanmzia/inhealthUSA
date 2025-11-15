#!/bin/bash
# InHealth EHR - SSL Setup Script
# This script automates SSL certificate setup with Let's Encrypt and Nginx

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration - CHANGE THESE VALUES
DOMAIN="yourdomain.com"
WWW_DOMAIN="www.yourdomain.com"
EMAIL="admin@yourdomain.com"  # For Let's Encrypt notifications
PROJECT_DIR="/home/user/inhealthUSA/django_inhealth"
VENV_DIR="/home/user/inhealthUSA/venv"
NGINX_CONF="/etc/nginx/sites-available/inhealth"
SERVICE_FILE="/etc/systemd/system/inhealth.service"

echo -e "${GREEN}=== InHealth EHR SSL Setup Script ===${NC}\n"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Step 1: Update system packages
echo -e "${YELLOW}[1/10] Updating system packages...${NC}"
apt update && apt upgrade -y

# Step 2: Install required packages
echo -e "${YELLOW}[2/10] Installing Nginx, Certbot, and dependencies...${NC}"
apt install -y nginx certbot python3-certbot-nginx postgresql postgresql-contrib python3-pip python3-venv

# Step 3: Create log directory
echo -e "${YELLOW}[3/10] Creating log directory...${NC}"
mkdir -p /var/log/inhealth
chown www-data:www-data /var/log/inhealth

# Step 4: Install Gunicorn in virtual environment
echo -e "${YELLOW}[4/10] Installing Gunicorn...${NC}"
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
    pip install gunicorn
    deactivate
else
    echo -e "${RED}Virtual environment not found at $VENV_DIR${NC}"
    echo "Please create it first with: python3 -m venv $VENV_DIR"
    exit 1
fi

# Step 5: Collect Django static files
echo -e "${YELLOW}[5/10] Collecting Django static files...${NC}"
cd "$PROJECT_DIR"
source "$VENV_DIR/bin/activate"
python manage.py collectstatic --noinput
deactivate

# Step 6: Set proper permissions
echo -e "${YELLOW}[6/10] Setting file permissions...${NC}"
chown -R www-data:www-data "$PROJECT_DIR"
chmod -R 755 "$PROJECT_DIR"

# Step 7: Copy Nginx configuration
echo -e "${YELLOW}[7/10] Configuring Nginx...${NC}"
if [ -f "/home/user/inhealthUSA/deployment_configs/nginx_ssl.conf" ]; then
    # Replace placeholders in nginx config
    sed -e "s/yourdomain.com/$DOMAIN/g" \
        -e "s/www.yourdomain.com/$WWW_DOMAIN/g" \
        /home/user/inhealthUSA/deployment_configs/nginx_ssl.conf > "$NGINX_CONF"

    # Enable site
    ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/

    # Remove default site
    rm -f /etc/nginx/sites-enabled/default

    # Test configuration
    nginx -t
else
    echo -e "${RED}Nginx configuration template not found${NC}"
    exit 1
fi

# Step 8: Obtain SSL certificate
echo -e "${YELLOW}[8/10] Obtaining SSL certificate from Let's Encrypt...${NC}"
echo "This will request a certificate for: $DOMAIN and $WWW_DOMAIN"
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    certbot --nginx -d "$DOMAIN" -d "$WWW_DOMAIN" --email "$EMAIL" --agree-tos --no-eff-email --redirect
else
    echo -e "${YELLOW}Skipping SSL certificate generation${NC}"
fi

# Step 9: Set up systemd service
echo -e "${YELLOW}[9/10] Setting up systemd service...${NC}"
if [ -f "/home/user/inhealthUSA/deployment_configs/inhealth.service" ]; then
    cp /home/user/inhealthUSA/deployment_configs/inhealth.service "$SERVICE_FILE"

    # Reload systemd
    systemctl daemon-reload

    # Enable and start service
    systemctl enable inhealth
    systemctl restart inhealth

    # Check status
    systemctl status inhealth --no-pager
else
    echo -e "${RED}Systemd service file not found${NC}"
    exit 1
fi

# Step 10: Configure firewall
echo -e "${YELLOW}[10/10] Configuring firewall...${NC}"
if command -v ufw &> /dev/null; then
    ufw allow 'Nginx Full'
    ufw allow OpenSSH
    ufw --force enable
    ufw status
fi

# Final checks
echo -e "\n${GREEN}=== Setup Complete! ===${NC}\n"
echo "Testing SSL certificate..."
certbot certificates

echo -e "\n${GREEN}Services Status:${NC}"
systemctl status nginx --no-pager | head -5
systemctl status inhealth --no-pager | head -5

echo -e "\n${GREEN}Next Steps:${NC}"
echo "1. Visit https://$DOMAIN to test your application"
echo "2. Check logs: sudo tail -f /var/log/inhealth/error.log"
echo "3. Monitor Nginx: sudo tail -f /var/log/nginx/inhealth_error.log"
echo "4. Certificate auto-renewal test: sudo certbot renew --dry-run"
echo -e "\n${GREEN}Useful Commands:${NC}"
echo "- Restart application: sudo systemctl restart inhealth"
echo "- Reload Nginx: sudo systemctl reload nginx"
echo "- Check certificate: sudo certbot certificates"
echo "- Renew certificate: sudo certbot renew"
