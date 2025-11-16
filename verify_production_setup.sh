#!/bin/bash
# Verification script for production deployment

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}InHealth EHR - Production Setup Verification${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check Nginx
echo -e "${YELLOW}Checking Nginx...${NC}"
if systemctl is-active --quiet nginx; then
    echo -e "  ${GREEN}✓ Nginx is running${NC}"
    if ss -tlnp 2>/dev/null | grep -q ":443"; then
        echo -e "  ${GREEN}✓ Port 443 (HTTPS) is listening${NC}"
    else
        echo -e "  ${RED}✗ Port 443 (HTTPS) is NOT listening${NC}"
    fi
    if ss -tlnp 2>/dev/null | grep -q ":80"; then
        echo -e "  ${GREEN}✓ Port 80 (HTTP) is listening${NC}"
    else
        echo -e "  ${RED}✗ Port 80 (HTTP) is NOT listening${NC}"
    fi
else
    echo -e "  ${RED}✗ Nginx is NOT running${NC}"
fi

# Check Nginx configuration
if nginx -t 2>/dev/null; then
    echo -e "  ${GREEN}✓ Nginx configuration is valid${NC}"
else
    echo -e "  ${RED}✗ Nginx configuration has errors${NC}"
fi

echo ""

# Check Gunicorn
echo -e "${YELLOW}Checking Gunicorn...${NC}"
if systemctl is-active --quiet inhealth; then
    echo -e "  ${GREEN}✓ Gunicorn service is running${NC}"
else
    echo -e "  ${RED}✗ Gunicorn service is NOT running${NC}"
fi

if ss -tlnp 2>/dev/null | grep -q ":8000"; then
    echo -e "  ${GREEN}✓ Port 8000 is listening (Gunicorn)${NC}"
else
    echo -e "  ${YELLOW}⚠ Port 8000 is NOT listening${NC}"
fi

echo ""

# Check SSL certificates
echo -e "${YELLOW}Checking SSL Certificates...${NC}"
if [ -d "/etc/letsencrypt/live" ]; then
    echo -e "  ${GREEN}✓ Let's Encrypt certificates found${NC}"
    for domain in /etc/letsencrypt/live/*/; do
        if [ -d "$domain" ]; then
            domain_name=$(basename "$domain")
            if [ -f "${domain}fullchain.pem" ]; then
                expiry=$(openssl x509 -enddate -noout -in "${domain}fullchain.pem" 2>/dev/null | cut -d= -f2)
                echo -e "    Domain: ${GREEN}${domain_name}${NC} - Expires: ${expiry}"
            fi
        fi
    done
elif [ -f "/etc/ssl/inhealth/certificate.crt" ]; then
    echo -e "  ${YELLOW}⚠ Self-signed certificate found${NC}"
    expiry=$(openssl x509 -enddate -noout -in /etc/ssl/inhealth/certificate.crt 2>/dev/null | cut -d= -f2)
    echo -e "    Expires: ${expiry}"
else
    echo -e "  ${RED}✗ No SSL certificates found${NC}"
fi

echo ""

# Check Django settings
echo -e "${YELLOW}Checking Django Configuration...${NC}"
if [ -f "/home/user/inhealthUSA/django_inhealth/.env" ]; then
    echo -e "  ${GREEN}✓ .env file exists${NC}"
    if grep -q "DEBUG=False" /home/user/inhealthUSA/django_inhealth/.env 2>/dev/null; then
        echo -e "  ${GREEN}✓ DEBUG is set to False (production mode)${NC}"
    else
        echo -e "  ${YELLOW}⚠ DEBUG might not be set to False${NC}"
    fi
else
    echo -e "  ${RED}✗ .env file not found${NC}"
fi

# Check static files
if [ -d "/home/user/inhealthUSA/django_inhealth/staticfiles" ]; then
    file_count=$(find /home/user/inhealthUSA/django_inhealth/staticfiles -type f 2>/dev/null | wc -l)
    if [ "$file_count" -gt 0 ]; then
        echo -e "  ${GREEN}✓ Static files collected (${file_count} files)${NC}"
    else
        echo -e "  ${YELLOW}⚠ Static files directory is empty${NC}"
    fi
else
    echo -e "  ${RED}✗ Static files directory not found${NC}"
fi

# Check media directory
if [ -d "/home/user/inhealthUSA/django_inhealth/media" ]; then
    echo -e "  ${GREEN}✓ Media directory exists${NC}"
else
    echo -e "  ${YELLOW}⚠ Media directory not found${NC}"
fi

echo ""

# Check permissions
echo -e "${YELLOW}Checking Permissions...${NC}"
if [ -d "/home/user/inhealthUSA/django_inhealth/staticfiles" ]; then
    owner=$(stat -c '%U:%G' /home/user/inhealthUSA/django_inhealth/staticfiles 2>/dev/null)
    if [ "$owner" == "www-data:www-data" ]; then
        echo -e "  ${GREEN}✓ Static files owned by www-data${NC}"
    else
        echo -e "  ${YELLOW}⚠ Static files owner: ${owner} (should be www-data:www-data)${NC}"
    fi
fi

if [ -d "/home/user/inhealthUSA/django_inhealth/media" ]; then
    owner=$(stat -c '%U:%G' /home/user/inhealthUSA/django_inhealth/media 2>/dev/null)
    if [ "$owner" == "www-data:www-data" ]; then
        echo -e "  ${GREEN}✓ Media files owned by www-data${NC}"
    else
        echo -e "  ${YELLOW}⚠ Media files owner: ${owner} (should be www-data:www-data)${NC}"
    fi
fi

echo ""

# Check firewall
echo -e "${YELLOW}Checking Firewall...${NC}"
if command -v ufw &> /dev/null; then
    if ufw status 2>/dev/null | grep -q "80.*ALLOW"; then
        echo -e "  ${GREEN}✓ Port 80 allowed in UFW${NC}"
    else
        echo -e "  ${YELLOW}⚠ Port 80 might not be allowed in UFW${NC}"
    fi
    if ufw status 2>/dev/null | grep -q "443.*ALLOW"; then
        echo -e "  ${GREEN}✓ Port 443 allowed in UFW${NC}"
    else
        echo -e "  ${YELLOW}⚠ Port 443 might not be allowed in UFW${NC}"
    fi
elif command -v firewall-cmd &> /dev/null; then
    if firewall-cmd --list-services 2>/dev/null | grep -q "http"; then
        echo -e "  ${GREEN}✓ HTTP service allowed in firewalld${NC}"
    else
        echo -e "  ${YELLOW}⚠ HTTP service might not be allowed in firewalld${NC}"
    fi
    if firewall-cmd --list-services 2>/dev/null | grep -q "https"; then
        echo -e "  ${GREEN}✓ HTTPS service allowed in firewalld${NC}"
    else
        echo -e "  ${YELLOW}⚠ HTTPS service might not be allowed in firewalld${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠ No firewall detected (ufw or firewalld)${NC}"
fi

echo ""

# Test local connection
echo -e "${YELLOW}Testing Local Connection...${NC}"
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000 2>/dev/null | grep -q "200\|301\|302"; then
    echo -e "  ${GREEN}✓ Gunicorn is responding on port 8000${NC}"
else
    echo -e "  ${YELLOW}⚠ Cannot connect to Gunicorn on port 8000${NC}"
fi

if curl -k -s -o /dev/null -w "%{http_code}" https://localhost 2>/dev/null | grep -q "200\|301\|302"; then
    echo -e "  ${GREEN}✓ Nginx HTTPS is responding${NC}"
else
    echo -e "  ${YELLOW}⚠ Cannot connect to Nginx HTTPS${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Verification Complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "1. Review any warnings or errors above"
echo -e "2. Check logs: ${GREEN}sudo journalctl -u inhealth -n 50${NC}"
echo -e "3. Check Nginx logs: ${GREEN}sudo tail -f /var/log/nginx/inhealth_error.log${NC}"
echo -e "4. Test from external browser: ${GREEN}https://your-domain.com${NC}"
echo ""
