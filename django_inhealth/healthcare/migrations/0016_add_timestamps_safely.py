# Generated manually to add created_at and updated_at fields safely
# This migration checks if columns exist before adding them

from django.db import migrations


def add_timestamps_safely(apps, schema_editor):
    """
    Add created_at and updated_at columns to tables that don't have them.
    Uses raw SQL with IF NOT EXISTS logic to handle cases where some columns
    may already exist from previous migration attempts.
    """
    db_alias = schema_editor.connection.alias

    # List of tables that need timestamp fields
    tables = [
        'hospitals',
        'departments',
        'patients',
        'providers',
        'nurses',
        'office_administrators',
        'encounters',
        'diagnoses',
        'prescriptions',
        'allergies',
        'lab_tests',
        'medical_histories',
        'social_histories',
        'insurance_information',
        'messages',
        'notifications',
        'user_profiles',
    ]

    for table in tables:
        # Check and add created_at if it doesn't exist
        schema_editor.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='{table}' AND column_name='created_at'
                ) THEN
                    ALTER TABLE {table}
                    ADD COLUMN created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
                END IF;
            END $$;
        """)

        # Check and add updated_at if it doesn't exist
        schema_editor.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='{table}' AND column_name='updated_at'
                ) THEN
                    ALTER TABLE {table}
                    ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
                END IF;
            END $$;
        """)


def remove_timestamps(apps, schema_editor):
    """
    Reverse migration - remove timestamp columns.
    """
    tables = [
        'hospitals',
        'departments',
        'patients',
        'providers',
        'nurses',
        'office_administrators',
        'encounters',
        'diagnoses',
        'prescriptions',
        'allergies',
        'lab_tests',
        'medical_histories',
        'social_histories',
        'insurance_information',
        'messages',
        'notifications',
        'user_profiles',
    ]

    for table in tables:
        schema_editor.execute(f"""
            ALTER TABLE {table} DROP COLUMN IF EXISTS created_at;
            ALTER TABLE {table} DROP COLUMN IF EXISTS updated_at;
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('healthcare', '0015_add_ai_treatment_plans'),
    ]

    operations = [
        migrations.RunPython(add_timestamps_safely, remove_timestamps),
    ]
