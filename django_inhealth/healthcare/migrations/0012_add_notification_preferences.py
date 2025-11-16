# Generated migration for NotificationPreferences model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('healthcare', '0011_add_profile_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationPreferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_enabled', models.BooleanField(default=True, help_text='Receive email notifications')),
                ('email_emergency', models.BooleanField(default=True, help_text='Receive emergency alerts via email')),
                ('email_critical', models.BooleanField(default=True, help_text='Receive critical alerts via email')),
                ('email_warning', models.BooleanField(default=True, help_text='Receive warning alerts via email')),
                ('sms_enabled', models.BooleanField(default=False, help_text='Receive SMS notifications')),
                ('sms_emergency', models.BooleanField(default=True, help_text='Receive emergency alerts via SMS')),
                ('sms_critical', models.BooleanField(default=True, help_text='Receive critical alerts via SMS')),
                ('sms_warning', models.BooleanField(default=False, help_text='Receive warning alerts via SMS')),
                ('enable_quiet_hours', models.BooleanField(default=False, help_text='Enable quiet hours (no non-emergency alerts)')),
                ('quiet_start_time', models.TimeField(blank=True, help_text='Quiet hours start time', null=True)),
                ('quiet_end_time', models.TimeField(blank=True, help_text='Quiet hours end time', null=True)),
                ('digest_mode', models.BooleanField(default=False, help_text='Send digest emails instead of individual alerts')),
                ('digest_frequency_hours', models.IntegerField(default=6, help_text='How often to send digest emails (in hours)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notification_preferences', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notification Preference',
                'verbose_name_plural': 'Notification Preferences',
                'db_table': 'notification_preferences',
            },
        ),
    ]
