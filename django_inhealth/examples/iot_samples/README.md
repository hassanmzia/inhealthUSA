# IoT Device Sample Data Files

This directory contains comprehensive sample JSON files demonstrating different IoT device data formats and clinical scenarios for testing the inHealth IoT device integration system.

## Overview

These sample files represent real-world clinical scenarios covering various patient populations and conditions. Each file demonstrates proper JSON structure for vital signs data submission via IoT devices, matching the data that nurses would manually enter.

## Sample Files

### Comprehensive Examples

#### 1. Complete Vital Signs (`sample_all_vitals_comprehensive.json`)
**Purpose**: Master reference showing ALL possible vital sign fields from a multi-function device
**Clinical Scenario**: Routine monitoring of stable adult patient
**Device**: DEV001
**Key Features**:
- All vital signs included (heart rate, BP, temperature, respiratory rate, O2 saturation, glucose, weight, height)
- Complete metadata (signal quality, battery level, notes)
- Proper timestamp format (ISO 8601)
- All measurement units specified
- Values within normal adult ranges

**Vital Signs**:
- Heart Rate: 78 bpm (Normal: 60-100)
- Blood Pressure: 118/76 mmHg (Normal: <120/<80)
- Temperature: 98.2°F (Normal: 97-99°F)
- Respiratory Rate: 16/min (Normal: 12-20)
- Oxygen Saturation: 97.5% (Normal: >95%)
- Glucose: 102 mg/dL (Normal: 70-140)
- Weight: 165.5 lbs
- Height: 68 inches

#### 2. Complete Vitals Alternative (`sample_vitals_complete.json`)
**Purpose**: Alternative comprehensive example
**Clinical Scenario**: Standard complete vital signs check
**Device**: DEV001
**Similar to**: sample_all_vitals_comprehensive.json with slightly different values

### Clinical Scenario Examples

#### 3. Morning Vitals - Stable Patient (`sample_morning_vitals.json`)
**Clinical Scenario**: Morning vital signs check for stable hospitalized patient
**Device**: DEV002
**Time**: 07:00 AM
**Patient Status**: Fasting for morning labs
**Key Features**:
- Fasting glucose: 95 mg/dL (excellent control)
- All vitals within normal range
- Patient resting comfortably
- No alerts triggered

**Clinical Notes**: "Morning vitals check - Patient fasting for labs. All vitals stable and within normal limits. Patient reports good sleep. No complaints."

#### 4. Post-Meal Diabetic Patient (`sample_postmeal_diabetic.json`)
**Clinical Scenario**: Diabetic patient 2 hours after meal
**Device**: DEV003
**Time**: 1:30 PM (post-lunch)
**Patient Status**: Type 2 Diabetes, managed with oral medications
**Key Features**:
- Elevated post-meal glucose: 145 mg/dL (expected for diabetic patient)
- Slight tachycardia: 82 bpm
- Otherwise stable vitals
- May trigger glucose monitoring alert

**Clinical Notes**: "Post-meal vitals - Type 2 diabetic patient, 2 hours post-lunch. Glucose at 145 mg/dL (within target range for this patient). Patient states took medication with meal."

#### 5. Elderly Bedtime Vitals (`sample_elderly_bedtime.json`)
**Clinical Scenario**: 75-year-old patient bedtime check
**Device**: DEV004
**Time**: 10:00 PM
**Patient Demographics**: Age 75, male, history of hypertension (controlled)
**Key Features**:
- Slightly elevated BP: 128/82 mmHg (acceptable for age and history)
- Slower heart rate: 68 bpm (normal for elderly at rest)
- Normal weight for height
- All other vitals stable

**Clinical Notes**: "Bedtime vitals for 75-year-old patient. Slight elevation in blood pressure (128/82) - within acceptable range given age and hypertension history. Patient reports feeling well, no dizziness or headache."

