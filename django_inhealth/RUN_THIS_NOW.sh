#!/bin/bash
# COPY AND PASTE THIS ENTIRE SCRIPT TO FIX THE ERROR NOW
#
# This script adds the missing security fields to user_profiles table
# Run as: bash RUN_THIS_NOW.sh

set -e  # Exit on any error

echo "=================================================="
echo "FIXING MISSING SECURITY FIELDS IN user_profiles"
echo "=================================================="
echo ""

# Get database connection info
DB_HOST="${DB_HOST:-localhost}"
DB_USER="${DB_USER:-inhealth_user}"
DB_NAME="${DB_NAME:-inhealth_db}"

echo "Connecting to database: $DB_NAME on $DB_HOST as $DB_USER"
echo ""

# Run the SQL commands
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" << 'EOF'
BEGIN;

-- Add all missing security fields
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0 NOT NULL;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS account_locked_until TIMESTAMP WITH TIME ZONE NULL;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR(255) NULL;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS password_reset_token_expires TIMESTAMP WITH TIME ZONE NULL;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS last_password_change TIMESTAMP WITH TIME ZONE NULL;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(255) NULL;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE NOT NULL;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP WITH TIME ZONE NULL;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(50) NULL;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS external_id VARCHAR(255) NULL;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS mfa_backup_codes TEXT NULL;

COMMIT;

-- Verify the changes
\echo ''
\echo '=== VERIFICATION: New columns added ==='
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'user_profiles'
    AND column_name IN (
        'failed_login_attempts', 'account_locked_until', 'password_reset_token',
        'password_reset_token_expires', 'last_password_change', 'email_verification_token',
        'email_verified', 'email_verified_at', 'auth_provider', 'external_id', 'mfa_backup_codes'
    )
ORDER BY column_name;
\echo ''
\echo '=== SUCCESS! Security fields added to user_profiles table ==='
\echo ''
EOF

echo ""
echo "=================================================="
echo "FIX APPLIED SUCCESSFULLY!"
echo "=================================================="
echo ""
echo "Now restart your Django application:"
echo "  sudo systemctl restart gunicorn"
echo ""
echo "Then test: https://inhealth.eminencetechsolutions.com:8899/mfa/setup/"
echo ""
