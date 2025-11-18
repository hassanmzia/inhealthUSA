#!/bin/bash
# Quick fix script to rename backup_codes to mfa_backup_codes in code

set -e

cd /home/zia/ihealth/inhealthUSA/django_inhealth

echo "Fixing backup_codes references..."

# Backup the files first
cp healthcare/views.py healthcare/views.py.backup
cp healthcare/mfa_utils.py healthcare/mfa_utils.py.backup

# Replace .backup_codes with .mfa_backup_codes in views.py
sed -i 's/\.backup_codes/.mfa_backup_codes/g' healthcare/views.py

# Replace .backup_codes with .mfa_backup_codes in mfa_utils.py
sed -i 's/\.backup_codes/.mfa_backup_codes/g' healthcare/mfa_utils.py

echo "✅ Fixed! Restarting application..."

# Restart gunicorn
sudo systemctl restart gunicorn

echo ""
echo "✅ Done! The backup_codes attribute error should be fixed."
echo "Test: https://inhealth.eminencetechsolutions.com:8899/mfa/verify/"