#### 6. Post-Exercise Recovery (`sample_postexercise.json`)
**Clinical Scenario**: Athletic patient after cardiac rehabilitation exercise
**Device**: DEV005
**Time**: 4:30 PM (immediately post-exercise)
**Patient Status**: Recovering from MI, in cardiac rehab program
**Key Features**:
- Elevated heart rate: 95 bpm (recovering from exercise, within target zone)
- Slightly elevated respiratory rate: 20/min
- Excellent oxygen saturation: 99%
- All vitals showing appropriate recovery response

**Clinical Notes**: "Post-cardiac rehab exercise vitals. Patient completed 20 minutes of supervised treadmill. Heart rate recovering appropriately. Respiratory rate slightly elevated but returning to baseline. No chest pain or shortness of breath reported."

### Alert-Triggering Scenarios

#### 7. Fever Patient - TRIGGERS ALERT (`sample_fever_patient.json`)
**Clinical Scenario**: Patient with fever during night shift
**Device**: DEV009
**Time**: 3:30 AM
**Alert Status**: **WILL TRIGGER TEMPERATURE ALERT**
**Key Features**:
- Temperature: 100.8°F (ALERT: >100.4°F threshold)
- Slightly elevated heart rate: 88 bpm (associated with fever)
- Other vitals compensating appropriately
- Intervention documented in notes

**Clinical Notes**: "Night vitals check - Patient has mild fever (100.8°F). Administered acetaminophen 500mg at 03:15. Will recheck temperature in 2 hours. Patient resting, denies chills."

**Expected System Response**:
1. Temperature alert triggered
2. Patient notification (if consented)
3. Provider notification
4. Documented in alert log

#### 8. Hypertensive Patient - TRIGGERS ALERT (`sample_hypertensive_patient.json`)
**Clinical Scenario**: Hypertensive patient with elevated blood pressure
**Device**: DEV011
**Time**: 9:30 AM
**Alert Status**: **WILL TRIGGER BLOOD PRESSURE ALERT**
**Patient History**: Known hypertension on medication
**Key Features**:
- Blood Pressure: 142/92 mmHg (ALERT: >140/>90 threshold)
- Heart rate normal: 76 bpm
- Patient states medication compliance
- Provider notification needed for medication adjustment

**Clinical Notes**: "Hypertensive patient vitals - Blood pressure elevated (142/92). Patient states took morning medications. Will notify provider for possible medication adjustment. Patient advised to rest and avoid sodium."

**Expected System Response**:
1. Blood pressure alert triggered
2. Medication review recommended
3. Provider consultation flagged
4. Follow-up BP check scheduled

#### 9. COPD Patient Low O2 - TRIGGERS ALERT (`sample_copd_patient.json`)
**Clinical Scenario**: COPD patient with chronic low oxygen saturation
**Device**: DEV012
**Time**: 6:45 AM
**Alert Status**: **WILL TRIGGER OXYGEN SATURATION ALERT**
**Patient History**: Chronic Obstructive Pulmonary Disease, home oxygen
**Key Features**:
- Oxygen Saturation: 91% (ALERT: <95%, but baseline for this patient)
- Elevated respiratory rate: 24/min (compensatory)
- Patient on 2L O2 via nasal cannula
- Chronic condition monitoring

**Clinical Notes**: "COPD patient morning vitals - Oxygen saturation at 91% (baseline for patient). Respiratory rate slightly elevated. Patient on 2L O2 via nasal cannula. Breath sounds clear bilaterally."

**Expected System Response**:
1. Oxygen saturation alert triggered
2. Alert may be suppressed if 91% is documented baseline
3. Respiratory assessment documented
4. Oxygen therapy compliance verified

#### 10. Critical Reading - MULTIPLE ALERTS (`sample_critical_reading.json`)
**Clinical Scenario**: Patient in acute distress with multiple abnormal vitals
**Device**: DEV008
**Alert Status**: **WILL TRIGGER MULTIPLE CRITICAL ALERTS**
**Key Features**:
- Heart Rate: 125 bpm (CRITICAL: >100)
- Blood Pressure: 165/105 mmHg (CRITICAL: significantly elevated)
- Temperature: 101.2°F (ALERT: >100.4°F)
- Oxygen Saturation: 92% (ALERT: <95%)
- Multiple system involvement
- Urgent intervention required

