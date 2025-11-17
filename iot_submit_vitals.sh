#!/bin/bash
################################################################################
# InHealth EHR - IoT Device Data Submission Script (Bash)
################################################################################
# Submit vital signs data from IoT devices to InHealth EHR via REST API
#
# Requirements:
#   - curl
#   - jq (optional, for pretty JSON output)
#
# Configuration:
#   Set environment variables:
#     export INHEALTH_API_KEY="your-api-key-here"
#     export INHEALTH_API_URL="https://inhealth.eminencetechsolutions.com:8899"
#     export INHEALTH_DEVICE_ID="DEV001"
#
# Usage:
#   ./iot_submit_vitals.sh                    # Submit sample data
#   ./iot_submit_vitals.sh vitals.json        # Submit data from JSON file
#   ./iot_submit_vitals.sh --status           # Check API status
################################################################################

set -o pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="${INHEALTH_API_URL:-https://inhealth.eminencetechsolutions.com:8899}"
API_KEY="${INHEALTH_API_KEY:-}"
DEVICE_ID="${INHEALTH_DEVICE_ID:-DEV001}"
MAX_RETRIES=3
TIMEOUT=30

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check dependencies
check_dependencies() {
    if ! command -v curl &> /dev/null; then
        log_error "curl is not installed. Please install it first."
        exit 1
    fi

    if command -v jq &> /dev/null; then
        HAS_JQ=true
    else
        HAS_JQ=false
        log_warning "jq not installed - JSON output will not be pretty-printed"
    fi
}

# Get current timestamp in ISO 8601 format
get_timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

# Submit vitals to InHealth EHR
submit_vitals() {
    local device_id="$1"
    local vitals_json="$2"
    local attempt=1

    # Add timestamp and device_id to vitals if not present
    local timestamp=$(get_timestamp)
    local payload=$(echo "$vitals_json" | jq -c --arg did "$device_id" --arg ts "$timestamp" \
        '. + {device_id: $did, timestamp: $ts}' 2>/dev/null || echo "$vitals_json")

    local endpoint="${API_URL}/api/iot/vitals/"

    log_info "Submitting vitals for device: $device_id"

    # Retry loop with exponential backoff
    while [ $attempt -le $MAX_RETRIES ]; do
        log_info "Attempt $attempt/$MAX_RETRIES..."

        # Make API request
        response=$(curl -s -w "\n%{http_code}" -X POST "$endpoint" \
            -H "Authorization: Bearer ${API_KEY}" \
            -H "Content-Type: application/json" \
            -H "User-Agent: InHealth-IoT-Client-Bash/1.0" \
            --data "$payload" \
            --connect-timeout $TIMEOUT \
            --max-time $TIMEOUT \
            2>&1)

        # Extract HTTP status code (last line)
        http_code=$(echo "$response" | tail -n1)
        # Extract response body (all except last line)
        body=$(echo "$response" | sed '$d')

        case $http_code in
            200)
                log_success "Data submitted successfully!"

                # Parse response
                if [ "$HAS_JQ" = true ]; then
                    echo "$body" | jq '.'

                    # Check for alerts
                    alerts=$(echo "$body" | jq -r '.alerts_triggered // 0')
                    if [ "$alerts" -gt 0 ]; then
                        log_warning "$alerts critical alert(s) triggered!"
                    fi

                    vital_id=$(echo "$body" | jq -r '.vital_sign_id // "N/A"')
                    log_info "Vital sign ID: $vital_id"
                else
                    echo "$body"
                fi

                return 0
                ;;

            401)
                log_error "Authentication failed - check your API key"
                echo "$body"
                return 1
                ;;

            400)
                log_error "Bad request - invalid data format"
                echo "$body"
                return 1
                ;;

            000)
                log_warning "Connection failed (attempt $attempt/$MAX_RETRIES)"
                ;;

            *)
                log_warning "HTTP $http_code (attempt $attempt/$MAX_RETRIES)"
                echo "$body"
                ;;
        esac

        # Exponential backoff before retry
        if [ $attempt -lt $MAX_RETRIES ]; then
            sleep_time=$((2 ** (attempt - 1)))
            log_info "Waiting ${sleep_time}s before retry..."
            sleep $sleep_time
        fi

        attempt=$((attempt + 1))
    done

    log_error "Failed to submit data after $MAX_RETRIES attempts"
    return 1
}

