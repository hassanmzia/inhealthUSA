# Generated manually for MFA fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthcare', '0008_add_admin_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='mfa_enabled',
            field=models.BooleanField(default=False, help_text='Enable Two-Factor Authentication'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='mfa_secret',
            field=models.CharField(blank=True, help_text='TOTP Secret Key', max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='backup_codes',
            field=models.JSONField(blank=True, default=list, help_text='Backup codes for MFA recovery'),
        ),
    ]