**Expected System Response**:
1. Multiple simultaneous alerts
2. Critical priority notification
3. Immediate provider notification
4. May trigger rapid response protocol

### Special Population Examples

#### 11. Pediatric Patient (`sample_pediatric_patient.json`)
**Clinical Scenario**: Routine vitals for 10-year-old child
**Device**: DEV010
**Time**: 11:00 AM
**Patient Demographics**: Age 10, male, 80 lbs, 54 inches tall
**Key Features**:
- Age-appropriate vital sign ranges (different from adults)
- Heart Rate: 90 bpm (Normal for pediatrics: 70-120)
- Blood Pressure: 105/65 mmHg (Normal for age)
- Respiratory Rate: 22/min (Normal for pediatrics: 18-30)
- Parent present during measurement

**Clinical Notes**: "Pediatric patient vitals - 10-year-old male. All vitals within normal pediatric ranges. Child cooperative during measurement. Parent present."

**Important**: Pediatric vital signs have different normal ranges than adults. Alert thresholds should be age-adjusted.

#### 12. Pregnant Patient (`sample_pregnant_patient.json`)
**Clinical Scenario**: Third trimester prenatal monitoring
**Device**: DEV013
**Time**: 3:15 PM
**Patient Status**: 32 weeks gestation, uncomplicated pregnancy
**Key Features**:
- Pregnancy-adjusted normal ranges
- Heart Rate: 88 bpm (slightly elevated normal for pregnancy)
- Blood Pressure: 120/75 mmHg (excellent for pregnancy)
- Weight gain appropriate for gestational age
- Fetal movement documentation

**Clinical Notes**: "Prenatal vitals check - 32 weeks gestation. All vitals within normal pregnancy ranges. No edema noted. Fetal movement reported as active. Next OB appointment in 2 weeks."

**Important**: Pregnancy causes physiological changes requiring adjusted normal ranges.

### Device-Specific Examples

#### 13. Blood Pressure Monitor (`sample_blood_pressure.json`)
**Purpose**: Typical output from a dedicated blood pressure monitor
**Device**: DEV006
**Key Features**:
- Focused on cardiovascular metrics only
- Heart rate
- Systolic and diastolic pressure
- Minimal fields (device-specific limitation)
- Efficient for targeted monitoring

#### 14. Glucose Monitor (`sample_glucose_monitor.json`)
**Purpose**: Output from a continuous glucose monitor (CGM)
**Device**: DEV007
**Key Features**:
- Single glucose reading focus
- Timestamp precision for trend analysis
- Notes field for meal/medication correlation
- Ideal for diabetic patients

#### 15. Pulse Oximeter (`sample_pulse_oximeter.json`)
**Purpose**: Output from a dedicated pulse oximeter device
**Device**: DEV005
**Key Features**:
- Heart rate measurement
- Oxygen saturation measurement
- Signal quality indicator
- Portable/spot-check monitoring

## Normal Vital Sign Ranges

### Adult Normal Ranges

| Vital Sign | Normal Range | Alert Low | Alert High | Critical Low | Critical High |
|------------|--------------|-----------|------------|--------------|---------------|
| **Heart Rate** | 60-100 bpm | <60 | >100 | <40 | >120 |
| **Systolic BP** | 90-120 mmHg | <90 | >140 | <70 | >180 |
| **Diastolic BP** | 60-80 mmHg | <60 | >90 | <40 | >110 |
| **Temperature (F)** | 97.0-99.0°F | <95 | >100.4 | <94 | >103 |
| **Temperature (C)** | 36.1-37.2°C | <35 | >38 | <34 | >39.4 |
| **O2 Saturation** | 95-100% | <95 | N/A | <90 | N/A |
| **Respiratory Rate** | 12-20/min | <12 | >20 | <8 | >30 |
| **Glucose (Fasting)** | 70-100 mg/dL | <70 | >100 | <50 | >250 |
| **Glucose (Random)** | 70-140 mg/dL | <70 | >180 | <50 | >300 |

### Pediatric Normal Ranges (Age 10)

