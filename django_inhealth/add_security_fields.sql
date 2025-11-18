-- SQL script to add missing security fields to user_profiles table
-- Run this script on the production database to fix the ProgrammingError

-- Connect to your database first:
-- psql -h localhost -U inhealth_user -d inhealth_db

BEGIN;

-- Add security fields if they don't exist
DO $$
BEGIN
    -- Add failed_login_attempts field
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles' AND column_name = 'failed_login_attempts'
    ) THEN
        ALTER TABLE user_profiles ADD COLUMN failed_login_attempts INTEGER DEFAULT 0 NOT NULL;
    END IF;

    -- Add account_locked_until field
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles' AND column_name = 'account_locked_until'
    ) THEN
        ALTER TABLE user_profiles ADD COLUMN account_locked_until TIMESTAMP WITH TIME ZONE NULL;
    END IF;

    -- Add password_reset_token field
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles' AND column_name = 'password_reset_token'
    ) THEN
        ALTER TABLE user_profiles ADD COLUMN password_reset_token VARCHAR(255) NULL;
    END IF;

    -- Add password_reset_token_expires field
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles' AND column_name = 'password_reset_token_expires'
    ) THEN
        ALTER TABLE user_profiles ADD COLUMN password_reset_token_expires TIMESTAMP WITH TIME ZONE NULL;
    END IF;

    -- Add last_password_change field
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles' AND column_name = 'last_password_change'
    ) THEN
        ALTER TABLE user_profiles ADD COLUMN last_password_change TIMESTAMP WITH TIME ZONE NULL;
    END IF;

    -- Add email_verification_token field
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles' AND column_name = 'email_verification_token'
    ) THEN
        ALTER TABLE user_profiles ADD COLUMN email_verification_token VARCHAR(255) NULL;
    END IF;

    -- Add email_verified field
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles' AND column_name = 'email_verified'
    ) THEN
        ALTER TABLE user_profiles ADD COLUMN email_verified BOOLEAN DEFAULT FALSE NOT NULL;
    END IF;

    -- Add email_verified_at field
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles' AND column_name = 'email_verified_at'
    ) THEN
        ALTER TABLE user_profiles ADD COLUMN email_verified_at TIMESTAMP WITH TIME ZONE NULL;
    END IF;

    -- Add auth_provider field
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles' AND column_name = 'auth_provider'
    ) THEN
        ALTER TABLE user_profiles ADD COLUMN auth_provider VARCHAR(50) NULL;
    END IF;

    -- Add external_id field
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles' AND column_name = 'external_id'
    ) THEN
        ALTER TABLE user_profiles ADD COLUMN external_id VARCHAR(255) NULL;
    END IF;

    -- Rename backup_codes to mfa_backup_codes if needed
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles' AND column_name = 'backup_codes'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles' AND column_name = 'mfa_backup_codes'
    ) THEN
        ALTER TABLE user_profiles RENAME COLUMN backup_codes TO mfa_backup_codes;
    END IF;

    -- If mfa_backup_codes doesn't exist and backup_codes doesn't exist either, create it
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles' AND column_name = 'mfa_backup_codes'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles' AND column_name = 'backup_codes'
    ) THEN
        ALTER TABLE user_profiles ADD COLUMN mfa_backup_codes TEXT NULL;
    END IF;

END $$;

COMMIT;

-- Verify the changes
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'user_profiles'
ORDER BY ordinal_position;
