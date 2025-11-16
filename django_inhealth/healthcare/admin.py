from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Hospital, UserProfile, Patient, Department, Provider, Nurse, OfficeAdministrator, Encounter, VitalSign,
    Diagnosis, Prescription, Allergy, MedicalHistory, SocialHistory, FamilyHistory,
    Message, LabTest, Notification, InsuranceInformation, Billing, BillingItem, Payment, Device,
    NotificationPreferences
)


# Inline for UserProfile in User admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'
    fields = ['role', 'phone', 'date_of_birth']


# Custom User Admin with UserProfile inline
class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email']

    def get_role(self, obj):
        try:
            return obj.profile.get_role_display()
        except UserProfile.DoesNotExist:
            return 'No Profile'
    get_role.short_description = 'Role'


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


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
    list_display = ['patient_id', 'full_name', 'user', 'primary_doctor', 'date_of_birth', 'gender', 'phone', 'is_active']
    list_filter = ['gender', 'is_active', 'primary_doctor']
    search_fields = ['first_name', 'last_name', 'ssn', 'email', 'user__username', 'user__email']
    ordering = ['last_name', 'first_name']
    autocomplete_fields = ['user', 'primary_doctor']
    fieldsets = (
        ('User Account Link', {
            'fields': ('user',),
            'description': 'Link this patient to a User account. The user\'s role should be set to "Patient" in User Profiles.'
        }),
        ('Patient Information', {
            'fields': ('first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender', 'ssn')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address', 'city', 'state', 'zip_code')
        }),
        ('Medical Information', {
            'fields': ('primary_doctor',)
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Insurance Information', {
            'fields': ('insurance_provider', 'insurance_policy_number')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['department_id', 'department_name', 'hospital', 'location', 'phone', 'is_active']
    list_filter = ['is_active', 'hospital']
    search_fields = ['department_name', 'location']
    raw_id_fields = ['hospital']


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['provider_id', 'full_name', 'user', 'hospital', 'specialty', 'npi', 'email', 'is_active']
    list_filter = ['specialty', 'is_active', 'department', 'hospital']
    search_fields = ['first_name', 'last_name', 'npi', 'license_number', 'user__username', 'user__email']
    autocomplete_fields = ['user', 'hospital', 'department']
    fieldsets = (
        ('User Account Link', {
            'fields': ('user',),
            'description': 'Link this provider to a User account. The user\'s role should be set to "Doctor" in User Profiles.'
        }),
        ('Provider Information', {
            'fields': ('first_name', 'last_name', 'npi', 'specialty', 'license_number')
        }),
        ('Organization', {
            'fields': ('hospital', 'department')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Nurse)
class NurseAdmin(admin.ModelAdmin):
    list_display = ['nurse_id', 'full_name', 'user', 'hospital', 'specialty', 'license_number', 'email', 'is_active']
    list_filter = ['specialty', 'is_active', 'department', 'hospital']
    search_fields = ['first_name', 'last_name', 'license_number', 'user__username', 'user__email']
    autocomplete_fields = ['user', 'hospital', 'department']
    fieldsets = (
        ('User Account Link', {
            'fields': ('user',),
            'description': 'Link this nurse to a User account. The user\'s role should be set to "Nurse" in User Profiles.'
        }),
        ('Nurse Information', {
            'fields': ('first_name', 'last_name', 'license_number', 'specialty')
        }),
        ('Organization', {
            'fields': ('hospital', 'department'),
            'description': 'Hospital assignment is required. Each nurse must be assigned to an existing hospital.'
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(OfficeAdministrator)
class OfficeAdministratorAdmin(admin.ModelAdmin):
    list_display = ['admin_id', 'full_name', 'user', 'hospital', 'position', 'employee_id', 'email', 'is_active']
    list_filter = ['position', 'is_active', 'department', 'hospital']
    search_fields = ['first_name', 'last_name', 'employee_id', 'user__username', 'user__email']
    autocomplete_fields = ['user', 'hospital', 'department']
    fieldsets = (
        ('User Account Link', {
            'fields': ('user',),
            'description': 'Link this office administrator to a User account. The user\'s role should be set to "Office Administrator" in User Profiles.'
        }),
        ('Administrator Information', {
            'fields': ('first_name', 'last_name', 'employee_id', 'position')
        }),
        ('Organization', {
            'fields': ('hospital', 'department'),
            'description': 'Hospital assignment is required. Each office administrator must be assigned to an existing hospital.'
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


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


@admin.register(InsuranceInformation)
class InsuranceInformationAdmin(admin.ModelAdmin):
    list_display = ['insurance_id', 'patient', 'provider_name', 'policy_number', 'is_primary', 'effective_date', 'termination_date']
    list_filter = ['is_primary', 'effective_date', 'termination_date']
    search_fields = ['provider_name', 'policy_number', 'patient__first_name', 'patient__last_name']
    date_hierarchy = 'effective_date'
    raw_id_fields = ['patient']


class BillingItemInline(admin.TabularInline):
    model = BillingItem
    extra = 1
    fields = ['service_code', 'service_description', 'quantity', 'unit_price', 'total_price']


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ['billing_id', 'invoice_number', 'patient', 'billing_date', 'total_amount', 'amount_paid', 'amount_due', 'status']
    list_filter = ['status', 'billing_date', 'due_date']
    search_fields = ['invoice_number', 'patient__first_name', 'patient__last_name']
    date_hierarchy = 'billing_date'
    raw_id_fields = ['patient', 'encounter']
    inlines = [BillingItemInline]


@admin.register(BillingItem)
class BillingItemAdmin(admin.ModelAdmin):
    list_display = ['item_id', 'billing', 'service_code', 'service_description', 'quantity', 'unit_price', 'total_price']
    search_fields = ['service_code', 'service_description']
    raw_id_fields = ['billing']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'patient', 'payment_date', 'amount', 'payment_method', 'status', 'transaction_id']
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'transaction_id']
    date_hierarchy = 'payment_date'
    raw_id_fields = ['patient', 'billing']


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['device_id', 'patient', 'device_name', 'device_type', 'device_unique_id', 'status', 'battery_level', 'last_sync']
    list_filter = ['device_type', 'status', 'registration_date']
    search_fields = ['device_name', 'device_unique_id', 'patient__first_name', 'patient__last_name', 'manufacturer']
    date_hierarchy = 'registration_date'
    raw_id_fields = ['patient']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NotificationPreferences)
class NotificationPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_enabled', 'sms_enabled', 'whatsapp_enabled', 'enable_quiet_hours', 'digest_mode']
    list_filter = ['email_enabled', 'sms_enabled', 'whatsapp_enabled', 'enable_quiet_hours', 'digest_mode']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email', 'whatsapp_number']
    raw_id_fields = ['user']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Notifications', {
            'fields': ('email_enabled', 'email_emergency', 'email_critical', 'email_warning'),
            'description': 'Configure email alerts for different severity levels'
        }),
        ('SMS Notifications', {
            'fields': ('sms_enabled', 'sms_emergency', 'sms_critical', 'sms_warning'),
            'description': 'SMS notifications require Twilio configuration in settings'
        }),
        ('WhatsApp Notifications', {
            'fields': ('whatsapp_enabled', 'whatsapp_number', 'whatsapp_emergency', 'whatsapp_critical', 'whatsapp_warning'),
            'description': 'WhatsApp notifications via Twilio WhatsApp API. Provide WhatsApp number with country code (e.g., +1234567890). If not provided, phone number will be used.'
        }),
        ('Quiet Hours', {
            'fields': ('enable_quiet_hours', 'quiet_start_time', 'quiet_end_time'),
            'description': 'Emergency alerts will still be sent during quiet hours'
        }),
        ('Advanced Settings', {
            'fields': ('digest_mode', 'digest_frequency_hours'),
            'description': 'Digest mode sends a summary of alerts instead of individual messages'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
