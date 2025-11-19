# Generated migration to add timestamp fields to FamilyHistory

from django.db import migrations


def add_familyhistory_timestamps(apps, schema_editor):
    """Add timestamp fields to family_history table if they don't exist"""

    fields_to_add = [
        ('created_at', 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()'),
        ('updated_at', 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()'),
    ]

    for field_name, field_def in fields_to_add:
        schema_editor.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='family_history' AND column_name='{field_name}'
                ) THEN
                    ALTER TABLE family_history ADD COLUMN {field_name} {field_def};
                END IF;
            END $$;
        """)


def remove_familyhistory_timestamps(apps, schema_editor):
    """Remove timestamp fields"""
    schema_editor.execute("""
        ALTER TABLE family_history
        DROP COLUMN IF EXISTS created_at,
        DROP COLUMN IF EXISTS updated_at;
    """)


class Migration(migrations.Migration):

    dependencies = [
        ('healthcare', '0016_add_security_fields'),
    ]

    operations = [
        migrations.RunPython(add_familyhistory_timestamps, remove_familyhistory_timestamps),
    ]
