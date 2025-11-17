# IoT Device Data Processing System

## Overview

This system allows IoT medical devices to send patient vital signs data to the InHealth EHR system through two methods:

1. **REST API (Real-time)**: Devices POST data directly to the API endpoint
2. **File Drop (Batch Processing)**: Devices upload JSON files that are processed periodically

The system automatically:
- Validates device authentication and patient mapping
- Creates vital sign records with source marked as "device"
- Triggers the existing alert system for abnormal vitals
- Archives processed files with timestamps

---

## System Architecture

```
IoT Device → [REST API or File Drop] → Data Processor → VitalSign Record → Alert System
                                              ↓
                                        Archive (timestamped)
```

### Components

1. **`iot_data_processor.py`**: Core processing logic
2. **`iot_api_views.py`**: REST API endpoints
3. **`management/commands/process_iot_data.py`**: Batch processing command
4. **`models_iot.py`**: IoT device models (API keys, readings, logs)

---

## Method 1: REST API Integration (Recommended)

### Setup

1. **Create Device in EHR**:
   - Go to Admin → Devices
   - Create new device with device_id (e.g., "DEV001")
   - Assign to patient

2. **Generate API Key**:
   ```python
   from healthcare.models import Device
   from healthcare.models_iot import DeviceAPIKey

   device = Device.objects.get(device_id='DEV001')
   api_key_obj, api_key = DeviceAPIKey.create_key(
       device=device,
       key_name="Primary API Key",
       expires_in_days=365  # Optional expiration
   )

   print(f"API Key: {api_key}")
   # Save this key securely - it won't be shown again!
   ```

### API Endpoints

#### 1. Submit Vital Signs (Single Reading)

**Endpoint**: `POST /api/iot/vitals/`

**Headers**:
```
Authorization: Bearer <your_api_key>
Content-Type: application/json
```

**Request Body**:
```json
{
    "device_id": "DEV001",
    "timestamp": "2025-11-17T10:30:00Z",
    "heart_rate": 75,
    "blood_pressure_systolic": 120,
    "blood_pressure_diastolic": 80,
    "temperature": 98.6,
    "temperature_unit": "F",
    "respiratory_rate": 16,
    "oxygen_saturation": 98.0,
    "glucose": 95.0,
    "weight": 150.0,
    "weight_unit": "lbs",
    "notes": "Morning reading",
    "signal_quality": 95,
    "battery_level": 80
}
```

**Response** (Success):
```json
{
    "success": true,
    "message": "Vital signs received successfully",
    "vital_sign_id": 123,
    "alerts_triggered": 0,
    "timestamp": "2025-11-17T10:30:00Z"
}
```

**Response** (Error):
```json
{
    "success": false,
    "error": "Invalid API key"
}
```

#### 2. Submit Multiple Readings (Batch)

**Endpoint**: `POST /api/iot/vitals/batch/`

**Request Body**:
```json
{
    "device_id": "DEV001",
    "readings": [
        {
            "timestamp": "2025-11-17T10:00:00Z",
            "heart_rate": 75,
            "blood_pressure_systolic": 120,
            "blood_pressure_diastolic": 80
        },
        {
            "timestamp": "2025-11-17T11:00:00Z",
            "heart_rate": 78,
            "blood_pressure_systolic": 122,
            "blood_pressure_diastolic": 81
        }
    ]
}
```

**Response**:
```json
{
    "success": true,
    "message": "Batch submitted successfully",
    "total_readings": 2,
    "processed": 2,
    "failed": 0,
    "vitals_created": [123, 124],
    "alerts_triggered": 1
}
```

#### 3. Check Device Status

**Endpoint**: `GET /api/iot/status/`

**Response**:
```json
{
    "success": true,
    "device_id": "DEV001",
    "device_name": "Smart BP Monitor",
    "device_type": "Blood Pressure Monitor",
    "is_active": true,
    "patient_assigned": true,
    "patient_id": "P123",
    "api_key_valid": true,
    "last_reading": "2025-11-17T10:30:00Z"
}
```

### Example Client Code (Python)

```python
import requests
import json
from datetime import datetime

API_KEY = "your_api_key_here"
BASE_URL = "https://your-ehr-server.com"

def submit_vitals(device_id, vitals_data):
    """Submit vital signs to EHR"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "device_id": device_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **vitals_data
    }

    response = requests.post(
        f"{BASE_URL}/api/iot/vitals/",
        headers=headers,
        json=payload
    )

    return response.json()

# Usage
result = submit_vitals("DEV001", {
    "heart_rate": 75,
    "blood_pressure_systolic": 120,
    "blood_pressure_diastolic": 80,
    "temperature": 98.6,
    "temperature_unit": "F",
    "oxygen_saturation": 98.0
})

print(result)
```