| Vital Sign | Normal Range | Notes |
|------------|--------------|-------|
| **Heart Rate** | 70-120 bpm | Higher than adult |
| **Blood Pressure** | 95-110/60-70 mmHg | Age-dependent |
| **Respiratory Rate** | 18-30/min | Higher than adult |
| **Temperature** | Same as adult | 97-99°F |
| **O2 Saturation** | 95-100% | Same as adult |

### Pregnancy Adjustments (Third Trimester)

| Vital Sign | Pregnancy Adjustment |
|------------|---------------------|
| **Heart Rate** | 15-20 bpm higher than baseline |
| **Blood Pressure** | May decrease slightly in 2nd trimester, return to baseline 3rd |
| **Respiratory Rate** | Slightly elevated (16-22/min) |
| **Weight** | 25-35 lbs total gain for normal BMI |

### Geriatric Considerations (Age 65+)

| Vital Sign | Geriatric Adjustment |
|------------|---------------------|
| **Heart Rate** | Resting may be 50-70 bpm (normal) |
| **Blood Pressure** | <140/90 acceptable (was <130/80) |
| **Temperature** | Baseline may be lower (96.5-98°F) |
| **O2 Saturation** | May be 92-96% (acceptable if chronic) |

## Testing with Sample Files

### Method 1: Copy to Inbox for Batch Processing

```bash
# Copy sample file to inbox
cp sample_all_vitals_comprehensive.json /var/iot_data/inbox/

# Process all pending files
cd /path/to/django_inhealth
python manage.py process_iot_data

# Check results
python manage.py process_iot_data --verbose

# Check archive (files moved after processing)
ls -la /var/iot_data/archive/$(date +%Y-%m-%d)/

# View processing log
tail -f /var/log/iot_processing.log
```

### Method 2: POST to API (Individual Reading)

```bash
# Replace with your API key and server URL
API_KEY="your_api_key_here"
SERVER="https://your-server.com"

# Submit single reading
curl -X POST ${SERVER}/api/iot/vitals/ \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d @sample_all_vitals_comprehensive.json

# Expected successful response:
# {
#   "success": true,
#   "message": "Vital signs recorded successfully",
#   "vital_sign_id": 123,
#   "alerts_triggered": 0,
#   "patient_id": 456,
#   "recorded_at": "2025-11-17T14:30:00Z"
# }
```

### Method 3: POST to API (Batch Submission)

```bash
# Create batch file with multiple readings
cat > batch_readings.json <<'EOF'
{
  "readings": [
    $(cat sample_morning_vitals.json),
    $(cat sample_postmeal_diabetic.json),
    $(cat sample_elderly_bedtime.json)
  ]
}
EOF

# Submit batch
curl -X POST ${SERVER}/api/iot/vitals/batch/ \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d @batch_readings.json

# Expected response:
# {
#   "success": true,
#   "total_submitted": 3,
#   "successful": 3,
#   "failed": 0,
#   "results": [...]
# }
```

### Method 4: Python Script for Testing

```python
import requests
import json
from pathlib import Path

API_KEY = "your_api_key_here"
SERVER = "https://your-server.com"

def submit_sample_file(filename):
    """Submit a single sample file to the API"""
    # Read sample file
    with open(filename) as f:
        data = json.load(f)

    # Submit to API
    response = requests.post(
        f"{SERVER}/api/iot/vitals/",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json=data
    )

    return response.json()

# Test with comprehensive sample
result = submit_sample_file('sample_all_vitals_comprehensive.json')
print(f"Result: {result}")

# Test alert-triggering scenarios
alert_samples = [
    'sample_fever_patient.json',
    'sample_hypertensive_patient.json',
    'sample_copd_patient.json'
]

for sample in alert_samples:
    print(f"\nTesting {sample}...")
    result = submit_sample_file(sample)
    print(f"Alerts triggered: {result.get('alerts_triggered', 0)}")
```

### Method 5: Automated Testing Script

