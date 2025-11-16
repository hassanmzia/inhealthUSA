#!/bin/bash
###############################################################################
# Helper Script to Copy SSL Certificates to Rocky Linux 9 Server
# Run this script from your LOCAL MACHINE (where certificates are located)
###############################################################################

echo "========================================================================="
echo "SSL Certificate Copy Helper - InHealth EHR"
echo "========================================================================="
echo ""

# Configuration - UPDATE THESE VALUES
CERT_DIR="/home/zia/test2/inhealth-cert"
SERVER_IP="YOUR_SERVER_IP_HERE"     # UPDATE THIS
SERVER_USER="root"                  # Usually root, or your sudo user

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if server IP is set
if [ "$SERVER_IP" = "YOUR_SERVER_IP_HERE" ]; then
    echo -e "${RED}ERROR: Please update SERVER_IP in this script${NC}"
    echo ""
    echo "Edit this file and set SERVER_IP to your Rocky Linux 9 server IP address"
    echo "  Example: SERVER_IP=\"192.168.1.100\""
    echo ""
    exit 1
fi

# Check if certificate directory exists
if [ ! -d "$CERT_DIR" ]; then
    echo -e "${RED}ERROR: Certificate directory not found: $CERT_DIR${NC}"
    echo ""
    echo "Please update CERT_DIR in this script to match your certificate location"
    exit 1
fi

echo "Certificate Directory: $CERT_DIR"
echo "Target Server: $SERVER_USER@$SERVER_IP"
echo ""

# Check for required certificate files
echo "Checking for certificate files..."
echo "========================================================================="

if [ -f "$CERT_DIR/certificate.crt" ]; then
    echo -e "${GREEN}✓ Found: certificate.crt${NC}"
    HAS_CERT=true
else
    echo -e "${RED}✗ Missing: certificate.crt${NC}"
    HAS_CERT=false
fi

if [ -f "$CERT_DIR/private.key" ]; then
    echo -e "${GREEN}✓ Found: private.key${NC}"
    HAS_KEY=true
else
    echo -e "${RED}✗ Missing: private.key${NC}"
    HAS_KEY=false
fi

if [ -f "$CERT_DIR/ca_bundle.crt" ]; then
    echo -e "${GREEN}✓ Found: ca_bundle.crt (optional)${NC}"
    HAS_BUNDLE=true
else
    echo -e "${YELLOW}⚠ Not found: ca_bundle.crt (optional - may not be needed)${NC}"
    HAS_BUNDLE=false
fi

echo ""

if [ "$HAS_CERT" = false ] || [ "$HAS_KEY" = false ]; then
    echo -e "${RED}ERROR: Required certificate files are missing${NC}"
    echo ""
    echo "Please ensure these files exist in $CERT_DIR:"
    echo "  - certificate.crt (your SSL certificate)"
    echo "  - private.key (your private key)"
    echo "  - ca_bundle.crt (optional certificate chain)"
    echo ""
    exit 1
fi

# Test SSH connection
echo "Testing SSH connection to server..."
echo "========================================================================="
if ssh -o ConnectTimeout=5 -o BatchMode=yes "$SERVER_USER@$SERVER_IP" "echo 'SSH connection successful'" 2>/dev/null; then
    echo -e "${GREEN}✓ SSH connection successful${NC}"
else
    echo -e "${YELLOW}⚠ SSH connection test failed${NC}"
    echo ""
    echo "You may need to:"
    echo "  1. Set up SSH key authentication"
    echo "  2. Verify the server IP and username"
    echo "  3. Check firewall rules"
    echo ""
    echo "Continuing anyway - you'll be prompted for password..."
fi
echo ""

# Copy certificate files
echo "Copying certificate files to server..."
echo "========================================================================="

# Copy certificate
echo "Copying certificate.crt..."
if scp "$CERT_DIR/certificate.crt" "$SERVER_USER@$SERVER_IP:/tmp/"; then
    echo -e "${GREEN}✓ Copied certificate.crt${NC}"
else
    echo -e "${RED}✗ Failed to copy certificate.crt${NC}"
    exit 1
fi

# Copy private key
echo "Copying private.key..."
if scp "$CERT_DIR/private.key" "$SERVER_USER@$SERVER_IP:/tmp/"; then
    echo -e "${GREEN}✓ Copied private.key${NC}"
else
    echo -e "${RED}✗ Failed to copy private.key${NC}"
    exit 1
fi

# Copy CA bundle if exists
if [ "$HAS_BUNDLE" = true ]; then
    echo "Copying ca_bundle.crt..."
    if scp "$CERT_DIR/ca_bundle.crt" "$SERVER_USER@$SERVER_IP:/tmp/"; then
        echo -e "${GREEN}✓ Copied ca_bundle.crt${NC}"
    else
        echo -e "${YELLOW}⚠ Failed to copy ca_bundle.crt (continuing anyway)${NC}"
    fi
fi

echo ""

echo "========================================================================="
echo -e "${GREEN}✓ Certificate files copied successfully!${NC}"
echo "========================================================================="
echo ""
echo "Files copied to server /tmp/ directory:"
echo "  - /tmp/certificate.crt"
echo "  - /tmp/private.key"
if [ "$HAS_BUNDLE" = true ]; then
    echo "  - /tmp/ca_bundle.crt"
fi
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "-----------"
echo "1. SSH into your server:"
echo "   ssh $SERVER_USER@$SERVER_IP"
echo ""
echo "2. Run the SSL installation script:"
echo "   cd /home/user/inhealthUSA"
echo "   sudo ./install_ssl_rocky9.sh --from-tmp"
echo ""
echo "3. Follow the on-screen instructions"
echo ""
echo "The script will:"
echo "  ✓ Validate your certificates"
echo "  ✓ Install them in /etc/ssl/inhealth/"
echo "  ✓ Configure Nginx for HTTPS"
echo "  ✓ Set up SELinux contexts"
echo "  ✓ Configure firewall rules"
echo "  ✓ Start HTTPS service"
echo ""
echo "========================================================================="
