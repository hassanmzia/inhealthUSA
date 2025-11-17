# IoT Device Sample Data Files

This directory contains sample JSON files demonstrating different IoT device data formats.

## Sample Files

### 1. Complete Vital Signs (`sample_vitals_complete.json`)
Demonstrates all possible vital sign fields from a multi-function device.
- All vital signs included
- Metadata (signal quality, battery level)
- Proper timestamp format

### 2. Blood Pressure Monitor (`sample_blood_pressure.json`)
Typical output from a dedicated blood pressure monitor.
- Heart rate
- Systolic and diastolic pressure
- Minimal fields

### 3. Glucose Monitor (`sample_glucose_monitor.json`)
Output from a continuous glucose monitor.
- Single glucose reading
- Timestamp and notes

### 4. Pulse Oximeter (`sample_pulse_oximeter.json`)
Output from a pulse oximeter device.
- Heart rate
- Oxygen saturation
- Signal quality indicator

### 5. Critical Reading (`sample_critical_reading.json`)
Example of abnormal vital signs that will trigger alerts.
- High heart rate (125 bpm)
- High blood pressure (165/105)
- High temperature (101.2°F)
- Low oxygen saturation (92%)
- Will trigger two-stage alert system

## Testing with Sample Files

### Method 1: Copy to Inbox for Batch Processing
```bash
# Copy sample file to inbox
cp sample_vitals_complete.json /var/iot_data/inbox/

# Process
cd /path/to/django_inhealth
python manage.py process_iot_data

# Check archive
ls -la /var/iot_data/archive/$(date +%Y-%m-%d)/
```

### Method 2: POST to API
```bash
# Replace with your API key and server URL
API_KEY="your_api_key_here"
SERVER="https://your-server.com"

curl -X POST ${SERVER}/api/iot/vitals/ \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d @sample_vitals_complete.json
```

### Method 3: Python Script
```python
import requests
import json

API_KEY = "your_api_key_here"
SERVER = "https://your-server.com"

# Read sample file
with open('sample_vitals_complete.json') as f:
    data = json.load(f)

# Submit
response = requests.post(
    f"{SERVER}/api/iot/vitals/",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json=data
)

print(response.json())
```

## Creating Your Own Test Files

### Required Fields
- `device_id`: Must match a device in the system
- `timestamp`: ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
- At least one vital sign measurement

### Optional Fields
- `notes`: Free text description
- `signal_quality`: 0-100
- `battery_level`: 0-100
- `temperature_unit`: "F" or "C"
- `weight_unit`: "lbs" or "kg"

### Example Template
```json
{
    "device_id": "DEV_XXX",
    "timestamp": "2025-11-17T10:30:00Z",
    "heart_rate": 75,
    "notes": "Your notes here"
}
```

## Alert Triggers

These vital sign ranges will trigger alerts:

| Vital Sign | Normal Range | Alert Triggers |
|------------|--------------|----------------|
| Heart Rate | 60-100 bpm | < 60 or > 100 |
| Systolic BP | 90-120 mmHg | < 90 or > 140 |
| Diastolic BP | 60-80 mmHg | < 60 or > 90 |
| Temperature | 97-99°F | < 95 or > 100.4 |
| Oxygen Saturation | > 95% | < 90% |
| Respiratory Rate | 12-20/min | < 12 or > 20 |
| Glucose | 70-140 mg/dL | < 70 or > 180 |

## Troubleshooting

**"Device not found" error:**
- Verify device_id matches exactly (case-sensitive)
- Check device exists in admin panel

**"Device not assigned to patient" error:**
- Assign device to patient in admin panel

**"Invalid API key" error:**
- Check Authorization header format
- Verify API key hasn't expired
- Ensure API key is active

**No alerts triggered:**
- Check vital sign values are outside normal ranges
- Verify alert system is enabled
- Check patient notification preferences
