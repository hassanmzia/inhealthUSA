from django.contrib import admin
from .models import (
    Patient, Department, Provider, Encounter, VitalSign,
    Diagnosis, Prescription, Allergy, MedicalHistory, SocialHistory
)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'full_name', 'date_of_birth', 'gender', 'phone', 'is_active']
    list_filter = ['gender', 'is_active']
    search_fields = ['first_name', 'last_name', 'ssn', 'email']
    ordering = ['last_name', 'first_name']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['department_id', 'department_name', 'location', 'phone', 'is_active']
    list_filter = ['is_active']
    search_fields = ['department_name', 'location']


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['provider_id', 'full_name', 'specialty', 'npi', 'email', 'is_active']
    list_filter = ['specialty', 'is_active', 'department']
    search_fields = ['first_name', 'last_name', 'npi', 'license_number']


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    list_display = ['encounter_id', 'patient', 'provider', 'encounter_date', 'encounter_type', 'status']
    list_filter = ['encounter_type', 'status', 'encounter_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'provider__first_name', 'provider__last_name']
    date_hierarchy = 'encounter_date'


@admin.register(VitalSign)
class VitalSignAdmin(admin.ModelAdmin):
    list_display = ['vital_signs_id', 'encounter', 'recorded_at', 'blood_pressure', 'heart_rate', 'temperature_value']
    list_filter = ['recorded_at']
    date_hierarchy = 'recorded_at'


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ['diagnosis_id', 'encounter', 'diagnosis_description', 'diagnosis_type', 'status', 'diagnosed_at']
    list_filter = ['diagnosis_type', 'status', 'diagnosed_at']
    search_fields = ['diagnosis_description', 'icd10_code', 'icd11_code']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['prescription_id', 'patient', 'medication_name', 'dosage', 'start_date', 'status']
    list_filter = ['status', 'start_date']
    search_fields = ['medication_name', 'patient__first_name', 'patient__last_name']
    date_hierarchy = 'start_date'


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ['allergy_id', 'patient', 'allergen', 'allergy_type', 'severity', 'is_active']
    list_filter = ['allergy_type', 'severity', 'is_active']
    search_fields = ['allergen', 'patient__first_name', 'patient__last_name']


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ['medical_history_id', 'patient', 'condition', 'diagnosis_date', 'status']
    list_filter = ['status', 'diagnosis_date']
    search_fields = ['condition', 'patient__first_name', 'patient__last_name']


@admin.register(SocialHistory)
class SocialHistoryAdmin(admin.ModelAdmin):
    list_display = ['social_history_id', 'patient', 'smoking_status', 'alcohol_use', 'marital_status', 'recorded_date']
    list_filter = ['smoking_status', 'marital_status', 'recorded_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'occupation']
