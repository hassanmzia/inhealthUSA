#!/bin/bash

#############################################################################
# InHealth Healthcare Application - Quick Development Setup
# For development purposes only - simpler than full production install
#############################################################################

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}InHealth EHR - Quick Setup${NC}"
echo -e "${GREEN}========================================${NC}"

# Check for required commands
command -v php >/dev/null 2>&1 || { echo "PHP is required but not installed. Aborting." >&2; exit 1; }
command -v composer >/dev/null 2>&1 || { echo "Composer is required but not installed. Aborting." >&2; exit 1; }
command -v mysql >/dev/null 2>&1 || { echo "MySQL is required but not installed. Aborting." >&2; exit 1; }

# Install Laravel dependencies
if [ ! -d "vendor" ]; then
    echo -e "${GREEN}Installing Composer dependencies...${NC}"
    composer install
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${GREEN}Creating .env file...${NC}"
    cp .env.example .env

    # Configure database
    sed -i "s/DB_DATABASE=.*/DB_DATABASE=ehr_database/" .env
    sed -i "s/DB_USERNAME=.*/DB_USERNAME=ehr_user/" .env
    sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=ehr_password_123/" .env

    # Generate application key
    php artisan key:generate
fi

# Import database schema
echo -e "${GREEN}Do you want to import the database schema? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${YELLOW}Please enter MySQL root password:${NC}"
    mysql -u root -p < ehr_schema.sql
fi

# Clear caches
php artisan config:clear
php artisan cache:clear

# Create storage link
php artisan storage:link 2>/dev/null || true

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Start the development server:${NC}"
echo -e "  ${YELLOW}php artisan serve${NC}"
echo ""
