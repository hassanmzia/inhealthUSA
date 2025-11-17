# IoT Cron Job Email Troubleshooting Guide

## Problem

The cron job that processes IoT device data can't send critical alert emails, but manual vital sign entry can send emails successfully.

**Error Message:**
```
Failed to send email to hassanmzia@gmail.com: (530, b'5.7.0 Authentication Required. For more information, go to
5.7.0  https://support.google.com/accounts/troubleshooter/2402620. af79cd13be357-8b2dce77d27sm444328885a.13 - gsmtp', 'noreply@inhealthehr.com'
```

## Root Cause

Cron jobs run in a minimal environment without access to:
- Environment variables (like email credentials)
- Virtual environment activation
- Proper PATH settings
- Django settings configuration

When you run commands manually, your shell has access to all these settings, but cron doesn't.

## Solution Options

### Option 1: Use the Wrapper Script (Recommended)

We've created a wrapper script that properly sets up the environment before running the management command.

**Step 1: Edit the wrapper script**

Edit `/home/zia/ihealth/inhealthUSA/django_inhealth/scripts/process_iot_data_cron.sh` and configure your environment:

```bash
#!/bin/bash
PROJECT_DIR="/home/zia/ihealth/inhealthUSA/django_inhealth"

cd "$PROJECT_DIR" || exit 1

# Option A: Load from .env file (recommended)
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

# Option B: Or set environment variables directly here
# export DJANGO_SETTINGS_MODULE="inhealth.settings"
# export EMAIL_HOST="smtp.gmail.com"
# export EMAIL_PORT="587"
# export EMAIL_HOST_USER="your-email@gmail.com"
# export EMAIL_HOST_PASSWORD="your-app-password"  # Use Gmail App Password
# export EMAIL_USE_TLS="True"
# export DEFAULT_FROM_EMAIL="noreply@inhealthehr.com"

# Activate virtual environment
if [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
    source "$PROJECT_DIR/venv/bin/activate"
fi

# Run the Django management command
python manage.py process_iot_data

exit $?
```

**Step 2: Update your crontab**

Instead of calling Python directly, call the wrapper script:

```bash
# Edit crontab
crontab -e

# Replace your current entry with:
* * * * * /home/zia/ihealth/inhealthUSA/django_inhealth/scripts/process_iot_data_cron.sh >> /var/log/iot_processing.log 2>&1
```

### Option 2: Set Environment Variables in Crontab

You can set environment variables directly in your crontab file:

```bash
# Edit crontab
crontab -e

# Add these lines at the top of your crontab:
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
DJANGO_SETTINGS_MODULE=inhealth.settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@inhealthehr.com

# Then your cron job:
* * * * * cd /home/zia/ihealth/inhealthUSA/django_inhealth && /home/zia/ihealth/inhealthUSA/django_inhealth/venv/bin/python manage.py process_iot_data >> /var/log/iot_processing.log 2>&1
```

### Option 3: Use a .env File (Most Secure)

**Step 1: Create a .env file**

Create `/home/zia/ihealth/inhealthUSA/django_inhealth/.env`:

```bash
DJANGO_SETTINGS_MODULE=inhealth.settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@inhealthehr.com
```

**Step 2: Secure the .env file**

```bash
chmod 600 /home/zia/ihealth/inhealthUSA/django_inhealth/.env
```

**Step 3: Use the wrapper script** (which loads the .env file)

The wrapper script we created automatically loads the .env file if it exists.

## Gmail-Specific Configuration

### Generate App Password

If you're using Gmail, you need an **App Password** (not your regular Gmail password):

1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to Security
3. Enable 2-Step Verification if not already enabled
4. Go to "App passwords"
5. Generate a new app password for "Mail"
6. Use this 16-character password in your EMAIL_HOST_PASSWORD setting

### Gmail SMTP Settings

```
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-16-char-app-password'
DEFAULT_FROM_EMAIL = 'noreply@inhealthehr.com'
```

## Testing

### Test the wrapper script manually

```bash
# Run the wrapper script manually to test
/home/zia/ihealth/inhealthUSA/django_inhealth/scripts/process_iot_data_cron.sh

# Check for any errors
echo $?  # Should return 0 if successful
```

