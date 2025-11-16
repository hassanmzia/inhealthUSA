# Generated migration for AI Treatment Plan models

from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('healthcare', '0014_add_vital_sign_alert_response'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIProposedTreatmentPlan',
            fields=[
                ('proposal_id', models.AutoField(primary_key=True, serialize=False)),
                ('vital_signs_data', models.JSONField(blank=True, help_text='Vital signs data used for proposal', null=True)),
                ('diagnosis_data', models.JSONField(blank=True, help_text='Diagnosis information used for proposal', null=True)),
                ('lab_test_data', models.JSONField(blank=True, help_text='Lab test results used for proposal', null=True)),
                ('medical_history_data', models.JSONField(blank=True, help_text='Medical history used for proposal', null=True)),
                ('family_history_data', models.JSONField(blank=True, help_text='Family history used for proposal', null=True)),
                ('social_history_data', models.JSONField(blank=True, help_text='Social history used for proposal', null=True)),
                ('proposed_treatment', models.TextField(help_text='AI-generated treatment plan proposal')),
                ('medications_suggested', models.TextField(blank=True, help_text='AI-suggested medications', null=True)),
                ('lifestyle_recommendations', models.TextField(blank=True, help_text='AI-suggested lifestyle changes', null=True)),
                ('follow_up_recommendations', models.TextField(blank=True, help_text='AI-suggested follow-up care', null=True)),
                ('warnings_and_precautions', models.TextField(blank=True, help_text='AI-generated warnings and precautions', null=True)),
                ('ai_model_name', models.CharField(default='llama3.2', help_text='Name of AI model used', max_length=100)),
                ('ai_model_version', models.CharField(blank=True, help_text='Version of AI model', max_length=50, null=True)),
                ('generation_time_seconds', models.FloatField(blank=True, help_text='Time taken to generate proposal', null=True)),
                ('prompt_tokens', models.IntegerField(blank=True, help_text='Number of tokens in prompt', null=True)),
                ('completion_tokens', models.IntegerField(blank=True, help_text='Number of tokens in completion', null=True)),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending Review'),
                        ('reviewed', 'Reviewed'),
                        ('accepted', 'Accepted'),
                        ('modified', 'Modified and Used'),
                        ('rejected', 'Rejected'),
                    ],
                    default='pending',
                    help_text='Doctor review status',
                    max_length=20
                )),
                ('doctor_notes', models.TextField(blank=True, help_text="Doctor's notes on the AI proposal", null=True)),
                ('reviewed_at', models.DateTimeField(blank=True, help_text='When doctor reviewed the proposal', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(
                    help_text='Patient for whom the treatment plan is proposed',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='ai_treatment_proposals',
                    to='healthcare.patient'
                )),
                ('provider', models.ForeignKey(
                    blank=True,
                    help_text='Doctor who requested the AI proposal',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='ai_treatment_proposals',
                    to='healthcare.provider'
                )),
            ],
            options={
                'verbose_name': 'AI Proposed Treatment Plan',
                'verbose_name_plural': 'AI Proposed Treatment Plans',
                'db_table': 'ai_proposed_treatment_plans',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DoctorTreatmentPlan',
            fields=[
                ('plan_id', models.AutoField(primary_key=True, serialize=False)),
                ('plan_title', models.CharField(help_text='Title/summary of treatment plan', max_length=255)),
                ('chief_complaint', models.TextField(blank=True, help_text='Primary complaint being addressed', null=True)),
                ('assessment', models.TextField(help_text="Doctor's clinical assessment")),
                ('treatment_goals', models.TextField(help_text='Goals of the treatment plan')),
                ('medications', models.TextField(blank=True, help_text='Prescribed medications with dosage and instructions', null=True)),
                ('procedures', models.TextField(blank=True, help_text='Recommended procedures or interventions', null=True)),
                ('lifestyle_modifications', models.TextField(blank=True, help_text='Lifestyle changes recommended', null=True)),
                ('dietary_recommendations', models.TextField(blank=True, help_text='Diet and nutrition recommendations', null=True)),
                ('exercise_recommendations', models.TextField(blank=True, help_text='Exercise and physical activity recommendations', null=True)),
                ('follow_up_instructions', models.TextField(help_text='Follow-up care instructions')),
                ('warning_signs', models.TextField(blank=True, help_text='Warning signs to watch for', null=True)),
                ('emergency_instructions', models.TextField(blank=True, help_text='When to seek emergency care', null=True)),
                ('additional_notes', models.TextField(blank=True, help_text='Any additional notes or instructions', null=True)),
                ('status', models.CharField(
                    choices=[
                        ('draft', 'Draft'),
                        ('active', 'Active'),
                        ('completed', 'Completed'),
                        ('cancelled', 'Cancelled'),
                        ('superseded', 'Superseded by Newer Plan'),
                    ],
                    default='draft',
                    help_text='Status of treatment plan',
                    max_length=20
                )),
                ('is_visible_to_patient', models.BooleanField(default=False, help_text='Whether patient can view this plan')),
                ('plan_start_date', models.DateField(default=timezone.now, help_text='Start date of treatment plan')),
                ('plan_end_date', models.DateField(blank=True, help_text='Expected end date of treatment plan', null=True)),
                ('next_review_date', models.DateField(blank=True, help_text='Date for next review of plan', null=True)),
                ('patient_viewed_at', models.DateTimeField(blank=True, help_text='When patient first viewed the plan', null=True)),
                ('patient_acknowledged_at', models.DateTimeField(blank=True, help_text='When patient acknowledged understanding', null=True)),
                ('patient_feedback', models.TextField(blank=True, help_text='Patient feedback or questions', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ai_proposal', models.ForeignKey(
                    blank=True,
                    help_text='AI proposal that influenced this plan (if any)',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='doctor_treatment_plans',
                    to='healthcare.aiproposedtreatmentplan'
                )),
                ('encounter', models.ForeignKey(
                    blank=True,
                    help_text='Related encounter/visit',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='treatment_plans',
                    to='healthcare.encounter'
                )),
                ('patient', models.ForeignKey(
                    help_text='Patient receiving the treatment plan',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='treatment_plans',
                    to='healthcare.patient'
                )),
                ('provider', models.ForeignKey(
                    help_text='Doctor who created the treatment plan',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='treatment_plans_created',
                    to='healthcare.provider'
                )),
            ],
            options={
                'verbose_name': "Doctor's Treatment Plan",
                'verbose_name_plural': "Doctor's Treatment Plans",
                'db_table': 'doctor_treatment_plans',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='aiproposedtreatmentplan',
            index=models.Index(fields=['patient', '-created_at'], name='idx_ai_proposal_patient'),
        ),
        migrations.AddIndex(
            model_name='aiproposedtreatmentplan',
            index=models.Index(fields=['provider', '-created_at'], name='idx_ai_proposal_provider'),
        ),
        migrations.AddIndex(
            model_name='aiproposedtreatmentplan',
            index=models.Index(fields=['status'], name='idx_ai_proposal_status'),
        ),
        migrations.AddIndex(
            model_name='doctortreatmentplan',
            index=models.Index(fields=['patient', '-created_at'], name='idx_treatment_plan_patient'),
        ),
        migrations.AddIndex(
            model_name='doctortreatmentplan',
            index=models.Index(fields=['provider', '-created_at'], name='idx_treatment_plan_provider'),
        ),
        migrations.AddIndex(
            model_name='doctortreatmentplan',
            index=models.Index(fields=['status'], name='idx_treatment_plan_status'),
        ),
        migrations.AddIndex(
            model_name='doctortreatmentplan',
            index=models.Index(fields=['is_visible_to_patient'], name='idx_treatment_plan_visible'),
        ),
    ]
