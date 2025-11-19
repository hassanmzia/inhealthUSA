# Generated manually to add created_at and updated_at fields to all models

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('healthcare', '0014_add_vital_sign_alert_response'),
    ]

    operations = [
        # Add timestamps to Allergy
        migrations.AddField(
            model_name='allergy',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allergy',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamps to Diagnosis
        migrations.AddField(
            model_name='diagnosis',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='diagnosis',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamps to Department
        migrations.AddField(
            model_name='department',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='department',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamps to Encounter
        migrations.AddField(
            model_name='encounter',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='encounter',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamps to Hospital
        migrations.AddField(
            model_name='hospital',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hospital',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamps to InsuranceInformation
        migrations.AddField(
            model_name='insuranceinformation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='insuranceinformation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamps to LabTest
        migrations.AddField(
            model_name='labtest',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='labtest',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamps to MedicalHistory
        migrations.AddField(
            model_name='medicalhistory',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='medicalhistory',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamps to Message
        migrations.AddField(
            model_name='message',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        # Add timestamps to Notification
        migrations.AddField(
            model_name='notification',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        # Add timestamps to Nurse
        migrations.AddField(
            model_name='nurse',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='nurse',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamps to OfficeAdministrator
        migrations.AddField(
            model_name='officeadministrator',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='officeadministrator',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamps to Patient
        migrations.AddField(
            model_name='patient',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patient',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamps to Prescription
        migrations.AddField(
            model_name='prescription',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='prescription',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamps to Provider
        migrations.AddField(
            model_name='provider',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='provider',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamps to SocialHistory
        migrations.AddField(
            model_name='socialhistory',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='socialhistory',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add timestamps to UserProfile
        migrations.AddField(
            model_name='userprofile',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
