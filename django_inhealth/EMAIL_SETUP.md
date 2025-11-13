# Email Setup Guide for InHealth EHR

This guide explains how to configure email notifications for the InHealth EHR system.

## Prerequisites

- An email account (Gmail, Yahoo, Outlook, or other SMTP-compatible email service)
- Access to email account settings

## Setup Steps

### Option 1: Using Gmail (Recommended)

#### Step 1: Enable 2-Step Verification

1. Go to your Google Account settings: https://myaccount.google.com/
2. Navigate to Security
3. Enable 2-Step Verification if not already enabled

#### Step 2: Generate App Password

1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" as the app
3. Select your device or enter a custom name (e.g., "InHealth EHR")
4. Click "Generate"
5. Copy the 16-character app password (you'll use this instead of your regular password)

#### Step 3: Configure Environment Variables

Add the following to your `.env` file in `django_inhealth/`:

```bash
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your.email@gmail.com
EMAIL_HOST_PASSWORD=your_16_char_app_password
DEFAULT_FROM_EMAIL=InHealth EHR <your.email@gmail.com>
```

Replace:
- `your.email@gmail.com` with your actual Gmail address
- `your_16_char_app_password` with the app password you generated

### Option 2: Using Other Email Providers

#### Yahoo Mail
```bash
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your.email@yahoo.com
EMAIL_HOST_PASSWORD=your_app_password
```

#### Outlook/Hotmail
```bash
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your.email@outlook.com
EMAIL_HOST_PASSWORD=your_password
```

#### Custom SMTP Server
```bash
EMAIL_HOST=your.smtp.server.com
EMAIL_PORT=587  # or 465 for SSL
EMAIL_USE_TLS=True  # or False if using SSL
EMAIL_HOST_USER=your_username
EMAIL_HOST_PASSWORD=your_password
```

### Step 4: Restart Django Server

After configuring the environment variables:

```bash
# Restart your Django development server
python manage.py runserver
```

Or restart your production server (gunicorn, uwsgi, etc.)

## Testing Email Functionality

1. Ensure doctors and patients have valid email addresses in their profiles
2. Compose a message from doctor to patient (or vice versa)
3. Check the "Also send via Email" checkbox
4. Send the message
5. The recipient should receive an email notification at their registered email address

## Email Content

When a message is sent with email notification:

**From Doctor to Patient:**
```
Subject: New message from Dr. [Doctor Name]

You have received a new message from Dr. [Doctor Name]

Subject: [Message Subject]

Message:
[Message Body]

Please log in to your InHealth EHR account to view and reply to this message.

---
InHealth EHR System
This is an automated notification. Please do not reply to this email.
```

**From Patient to Doctor:**
```
Subject: New message from patient [Patient Name]

You have received a new message from patient [Patient Name]

Subject: [Message Subject]

Message:
[Message Body]

Please log in to your InHealth EHR account to view and reply to this message.

---
InHealth EHR System
This is an automated notification. Please do not reply to this email.
```

## Troubleshooting

### "Email server connection failed"
- Check that EMAIL_HOST and EMAIL_PORT are correct
- Verify your internet connection
- Ensure your firewall isn't blocking SMTP connections

### "Email authentication failed"
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are correct
- For Gmail: Make sure you're using an App Password, not your regular password
- For other providers: Check if you need to enable "less secure app access"

### "Email not sent" or timeout errors
- Check if your email provider requires SSL instead of TLS
- Try changing EMAIL_PORT (587 for TLS, 465 for SSL)
- Verify your email provider's SMTP settings

### Email goes to spam folder
- Add a custom DEFAULT_FROM_EMAIL with a recognizable name
- Consider using a dedicated email domain for production
- Implement SPF, DKIM, and DMARC records for your domain

### Email address not in profile
- Doctors: Update email in Provider profile via Django admin
- Patients: Update email in Patient profile via Django admin

## Production Considerations

### Security
1. **Never commit .env files to version control**
2. Use strong, unique passwords for email accounts
3. Enable 2-factor authentication on email accounts
4. Use App Passwords instead of regular passwords when available

### Reliability
1. **Rate Limits**: Most email providers have sending limits (Gmail: 500/day for free accounts)
2. **Monitoring**: Monitor email delivery failures and bounces
3. **Queue**: For high-volume, consider using a message queue (Celery + Redis)
4. **Service**: Consider using dedicated email services like SendGrid, Mailgun, or Amazon SES for production

### Compliance
1. **HIPAA**: Ensure email service is HIPAA-compliant for healthcare data
2. **Encryption**: Use TLS/SSL for all email transmissions
3. **Opt-out**: Implement email opt-out functionality
4. **Retention**: Follow email retention policies for healthcare records

## Alternative Email Backends

For development/testing without a real email server:

### Console Backend (prints to console)
```python
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### File Backend (saves to files)
```python
EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
EMAIL_FILE_PATH=/tmp/app-emails
```

### Dummy Backend (discards all emails)
```python
EMAIL_BACKEND=django.core.mail.backends.dummy.EmailBackend
```

## Getting Help

- **Django Email Documentation**: https://docs.djangoproject.com/en/4.2/topics/email/
- **Gmail App Passwords**: https://support.google.com/accounts/answer/185833
- **InHealth EHR Support**: Contact your system administrator

## Common SMTP Settings Reference

| Provider | SMTP Server | Port | TLS |
|----------|-------------|------|-----|
| Gmail | smtp.gmail.com | 587 | Yes |
| Yahoo | smtp.mail.yahoo.com | 587 | Yes |
| Outlook | smtp.office365.com | 587 | Yes |
| iCloud | smtp.mail.me.com | 587 | Yes |
| AOL | smtp.aol.com | 587 | Yes |
| Zoho | smtp.zoho.com | 587 | Yes |