---

## Method 2: File Drop Processing

### Setup

1. **Configure Directories** in `settings.py`:
```python
# IoT Device Data Processing
IOT_INBOX_DIR = '/var/iot_data/inbox'
IOT_ARCHIVE_DIR = '/var/iot_data/archive'
```

2. **Create Directories**:
```bash
sudo mkdir -p /var/iot_data/inbox /var/iot_data/archive
sudo chown www-data:www-data /var/iot_data/inbox /var/iot_data/archive
sudo chmod 755 /var/iot_data/inbox /var/iot_data/archive
```

### JSON File Format

Create JSON files in the inbox directory. The system will process them automatically.

**Example**: `DEV001_20251117_103000.json`

```json
{
    "device_id": "DEV001",
    "timestamp": "2025-11-17T10:30:00Z",
    "heart_rate": 75,
    "blood_pressure_systolic": 120,
    "blood_pressure_diastolic": 80,
    "temperature": 98.6,
    "temperature_unit": "F",
    "respiratory_rate": 16,
    "oxygen_saturation": 98.0,
    "glucose": 95.0,
    "weight": 150.0,
    "weight_unit": "lbs",
    "notes": "Automated reading from device",
    "signal_quality": 95,
    "battery_level": 80
}
```

### Processing Command

Run manually:
```bash
python manage.py process_iot_data
```

With cleanup of old archives:
```bash
python manage.py process_iot_data --cleanup --cleanup-days 90
```

### Automated Processing with Cron

**Option 1: Every Minute**
```bash
# Edit crontab
crontab -e

# Add this line (runs every minute)
* * * * * cd /path/to/django_inhealth && /path/to/venv/bin/python manage.py process_iot_data >> /var/log/iot_processor.log 2>&1
```

**Option 2: Every 5 Minutes**
```bash
*/5 * * * * cd /path/to/django_inhealth && /path/to/venv/bin/python manage.py process_iot_data >> /var/log/iot_processor.log 2>&1
```

**Option 3: Daily Cleanup**
```bash
# Process every 5 minutes
*/5 * * * * cd /path/to/django_inhealth && /path/to/venv/bin/python manage.py process_iot_data >> /var/log/iot_processor.log 2>&1

# Cleanup old archives daily at 2 AM
0 2 * * * cd /path/to/django_inhealth && /path/to/venv/bin/python manage.py process_iot_data --cleanup --cleanup-days 90 >> /var/log/iot_cleanup.log 2>&1
```

### Systemd Timer (Alternative to Cron)

Create `/etc/systemd/system/iot-processor.service`:
```ini
[Unit]
Description=IoT Device Data Processor
After=network.target

[Service]
Type=oneshot
User=www-data
WorkingDirectory=/path/to/django_inhealth
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python manage.py process_iot_data
```

Create `/etc/systemd/system/iot-processor.timer`:
```ini
[Unit]
Description=Run IoT Processor Every Minute
Requires=iot-processor.service

[Timer]
OnBootSec=1min
OnUnitActiveSec=1min
Unit=iot-processor.service

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable iot-processor.timer
sudo systemctl start iot-processor.timer

# Check status
sudo systemctl status iot-processor.timer
```

---

## File Archiving

After successful processing:
1. Files are moved to archive directory
2. Organized in dated folders: `archive/2025-11-17/filename_timestamp.json`
3. Original filename gets timestamp appended
4. Old archives are cleaned up based on retention policy

**Archive Structure**:
```
/var/iot_data/archive/
├── 2025-11-17/
│   ├── DEV001_reading1_20251117_103045.json
│   ├── DEV001_reading2_20251117_104012.json
│   └── DEV002_reading1_20251117_105230.json
├── 2025-11-16/
│   └── ...
└── 2025-11-15/
    └── ...
```

---

## Alert System Integration

The system automatically triggers the existing vital sign alert system when:

1. **Critical values detected** (based on VitalSign model status methods)
2. **Two-stage alert process**:
   - First asks patient for permission
   - Then notifies doctor/nurse/EMS based on patient response
   - Auto-escalates if patient doesn't respond

Alerts are triggered for:
- Heart rate outside normal range
- Blood pressure (systolic/diastolic) abnormal
- Temperature too high/low
- Low oxygen saturation
- Abnormal glucose levels
- Respiratory rate issues

---

## Data Source Tracking

All vital signs records include:
- **`data_source`**: 'manual' or 'device'
- **`device`**: Foreign key to Device model (if from IoT)
- **`recorded_by`**: Provider (for manual) or null (for device)
- **`recorded_by_nurse`**: Nurse (for manual) or null (for device)

