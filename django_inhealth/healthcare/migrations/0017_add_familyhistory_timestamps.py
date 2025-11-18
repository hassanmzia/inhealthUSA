# Generated migration to add timestamp fields to FamilyHistory
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('healthcare', '0016_add_security_fields'),
    ]

    operations = [
        # Add created_at with a default for existing rows
        migrations.AddField(
            model_name='familyhistory',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,  # Don't keep default in schema after migration
        ),
        # Add updated_at
        migrations.AddField(
            model_name='familyhistory',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
