# InHealth EHR - IoT Device API Quick Start Guide

## Overview

This guide will help you quickly set up and start using the InHealth EHR IoT Device REST API for transmitting health data from medical devices.

---

## Prerequisites

✅ InHealth EHR system deployed with HTTPS
✅ Device registered in the system
✅ Patient assigned to device
✅ Python 3.7+ or compatible IoT platform

---

## Step 1: Install Dependencies

### Server-Side (Django)

```bash
cd /home/user/inhealthUSA
pip install -r iot_api_requirements.txt
```

This installs:
- Django REST Framework
- JWT Authentication libraries
- API documentation tools

### Client-Side (IoT Device)

**Python:**
```bash
pip install requests
```

**Arduino/ESP32:**
```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
```

**Raspberry Pi:**
```bash
sudo pip3 install requests RPi.GPIO
```

---

## Step 2: Apply Database Migrations

```bash
cd /home/user/inhealthUSA/django_inhealth
source ../venv/bin/activate

# Create migrations for IoT models
python manage.py makemigrations healthcare

# Apply migrations
python manage.py migrate

# Verify migrations
python manage.py showmigrations healthcare
```

---

## Step 3: Update Django Settings

### Add REST Framework to Installed Apps

Edit `django_inhealth/inhealth/settings.py`:

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'rest_framework',
    'healthcare',
]

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # API key auth handled in views
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}
```

### Add API URLs

Edit `django_inhealth/inhealth/urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... existing patterns ...

    # IoT Device API
    path('api/', include('healthcare.api_urls')),
]
```

---

## Step 4: Register a Device

### Option A: Using Django Admin

1. Log in to Django admin: `https://yourdomain.com/admin/`
2. Go to **Healthcare** → **Devices**
3. Click **Add Device**
4. Fill in device information:
   - **Device Unique ID**: `MAC:00:11:22:33:44:55` (or IMEI, serial number)
   - **Device Type**: Watch, Ring, EarClip, etc.
   - **Device Name**: Patient's Watch
   - **Patient**: Select patient
   - **Status**: Active
5. Click **Save**

### Option B: Using Django Shell

```bash
python manage.py shell
```

```python
from healthcare.models import Device, Patient
from datetime import date

# Get patient
patient = Patient.objects.get(patient_id=1)

# Create device
device = Device.objects.create(
    device_unique_id="MAC:00:11:22:33:44:55",
    device_type="Watch",
    device_name="Patient's Smartwatch",
    manufacturer="HealthTech Inc",
    model_number="HT-W100",
    firmware_version="1.0.0",
    patient=patient,
    status="Active",
    registration_date=date.today()
)

print(f"Device created: {device.device_id}")
```

---

## Step 5: Generate API Key

### Using Management Command (Recommended)

```bash
python manage.py create_device_api_key \
    --device-unique-id="MAC:00:11:22:33:44:55" \
    --key-name="Primary API Key" \
    --expires=365
```

**Output:**
```
=== API Key Created Successfully ===
Device: Patient's Smartwatch (MAC:00:11:22:33:44:55)
Patient: John Doe
Key Name: Primary API Key
Key Prefix: abc12345
Expires: 2026-11-15 20:00:00

Permissions:
  - Can Write Vitals: True
  - Can Read Patient: False

=== API KEY (Save this - it will not be shown again!) ===
abc12345defghijklmnopqrstuvwxyz1234567890ABCDEFG
======================================================================

API key created and ready to use!

Usage in device code:
  Authorization: Bearer abc12345defghijklmnopqrstuvwxyz1234567890ABCDEFG
```

**⚠️ IMPORTANT**: Save this API key immediately! It will never be shown again.

### Using Django Shell

```python
from healthcare.models import Device
from healthcare.models_iot import DeviceAPIKey

# Get device
device = Device.objects.get(device_unique_id="MAC:00:11:22:33:44:55")

# Create API key
api_key_obj, api_key = DeviceAPIKey.create_key(
    device=device,
    key_name="Primary API Key",
    expires_in_days=365
)

print(f"API Key: {api_key}")
print(f"Key Prefix: {api_key_obj.key_prefix}")
```

---

## Step 6: Test API Connection

### Test with cURL

```bash
# Replace with your actual API key and domain
API_KEY="abc12345defghijklmnopqrstuvwxyz1234567890ABCDEFG"
DOMAIN="yourdomain.com"

curl -X POST https://$DOMAIN/api/v1/device/auth \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "device_unique_id": "MAC:00:11:22:33:44:55",
    "api_key": "'"$API_KEY"'"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Authentication successful",
  "data": {
    "device_id": 1,
    "device_name": "Patient's Smartwatch",
    "patient_id": 1,
    "permissions": {
      "can_write_vitals": true,
      "can_read_patient": false
    }
  },
  "timestamp": "2025-11-15T20:00:00Z"
}
```