This allows filtering and reporting:
```python
# Get all device-sourced vitals
device_vitals = VitalSign.objects.filter(data_source='device')

# Get all manual vitals
manual_vitals = VitalSign.objects.filter(data_source='manual')

# Get vitals from specific device
device_vitals = VitalSign.objects.filter(device__device_id='DEV001')
```

---

## Security

### API Key Security
- API keys are hashed (never stored in plain text)
- Prefix-based lookup for performance
- Optional expiration dates
- Per-key permissions (can_write_vitals, can_read_patient)
- Rate limiting tracking

### Authentication Flow
1. Device sends API key in Authorization header
2. System looks up key by prefix
3. Verifies full key hash
4. Checks expiration and active status
5. Validates permissions
6. Records usage for auditing

### Activity Logging
All API requests are logged with:
- Device ID
- API key used
- IP address
- Timestamp
- Response status
- Error messages (if any)

---

## Monitoring & Troubleshooting

### Check Processing Stats
```bash
python manage.py process_iot_data
```

### View Logs
```bash
# Application logs
tail -f /var/log/iot_processor.log

# Django logs
tail -f /var/log/django/django.log
```

### Database Queries

**Check device readings:**
```sql
SELECT * FROM healthcare_device_data_reading
WHERE device_id = 'DEV001'
ORDER BY timestamp DESC LIMIT 10;
```

**Check API activity:**
```sql
SELECT * FROM healthcare_device_activity_log
WHERE device_id = 'DEV001'
ORDER BY timestamp DESC LIMIT 10;
```

**Check vital signs from devices:**
```sql
SELECT vs.*, d.device_name
FROM healthcare_vital_signs vs
JOIN healthcare_device d ON vs.device_id = d.device_id
WHERE vs.data_source = 'device'
ORDER BY vs.recorded_at DESC LIMIT 10;
```

---

## Testing

### Test API Endpoint
```bash
curl -X POST https://your-server.com/api/iot/vitals/ \
  -H "Authorization: Bearer your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "DEV001",
    "timestamp": "2025-11-17T10:30:00Z",
    "heart_rate": 75,
    "blood_pressure_systolic": 120,
    "blood_pressure_diastolic": 80,
    "temperature": 98.6,
    "temperature_unit": "F"
  }'
```

### Test File Processing
```bash
# Create test file
cat > /var/iot_data/inbox/test.json <<EOF
{
    "device_id": "DEV001",
    "timestamp": "2025-11-17T10:30:00Z",
    "heart_rate": 75,
    "blood_pressure_systolic": 120,
    "blood_pressure_diastolic": 80
}
EOF

# Process
python manage.py process_iot_data

# Check archive
ls -la /var/iot_data/archive/$(date +%Y-%m-%d)/
```

---

## Supported Vital Signs

| Field | Type | Unit | Example |
|-------|------|------|---------|
| `heart_rate` | Integer | bpm | 75 |
| `blood_pressure_systolic` | Integer | mmHg | 120 |
| `blood_pressure_diastolic` | Integer | mmHg | 80 |
| `temperature` | Decimal | F or C | 98.6 |
| `respiratory_rate` | Integer | breaths/min | 16 |
| `oxygen_saturation` | Decimal | % | 98.0 |
| `glucose` | Decimal | mg/dL | 95.0 |
| `weight` | Decimal | lbs or kg | 150.0 |

**Note**: At least one vital sign measurement must be provided in each submission.

---

## Error Handling

### Common Errors

**401 Unauthorized**:
- Invalid API key
- Expired API key
- API key not active

**403 Forbidden**:
- device_id doesn't match authenticated device
- API key lacks permission

**400 Bad Request**:
- Invalid JSON format
- Missing required fields (device_id, timestamp)
- No vital sign measurements provided
- Device not found in system
- Device not assigned to patient

**500 Internal Server Error**:
- Database error
- Processing exception

### Retry Strategy

Implement exponential backoff for failed submissions:
```python
import time

def submit_with_retry(data, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = submit_vitals(data)
            if response['success']:
                return response
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 1s, 2s, 4s
                continue
            raise
```

---

## Best Practices

1. **Use HTTPS**: Always use secure connections for API calls
2. **Secure API Keys**: Store keys in secure configuration, never in code
3. **Timestamp Accuracy**: Use device local time or NTP-synced time
4. **Batch When Offline**: Queue readings when offline, batch submit when connected
5. **Monitor Battery**: Include battery_level to track device health
6. **Signal Quality**: Include signal_quality for data reliability
7. **Error Logging**: Log all errors locally on device for debugging
8. **Heartbeat**: Send status checks periodically to verify connectivity

---

## Support

For issues or questions:
- Check logs in `/var/log/iot_processor.log`
- Review DeviceActivityLog in database
- Contact system administrator
