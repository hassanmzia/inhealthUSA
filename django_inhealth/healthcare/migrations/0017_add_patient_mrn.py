# Generated migration to add missing mrn field to Patient model

from django.db import migrations, models
import uuid


def generate_unique_mrn(apps, schema_editor):
    """
    Generate unique MRN for existing patients.
    MRN format: MRN-{6-digit-number}
    """
    Patient = apps.get_model('healthcare', 'Patient')
    db_alias = schema_editor.connection.alias

    patients = Patient.objects.using(db_alias).all()
    for i, patient in enumerate(patients, start=1):
        patient.mrn = f"MRN-{str(i).zfill(6)}"
        patient.save(using=db_alias)


class Migration(migrations.Migration):

    dependencies = [
        ('healthcare', '0016_add_timestamps_safely'),
    ]

    operations = [
        # Add mrn field as nullable first
        migrations.AddField(
            model_name='patient',
            name='mrn',
            field=models.CharField(
                max_length=50,
                null=True,
                blank=True,
                help_text='Medical Record Number'
            ),
        ),
        # Populate existing records with unique MRNs
        migrations.RunPython(generate_unique_mrn, migrations.RunPython.noop),
        # Now make it unique and non-nullable
        migrations.AlterField(
            model_name='patient',
            name='mrn',
            field=models.CharField(
                max_length=50,
                unique=True,
                help_text='Medical Record Number'
            ),
        ),
        # Add index
        migrations.AddIndex(
            model_name='patient',
            index=models.Index(fields=['mrn'], name='idx_patient_mrn'),
        ),
    ]