---

## Step 7: Send Test Data

### Python Test Script

Create `test_iot_api.py`:

```python
#!/usr/bin/env python3
import requests
from datetime import datetime

# Configuration
API_BASE_URL = "https://yourdomain.com/api"
API_KEY = "YOUR_API_KEY_HERE"  # Replace with actual key

def test_send_vitals():
    """Test sending vital signs"""

    url = f"{API_BASE_URL}/v1/device/vitals"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "heart_rate": 72,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80,
        "temperature": 98.6,
        "oxygen_saturation": 98,
        "battery_level": 85,
        "signal_quality": 95
    }

    print("Sending test vital signs data...")
    response = requests.post(url, json=data, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 201:
        print("✓ SUCCESS: Data sent successfully!")
        return True
    else:
        print("✗ FAILED: Error sending data")
        return False

if __name__ == "__main__":
    test_send_vitals()
```

Run the test:
```bash
python test_iot_api.py
```

---

## Step 8: Verify Data in Database

### Check Vital Signs in Django Admin

1. Go to: `https://yourdomain.com/admin/`
2. Navigate to **Healthcare** → **Vital Signs**
3. You should see the newly created record

### Check via Django Shell

```bash
python manage.py shell
```

```python
from healthcare.models import VitalSign
from healthcare.models_iot import DeviceDataReading

# Get recent vital signs
recent_vitals = VitalSign.objects.order_by('-recorded_date')[:5]
for vital in recent_vitals:
    print(f"{vital.patient.full_name}: HR={vital.heart_rate}, BP={vital.blood_pressure}")

# Get device readings
readings = DeviceDataReading.objects.order_by('-timestamp')[:5]
for reading in readings:
    print(f"{reading.device.device_name}: {reading.reading_type} at {reading.timestamp}")
```

---

## Complete Integration Examples

### Example 1: Continuous Monitoring (Python)

```python
#!/usr/bin/env python3
"""
Continuous vital signs monitoring and transmission
"""
import requests
import time
from datetime import datetime
import random  # Replace with actual sensor library

API_BASE_URL = "https://yourdomain.com/api"
API_KEY = "YOUR_API_KEY_HERE"

class VitalSignsMonitor:
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    def read_sensors(self):
        """Read data from sensors (replace with actual sensor code)"""
        return {
            "heart_rate": random.randint(60, 100),
            "blood_pressure_systolic": random.randint(110, 130),
            "blood_pressure_diastolic": random.randint(70, 90),
            "temperature": round(random.uniform(97.5, 99.5), 1),
            "oxygen_saturation": random.randint(95, 100),
        }

    def send_vitals(self, vitals):
        """Send vitals to server"""
        url = f"{API_BASE_URL}/v1/device/vitals"

        vitals["timestamp"] = datetime.utcnow().isoformat() + "Z"

        try:
            response = self.session.post(url, json=vitals, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result['success']:
                print(f"✓ Sent: HR={vitals['heart_rate']}, BP={vitals['blood_pressure_systolic']}/{vitals['blood_pressure_diastolic']}")
                return True
            else:
                print(f"✗ Error: {result['message']}")
                return False

        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False

    def run(self, interval=300):
        """Run continuous monitoring"""
        print(f"Starting vital signs monitoring (interval: {interval}s)")

        while True:
            try:
                # Read sensors
                vitals = self.read_sensors()

                # Send to server
                self.send_vitals(vitals)

                # Wait for next reading
                time.sleep(interval)

            except KeyboardInterrupt:
                print("\nStopping monitor...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(60)

# Start monitoring
monitor = VitalSignsMonitor(API_KEY)
monitor.run(interval=300)  # Send every 5 minutes
```

### Example 2: Batch Upload (Offline Support)

