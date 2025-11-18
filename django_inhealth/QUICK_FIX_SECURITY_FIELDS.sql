-- QUICK FIX: Add missing security fields to user_profiles table
-- Run this NOW to fix the MFA setup error
--
-- USAGE:
-- psql -h localhost -U inhealth_user -d inhealth_db -f QUICK_FIX_SECURITY_FIELDS.sql

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

-- Show the columns to verify
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'user_profiles'
    AND column_name IN (
        'failed_login_attempts', 'account_locked_until', 'password_reset_token',
        'password_reset_token_expires', 'last_password_change', 'email_verification_token',
        'email_verified', 'email_verified_at', 'auth_provider', 'external_id', 'mfa_backup_codes'
    )
ORDER BY column_name;