### Test email sending from cron environment

Create a test script:

```bash
#!/bin/bash
cd /home/zia/ihealth/inhealthUSA/django_inhealth
source venv/bin/activate
python manage.py shell <<EOF
from django.core.mail import send_mail
from django.conf import settings

print("Testing email configuration...")
print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'NOT SET')}")
print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'NOT SET')}")
print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'NOT SET')}")
print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'NOT SET')}")

try:
    send_mail(
        'Test Email from Cron',
        'If you receive this, email configuration is working!',
        'noreply@inhealthehr.com',
        ['hassanmzia@gmail.com'],
        fail_silently=False,
    )
    print("Email sent successfully!")
except Exception as e:
    print(f"Email failed: {str(e)}")
EOF
```

### Verify cron is using the wrapper

Check cron execution:

```bash
# View cron log
tail -f /var/log/iot_processing.log

# Check if cron job is running
grep process_iot_data /var/log/syslog
```

## Debugging

### Check current email settings

```bash
cd /home/zia/ihealth/inhealthUSA/django_inhealth
source venv/bin/activate
python manage.py shell

# Then in the shell:
from django.conf import settings
print("EMAIL_HOST:", settings.EMAIL_HOST)
print("EMAIL_PORT:", settings.EMAIL_PORT)
print("EMAIL_HOST_USER:", settings.EMAIL_HOST_USER)
print("EMAIL_USE_TLS:", settings.EMAIL_USE_TLS)
```

### Check if environment variables are accessible

Add debug output to the wrapper script:

```bash
#!/bin/bash
echo "=== Environment Debug ==="
echo "Current user: $(whoami)"
echo "Current directory: $(pwd)"
echo "Python path: $(which python)"
echo "EMAIL_HOST: $EMAIL_HOST"
echo "EMAIL_HOST_USER: $EMAIL_HOST_USER"
echo "========================="
```

### Common Issues

1. **Wrong email password**: Use Gmail App Password, not regular password
2. **2-Step Verification not enabled**: Required for App Passwords
3. **Firewall blocking port 587**: Check with `telnet smtp.gmail.com 587`
4. **Virtual environment not activated**: Make sure venv is activated in cron
5. **Wrong Python interpreter**: Use full path to venv Python

## Verification Checklist

- [ ] Gmail App Password generated and configured
- [ ] .env file created with correct credentials (or environment variables set)
- [ ] .env file has restricted permissions (600)
- [ ] Wrapper script is executable (`chmod +x`)
- [ ] Wrapper script paths are correct
- [ ] Crontab updated to use wrapper script
- [ ] Manual test of wrapper script successful
- [ ] Test email sent successfully from cron environment
- [ ] Cron log shows successful processing

## Alternative Email Backends

If Gmail continues to have issues, consider:

### SendGrid

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'
```

### AWS SES

```python
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_SES_REGION_NAME = 'us-east-1'
```

### Mailgun

```python
EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
ANYMAIL = {
    "MAILGUN_API_KEY": "your-api-key",
    "MAILGUN_SENDER_DOMAIN": "yourdomain.com",
}
```

## Support

If issues persist:

1. Check Django logs: `/var/log/django/error.log`
2. Check email backend: `python manage.py sendtestemail hassanmzia@gmail.com`
3. Verify DNS/network: `nslookup smtp.gmail.com`
4. Check firewall: `sudo iptables -L | grep 587`
5. Review Gmail security: https://myaccount.google.com/lesssecureapps

## Quick Fix Command

Run this to quickly set up the cron job with the wrapper:

```bash
# Make wrapper executable
chmod +x /home/zia/ihealth/inhealthUSA/django_inhealth/scripts/process_iot_data_cron.sh

# Test wrapper manually
/home/zia/ihealth/inhealthUSA/django_inhealth/scripts/process_iot_data_cron.sh

# If successful, update crontab
(crontab -l 2>/dev/null; echo "* * * * * /home/zia/ihealth/inhealthUSA/django_inhealth/scripts/process_iot_data_cron.sh >> /var/log/iot_processing.log 2>&1") | crontab -

# Verify
crontab -l
```
