from django.contrib import admin
from .models import (
    Hospital, UserProfile, Patient, Department, Provider, Encounter, VitalSign,
    Diagnosis, Prescription, Allergy, MedicalHistory, SocialHistory, FamilyHistory,
    Message, LabTest, Notification
)


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['hospital_id', 'name', 'city', 'state', 'phone', 'is_active']
    list_filter = ['is_active', 'state']
    search_fields = ['name', 'city', 'state']
    ordering = ['name']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'date_of_birth']
    list_filter = ['role']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']
    ordering = ['user__last_name']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'full_name', 'primary_doctor', 'date_of_birth', 'gender', 'phone', 'is_active']
    list_filter = ['gender', 'is_active', 'primary_doctor']
    search_fields = ['first_name', 'last_name', 'ssn', 'email']
    ordering = ['last_name', 'first_name']
    raw_id_fields = ['user', 'primary_doctor']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['department_id', 'department_name', 'hospital', 'location', 'phone', 'is_active']
    list_filter = ['is_active', 'hospital']
    search_fields = ['department_name', 'location']
    raw_id_fields = ['hospital']


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['provider_id', 'full_name', 'hospital', 'specialty', 'npi', 'email', 'is_active']
    list_filter = ['specialty', 'is_active', 'department', 'hospital']
    search_fields = ['first_name', 'last_name', 'npi', 'license_number']
    raw_id_fields = ['user', 'hospital', 'department']


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    list_display = ['encounter_id', 'patient', 'provider', 'encounter_date', 'encounter_type', 'status']
    list_filter = ['encounter_type', 'status', 'encounter_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'provider__first_name', 'provider__last_name']
    date_hierarchy = 'encounter_date'
    raw_id_fields = ['patient', 'provider', 'department']


@admin.register(VitalSign)
class VitalSignAdmin(admin.ModelAdmin):
    list_display = ['vital_signs_id', 'encounter', 'recorded_by', 'recorded_at', 'blood_pressure', 'heart_rate', 'temperature_value']
    list_filter = ['recorded_at']
    date_hierarchy = 'recorded_at'
    raw_id_fields = ['encounter', 'recorded_by']


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ['diagnosis_id', 'encounter', 'diagnosis_description', 'diagnosis_type', 'status', 'diagnosed_by', 'diagnosed_at']
    list_filter = ['diagnosis_type', 'status', 'diagnosed_at']
    search_fields = ['diagnosis_description', 'icd10_code', 'icd11_code']
    raw_id_fields = ['encounter', 'diagnosed_by']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['prescription_id', 'patient', 'medication_name', 'dosage', 'provider', 'start_date', 'status']
    list_filter = ['status', 'start_date']
    search_fields = ['medication_name', 'patient__first_name', 'patient__last_name']
    date_hierarchy = 'start_date'
    raw_id_fields = ['patient', 'provider', 'encounter']


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ['allergy_id', 'patient', 'allergen', 'allergy_type', 'severity', 'is_active']
    list_filter = ['allergy_type', 'severity', 'is_active']
    search_fields = ['allergen', 'patient__first_name', 'patient__last_name']
    raw_id_fields = ['patient']


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ['medical_history_id', 'patient', 'condition', 'diagnosis_date', 'status']
    list_filter = ['status', 'diagnosis_date']
    search_fields = ['condition', 'patient__first_name', 'patient__last_name']
    raw_id_fields = ['patient']


@admin.register(SocialHistory)
class SocialHistoryAdmin(admin.ModelAdmin):
    list_display = ['social_history_id', 'patient', 'smoking_status', 'alcohol_use', 'marital_status', 'recorded_date']
    list_filter = ['smoking_status', 'marital_status', 'recorded_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'occupation']
    raw_id_fields = ['patient']


@admin.register(FamilyHistory)
class FamilyHistoryAdmin(admin.ModelAdmin):
    list_display = ['family_history_id', 'patient', 'relationship', 'condition', 'is_alive', 'recorded_date']
    list_filter = ['relationship', 'is_alive', 'recorded_date']
    search_fields = ['condition', 'patient__first_name', 'patient__last_name']
    raw_id_fields = ['patient']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['message_id', 'sender', 'recipient', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'recipient__username', 'subject', 'body']
    date_hierarchy = 'created_at'
    raw_id_fields = ['sender', 'recipient', 'parent_message']


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ['lab_test_id', 'patient', 'provider', 'test_name', 'ordered_date', 'status', 'abnormal_flag']
    list_filter = ['status', 'abnormal_flag', 'ordered_date']
    search_fields = ['test_name', 'test_code', 'patient__first_name', 'patient__last_name']
    date_hierarchy = 'ordered_date'
    raw_id_fields = ['patient', 'provider', 'encounter']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['notification_id', 'user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    date_hierarchy = 'created_at'
    raw_id_fields = ['user']