```python
#!/usr/bin/env python3
"""
Automated test suite for IoT device integration
Tests all sample files and validates responses
"""
import requests
import json
from pathlib import Path
import sys

API_KEY = "your_api_key_here"
SERVER = "https://your-server.com"

def test_all_samples():
    """Test all sample files in directory"""
    samples_dir = Path(__file__).parent
    results = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'alerts': 0
    }

    # Get all sample JSON files
    sample_files = sorted(samples_dir.glob('sample_*.json'))

    for sample_file in sample_files:
        print(f"\nTesting: {sample_file.name}")
        results['total'] += 1

        try:
            with open(sample_file) as f:
                data = json.load(f)

            response = requests.post(
                f"{SERVER}/api/iot/vitals/",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                results['success'] += 1
                alerts = result.get('alerts_triggered', 0)
                results['alerts'] += alerts

                print(f"  ✓ Success - Vital Sign ID: {result.get('vital_sign_id')}")
                if alerts > 0:
                    print(f"  ⚠ Alerts triggered: {alerts}")
            else:
                results['failed'] += 1
                print(f"  ✗ Failed - Status: {response.status_code}")
                print(f"  Error: {response.text}")

        except Exception as e:
            results['failed'] += 1
            print(f"  ✗ Exception: {str(e)}")

    # Print summary
    print("\n" + "="*50)
    print("Test Summary:")
    print(f"  Total files tested: {results['total']}")
    print(f"  Successful: {results['success']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Total alerts triggered: {results['alerts']}")
    print("="*50)

    return results['failed'] == 0

if __name__ == '__main__':
    success = test_all_samples()
    sys.exit(0 if success else 1)
```

## Creating Your Own Test Files

### Required Fields

- **device_id** (string): Must match a device's `device_unique_id` field in the system (case-sensitive). This is the string identifier like 'DEV001', NOT the numeric database ID.
- **timestamp** (string): ISO 8601 format - `YYYY-MM-DDTHH:MM:SSZ` (UTC timezone)
- **At least one vital sign measurement**: heart_rate, blood_pressure, temperature, etc.

### Optional but Recommended Fields

- **notes** (string): Clinical notes, free text description
- **signal_quality** (integer): 0-100, device signal strength
- **battery_level** (integer): 0-100, device battery percentage
- **temperature_unit** (string): "F" or "C" (defaults to "F" if not specified)
- **weight_unit** (string): "lbs" or "kg" (defaults to "lbs" if not specified)
- **height_unit** (string): "in" or "cm" (defaults to "in" if not specified)

### All Available Vital Sign Fields

```json
{
    "device_id": "DEV_XXX",
    "timestamp": "2025-11-17T10:30:00Z",

    "heart_rate": 75,
    "blood_pressure_systolic": 120,
    "blood_pressure_diastolic": 80,
    "temperature": 98.6,
    "temperature_unit": "F",
    "respiratory_rate": 16,
    "oxygen_saturation": 98.0,
    "glucose": 95.0,
    "weight": 165.0,
    "weight_unit": "lbs",
    "height": 68.0,
    "height_unit": "in",

    "signal_quality": 95,
    "battery_level": 85,
    "notes": "Your clinical notes here"
}
```

### Minimal Valid Example

```json
{
    "device_id": "DEV001",
    "timestamp": "2025-11-17T10:30:00Z",
    "heart_rate": 75
}
```

### Tips for Creating Test Data

1. **Use realistic values**: Reference the normal ranges table above
2. **Include context in notes**: Explain the clinical scenario
3. **Test edge cases**: Include values at alert thresholds
4. **Vary timestamps**: Test different times of day
5. **Test units**: Mix F/C temperatures, lbs/kg weights
6. **Test incomplete data**: Not all devices send all vital signs
7. **Test alert scenarios**: Create values that should trigger alerts

## Alert System Testing

### Understanding the Alert Flow

1. **Data Received**: IoT device data arrives via API or file processing
2. **Vital Signs Extracted**: System creates VitalSign record with `data_source='device'`
3. **Alert Evaluation**: `process_vital_alerts()` function checks all vital signs against thresholds
4. **Patient Consent Check**: If alerts triggered, checks if patient has consented to notifications
5. **Patient Notification**: If consented, sends notification to patient
6. **Provider Notification**: Sends notification to assigned provider
7. **Alert Logging**: Records alert in system log

