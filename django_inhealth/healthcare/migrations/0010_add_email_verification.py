# Generated manually for email verification fields
from django.db import migrations, models


def add_email_verification_fields(apps, schema_editor):
    """Add email verification fields if they don't exist"""

    fields_to_add = [
        ('email_verified', 'BOOLEAN DEFAULT FALSE'),
        ('email_verification_token', 'VARCHAR(100) NULL'),
        ('email_verification_sent_at', 'TIMESTAMP WITH TIME ZONE NULL'),
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


def remove_email_verification_fields(apps, schema_editor):
    """Remove email verification fields"""
    schema_editor.execute("""
        ALTER TABLE user_profiles
        DROP COLUMN IF EXISTS email_verified,
        DROP COLUMN IF EXISTS email_verification_token,
        DROP COLUMN IF EXISTS email_verification_sent_at;
    """)


class Migration(migrations.Migration):

    dependencies = [
        ('healthcare', '0009_add_mfa_fields'),
    ]

    operations = [
        migrations.RunPython(add_email_verification_fields, remove_email_verification_fields),
    ]