# Check API status
check_status() {
    local endpoint="${API_URL}/api/iot/status/"

    log_info "Checking API status at: $endpoint"

    response=$(curl -s -w "\n%{http_code}" -X GET "$endpoint" \
        -H "Authorization: Bearer ${API_KEY}" \
        --connect-timeout 10 \
        --max-time 10)

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        log_success "API is reachable"
        if [ "$HAS_JQ" = true ]; then
            echo "$body" | jq '.'
        else
            echo "$body"
        fi
        return 0
    else
        log_error "API status check failed (HTTP $http_code)"
        echo "$body"
        return 1
    fi
}

# Read vitals from JSON file
read_vitals_file() {
    local filepath="$1"

    if [ ! -f "$filepath" ]; then
        log_error "File not found: $filepath"
        return 1
    fi

    # Validate JSON
    if [ "$HAS_JQ" = true ]; then
        if ! jq empty "$filepath" 2>/dev/null; then
            log_error "Invalid JSON in file: $filepath"
            return 1
        fi
        cat "$filepath" | jq -c '.'
    else
        cat "$filepath"
    fi
}

# Generate sample vitals data
generate_sample_vitals() {
    cat <<EOF
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
EOF
}

# Main function
main() {
    check_dependencies

    # Check if API key is set
    if [ -z "$API_KEY" ]; then
        log_error "INHEALTH_API_KEY environment variable not set!"
        echo ""
        echo "Usage:"
        echo "  export INHEALTH_API_KEY='your-api-key-here'"
        echo "  export INHEALTH_API_URL='https://inhealth.eminencetechsolutions.com:8899'"
        echo "  export INHEALTH_DEVICE_ID='DEV001'"
        echo "  $0 [vitals.json|--status]"
        exit 1
    fi

    log_info "InHealth EHR IoT Data Submission"
    log_info "API URL: $API_URL"
    log_info "Device ID: $DEVICE_ID"
    echo ""

    # Handle command line arguments
    case "${1:-}" in
        --status|-s)
            check_status
            exit $?
            ;;

        --help|-h)
            echo "Usage: $0 [OPTIONS] [JSON_FILE]"
            echo ""
            echo "Options:"
            echo "  --status, -s    Check API status"
            echo "  --help, -h      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                     Submit sample vitals data"
            echo "  $0 vitals.json         Submit data from JSON file"
            echo "  $0 --status            Check API connectivity"
            echo ""
            echo "Environment Variables:"
            echo "  INHEALTH_API_KEY       API key (required)"
            echo "  INHEALTH_API_URL       API base URL (default: https://inhealth.eminencetechsolutions.com:8899)"
            echo "  INHEALTH_DEVICE_ID     Device identifier (default: DEV001)"
            exit 0
            ;;

        "")
            # No arguments - use sample data
            log_info "=== Submitting sample vitals data ==="
            vitals=$(generate_sample_vitals)
            submit_vitals "$DEVICE_ID" "$vitals"
            exit $?
            ;;

        *)
            # JSON file provided
            log_info "=== Submitting vitals from file: $1 ==="
            vitals=$(read_vitals_file "$1")

            if [ $? -ne 0 ]; then
                exit 1
            fi

            # Extract device_id from JSON if present
            if [ "$HAS_JQ" = true ]; then
                file_device_id=$(echo "$vitals" | jq -r '.device_id // empty')
                if [ -n "$file_device_id" ]; then
                    DEVICE_ID="$file_device_id"
                fi
            fi

            submit_vitals "$DEVICE_ID" "$vitals"
            exit $?
            ;;
    esac
}

# Run main function
main "$@"