### Files That Will Trigger Alerts

| Sample File | Alert Type | Trigger Value | Expected Response |
|-------------|------------|---------------|-------------------|
| `sample_fever_patient.json` | Temperature | 100.8°F | Patient + Provider notification |
| `sample_hypertensive_patient.json` | Blood Pressure | 142/92 mmHg | Patient + Provider notification |
| `sample_copd_patient.json` | Oxygen Saturation | 91% | Patient + Provider notification |
| `sample_critical_reading.json` | Multiple | HR 125, BP 165/105, Temp 101.2, O2 92% | Critical priority, multiple alerts |
| `sample_postmeal_diabetic.json` | Glucose (borderline) | 145 mg/dL | May trigger depending on patient settings |

### Files That Will NOT Trigger Alerts (Normal Values)

- `sample_all_vitals_comprehensive.json` - All normal
- `sample_morning_vitals.json` - All normal
- `sample_elderly_bedtime.json` - Elevated but acceptable for age
- `sample_postexercise.json` - Elevated but expected post-exercise
- `sample_pediatric_patient.json` - Normal for age
- `sample_pregnant_patient.json` - Normal for pregnancy

### Testing Alert Functionality

```bash
# Test alert-triggering samples
for file in sample_fever_patient.json sample_hypertensive_patient.json sample_copd_patient.json; do
    echo "Testing $file..."
    cp $file /var/iot_data/inbox/
    python manage.py process_iot_data --verbose

    # Check alerts in Django admin or database
    python manage.py shell <<EOF
from healthcare.models import VitalSign, Notification
vs = VitalSign.objects.latest('recorded_at')
print(f"Latest vital sign: {vs.id}")
alerts = Notification.objects.filter(vital_sign=vs)
print(f"Alerts triggered: {alerts.count()}")
for alert in alerts:
    print(f"  - {alert.recipient}: {alert.message}")
EOF
done
```

## Troubleshooting

### Common Errors and Solutions

#### "Device not found" Error
```json
{
    "success": false,
    "error": "Device DEV999 not found in system"
}
```
**Solution**:
- Verify `device_id` in JSON matches the device's `device_unique_id` field (case-sensitive)
- The `device_id` in JSON should be a STRING (like 'DEV001'), not a number
- Check existing devices: `python manage.py shell -c "from healthcare.models import Device; print(list(Device.objects.values_list('device_unique_id', flat=True)))"`
- Create device in Django admin panel if needed with a unique `device_unique_id`

**Common mistake**: Using numeric database ID instead of string unique identifier

#### "Device not assigned to patient" Error
```json
{
    "success": false,
    "error": "Device DEV001 is not assigned to any patient"
}
```
**Solution**:
- Assign device to patient in Django admin panel
- Update device: `Device.objects.get(device_id='DEV001').update(patient=patient_obj)`

#### "Invalid timestamp format" Error
```json
{
    "success": false,
    "error": "Invalid timestamp format. Use ISO 8601: YYYY-MM-DDTHH:MM:SSZ"
}
```
**Solution**:
- Use ISO 8601 format: `2025-11-17T14:30:00Z`
- Include the "T" between date and time
- Include the "Z" suffix for UTC timezone
- Use 24-hour time format

#### "Invalid API key" Error
```json
{
    "success": false,
    "error": "Invalid or expired API key"
}
```
**Solution**:
- Check `Authorization` header format: `Bearer YOUR_API_KEY`
- Verify API key in Django admin panel
- Check API key is active and not expired
- Generate new API key if needed

#### No Alerts Triggered (When Expected)
**Possible Causes**:
1. Vital sign values within normal range
2. Patient notification preferences disabled
3. Alert system configuration issue
4. Patient consent not recorded

