# Generated migration to add all missing security and authentication fields to UserProfile

from django.db import migrations


def add_missing_userprofile_fields(apps, schema_editor):
    """Add all missing fields to user_profiles table if they don't exist"""

    # Define all fields that should exist
    fields_to_add = [
        # Security fields
        ('failed_login_attempts', 'INTEGER DEFAULT 0'),
        ('account_locked_until', 'TIMESTAMP WITH TIME ZONE NULL'),
        ('password_reset_token', 'VARCHAR(255) NULL'),
        ('password_reset_token_expires', 'TIMESTAMP WITH TIME ZONE NULL'),
        ('last_password_change', 'TIMESTAMP WITH TIME ZONE NULL'),

        # Email verification fields
        ('email_verification_token', 'VARCHAR(255) NULL'),
        ('email_verified', 'BOOLEAN DEFAULT FALSE'),
        ('email_verified_at', 'TIMESTAMP WITH TIME ZONE NULL'),

        # Enterprise authentication fields
        ('auth_provider', 'VARCHAR(50) NULL'),
        ('external_id', 'VARCHAR(255) NULL'),

        # MFA fields
        ('mfa_enabled', 'BOOLEAN DEFAULT FALSE'),
        ('mfa_secret', 'VARCHAR(32) NULL'),
        ('mfa_backup_codes', 'TEXT NULL'),

        # Timestamp fields
        ('created_at', 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()'),
        ('updated_at', 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()'),
    ]

    for field_name, field_def in fields_to_add:
        schema_editor.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='user_profiles' AND column_name='{field_name}'
                ) THEN
                    ALTER TABLE user_profiles ADD COLUMN {field_name} {field_def};
                END IF;
            END $$;
        """)


def remove_security_fields(apps, schema_editor):
    """Remove security fields"""
    schema_editor.execute("""
        ALTER TABLE user_profiles
        DROP COLUMN IF EXISTS failed_login_attempts,
        DROP COLUMN IF EXISTS account_locked_until,
        DROP COLUMN IF EXISTS password_reset_token,
        DROP COLUMN IF EXISTS password_reset_token_expires,
        DROP COLUMN IF EXISTS last_password_change,
        DROP COLUMN IF EXISTS email_verification_token,
        DROP COLUMN IF EXISTS email_verified,
        DROP COLUMN IF EXISTS email_verified_at,
        DROP COLUMN IF EXISTS auth_provider,
        DROP COLUMN IF EXISTS external_id,
        DROP COLUMN IF EXISTS mfa_enabled,
        DROP COLUMN IF EXISTS mfa_secret,
        DROP COLUMN IF EXISTS mfa_backup_codes;
    """)


class Migration(migrations.Migration):

    dependencies = [
        ('healthcare', '0015_add_ai_treatment_plans'),
    ]

    operations = [
        migrations.RunPython(add_missing_userprofile_fields, remove_security_fields),
    ]
