# Generated migration for VitalSignAlertResponse model

from django.db import migrations, models
import django.db.models.deletion
import uuid


def generate_default_token():
    """Generate a unique token for existing records"""
    return str(uuid.uuid4())


class Migration(migrations.Migration):

    dependencies = [
        ('healthcare', '0013_add_whatsapp_notifications'),
    ]

    operations = [
        migrations.CreateModel(
            name='VitalSignAlertResponse',
            fields=[
                ('alert_id', models.AutoField(primary_key=True, serialize=False)),
                ('alert_type', models.CharField(max_length=20, help_text='emergency, critical, or warning')),
                ('critical_vitals_json', models.JSONField(help_text='JSON data of critical vital signs')),
                ('patient_response_status', models.CharField(
                    max_length=20,
                    choices=[
                        ('pending', 'Waiting for Patient Response'),
                        ('approved_doctor', 'Patient Approved - Notify Doctor'),
                        ('approved_nurse', 'Patient Approved - Notify Nurse'),
                        ('approved_ems', 'Patient Approved - Notify EMS'),
                        ('approved_all', 'Patient Approved - Notify All'),
                        ('declined', 'Patient Declined Notification'),
                        ('timeout', 'No Response - Auto-escalated'),
                        ('completed', 'Notifications Sent'),
                    ],
                    default='pending',
                    help_text='Current status of the alert response'
                )),
                ('patient_wants_doctor', models.BooleanField(default=False, help_text='Patient wants to notify doctor')),
                ('patient_wants_nurse', models.BooleanField(default=False, help_text='Patient wants to notify nurse')),
                ('patient_wants_ems', models.BooleanField(default=False, help_text='Patient wants to notify EMS')),
                ('patient_response_time', models.DateTimeField(blank=True, null=True, help_text='When patient responded')),
                ('patient_response_method', models.CharField(
                    max_length=20,
                    blank=True,
                    null=True,
                    help_text='How patient responded (email, sms, whatsapp, web)'
                )),
                ('timeout_minutes', models.IntegerField(default=15, help_text='Minutes before auto-escalation')),
                ('auto_escalated', models.BooleanField(default=False, help_text='Whether alert was auto-escalated')),
                ('auto_escalation_time', models.DateTimeField(blank=True, null=True, help_text='When auto-escalation occurred')),
                ('doctor_notified', models.BooleanField(default=False, help_text='Doctor notification sent')),
                ('nurse_notified', models.BooleanField(default=False, help_text='Nurse notification sent')),
                ('ems_notified', models.BooleanField(default=False, help_text='EMS notification sent')),
                ('notifications_sent_at', models.DateTimeField(blank=True, null=True, help_text='When provider notifications were sent')),
                ('response_token', models.CharField(
                    max_length=100,
                    unique=True,
                    help_text='Unique token for response links'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('vital_sign', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='alert_responses',
                    to='healthcare.vitalsign',
                    help_text='The vital sign that triggered this alert'
                )),
                ('patient', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='vital_alert_responses',
                    to='healthcare.patient',
                    help_text='The patient who received the alert'
                )),
            ],
            options={
                'verbose_name': 'Vital Sign Alert Response',
                'verbose_name_plural': 'Vital Sign Alert Responses',
                'db_table': 'vital_sign_alert_responses',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['patient_response_status', 'created_at'], name='idx_response_status_created'),
                    models.Index(fields=['patient', '-created_at'], name='idx_patient_created'),
                    models.Index(fields=['response_token'], name='idx_response_token'),
                ],
            },
        ),
    ]