```python
#!/usr/bin/env python3
"""
Batch upload with offline queue support
"""
import requests
import json
import time
from datetime import datetime
from pathlib import Path

API_BASE_URL = "https://yourdomain.com/api"
API_KEY = "YOUR_API_KEY_HERE"
QUEUE_FILE = "vitals_queue.json"

class OfflineVitalsQueue:
    def __init__(self, api_key, queue_file):
        self.api_key = api_key
        self.queue_file = Path(queue_file)
        self.queue = self.load_queue()

    def load_queue(self):
        """Load queued readings from file"""
        if self.queue_file.exists():
            with open(self.queue_file, 'r') as f:
                return json.load(f)
        return []

    def save_queue(self):
        """Save queue to file"""
        with open(self.queue_file, 'w') as f:
            json.dump(self.queue, f, indent=2)

    def add_reading(self, vitals):
        """Add reading to queue"""
        vitals["timestamp"] = datetime.utcnow().isoformat() + "Z"
        self.queue.append(vitals)
        self.save_queue()
        print(f"Added to queue: {len(self.queue)} readings pending")

    def upload_queue(self):
        """Upload all queued readings"""
        if not self.queue:
            print("Queue is empty")
            return

        url = f"{API_BASE_URL}/v1/device/vitals/bulk"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Sort by timestamp
        self.queue.sort(key=lambda x: x['timestamp'])

        # Split into batches of 100
        batch_size = 100
        for i in range(0, len(self.queue), batch_size):
            batch = self.queue[i:i+batch_size]

            data = {"readings": batch}

            try:
                response = requests.post(url, json=data, headers=headers, timeout=30)
                response.raise_for_status()

                result = response.json()
                if result['success']:
                    print(f"✓ Uploaded {len(batch)} readings")
                    # Remove uploaded readings from queue
                    self.queue = self.queue[i+batch_size:]
                    self.save_queue()
                else:
                    print(f"✗ Upload failed: {result['message']}")
                    break

            except Exception as e:
                print(f"✗ Upload error: {e}")
                break

        if not self.queue:
            print("✓ All readings uploaded successfully!")

# Usage
queue = OfflineVitalsQueue(API_KEY, QUEUE_FILE)

# Add readings (even when offline)
queue.add_reading({
    "heart_rate": 72,
    "blood_pressure_systolic": 120,
    "blood_pressure_diastolic": 80
})

# Upload when online
queue.upload_queue()
```

---

## Troubleshooting

### Issue: 401 Unauthorized

**Cause**: Invalid API key

**Solution**:
1. Verify API key is correct
2. Check Authorization header format: `Bearer YOUR_KEY`
3. Ensure device is active in database

### Issue: 400 Validation Error

**Cause**: Invalid data format

**Solution**:
1. Check timestamp is ISO 8601 format with timezone
2. Verify all required fields are present
3. Check value ranges (e.g., heart_rate: 20-300)

### Issue: Connection Timeout

**Cause**: Network issues or server down

**Solution**:
1. Check internet connection
2. Verify server is running: `sudo systemctl status inhealth`
3. Check firewall allows HTTPS (port 443)
4. Implement retry logic with exponential backoff

### Issue: 403 Permission Denied

**Cause**: API key lacks permissions

**Solution**:
```bash
# Update API key permissions
python manage.py shell

from healthcare.models_iot import DeviceAPIKey
api_key = DeviceAPIKey.objects.get(key_prefix="abc12345")
api_key.can_write_vitals = True
api_key.save()
```

---

## Best Practices

### 1. Error Handling

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_session():
    """Create session with retry logic"""
    session = requests.Session()

    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)

    return session
```

### 2. Data Validation

```python
def validate_vitals(vitals):
    """Validate vital signs before sending"""
    if vitals.get('heart_rate'):
        if not (20 <= vitals['heart_rate'] <= 300):
            raise ValueError("Heart rate out of range")

    # Add more validations...
    return True
```

### 3. Secure Key Storage

```python
import os
from dotenv import load_dotenv

# Load from environment file
load_dotenv()
API_KEY = os.getenv('INHEALTH_API_KEY')

# Never hardcode API keys in source code!
```

### 4. Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('device.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Vital signs sent successfully")
```

---

## Next Steps

1. **Production Deployment**:
   - Set up HTTPS with SSL certificate (see SSL_SETUP_GUIDE.md)
   - Configure rate limiting
   - Set up monitoring and alerts

2. **Device Management**:
   - Create multiple API keys for backup
   - Set expiration dates on keys
   - Monitor API key usage

3. **Advanced Features**:
   - Implement ECG data transmission
   - Add activity/sleep data
   - Set up alert rules for abnormal readings

---

## Additional Resources

- **Full API Documentation**: IOT_API_DOCUMENTATION.md
- **SSL Setup Guide**: SSL_SETUP_GUIDE.md
- **Session Security**: SESSION_SECURITY_GUIDE.md
- **Support**: api-support@yourdomain.com

---

**Ready to deploy? Follow the SSL setup guide to enable HTTPS and go live!**
