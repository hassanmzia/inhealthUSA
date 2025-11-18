# Generated manually for security and authentication fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthcare', '0015_add_ai_treatment_plans'),
    ]

    operations = [
        # Add security fields to UserProfile
        migrations.AddField(
            model_name='userprofile',
            name='failed_login_attempts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='account_locked_until',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='password_reset_token',
            field=models.CharField(max_length=255, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='password_reset_token_expires',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_password_change',
            field=models.DateTimeField(null=True, blank=True),
        ),
        # Add email verification fields to UserProfile
        migrations.AddField(
            model_name='userprofile',
            name='email_verification_token',
            field=models.CharField(max_length=255, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='email_verified_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        # Add enterprise authentication fields to UserProfile
        migrations.AddField(
            model_name='userprofile',
            name='auth_provider',
            field=models.CharField(max_length=50, blank=True, null=True, help_text='cac, okta, cognito, azure_ad, etc.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='external_id',
            field=models.CharField(max_length=255, blank=True, null=True, help_text='External authentication provider ID'),
        ),
        # Rename backup_codes to mfa_backup_codes if it exists
        migrations.RenameField(
            model_name='userprofile',
            old_name='backup_codes',
            new_name='mfa_backup_codes',
        ),
    ]
