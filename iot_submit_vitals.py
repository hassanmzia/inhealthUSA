#!/usr/bin/env python3
"""
InHealth EHR - IoT Device Data Submission Script
=================================================
Submit vital signs data from IoT devices to InHealth EHR via REST API

Requirements:
    pip install requests

Configuration:
    Set your API credentials in the script or use environment variables:
    export INHEALTH_API_KEY="your-api-key-here"
    export INHEALTH_API_URL="https://inhealth.eminencetechsolutions.com:8899"
"""

import requests
import json
import sys
import os
from datetime import datetime
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InHealthIoTClient:
    """Client for submitting IoT vital signs data to InHealth EHR"""

    def __init__(self, api_url, api_key):
        """
        Initialize the IoT client

        Args:
            api_url: Base URL of InHealth EHR (e.g., https://inhealth.example.com:8899)
            api_key: API key from InHealth EHR system admin
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'InHealth-IoT-Client/1.0'
        })

    def submit_vitals(self, device_id, vitals_data, max_retries=3):
        """
        Submit vital signs data to InHealth EHR

        Args:
            device_id: Unique device identifier (e.g., "DEV001")
            vitals_data: Dictionary containing vital signs measurements
            max_retries: Number of retry attempts on failure

        Returns:
            dict: Response from API or None on failure

        Example vitals_data:
            {
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
                "signal_quality": 95,
                "battery_level": 80
            }
        """
        # Prepare payload
        payload = {
            "device_id": device_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            **vitals_data
        }

        endpoint = f"{self.api_url}/api/iot/vitals/"

        # Retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                logger.info(f"Submitting vitals for device {device_id} (attempt {attempt + 1}/{max_retries})")

                response = self.session.post(
                    endpoint,
                    json=payload,
                    timeout=30,
                    verify=True  # Set to False if using self-signed SSL cert
                )

                # Check response
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        logger.info(f"✓ Success: {result.get('message', 'Data submitted')}")
                        if result.get('alerts_triggered'):
                            logger.warning(f"⚠ {result['alerts_triggered']} critical alert(s) triggered!")
                        return result
                    else:
                        logger.error(f"✗ API returned error: {result.get('error', 'Unknown error')}")
                        return None

                elif response.status_code == 401:
                    logger.error("✗ Authentication failed - check your API key")
                    return None  # Don't retry auth failures

                elif response.status_code == 400:
                    logger.error(f"✗ Bad request: {response.text}")
                    return None  # Don't retry bad requests

                else:
                    logger.warning(f"HTTP {response.status_code}: {response.text}")

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{max_retries})")

            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error: {e} (attempt {attempt + 1}/{max_retries})")

            except Exception as e:
                logger.error(f"Unexpected error: {e}")

            # Wait before retry (exponential backoff)
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                logger.info(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)

        logger.error(f"✗ Failed to submit data after {max_retries} attempts")
        return None

    def check_status(self):
        """Check API status and connectivity"""
        endpoint = f"{self.api_url}/api/iot/status/"

        try:
            response = self.session.get(endpoint, timeout=10)
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✓ API Status: {result.get('status', 'unknown')}")
                return result
            else:
                logger.error(f"✗ Status check failed: HTTP {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"✗ Status check error: {e}")
            return None


def read_vitals_from_file(filepath):
    """
    Read vital signs data from JSON file

    Args:
        filepath: Path to JSON file containing vital signs

    Returns:
        dict: Vital signs data or None on error
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            logger.info(f"Loaded vitals from {filepath}")
            return data
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return None


def main():
    """Main entry point"""

    # Configuration - Use environment variables or hardcode
    API_URL = os.getenv('INHEALTH_API_URL', 'https://inhealth.eminencetechsolutions.com:8899')
    API_KEY = os.getenv('INHEALTH_API_KEY', '')
    DEVICE_ID = os.getenv('INHEALTH_DEVICE_ID', 'DEV001')

    if not API_KEY:
        logger.error("ERROR: INHEALTH_API_KEY environment variable not set!")
        logger.info("Usage: export INHEALTH_API_KEY='your-api-key-here'")
        sys.exit(1)

    # Initialize client
    client = InHealthIoTClient(API_URL, API_KEY)

    # Check API status (optional)
    logger.info("Checking API connectivity...")
    status = client.check_status()
    if not status:
        logger.warning("API status check failed, but continuing anyway...")

    # Example 1: Submit vitals from code
    logger.info("\n=== Example 1: Submitting vitals from code ===")
    vitals = {
        "heart_rate": 75,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80,
        "temperature": 98.6,
        "temperature_unit": "F",
        "respiratory_rate": 16,
        "oxygen_saturation": 98.0,
        "glucose": 95.0,
        "signal_quality": 95,
        "battery_level": 80
    }

    result = client.submit_vitals(DEVICE_ID, vitals)
    if result:
        logger.info(f"Vital sign ID: {result.get('vital_sign_id')}")

    # Example 2: Submit vitals from JSON file
    if len(sys.argv) > 1:
        logger.info(f"\n=== Example 2: Submitting vitals from file ===")
        json_file = sys.argv[1]
        vitals_from_file = read_vitals_from_file(json_file)

        if vitals_from_file:
            # Extract device_id if present in file, otherwise use default
            device_id = vitals_from_file.pop('device_id', DEVICE_ID)
            patient_id = vitals_from_file.pop('patient_id', None)

            # Add patient_id back if it was in the file
            if patient_id:
                vitals_from_file['patient_id'] = patient_id

            result = client.submit_vitals(device_id, vitals_from_file)
            if result:
                logger.info(f"Vital sign ID: {result.get('vital_sign_id')}")

    logger.info("\n=== Done ===")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
