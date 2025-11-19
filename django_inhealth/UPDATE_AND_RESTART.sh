#!/bin/bash
# Script to pull latest changes and restart the application

set -e

echo "=========================================="
echo "Updating InHealth EHR Application"
echo "=========================================="
echo ""

cd /home/zia/ihealth/inhealthUSA/django_inhealth

echo "1. Pulling latest code..."
git pull

echo ""
echo "2. Restarting gunicorn service..."
sudo systemctl restart gunicorn

echo ""
echo "3. Checking service status..."
sudo systemctl status gunicorn --no-pager | head -10

echo ""
echo "=========================================="
echo "✅ Update Complete!"
echo "=========================================="
echo ""
echo "Test your application:"
echo "  Homepage: https://inhealth.eminencetechsolutions.com:8899/"
echo "  MFA Verify: https://inhealth.eminencetechsolutions.com:8899/mfa/verify/"
echo ""
