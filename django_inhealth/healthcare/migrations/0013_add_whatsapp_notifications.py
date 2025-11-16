# Generated migration for WhatsApp notification fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthcare', '0012_add_notification_preferences'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationpreferences',
            name='whatsapp_enabled',
            field=models.BooleanField(default=False, help_text='Receive WhatsApp notifications'),
        ),
        migrations.AddField(
            model_name='notificationpreferences',
            name='whatsapp_emergency',
            field=models.BooleanField(default=True, help_text='Receive emergency alerts via WhatsApp'),
        ),
        migrations.AddField(
            model_name='notificationpreferences',
            name='whatsapp_critical',
            field=models.BooleanField(default=True, help_text='Receive critical alerts via WhatsApp'),
        ),
        migrations.AddField(
            model_name='notificationpreferences',
            name='whatsapp_warning',
            field=models.BooleanField(default=True, help_text='Receive warning alerts via WhatsApp'),
        ),
        migrations.AddField(
            model_name='notificationpreferences',
            name='whatsapp_number',
            field=models.CharField(blank=True, help_text='WhatsApp number with country code (e.g., +1234567890)', max_length=20, null=True),
        ),
    ]
