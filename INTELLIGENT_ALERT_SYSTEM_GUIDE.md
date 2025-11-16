# Intelligent Two-Stage Vital Sign Alert System

## Overview

The InHealth EHR system features an intelligent two-stage alert system that respects patient autonomy while ensuring timely medical intervention when needed. Instead of immediately notifying healthcare providers, the system first asks patients for permission, allowing them to decide who should be contacted.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [How It Works](#how-it-works)
3. [Patient Experience](#patient-experience)
4. [Provider Experience](#provider-experience)
5. [Auto-Escalation Safety Net](#auto-escalation-safety-net)
6. [Setup and Configuration](#setup-and-configuration)
7. [Management Commands](#management-commands)
8. [Database Schema](#database-schema)
9. [API Endpoints](#api-endpoints)
10. [Troubleshooting](#troubleshooting)

---

## System Architecture

### Two-Stage Process

**Stage 1: Patient Permission Request**
- Critical vital signs detected
- System creates `VitalSignAlertResponse` record
- Patient receives notification via Email/SMS/WhatsApp
- Patient is asked to choose who to notify

**Stage 2: Provider Notification**
- Triggered by patient response OR auto-escalation
- Notifications sent only to selected providers
- System tracks who was notified and when
- If patient declines, no provider notifications sent

### Key Components

1. **VitalSignAlertResponse Model** (`models.py`)
   - Tracks each alert and patient response
   - Manages auto-escalation logic
   - Records notification history

2. **Alert Processing** (`vital_alerts.py`)
   - `process_vital_alerts()`: Stage 1 - Creates alert and sends permission request
   - `send_alert_to_providers()`: Stage 2 - Notifies selected providers
   - Permission request functions for Email/SMS/WhatsApp

3. **Response Handling** (`views.py` + `urls.py`)
   - Web interface for patient responses
   - Token-based authentication for security
   - Multiple action endpoints

4. **Auto-Escalation** (Management Command)
   - Checks for timed-out alerts
   - Automatically escalates after timeout period
   - Ensures no critical alert is missed

---

## How It Works

### 1. Critical Vital Signs Detected

When a patient's vital signs enter critical ranges:

```python
# Example: Heart rate = 150 bpm (red zone)
vital_sign = VitalSign.objects.create(
    encounter=encounter,
    heart_rate=150,
    # ... other vitals
)

# This triggers the alert system
from healthcare.vital_alerts import process_vital_alerts
process_vital_alerts(vital_sign)
```

### 2. Alert Creation

The system creates a `VitalSignAlertResponse` record:

```python
alert_response = VitalSignAlertResponse.objects.create(
    vital_sign=vital_sign,
    patient=patient,
    alert_type='emergency',  # or 'critical', 'warning'
    critical_vitals_json=[...],
    response_token='<unique-uuid>',
    patient_response_status='pending',
    timeout_minutes=15
)
```

### 3. Patient Notification

Patient receives notification via their preferred channels:

**Email**: Interactive HTML email with buttons
- ✅ Notify My Doctor
- ✅ Notify Nursing Staff
- ✅ Call Emergency Services (EMS)
- ✅ Notify Everyone
- ❌ I'm Fine - No Action Needed

**SMS**: Text message with response link

**WhatsApp**: Rich message with formatted vital signs and action links

### 4. Patient Response

Patient clicks their choice, which triggers:

```python
# URL: /vital-alert/respond/<token>/approve_doctor/
alert_response.process_patient_response('approve_doctor', 'email')
```

This method:
1. Updates patient's decision flags
2. Calls `send_alert_to_providers()`
3. Sends notifications only to selected recipients
4. Marks alert as completed

### 5. Provider Notification (Stage 2)

Only the selected providers are notified:

```python
if alert_response.patient_wants_doctor:
    # Notify doctor via email, SMS, WhatsApp

if alert_response.patient_wants_nurse:
    # Notify nurses

if alert_response.patient_wants_ems:
    # Notify EMS
```

### 6. Auto-Escalation (If No Response)

If patient doesn't respond within timeout period:

```bash
# Run via cron job every 5 minutes
python manage.py check_vital_alert_timeouts
```

System automatically:
1. Marks alert as 'timeout'
2. Notifies doctor (safety default)
3. Records auto-escalation time

---

## Patient Experience

### Receiving an Alert

**Email Example:**

```
Subject: 🚨 Health Alert - Your Response Needed - John Doe

Critical Vital Signs Detected:
- Heart Rate: 150 bpm (Contact Provider)
- Blood Pressure: 180/110 mmHg (Contact Provider)

Who would you like us to notify?

[Notify My Doctor] [Notify Nurse] [Call EMS] [Notify All] [I'm Fine]

⏰ Please respond within 15 minutes, or we will automatically notify your doctor.
```

**SMS Example:**

```
🚨 HEALTH ALERT: 2 critical vital sign(s) detected for John Doe.
Should we notify your healthcare team? Respond: https://inhealth.com/vital-alert/respond/abc123
```

**WhatsApp Example:**

```
🚨 *EMERGENCY HEALTH ALERT*

*InHealth EHR - Your Response Needed*
Patient: *John Doe*

*Critical Vital Signs Detected:*
🔴 Heart Rate: *150 bpm* (Contact Provider)
🔴 Blood Pressure: *180/110 mmHg* (Contact Provider)

*Would you like us to notify your healthcare team?*

1️⃣ Notify Doctor: [link]
2️⃣ Notify Nurse: [link]
3️⃣ Call EMS: [link]
4️⃣ Notify All: [link]
❌ No Action Needed: [link]

⏰ *Please respond within 15 minutes, or we will automatically notify your doctor.*
```

### Response Options

| Option | What Happens |
|--------|--------------|
| **Notify My Doctor** | Your assigned physician receives alert via email, SMS, and WhatsApp |
| **Notify Nursing Staff** | All active nurses at your hospital receive alert |
| **Call EMS** | Emergency services are contacted immediately |
| **Notify Everyone** | Doctor, nurses, AND EMS are all notified |
| **I'm Fine - No Action** | No notifications sent; alert marked as declined |

### After Responding

Patient sees confirmation page showing:
- Their selected action
- Who was notified
- What happens next
- Emergency contact information

---

## Provider Experience

### No Alert (If Patient Declines)

If patient selects "I'm Fine - No Action Needed":
- ✅ Patient's decision is respected
- ❌ No provider notifications sent
- 📊 Alert recorded for future reference

### Alert Received (If Patient Approves)

Provider receives notification including:

**Email:**
- Patient name and ID
- Critical vital signs with values
- Timestamp of alert
- Patient's decision (approved via email/SMS/web)
- Recommended actions

**SMS:**
- Concise alert with top 3 critical vitals
- Link to full details in email

**WhatsApp:**
- Formatted vital signs
- Visual status indicators (🔴🔵🟠)
- Patient decision context

### Admin Dashboard

Healthcare administrators can view all alerts:

```
Django Admin > Healthcare > Vital Sign Alert Responses

Filters:
- Status (pending, approved, declined, timeout, completed)
- Alert Type (emergency, critical, warning)
- Auto-escalated (Yes/No)
- Date Range

Columns:
- Alert ID
- Patient
- Alert Type
- Patient Response Status
- Doctor Notified
- Nurse Notified
- EMS Notified
- Auto-escalated
- Created At
```

---

## Auto-Escalation Safety Net

### Why Auto-Escalation?

Patient safety is paramount. If a patient:
- Doesn't see the alert
- Is unable to respond
- Loses consciousness
- Ignores the alert

The system ensures providers are still notified.

### How It Works

```python
# In VitalSignAlertResponse model
def should_auto_escalate(self):
    """Check if alert should be auto-escalated"""
    if self.patient_response_status != 'pending':
        return False

    if self.auto_escalated:
        return False

    time_elapsed = timezone.now() - self.created_at
    timeout_delta = timedelta(minutes=self.timeout_minutes)

    return time_elapsed >= timeout_delta

def auto_escalate(self):
    """Auto-escalate to doctor for patient safety"""
    self.auto_escalated = True
    self.auto_escalation_time = timezone.now()
    self.patient_response_status = 'timeout'

    # Default: notify doctor for safety
    self.patient_wants_doctor = True
    self.save()

    # Send notifications to doctor
    send_alert_to_providers(self)
```

### Default Escalation Behavior

When auto-escalation occurs:
- ✅ Doctor is ALWAYS notified (safety default)
- ✅ Alert marked as 'timeout'
- ✅ Auto-escalation time recorded
- ❌ Patient's lack of response noted

### Customization

You can customize auto-escalation in `models.py`:

```python
# Example: Notify everyone on auto-escalation
def auto_escalate(self):
    # ...existing code...

    # Customize who gets notified
    if self.alert_type == 'emergency':
        self.patient_wants_doctor = True
        self.patient_wants_nurse = True
        self.patient_wants_ems = True  # For emergencies
    else:
        self.patient_wants_doctor = True
```

---

## Setup and Configuration

### 1. Database Migration

```bash
cd django_inhealth
python manage.py migrate healthcare
```

This runs migration `0014_add_vital_sign_alert_response.py`.

### 2. Configure Settings

Add to your `.env` or `settings.py`:

```python
# Site URL for generating response links
SITE_URL = 'https://your-domain.com'  # No trailing slash

# EMS Contact Information (optional)
EMS_CONTACT_EMAIL = 'ems-dispatch@hospital.com'
EMS_CONTACT_PHONE = '+18001234567'

# Twilio Configuration (for SMS/WhatsApp)
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = '+15551234567'
TWILIO_WHATSAPP_NUMBER = '+15551234567'  # Optional
```

### 3. Set Up Auto-Escalation Cron Job

**Option A: Cron (Linux/Mac)**

```bash
# Edit crontab
crontab -e

# Add this line (runs every 5 minutes)
*/5 * * * * cd /path/to/django_inhealth && /path/to/venv/bin/python manage.py check_vital_alert_timeouts >> /var/log/alert_escalation.log 2>&1
```

**Option B: Celery Beat (Recommended for Production)**

```python
# celerybeat-schedule.py
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'check-vital-alert-timeouts': {
        'task': 'healthcare.tasks.check_vital_alert_timeouts',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
}
```

**Option C: Django-Cron**

```python
# healthcare/cron.py
from django_cron import CronJobBase, Schedule

class CheckVitalAlertTimeouts(CronJobBase):
    RUN_EVERY_MINS = 5

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'healthcare.check_vital_alert_timeouts'

    def do(self):
        from django.core.management import call_command
        call_command('check_vital_alert_timeouts')
```

### 4. Configure Email Templates

Ensure templates exist:
- `healthcare/email/patient_permission_request.html`
- `healthcare/email/vital_alert_email.html` (for providers)

### 5. Test the System

```bash
# Test auto-escalation without actually sending
python manage.py check_vital_alert_timeouts --dry-run --verbose

# Test with actual escalation
python manage.py check_vital_alert_timeouts --verbose
```

---

## Management Commands

### check_vital_alert_timeouts

Checks for timed-out alerts and auto-escalates them.

**Usage:**

```bash
# Normal operation
python manage.py check_vital_alert_timeouts

# Dry run (see what would be escalated)
python manage.py check_vital_alert_timeouts --dry-run

# Verbose output
python manage.py check_vital_alert_timeouts --verbose

# Both
python manage.py check_vital_alert_timeouts --dry-run --verbose
```

**Output Example:**

```
======================================================================
Checking for timed-out vital sign alerts...
Time: 2025-11-16 15:30:00+00:00
======================================================================
Found 3 pending alerts
Escalating Alert #42 for John Doe (elapsed: 16.2 min, timeout: 15 min)
✓ Alert #42 auto-escalated successfully
======================================================================
Successfully escalated 1 alert(s)
======================================================================
```

**Scheduling:**

```bash
# Every 5 minutes (recommended)
*/5 * * * * python manage.py check_vital_alert_timeouts

# Every 1 minute (aggressive)
* * * * * python manage.py check_vital_alert_timeouts

# Every 10 minutes (conservative)
*/10 * * * * python manage.py check_vital_alert_timeouts
```

---

## Database Schema

### VitalSignAlertResponse Model

```sql
CREATE TABLE vital_sign_alert_responses (
    alert_id SERIAL PRIMARY KEY,
    vital_sign_id INTEGER REFERENCES healthcare_vitalsign(id),
    patient_id INTEGER REFERENCES healthcare_patient(id),

    -- Alert Details
    alert_type VARCHAR(20),  -- 'emergency', 'critical', 'warning'
    critical_vitals_json JSONB,

    -- Patient Response
    patient_response_status VARCHAR(20) DEFAULT 'pending',
    patient_wants_doctor BOOLEAN DEFAULT FALSE,
    patient_wants_nurse BOOLEAN DEFAULT FALSE,
    patient_wants_ems BOOLEAN DEFAULT FALSE,
    patient_response_time TIMESTAMP NULL,
    patient_response_method VARCHAR(20) NULL,

    -- Auto-escalation
    timeout_minutes INTEGER DEFAULT 15,
    auto_escalated BOOLEAN DEFAULT FALSE,
    auto_escalation_time TIMESTAMP NULL,

    -- Notifications Sent
    doctor_notified BOOLEAN DEFAULT FALSE,
    nurse_notified BOOLEAN DEFAULT FALSE,
    ems_notified BOOLEAN DEFAULT FALSE,
    notifications_sent_at TIMESTAMP NULL,

    -- Security
    response_token VARCHAR(100) UNIQUE NOT NULL,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_response_status_created
    ON vital_sign_alert_responses(patient_response_status, created_at);

CREATE INDEX idx_patient_created
    ON vital_sign_alert_responses(patient_id, created_at DESC);

CREATE INDEX idx_response_token
    ON vital_sign_alert_responses(response_token);
```

### Status Workflow

```
pending → (patient responds) → approved_* → completed
        → (timeout) → timeout → completed
        → (patient declines) → declined
```

**Status Values:**
- `pending`: Waiting for patient response
- `approved_doctor`: Patient approved - notify doctor
- `approved_nurse`: Patient approved - notify nurse
- `approved_ems`: Patient approved - notify EMS
- `approved_all`: Patient approved - notify all
- `declined`: Patient declined notification
- `timeout`: No response - auto-escalated
- `completed`: Notifications sent

---

## API Endpoints

### Patient Response Endpoints

All endpoints are **public** (no authentication required) for accessibility via email/SMS links.

#### 1. Response Form (GET)

```
GET /vital-alert/respond/<token>/
```

Shows interactive form for patient to select action.

**Example:**
```
GET /vital-alert/respond/a1b2c3d4-5678-90ef-ghij-klmnopqrstuv/
```

Returns HTML page with buttons for each action.

#### 2. Process Response (GET)

```
GET /vital-alert/respond/<token>/<action>/
```

Processes patient's selected action.

**Actions:**
- `approve_doctor`
- `approve_nurse`
- `approve_ems`
- `approve_all`
- `decline`

**Examples:**
```
GET /vital-alert/respond/a1b2c3d4-5678-90ef-ghij-klmnopqrstuv/approve_doctor/
GET /vital-alert/respond/a1b2c3d4-5678-90ef-ghij-klmnopqrstuv/decline/
```

**Optional Query Parameter:**
```
?method=email  # Track response method (email, sms, whatsapp, web)
```

**Responses:**

Success (200):
```html
<!-- response_success.html -->
Shows confirmation and next steps
```

Already Processed (200):
```html
<!-- response_already_processed.html -->
Shows previous response status
```

Error (200):
```html
<!-- response_error.html -->
Shows error message and help
```

### URL Configuration

```python
# healthcare/urls.py
urlpatterns = [
    # ... other patterns ...

    path('vital-alert/respond/<str:token>/',
         views.vital_alert_respond,
         name='vital_alert_respond'),

    path('vital-alert/respond/<str:token>/<str:action>/',
         views.vital_alert_respond,
         name='vital_alert_respond_action'),
]
```

---

## Troubleshooting

### Issue: Patients not receiving notifications

**Check:**
1. Email/SMS/WhatsApp settings in `NotificationPreferences`
2. Twilio credentials in settings
3. Email server configuration
4. Patient contact information (email, phone)

**Debug:**
```python
from healthcare.models import Patient, NotificationPreferences

patient = Patient.objects.get(id=1)
prefs = NotificationPreferences.objects.get(user=patient.user)

print(f"Email enabled: {prefs.email_enabled}")
print(f"SMS enabled: {prefs.sms_enabled}")
print(f"WhatsApp enabled: {prefs.whatsapp_enabled}")
print(f"Patient email: {patient.email}")
print(f"Patient phone: {patient.phone}")
```

### Issue: Auto-escalation not working

**Check:**
1. Cron job is running: `crontab -l`
2. Management command works: `python manage.py check_vital_alert_timeouts --verbose`
3. Timeout period: Default is 15 minutes

**Debug:**
```python
from healthcare.models import VitalSignAlertResponse
from django.utils import timezone

pending = VitalSignAlertResponse.objects.filter(
    patient_response_status='pending',
    auto_escalated=False
)

for alert in pending:
    elapsed = (timezone.now() - alert.created_at).total_seconds() / 60
    print(f"Alert {alert.alert_id}: {elapsed:.1f} min elapsed, timeout: {alert.timeout_minutes}")
    print(f"Should escalate: {alert.should_auto_escalate()}")
```

### Issue: Response links not working

**Check:**
1. `SITE_URL` setting is correct
2. Token is valid: `VitalSignAlertResponse.objects.filter(response_token='...')`
3. Alert is still pending

**Debug:**
```python
token = 'abc123...'
alert = VitalSignAlertResponse.objects.get(response_token=token)

print(f"Status: {alert.patient_response_status}")
print(f"Is pending: {alert.is_pending()}")
print(f"Response time: {alert.patient_response_time}")
```

### Issue: Providers not being notified

**Check:**
1. Patient selected appropriate action
2. Provider has valid contact information
3. Provider's notification preferences
4. Twilio balance (for SMS/WhatsApp)

**Debug:**
```python
alert = VitalSignAlertResponse.objects.get(alert_id=42)

print(f"Wants doctor: {alert.patient_wants_doctor}")
print(f"Wants nurse: {alert.patient_wants_nurse}")
print(f"Wants EMS: {alert.patient_wants_ems}")
print(f"Doctor notified: {alert.doctor_notified}")
print(f"Nurse notified: {alert.nurse_notified}")
print(f"EMS notified: {alert.ems_notified}")
```

### Issue: Alert stuck in pending

**Manual escalation:**
```python
from healthcare.models import VitalSignAlertResponse

alert = VitalSignAlertResponse.objects.get(alert_id=42)
alert.auto_escalate()
```

---

## Best Practices

### 1. Timeout Configuration

**Recommended timeout periods:**
- Emergency alerts: 10-15 minutes
- Critical alerts: 15-20 minutes
- Warning alerts: 20-30 minutes

```python
# Customize in vital_alerts.py
timeout_minutes = 10 if alert_type == 'emergency' else 15
```

### 2. Auto-Escalation Frequency

Run check every 5 minutes for balance between:
- Timely escalation
- Server load
- Database queries

### 3. Patient Education

Ensure patients understand:
- How to recognize alert notifications
- Importance of timely response
- What happens if they don't respond
- How to update notification preferences

### 4. Provider Training

Train healthcare providers on:
- New two-stage system workflow
- How to view alert history in admin
- Patient response patterns
- When to follow up

### 5. Monitoring

Regularly monitor:
- Auto-escalation rate (should be < 30%)
- Response times (average should be < 10 min)
- Declined alerts (may need patient education)
- Provider notification delivery rates

```python
# Example analytics query
from django.db.models import Avg, Count
from healthcare.models import VitalSignAlertResponse

stats = VitalSignAlertResponse.objects.aggregate(
    total=Count('alert_id'),
    auto_escalated_count=Count('alert_id', filter=Q(auto_escalated=True)),
    avg_response_minutes=Avg(
        (F('patient_response_time') - F('created_at')) / 60
    )
)
```

---

## Security Considerations

### 1. Token-Based Authentication

- Tokens are UUIDs (128-bit random)
- One-time use (can't re-submit)
- No user authentication required (accessibility)

### 2. HIPAA Compliance

- All patient data encrypted in transit (HTTPS)
- Alert responses logged for audit trail
- No PHI in URLs (only tokens)
- Secure email/SMS transmission

### 3. Rate Limiting

Consider adding rate limiting to response endpoints:

```python
# Example with Django Ratelimit
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/m')
def vital_alert_respond(request, token, action=None):
    # ...existing code...
```

---

## Future Enhancements

### Planned Features

1. **SMS Reply Support**
   - Patient texts back "1" for doctor, "2" for nurse, etc.
   - Twilio webhook processing

2. **Voice Call Integration**
   - Automated voice call for emergencies
   - IVR menu for response selection

3. **Mobile App Push Notifications**
   - Real-time push notifications
   - In-app response interface

4. **Machine Learning**
   - Predict patient response patterns
   - Adjust timeout based on patient history
   - Suggest appropriate action

5. **Multi-Language Support**
   - Translate notifications
   - Localized templates

---

## Support

For issues or questions:

1. Check this documentation
2. Review Django admin logs
3. Check application logs: `tail -f logs/inhealth.log`
4. Contact technical support

---

## Changelog

### Version 1.0 (2025-11-16)

- ✅ Two-stage intelligent alert system
- ✅ Patient permission requests
- ✅ Email/SMS/WhatsApp support
- ✅ Auto-escalation safety net
- ✅ Web-based response interface
- ✅ Management command for timeout checks
- ✅ Comprehensive admin interface
- ✅ Audit trail and logging

---

## License

Copyright © 2025 InHealth EHR. All rights reserved.
