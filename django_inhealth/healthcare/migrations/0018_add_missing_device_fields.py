# Generated migration to add missing fields to Device model

from django.db import migrations, models
from django.core.validators import MinValueValidator, MaxValueValidator


def check_and_add_device_fields(apps, schema_editor):
    """
    Add missing fields to devices table if they don't exist.
    """
    # List of fields to add with their SQL definitions
    fields_to_add = [
        ('manufacturer', "VARCHAR(255) DEFAULT ''"),
        ('model_number', "VARCHAR(100) DEFAULT ''"),
        ('serial_number', "VARCHAR(100) DEFAULT ''"),
        ('firmware_version', "VARCHAR(50) DEFAULT ''"),
        ('battery_level', "INTEGER NULL"),
        ('notes', "TEXT DEFAULT ''"),
    ]

    for field_name, field_def in fields_to_add:
        schema_editor.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='devices' AND column_name='{field_name}'
                ) THEN
                    ALTER TABLE devices ADD COLUMN {field_name} {field_def};
                END IF;
            END $$;
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('healthcare', '0017_add_patient_mrn'),
    ]

    operations = [
        migrations.RunPython(check_and_add_device_fields, migrations.RunPython.noop),
    ]
