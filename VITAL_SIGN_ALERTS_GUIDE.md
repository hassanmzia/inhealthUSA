# Vital Sign Alert System - User Guide

The InHealth EHR Vital Sign Alert System automatically monitors patient vital signs and sends notifications to patients, doctors, and nurses when critical values are detected.

## Table of Contents

1. [Overview](#overview)
2. [Alert Levels](#alert-levels)
3. [Notification Recipients](#notification-recipients)
4. [Notification Methods](#notification-methods)
5. [Notification Preferences](#notification-preferences)
6. [Quiet Hours](#quiet-hours)
7. [For Patients](#for-patients)
8. [For Doctors](#for-doctors)
9. [For Nurses](#for-nurses)
10. [Configuration](#configuration)
11. [Troubleshooting](#troubleshooting)

## Overview

The Vital Sign Alert System monitors the following vital signs:
- **Heart Rate** (HR)
- **Blood Pressure** - Systolic and Diastolic (BP)
- **Temperature** (Temp)
- **Respiratory Rate** (RR)
- **Oxygen Saturation** (SpO2)
- **Blood Glucose** (Glucose)

When any vital sign falls outside the normal range, the system automatically:
1. Determines the severity level (Emergency/Critical/Warning)
2. Identifies who should be notified (Patient, Doctor, Nurses)
3. Sends notifications via email and/or SMS
4. Logs the alert for record keeping

## Alert Levels

The system categorizes vital sign alerts into three severity levels:

### 1. Emergency (Blue Alert) 🚨
- **Severity:** Life-threatening
- **Action Required:** Immediate medical intervention
- **Notified:** Patient, Doctor, All Nurses
- **Example:** Heart rate < 40 or > 150, Oxygen saturation < 90%

### 2. Critical (Red Alert) 🔴
- **Severity:** Requires doctor attention
- **Action Required:** Contact doctor, schedule appointment
- **Notified:** Patient, Doctor, All Nurses
- **Example:** Heart rate 40-50 or 130-150, Blood pressure severely elevated

### 3. Warning (Orange Alert) ⚠️
- **Severity:** Abnormal but not immediately dangerous
- **Action Required:** Monitor closely, contact nurse if worsening
- **Notified:** Patient, Doctor, All Nurses
- **Example:** Slightly elevated blood pressure, minor temperature changes

## Notification Recipients

### Who Gets Notified?

For **ALL** critical vital signs (Emergency, Critical, and Warning levels):

| Recipient | Notified | Email | SMS |
|-----------|----------|-------|-----|
| **Patient** | ✅ Always | ✅ Default ON | ⚠️ Default OFF |
| **Doctor** | ✅ Always | ✅ Default ON | ⚠️ Optional |
| **All Nurses** | ✅ Always | ✅ Default ON | ⚠️ Optional |

**Note:** Previously, only emergency and critical alerts would notify patients and doctors, while warning alerts only notified nurses. Now, **all critical vital signs notify everyone** for better patient safety.

## Notification Methods

### Email Notifications

- **Format:** HTML email with color-coded alert levels
- **Content:**
  - Alert severity (Emergency/Critical/Warning)
  - Patient name
  - List of critical vital signs with values
  - Recommended actions
  - Timestamp

- **Example:**
  ```
  Subject: 🚨 Critical Vital Signs Alert - John Doe

  EMERGENCY ALERT
  Critical Vital Signs Detected

  Patient: John Doe
  Alert Time: November 16, 2025 - 03:45 PM

  Critical Vitals:
  - Heart Rate: 155 (EMERGENCY)
  - Oxygen Saturation: 88% (EMERGENCY)

  IMMEDIATE ACTION REQUIRED
  ```

### SMS Notifications

- **Format:** Plain text message
- **Content:** Brief summary of critical vitals (max 3)
- **Requires:** Twilio account configuration
- **Example:**
  ```
  🚨 InHealth Alert: Critical vitals for John Doe.
  Heart Rate: 155 (EMERGENCY).
  Oxygen Saturation: 88% (EMERGENCY).
  Please check your email for details.
  ```

## Notification Preferences

Users can customize how they receive vital sign alerts through their notification preferences.

### Accessing Notification Preferences

1. Log in to InHealth EHR
2. Go to **Settings** → **Notification Preferences**
3. Or via Django Admin (for administrators)

### Available Settings

#### Email Notifications
- **Email Enabled:** Master switch for all email notifications
- **Emergency Alerts:** Receive emergency-level alerts via email (Default: ON)
- **Critical Alerts:** Receive critical-level alerts via email (Default: ON)
- **Warning Alerts:** Receive warning-level alerts via email (Default: ON)

#### SMS Notifications
- **SMS Enabled:** Master switch for all SMS notifications (Default: OFF)
- **Emergency SMS:** Receive emergency alerts via SMS (Default: ON if SMS enabled)
- **Critical SMS:** Receive critical alerts via SMS (Default: ON if SMS enabled)
- **Warning SMS:** Receive warning alerts via SMS (Default: OFF)

**Note:** SMS notifications require Twilio configuration and may incur charges.

## Quiet Hours

Quiet hours allow you to suppress non-emergency notifications during specific times (e.g., sleeping hours).

### How Quiet Hours Work

- **Emergency alerts** (Blue level) are **ALWAYS** sent, even during quiet hours
- **Critical and Warning alerts** are suppressed during quiet hours
- You can set a start and end time (e.g., 10:00 PM to 7:00 AM)
- Supports overnight quiet hours (crossing midnight)

### Setting Up Quiet Hours

1. Enable "Quiet Hours" in notification preferences
2. Set **Start Time** (e.g., 22:00 / 10:00 PM)
3. Set **End Time** (e.g., 07:00 / 7:00 AM)
4. Save preferences

### Example

```
Quiet Hours: 10:00 PM - 7:00 AM

- 11:30 PM: Emergency alert (Heart rate dangerously low) → ✅ SENT
- 11:35 PM: Warning alert (Slightly elevated BP) → ❌ SUPPRESSED
- 2:00 AM: Critical alert (High blood pressure) → ❌ SUPPRESSED
- 7:30 AM: Warning alert (Elevated temperature) → ✅ SENT
```

## For Patients

### What You'll Receive

When your vital signs are critical, you will receive:

1. **Email notification** with:
   - Explanation of what's wrong
   - Your vital sign values
   - Recommended actions to take
   - When to seek medical help

2. **SMS notification** (if enabled):
   - Brief alert about critical vitals
   - Instruction to check email for details

### What You Should Do

#### For Emergency Alerts (🚨):
1. **Call 911** or go to the nearest emergency room immediately
2. Contact your doctor or emergency contact
3. Do NOT ignore these alerts

#### For Critical Alerts (🔴):
1. Contact your doctor as soon as possible
2. Schedule an appointment within 24-48 hours
3. Monitor your symptoms
4. Follow your doctor's previous instructions

#### For Warning Alerts (⚠️):
1. Monitor your condition
2. Take another reading if possible
3. Contact your doctor if symptoms worsen
4. Log any changes or symptoms

### Managing Your Preferences

You can customize your notifications:
- Turn off SMS if you don't want text messages
- Set quiet hours for nighttime
- Keep emergency alerts always enabled

## For Doctors

### What You'll Receive

You will be notified about **ALL** critical vital signs for your patients:

1. **Email with patient details:**
   - Patient name and contact information
   - All critical vital signs with values
   - Alert severity level
   - Recommended clinical actions
   - Timestamp of alert

2. **SMS (if enabled):**
   - Brief summary of patient and vitals
   - Severity level

### What You Should Do

#### For Emergency Alerts (🚨):
1. Contact patient immediately
2. Verify patient's current status and location
3. Call emergency services if needed
4. Review patient's complete medical history
5. Prepare for immediate intervention or hospitalization

#### For Critical Alerts (🔴):
1. Review patient's vital signs history in the system
2. Contact patient for follow-up within 24 hours
3. Schedule immediate appointment if needed
4. Review and adjust medication/treatment plan
5. Consider ordering additional tests

#### For Warning Alerts (⚠️):
1. Review the alert and patient history
2. Determine if follow-up is needed
3. Contact patient if pattern of abnormal vitals
4. Schedule routine follow-up

### Managing Your Preferences

- Enable SMS for emergency alerts for faster response
- Set quiet hours but keep emergency alerts enabled
- Configure email filters to highlight vital sign alerts

## For Nurses

### What You'll Receive

Nurses receive notifications for **ALL** critical vital signs:

1. **Email notifications** for all patients in your:
   - Hospital/Department
   - Assigned patient list

2. **Details included:**
   - Patient name
   - Critical vital signs with values
   - Alert severity
   - Monitoring instructions

### What You Should Do

#### For Emergency Alerts (🚨):
1. Immediately check on patient
2. Notify doctor on call
3. Prepare emergency equipment
4. Document patient status
5. Call emergency response team if needed

#### For Critical Alerts (🔴):
1. Contact patient to assess current condition
2. Record additional vital signs
3. Notify attending physician
4. Document findings in EHR
5. Schedule follow-up measurement

#### For Warning Alerts (⚠️):
1. Monitor patient's condition
2. Re-check vitals within specified timeframe
3. Record any symptoms or changes
4. Contact doctor if condition worsens
5. Document monitoring in patient chart

### Managing Your Preferences

- Enable notifications for your shift hours
- Use quiet hours for off-duty periods
- Keep emergency alerts always enabled
- Consider SMS for high-priority patients

## Configuration

### For Administrators

#### Email Configuration

Edit `django_inhealth/.env`:

```env
# Email Settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

#### SMS Configuration (Twilio)

1. Sign up for Twilio account: https://www.twilio.com/
2. Get your Account SID, Auth Token, and Phone Number
3. Edit `django_inhealth/.env`:

```env
# Twilio SMS Settings
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

#### Testing Alerts

To test the alert system:

```python
# In Django shell
python manage.py shell

from healthcare.models import VitalSign, Encounter
from healthcare.vital_alerts import process_vital_alerts

# Get a test vital sign record
vital_sign = VitalSign.objects.last()

# Manually trigger alerts
process_vital_alerts(vital_sign)
```

### Default Preferences

New users automatically get these default preferences:
- **Email notifications:** Enabled for all alert levels
- **SMS notifications:** Disabled (must opt-in)
- **Quiet hours:** Disabled
- **Digest mode:** Disabled

## Troubleshooting

### Not Receiving Email Alerts

**Check:**
1. Email address is correct in user profile
2. Email notifications are enabled in preferences
3. Check spam/junk folder
4. Verify email settings in `.env` file
5. Check Django logs for email errors

**Solution:**
```bash
# Check email configuration
python manage.py sendtestemail your-email@example.com

# Check Django logs
tail -f /home/user/inhealthUSA/django_inhealth/logs/django.log
```

### Not Receiving SMS Alerts

**Check:**
1. SMS notifications are enabled in preferences
2. Phone number is correct and includes country code
3. Twilio credentials are configured
4. Twilio account has sufficient balance
5. Check Django logs for Twilio errors

**Solution:**
```bash
# Verify Twilio configuration
python manage.py shell

from django.conf import settings
print(f"Twilio SID: {settings.TWILIO_ACCOUNT_SID}")
print(f"Twilio Phone: {settings.TWILIO_PHONE_NUMBER}")
```

### Alerts Sent During Quiet Hours

**Check:**
- Emergency alerts are ALWAYS sent (by design)
- Quiet hours settings are correct
- Time zone settings in Django

**Note:** Emergency alerts bypass quiet hours for patient safety.

### Too Many Alerts

**Solutions:**
1. Adjust alert thresholds (requires admin)
2. Enable digest mode (get summary instead of individual alerts)
3. Disable warning-level alerts
4. Set quiet hours for specific times

### Missing Nurse Notifications

**Check:**
1. Nurses are assigned to the patient's hospital
2. Nurses have `is_active=True` in the system
3. Nurse email addresses are correct
4. Notification preferences are enabled

**Solution:**
```bash
# Check active nurses
python manage.py shell

from healthcare.models import Nurse
active_nurses = Nurse.objects.filter(is_active=True)
print(f"Active nurses: {active_nurses.count()}")
```

## Alert Workflow Diagram

```
Vital Sign Recorded
       ↓
Analyze Vital Sign Values
       ↓
Critical Values Detected?
       ↓ YES
Determine Alert Level
(Emergency/Critical/Warning)
       ↓
Check Notification Preferences
       ↓
┌──────┴──────┬──────────┐
↓             ↓          ↓
PATIENT     DOCTOR    NURSES
↓             ↓          ↓
Email/SMS   Email/SMS  Email/SMS
(if enabled) (if enabled) (if enabled)
       ↓
Log Alert in System
       ↓
Done
```

## Best Practices

### For Healthcare Providers

1. **Review alerts promptly** - Especially emergency and critical levels
2. **Keep contact information updated** - Ensure email and phone are current
3. **Use quiet hours wisely** - Balance rest with patient safety
4. **Enable SMS for emergencies** - Faster response to critical situations
5. **Document responses** - Log actions taken in response to alerts

### For Patients

1. **Don't ignore emergency alerts** - Seek immediate medical attention
2. **Keep your contact info current** - Update email and phone number
3. **Understand your baseline** - Know your normal vital sign ranges
4. **Follow up with your doctor** - Discuss recurring abnormal readings
5. **Enable preferred notification method** - Choose what works best for you

### For System Administrators

1. **Test the system regularly** - Ensure alerts are working
2. **Monitor email delivery** - Check for bounced emails
3. **Review Twilio usage** - Monitor SMS costs and delivery
4. **Keep documentation updated** - Train staff on the system
5. **Backup alert logs** - Maintain records for compliance

## Privacy and Security

- All vital sign data is encrypted in transit and at rest
- Email notifications do not include sensitive medical history
- SMS messages contain minimal patient information
- HIPAA-compliant security measures are in place
- Audit logs track all alert notifications

## Support

For technical issues or questions:
- **Email:** support@inhealthehr.com
- **Documentation:** https://docs.inhealthehr.com
- **Emergency:** Contact system administrator

## Frequently Asked Questions (FAQ)

### Can I turn off all notifications?

Yes, but **strongly discouraged** for patients and medical staff. You can disable email and SMS notifications in your preferences, but consider keeping at least emergency alerts enabled.

### Will I get alerts for every vital sign reading?

No. Alerts are only sent when vital signs are outside normal ranges and meet critical thresholds.

### How many nurses will be notified?

All active nurses in the patient's hospital/department will receive notifications.

### Can I get alerts for specific patients only?

Currently, doctors and nurses receive alerts for all their assigned patients. Contact the administrator for custom filtering.

### What if I miss an emergency alert?

Emergency alerts are sent via multiple channels (email and SMS if enabled). The system also logs all alerts, and patients should seek immediate medical attention for emergency-level vital signs.

### Can family members receive alerts?

Not directly through the system. Patients can forward alert emails to family members or use email forwarding rules. Future versions may include family member notification features.

### How do I know if an alert was successfully sent?

Check the system logs or contact your administrator. The system logs all notification attempts and their status.

## Version Information

- **System Version:** InHealth EHR v2.0
- **Last Updated:** November 16, 2025
- **Alert System Version:** 2.0 (All recipients for all critical vitals)

---

**Important:** This system is designed to assist healthcare providers but does not replace clinical judgment. Always seek immediate medical attention for emergency situations.
