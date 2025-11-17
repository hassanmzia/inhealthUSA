# InHealth EHR - IoT Device Integration Guide

Complete guide for integrating IoT medical devices with InHealth EHR system.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Getting API Credentials](#getting-api-credentials)
- [Python Script Setup](#python-script-setup)
- [Bash Script Setup](#bash-script-setup)
- [JSON Data Format](#json-data-format)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

---

## Prerequisites

### For Python Script:
- Python 3.6 or higher
- `requests` library: `pip install requests`

### For Bash Script:
- `curl` (usually pre-installed on Linux)
- `jq` (optional, for pretty JSON output): `apt-get install jq` or `yum install jq`

---

## Getting API Credentials

1. **Log in to InHealth EHR** as System Administrator
2. **Navigate to**: System Admin Dashboard → **🔑 API Keys**
3. **Click**: "➕ Create New API Key"
4. **Configure the API Key**:
   - **Name**: e.g., "IoT Device Production"
   - **Description**: "API key for remote IoT vital sign devices"
   - **Permissions**: Check ✓ Vital Signs, ✓ IoT Devices
   - **Rate Limit**: 1000 requests/hour (or as needed)
   - **IP Whitelist**: (optional) Your IoT device IP addresses
   - **Expiration**: (optional) Set expiration date
   - **Status**: Active
5. **Click**: "✓ Create API Key"
6. **IMPORTANT**: Copy both the **API Key** and **API Secret** immediately - they are only shown once!

---

## Python Script Setup

### 1. Download the Script

```bash
# Download from your server
scp zia@inhealth.eminencetechsolutions.com:/home/user/inhealthUSA/iot_submit_vitals.py .
```

Or create `iot_submit_vitals.py` with the provided code.

### 2. Install Requirements

```bash
pip install requests
```

### 3. Set Environment Variables

```bash
# Add to ~/.bashrc or ~/.profile for persistence
export INHEALTH_API_KEY="your-api-key-here"
export INHEALTH_API_URL="https://inhealth.eminencetechsolutions.com:8899"
export INHEALTH_DEVICE_ID="DEV001"
```

### 4. Test the Script

```bash
# Make executable
chmod +x iot_submit_vitals.py

# Test connectivity
python3 iot_submit_vitals.py

# Submit data from JSON file
python3 iot_submit_vitals.py sample_vitals.json
```

### 5. Python Usage Examples

**Submit vitals from code:**
```python
from iot_submit_vitals import InHealthIoTClient

# Initialize client
client = InHealthIoTClient(
    api_url="https://inhealth.eminencetechsolutions.com:8899",
    api_key="your-api-key-here"
)

# Submit vitals
vitals = {
    "heart_rate": 75,
    "blood_pressure_systolic": 120,
    "blood_pressure_diastolic": 80,
    "temperature": 98.6,
    "temperature_unit": "F",
    "respiratory_rate": 16,
    "oxygen_saturation": 98.0,
    "glucose": 95.0
}

result = client.submit_vitals("DEV001", vitals)
print(result)
```

**Scheduled submission with cron:**
```bash
# Run every 5 minutes
*/5 * * * * /usr/bin/python3 /path/to/iot_submit_vitals.py >> /var/log/iot_submit.log 2>&1
```

---

## Bash Script Setup

### 1. Download the Script

```bash
# Download from your server
scp zia@inhealth.eminencetechsolutions.com:/home/user/inhealthUSA/iot_submit_vitals.sh .
```

Or create `iot_submit_vitals.sh` with the provided code.

### 2. Install Dependencies

```bash
# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install curl jq

# On RHEL/CentOS/Rocky
sudo yum install curl jq
```

### 3. Set Environment Variables

```bash
# Add to ~/.bashrc or /etc/environment
export INHEALTH_API_KEY="your-api-key-here"
export INHEALTH_API_URL="https://inhealth.eminencetechsolutions.com:8899"
export INHEALTH_DEVICE_ID="DEV001"
```

### 4. Test the Script

```bash
# Make executable
chmod +x iot_submit_vitals.sh

# Check API status
./iot_submit_vitals.sh --status

# Submit sample data
./iot_submit_vitals.sh

# Submit data from JSON file
./iot_submit_vitals.sh sample_vitals.json
```

### 5. Bash Usage Examples

**Submit vitals using curl directly:**
```bash
curl -X POST https://inhealth.eminencetechsolutions.com:8899/api/iot/vitals/ \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "DEV001",
    "timestamp": "2025-11-17T10:30:00Z",
    "heart_rate": 75,
    "blood_pressure_systolic": 120,
    "blood_pressure_diastolic": 80,
    "temperature": 98.6,
    "temperature_unit": "F",
    "respiratory_rate": 16,
    "oxygen_saturation": 98.0,
    "glucose": 95.0
  }'
```

**Scheduled submission with cron:**
```bash
# Run every 10 minutes
*/10 * * * * /path/to/iot_submit_vitals.sh /path/to/vitals.json >> /var/log/iot_submit.log 2>&1
```

---

## JSON Data Format

### Required Fields:
- `device_id` (string): Unique device identifier
- `timestamp` (string): ISO 8601 format (auto-generated if not provided)

### Optional Vital Sign Fields:
```json
{
  "device_id": "DEV001",
  "timestamp": "2025-11-17T10:30:00Z",
  "patient_id": 123,

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
  "height": 68.0,
  "height_unit": "in",

  "notes": "Optional notes about the reading",
  "signal_quality": 95,
  "battery_level": 80
}
```

### Temperature Units:
- `"F"` - Fahrenheit
- `"C"` - Celsius

### Weight Units:
- `"lbs"` - Pounds
- `"kg"` - Kilograms

### Height Units:
- `"in"` - Inches
- `"cm"` - Centimeters

---

## Testing

### 1. Test API Connectivity

**Python:**
```bash
python3 iot_submit_vitals.py
```

**Bash:**
```bash
./iot_submit_vitals.sh --status
```

### 2. Submit Test Data

Create `test_vitals.json`:
```json
{
  "device_id": "TEST001",
  "heart_rate": 72,
  "blood_pressure_systolic": 118,
  "blood_pressure_diastolic": 78,
  "temperature": 98.4,
  "temperature_unit": "F",
  "oxygen_saturation": 99.0
}
```

**Submit:**
```bash
# Python
python3 iot_submit_vitals.py test_vitals.json

# Bash
./iot_submit_vitals.sh test_vitals.json
```

### 3. Verify in InHealth EHR

1. Log in to InHealth EHR
2. Navigate to: System Admin Dashboard → **📁 IoT Device Files**
3. Check the **Inbox** for your JSON file
4. Wait for the cron job to process it (runs every minute)
5. Check **Archive** for processed files

---

## Troubleshooting

### Error: "Authentication failed"
- **Cause**: Invalid or missing API key
- **Fix**: Check that `INHEALTH_API_KEY` is set correctly
- **Verify**: Log in to InHealth EHR → API Keys → Check key status

### Error: "Connection refused" or "Connection timeout"
- **Cause**: Network connectivity issue
- **Fix**:
  - Check firewall rules
  - Verify URL: `https://inhealth.eminencetechsolutions.com:8899`
  - Test with: `curl -I https://inhealth.eminencetechsolutions.com:8899`

### Error: "Bad request" (HTTP 400)
- **Cause**: Invalid JSON format or missing required fields
- **Fix**:
  - Validate JSON: `cat vitals.json | jq '.'`
  - Ensure `device_id` is present
  - Check field names match expected format

### Error: "Rate limit exceeded"
- **Cause**: Too many API requests
- **Fix**:
  - Check rate limit in API key settings
  - Reduce request frequency
  - Contact admin to increase limit

### SSL Certificate Errors
- **Python**: Set `verify=False` in `session.post()` (not recommended for production)
- **Bash**: Add `-k` flag to curl (not recommended for production)
- **Recommended**: Install proper SSL certificate or add CA to trust store

---

## Production Deployment

### 1. Security Best Practices

**Protect API Keys:**
```bash
# Set restrictive permissions
chmod 600 ~/.env_inhealth

# Store in environment file
cat > ~/.env_inhealth <<EOF
export INHEALTH_API_KEY="your-api-key-here"
export INHEALTH_API_URL="https://inhealth.eminencetechsolutions.com:8899"
export INHEALTH_DEVICE_ID="PROD001"
EOF

# Source in scripts
source ~/.env_inhealth
```

**Use IP Whitelist:**
- Configure IP whitelist in API key settings
- Only allow specific IoT device IPs

### 2. Monitoring and Logging

**Enable logging:**
```bash
# Python with logging to file
python3 iot_submit_vitals.py >> /var/log/iot_vitals.log 2>&1

# Bash with timestamped logs
./iot_submit_vitals.sh 2>&1 | while read line; do echo "$(date '+%Y-%m-%d %H:%M:%S') $line"; done >> /var/log/iot_vitals.log
```

**Log rotation:**
```bash
# Create /etc/logrotate.d/iot_vitals
cat > /etc/logrotate.d/iot_vitals <<EOF
/var/log/iot_vitals.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

### 3. Systemd Service (Optional)

Create `/etc/systemd/system/iot-vitals.service`:
```ini
[Unit]
Description=InHealth IoT Vitals Submission
After=network.target

[Service]
Type=simple
User=iot
EnvironmentFile=/home/iot/.env_inhealth
ExecStart=/usr/bin/python3 /opt/iot/iot_submit_vitals.py
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable iot-vitals
sudo systemctl start iot-vitals
sudo systemctl status iot-vitals
```

### 4. Health Checks

**Create health check script:**
```bash
#!/bin/bash
# /opt/iot/health_check.sh

source ~/.env_inhealth

# Test API connectivity
if ./iot_submit_vitals.sh --status > /dev/null 2>&1; then
    echo "OK: InHealth EHR API is reachable"
    exit 0
else
    echo "CRITICAL: InHealth EHR API is unreachable"
    # Send alert (email, SMS, etc.)
    exit 2
fi
```

**Add to cron for monitoring:**
```bash
# Check every hour
0 * * * * /opt/iot/health_check.sh || mail -s "IoT API Alert" admin@example.com
```

---

## Support

For issues or questions:
- **System Administrator**: Check API Keys dashboard for usage statistics
- **Logs**: Review `/var/log/iot_vitals.log`
- **API Status**: Use `--status` flag to test connectivity
- **Documentation**: This guide and InHealth EHR admin documentation

---

## Quick Reference

| Action | Python | Bash |
|--------|--------|------|
| Submit sample data | `python3 iot_submit_vitals.py` | `./iot_submit_vitals.sh` |
| Submit from file | `python3 iot_submit_vitals.py vitals.json` | `./iot_submit_vitals.sh vitals.json` |
| Check API status | (automatic on run) | `./iot_submit_vitals.sh --status` |
| Help | Read code comments | `./iot_submit_vitals.sh --help` |

---

## Example Deployment Workflow

1. **Get API credentials** from InHealth EHR admin dashboard
2. **Download scripts** to IoT device/gateway
3. **Install dependencies** (Python requests or curl/jq)
4. **Set environment variables** with API credentials
5. **Test connectivity** with `--status` flag
6. **Submit test data** to verify setup
7. **Configure cron job** or systemd service for automated submission
8. **Monitor logs** and API key usage
9. **Set up alerts** for failures

---

*Last Updated: November 17, 2025*