**Solution**:
```bash
# Check alert system configuration
python manage.py shell <<EOF
from healthcare.models import Patient, VitalSign
from healthcare.vital_alerts import process_vital_alerts

# Get latest vital sign
vs = VitalSign.objects.latest('recorded_at')
print(f"Vital Sign ID: {vs.id}")
print(f"Patient: {vs.encounter.patient}")
print(f"Heart Rate: {vs.heart_rate}")
print(f"BP: {vs.blood_pressure_systolic}/{vs.blood_pressure_diastolic}")

# Manually trigger alert processing
result = process_vital_alerts(vs)
print(f"Alert result: {result}")
EOF
```

#### File Not Processed from Inbox
**Possible Causes**:
1. Invalid JSON format
2. File permissions issue
3. Processing cron job not running

**Solution**:
```bash
# Check JSON validity
cat /var/iot_data/inbox/sample_file.json | python -m json.tool

# Check file permissions
ls -la /var/iot_data/inbox/

# Manually run processor with verbose output
python manage.py process_iot_data --verbose

# Check cron job status
systemctl status crond
crontab -l | grep process_iot_data
```

## Production Deployment

### Cron Setup for Automated Processing

```bash
# Edit crontab
crontab -e

# Add this line to process every minute
* * * * * cd /path/to/django_inhealth && /path/to/venv/bin/python manage.py process_iot_data >> /var/log/iot_processing.log 2>&1

# Add this line to cleanup old archives weekly (Sunday 2 AM)
0 2 * * 0 cd /path/to/django_inhealth && /path/to/venv/bin/python manage.py process_iot_data --cleanup --cleanup-days=90
```

### Directory Setup

```bash
# Create required directories
sudo mkdir -p /var/iot_data/inbox
sudo mkdir -p /var/iot_data/archive
sudo mkdir -p /var/log

# Set permissions
sudo chown -R www-data:www-data /var/iot_data
sudo chmod -R 755 /var/iot_data

# Create log file
sudo touch /var/log/iot_processing.log
sudo chown www-data:www-data /var/log/iot_processing.log
```

### Security Considerations

1. **API Key Management**:
   - Store API keys securely (hashed in database)
   - Rotate keys regularly
   - Use HTTPS only for API endpoints
   - Implement rate limiting

2. **File Processing**:
   - Validate JSON structure before processing
   - Sanitize file contents
   - Limit file sizes
   - Archive with retention policy

3. **Data Privacy**:
   - PHI data - HIPAA compliance required
   - Encrypt data in transit (TLS/SSL)
   - Encrypt data at rest
   - Audit logging for all access

## Support and Documentation

For more detailed information:
- **API Documentation**: See `/docs/IOT_DEVICE_INTEGRATION.md`
- **Django Admin**: Configure devices, patients, and API keys
- **System Logs**: Check `/var/log/iot_processing.log`
- **Alert Configuration**: See `healthcare/vital_alerts.py`

## Quick Reference

### Sample File Categories

- **Complete Examples**: `sample_all_vitals_comprehensive.json`, `sample_vitals_complete.json`
- **Normal Scenarios**: `sample_morning_vitals.json`, `sample_elderly_bedtime.json`, `sample_postexercise.json`
- **Alert Scenarios**: `sample_fever_patient.json`, `sample_hypertensive_patient.json`, `sample_copd_patient.json`, `sample_critical_reading.json`
- **Special Populations**: `sample_pediatric_patient.json`, `sample_pregnant_patient.json`
- **Chronic Conditions**: `sample_postmeal_diabetic.json`, `sample_copd_patient.json`
- **Device-Specific**: `sample_blood_pressure.json`, `sample_glucose_monitor.json`, `sample_pulse_oximeter.json`

### Testing Checklist

- [ ] Device created in system
- [ ] Device assigned to patient
- [ ] API key generated and active
- [ ] Patient consent for notifications configured
- [ ] Provider assigned to patient
- [ ] Test normal vitals (no alerts)
- [ ] Test alert-triggering vitals
- [ ] Verify patient notifications
- [ ] Verify provider notifications
- [ ] Check file archiving
- [ ] Review processing logs
- [ ] Test batch processing
- [ ] Test API endpoints
- [ ] Verify data source field (`device` vs `manual`)
