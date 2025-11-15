# Generated manually for email verification fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthcare', '0009_add_mfa_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='email_verified',
            field=models.BooleanField(default=False, help_text='Email address verified'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='email_verification_token',
            field=models.CharField(blank=True, help_text='Email verification token', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='email_verification_sent_at',
            field=models.DateTimeField(blank=True, help_text='When verification email was sent', null=True),
        ),
    ]
