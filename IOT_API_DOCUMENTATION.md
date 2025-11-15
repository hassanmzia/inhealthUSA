```
# InHealth EHR - IoT Device REST API Documentation

## Overview

This REST API allows IoT medical devices to securely transmit health data to the InHealth EHR system using HTTPS and token-based authentication.

**API Version**: 1.0
**Base URL**: `https://yourdomain.com/api/`
**Authentication**: Bearer Token (API Key)
**Content-Type**: `application/json`

---

## Table of Contents

1. [Authentication](#authentication)
2. [API Endpoints](#api-endpoints)
3. [Data Formats](#data-formats)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Examples](#examples)
7. [SDKs and Libraries](#sdks-and-libraries)

---

## Authentication

### API Key Authentication

All API requests must include an API key in the Authorization header:

```http
Authorization: Bearer YOUR_API_KEY_HERE
```

### Obtaining an API Key

1. Register your device through the InHealth admin panel
2. An API key will be generated for your device
3. **Store this key securely** - it will only be shown once
4. Use the key in all API requests

### Example Authentication

```bash
curl -X POST https://yourdomain.com/api/v1/device/auth \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "device_unique_id": "MAC:00:11:22:33:44:55",
    "api_key": "YOUR_API_KEY"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Authentication successful",
  "data": {
    "device_id": 123,
    "device_name": "Patient Watch",
    "patient_id": 456,
    "permissions": {
      "can_write_vitals": true,
      "can_read_patient": false
    }
  },
  "timestamp": "2025-11-15T20:00:00Z"
}
```

---

## API Endpoints

### 1. Authentication

#### POST `/api/v1/device/auth`

Authenticate device and verify API key.

**Request:**
```json
{
  "device_unique_id": "MAC:00:11:22:33:44:55",
  "api_key": "YOUR_API_KEY"
}
```

**Response:** See example above

---

### 2. Device Information

#### GET `/api/v1/device/info`

Get current device information.

**Headers:**
```http
Authorization: Bearer YOUR_API_KEY
```

**Response:**
```json
{
  "success": true,
  "message": "Device information",
  "data": {
    "device_id": 123,
    "device_unique_id": "MAC:00:11:22:33:44:55",
    "device_type": "Watch",
    "device_name": "Patient Watch",
    "manufacturer": "HealthTech Inc",
    "model_number": "HT-W100",
    "firmware_version": "2.3.1",
    "status": "Active",
    "battery_level": 85,
    "last_sync": "2025-11-15T19:45:00Z"
  },
  "timestamp": "2025-11-15T20:00:00Z"
}
```

---

### 3. Update Device Status

#### PUT `/api/v1/device/status`

Update device status (battery level, firmware, etc.).

**Request:**
```json
{
  "battery_level": 85,
  "firmware_version": "2.3.1",
  "status": "Active",
  "last_sync": "2025-11-15T19:45:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Device status updated",
  "data": {
    "device_id": 123,
    "battery_level": 85,
    "firmware_version": "2.3.1",
    "status": "Active",
    "last_sync": "2025-11-15T19:45:00Z"
  },
  "timestamp": "2025-11-15T20:00:00Z"
}
```

---

### 4. Post Vital Signs Data

#### POST `/api/v1/device/vitals`

Submit vital signs data from device.

**Request:**
```json
{
  "timestamp": "2025-11-15T19:45:00Z",
  "heart_rate": 72,
  "blood_pressure_systolic": 120,
  "blood_pressure_diastolic": 80,
  "temperature": 98.6,
  "oxygen_saturation": 98,
  "respiratory_rate": 16,
  "battery_level": 85,
  "signal_quality": 95,
  "firmware_version": "2.3.1"
}
```

**Field Descriptions:**

| Field | Type | Required | Range | Description |
|-------|------|----------|-------|-------------|
| `timestamp` | ISO 8601 DateTime | Yes | Not future | When reading was taken |
| `heart_rate` | Integer | No | 20-300 | Heart rate in BPM |
| `blood_pressure_systolic` | Integer | No* | 50-300 | Systolic BP in mmHg |
| `blood_pressure_diastolic` | Integer | No* | 30-200 | Diastolic BP in mmHg |
| `temperature` | Float | No | 90-110 | Temperature in Fahrenheit |
| `oxygen_saturation` | Integer | No | 50-100 | SpO2 percentage |
| `respiratory_rate` | Integer | No | 5-60 | Breaths per minute |
| `weight` | Float | No | 0-1000 | Weight in pounds |
| `height` | Float | No | 0-300 | Height in inches |
| `battery_level` | Integer | No | 0-100 | Device battery percentage |
| `signal_quality` | Integer | No | 0-100 | Sensor signal quality |
| `firmware_version` | String | No | - | Device firmware version |

*Note: Both systolic and diastolic BP must be provided together

**Response:**
```json
{
  "success": true,
  "message": "Vital signs recorded successfully",
  "data": {
    "vital_sign_id": 789,
    "reading_id": 1001,
    "timestamp": "2025-11-15T19:45:00Z"
  },
  "timestamp": "2025-11-15T20:00:00Z"
}
```

---

### 5. Bulk Post Vital Signs

#### POST `/api/v1/device/vitals/bulk`

Submit multiple vital signs readings at once (up to 100).

**Request:**
```json
{
  "readings": [
    {
      "timestamp": "2025-11-15T19:00:00Z",
      "heart_rate": 70,
      "blood_pressure_systolic": 118,
      "blood_pressure_diastolic": 78
    },
    {
      "timestamp": "2025-11-15T19:15:00Z",
      "heart_rate": 72,
      "blood_pressure_systolic": 120,
      "blood_pressure_diastolic": 80
    },
    {
      "timestamp": "2025-11-15T19:30:00Z",
      "heart_rate": 75,
      "blood_pressure_systolic": 122,
      "blood_pressure_diastolic": 82
    }
  ]
}
```

**Requirements:**
- Maximum 100 readings per request
- Readings must be in chronological order
- Each reading follows same format as single vital signs post

**Response:**
```json
{
  "success": true,
  "message": "Successfully recorded 3 vital signs readings",
  "data": {
    "count": 3,
    "records": [
      {
        "vital_sign_id": 789,
        "timestamp": "2025-11-15T19:00:00Z"
      },
      {
        "vital_sign_id": 790,
        "timestamp": "2025-11-15T19:15:00Z"
      },
      {
        "vital_sign_id": 791,
        "timestamp": "2025-11-15T19:30:00Z"
      }
    ]
  },
  "timestamp": "2025-11-15T20:00:00Z"
}
```

---

### 6. Post Blood Glucose Data

#### POST `/api/v1/device/glucose`

Submit blood glucose readings.

**Request:**
```json
{
  "timestamp": "2025-11-15T19:45:00Z",
  "glucose_level": 95.5,
  "meal_context": "fasting",
  "notes": "Morning reading before breakfast"
}
```

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | ISO 8601 DateTime | Yes | When reading was taken |
| `glucose_level` | Float | Yes | Glucose in mg/dL (0-600) |
| `meal_context` | String | No | fasting, before_meal, after_meal, bedtime, random |
| `notes` | String | No | Additional notes (max 500 chars) |

**Response:**
```json
{
  "success": true,
  "message": "Glucose data recorded",
  "data": {
    "reading_id": 1002
  },
  "timestamp": "2025-11-15T20:00:00Z"
}
```

---

## Data Formats

### Timestamp Format

All timestamps must be in ISO 8601 format with timezone:

```
2025-11-15T19:45:00Z          # UTC
2025-11-15T14:45:00-05:00     # Eastern Time
```

**Invalid formats:**
- `2025-11-15 19:45:00` ❌ (missing T and timezone)
- `11/15/2025 7:45 PM` ❌ (wrong format)

### Standard Response Format

All API responses follow this structure:

```json
{
  "success": true | false,
  "message": "Human-readable message",
  "data": { ... },              // Present on success
  "errors": { ... },            // Present on validation errors
  "timestamp": "ISO 8601 datetime"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Data created successfully |
| 400 | Bad Request | Validation error or malformed request |
| 401 | Unauthorized | Invalid or missing API key |
| 403 | Forbidden | Valid key but insufficient permissions |
| 404 | Not Found | Device or resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error (contact support) |

### Error Response Format

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "heart_rate": ["Ensure this value is less than or equal to 300."],
    "timestamp": ["Timestamp cannot be in the future"]
  },
  "timestamp": "2025-11-15T20:00:00Z"
}
```

### Common Errors

#### 1. Invalid API Key

```json
{
  "success": false,
  "message": "Unauthorized: Invalid or missing API key",
  "timestamp": "2025-11-15T20:00:00Z"
}
```

**Solution:** Check API key in Authorization header

#### 2. Validation Error

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "timestamp": ["This field is required"],
    "heart_rate": ["Ensure this value is greater than or equal to 20"]
  },
  "timestamp": "2025-11-15T20:00:00Z"
}
```

**Solution:** Fix validation errors and retry

#### 3. Permission Denied

```json
{
  "success": false,
  "message": "Permission denied: Cannot write vital signs",
  "timestamp": "2025-11-15T20:00:00Z"
}
```

**Solution:** Contact admin to update API key permissions

---

## Rate Limiting

To protect server resources, rate limiting is enforced:

| Endpoint | Limit |
|----------|-------|
| Authentication | 10 requests/minute |
| Data Submission | 100 requests/minute |
| Bulk Upload | 10 requests/minute |
| Device Info | 60 requests/minute |

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1636992000
```

**Rate Limit Exceeded Response:**
```json
{
  "success": false,
  "message": "Rate limit exceeded. Please try again later.",
  "timestamp": "2025-11-15T20:00:00Z"
}
```

---

## Examples

### Example 1: Simple Vital Signs Submission (Python)

```python
import requests
from datetime import datetime

# Configuration
API_BASE_URL = "https://yourdomain.com/api"
API_KEY = "YOUR_API_KEY_HERE"

def send_vitals(heart_rate, blood_pressure_sys, blood_pressure_dia):
    """Send vital signs to InHealth EHR"""

    url = f"{API_BASE_URL}/v1/device/vitals"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "heart_rate": heart_rate,
        "blood_pressure_systolic": blood_pressure_sys,
        "blood_pressure_diastolic": blood_pressure_dia,
        "battery_level": 85,
        "signal_quality": 95
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        result = response.json()
        print(f"✓ Success: {result['message']}")
        print(f"  Vital Sign ID: {result['data']['vital_sign_id']}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"  {response.json()['message']}")

# Example usage
send_vitals(heart_rate=72, blood_pressure_sys=120, blood_pressure_dia=80)
```

### Example 2: Bulk Upload with Error Handling (Python)

```python
import requests
from datetime import datetime, timedelta

API_BASE_URL = "https://yourdomain.com/api"
API_KEY = "YOUR_API_KEY_HERE"

def send_bulk_vitals(readings):
    """Send multiple vital signs readings"""

    url = f"{API_BASE_URL}/v1/device/vitals/bulk"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {"readings": readings}

    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()

        result = response.json()
        if result['success']:
            print(f"✓ Uploaded {result['data']['count']} readings")
            return True
        else:
            print(f"✗ Upload failed: {result['message']}")
            if 'errors' in result:
                print(f"  Errors: {result['errors']}")
            return False

    except requests.exceptions.Timeout:
        print("✗ Request timeout - check network connection")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ Connection error - server may be down")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

# Generate sample readings
base_time = datetime.utcnow()
readings = []

for i in range(5):
    timestamp = (base_time - timedelta(minutes=15*i)).isoformat() + "Z"
    readings.append({
        "timestamp": timestamp,
        "heart_rate": 70 + i,
        "blood_pressure_systolic": 118 + i,
        "blood_pressure_diastolic": 78 + i
    })

# Reverse to put in chronological order
readings.reverse()

# Send readings
send_bulk_vitals(readings)
```

### Example 3: Arduino/ESP32 Integration (C++)

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// Configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* apiBaseUrl = "https://yourdomain.com/api";
const char* apiKey = "YOUR_API_KEY_HERE";

void sendVitals(int heartRate, int sysBP, int diaBP) {
    HTTPClient http;

    // Prepare URL
    String url = String(apiBaseUrl) + "/v1/device/vitals";

    // Prepare JSON payload
    StaticJsonDocument<512> doc;
    doc["timestamp"] = getCurrentISOTime();  // Implement this function
    doc["heart_rate"] = heartRate;
    doc["blood_pressure_systolic"] = sysBP;
    doc["blood_pressure_diastolic"] = diaBP;
    doc["battery_level"] = getBatteryLevel();  // Implement this function
    doc["signal_quality"] = 95;

    String jsonPayload;
    serializeJson(doc, jsonPayload);

    // Send POST request
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", String("Bearer ") + apiKey);

    int httpCode = http.POST(jsonPayload);

    if (httpCode == 201) {
        String response = http.getString();
        Serial.println("✓ Vitals sent successfully");
        Serial.println(response);
    } else {
        Serial.printf("✗ Error: HTTP %d\n", httpCode);
        Serial.println(http.getString());
    }

    http.end();
}

void setup() {
    Serial.begin(115200);

    // Connect to WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");
}

void loop() {
    // Read sensors
    int heartRate = readHeartRateSensor();  // Implement this
    int sysBP = readBPSystolic();           // Implement this
    int diaBP = readBPDiastolic();          // Implement this

    // Send to server
    sendVitals(heartRate, sysBP, diaBP);

    // Wait 15 minutes
    delay(900000);
}
```

### Example 4: Raspberry Pi Integration (Python)

```python
#!/usr/bin/env python3
"""
InHealth EHR IoT Device Client
For Raspberry Pi with connected sensors
"""

import requests
import time
import json
from datetime import datetime
import RPi.GPIO as GPIO  # For sensor reading

# Configuration
API_BASE_URL = "https://yourdomain.com/api"
API_KEY = "YOUR_API_KEY_HERE"
DEVICE_ID = "RPI:B827EB123456"

class InHealthClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    def send_vitals(self, vitals_data):
        """Send vital signs to InHealth EHR"""
        url = f"{API_BASE_URL}/v1/device/vitals"

        vitals_data["timestamp"] = datetime.utcnow().isoformat() + "Z"

        try:
            response = self.session.post(url, json=vitals_data, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result['success']:
                print(f"✓ Vitals sent: ID {result['data']['vital_sign_id']}")
                return True
            else:
                print(f"✗ Failed: {result['message']}")
                return False

        except Exception as e:
            print(f"✗ Error sending vitals: {e}")
            return False

    def update_status(self, battery_level):
        """Update device status"""
        url = f"{API_BASE_URL}/v1/device/status"

        data = {
            "battery_level": battery_level,
            "firmware_version": "1.0.0",
            "status": "Active"
        }

        try:
            response = self.session.put(url, json=data, timeout=10)
            response.raise_for_status()
            print("✓ Status updated")
            return True
        except Exception as e:
            print(f"✗ Error updating status: {e}")
            return False

# Initialize client
client = InHealthClient(API_KEY)

def read_sensors():
    """Read data from connected sensors"""
    # Replace with actual sensor reading code
    return {
        "heart_rate": 72,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80,
        "temperature": 98.6,
        "oxygen_saturation": 98,
        "battery_level": 85,
        "signal_quality": 95
    }

def main():
    """Main loop"""
    print("InHealth EHR IoT Client Started")

    while True:
        try:
            # Read sensors
            vitals = read_sensors()

            # Send to server
            client.send_vitals(vitals)

            # Update status every 10th reading
            if int(time.time()) % 600 == 0:
                client.update_status(vitals.get("battery_level", 100))

            # Wait 5 minutes
            time.sleep(300)

        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(60)  # Wait 1 minute on error

if __name__ == "__main__":
    main()
```

---

## SDKs and Libraries

### Official Python SDK

```bash
pip install inhealth-iot-sdk
```

```python
from inhealth_iot import InHealthClient

client = InHealthClient(api_key="YOUR_API_KEY")

# Send vitals
client.send_vitals(
    heart_rate=72,
    blood_pressure=(120, 80),
    temperature=98.6
)

# Bulk upload
client.send_bulk_vitals(readings_list)
```

### JavaScript/Node.js SDK

```bash
npm install inhealth-iot-sdk
```

```javascript
const InHealthClient = require('inhealth-iot-sdk');

const client = new InHealthClient('YOUR_API_KEY');

// Send vitals
await client.sendVitals({
    heartRate: 72,
    bloodPressure: [120, 80],
    temperature: 98.6
});
```

---

## Security Best Practices

### 1. API Key Security

✅ **DO:**
- Store API keys in environment variables or secure key storage
- Use HTTPS for all API requests
- Rotate API keys periodically (every 90 days)
- Use separate API keys for development and production

❌ **DON'T:**
- Hardcode API keys in source code
- Commit API keys to version control
- Share API keys between devices
- Log API keys in plain text

### 2. Data Transmission

✅ **DO:**
- Always use HTTPS (never HTTP)
- Validate SSL certificates
- Implement request timeout (10-30 seconds)
- Retry failed requests with exponential backoff

### 3. Error Handling

✅ **DO:**
- Implement comprehensive error handling
- Log errors for debugging
- Queue data locally if server is unreachable
- Validate data before sending

---

## Testing

### Test Endpoint

Use the authentication endpoint to test connectivity:

```bash
curl -X POST https://yourdomain.com/api/v1/device/auth \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "device_unique_id": "TEST-DEVICE-001",
    "api_key": "YOUR_API_KEY"
  }'
```

### Test Data

Use these test values for initial testing:

```json
{
  "timestamp": "2025-11-15T20:00:00Z",
  "heart_rate": 72,
  "blood_pressure_systolic": 120,
  "blood_pressure_diastolic": 80,
  "temperature": 98.6,
  "oxygen_saturation": 98,
  "respiratory_rate": 16,
  "battery_level": 85,
  "signal_quality": 95
}
```

---

## Support

### API Status

Check API status at: https://status.yourdomain.com

### Documentation

- Full API Reference: https://api.yourdomain.com/docs
- Developer Portal: https://developers.yourdomain.com

### Contact

- Technical Support: api-support@yourdomain.com
- Emergency Issues: +1-555-API-HELP

---

## Changelog

### Version 1.0 (2025-11-15)

- Initial release
- Device authentication with API keys
- Vital signs data submission (single and bulk)
- Blood glucose data support
- Device status updates
- Rate limiting
- Comprehensive error handling

---

## License

This API is provided for use with registered InHealth EHR IoT devices only.
Unauthorized use is prohibited.

Copyright © 2025 InHealth EHR. All rights reserved.
```
