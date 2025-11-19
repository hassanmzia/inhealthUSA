from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
import uuid


class Hospital(models.Model):
    """Hospital model for healthcare organizations"""
    hospital_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'hospitals'
        verbose_name = 'Hospital'
        verbose_name_plural = 'Hospitals'
        ordering = ['name']

    def __str__(self):
        return self.name


class Department(models.Model):
    """Department model for hospital departments"""
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=255)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='departments')
    location = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    head_of_department = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['department_name']

    def __str__(self):
        return f"{self.department_name} - {self.hospital.name}"


class UserProfile(models.Model):
    """Extended user profile with healthcare-specific fields"""
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('office_admin', 'Office Administrator'),
        ('admin', 'System Administrator'),
    ]

    profile_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    # Security fields
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    password_reset_token = models.CharField(max_length=255, blank=True, null=True)
    password_reset_token_expires = models.DateTimeField(null=True, blank=True)
    last_password_change = models.DateTimeField(null=True, blank=True)

    # Email verification
    email_verification_token = models.CharField(max_length=255, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    # Enterprise authentication fields
    auth_provider = models.CharField(max_length=50, blank=True, null=True, help_text='cac, okta, cognito, azure_ad, etc.')
    external_id = models.CharField(max_length=255, blank=True, null=True, help_text='External authentication provider ID')

    # MFA fields
    mfa_enabled = models.BooleanField(default=False, help_text='Multi-Factor Authentication enabled')
    mfa_secret = models.CharField(max_length=32, blank=True, null=True, help_text='TOTP secret key')
    mfa_backup_codes = models.TextField(blank=True, null=True, help_text='Comma-separated backup codes')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    def is_account_locked(self):
        """Check if account is currently locked"""
        if self.account_locked_until:
            if timezone.now() < self.account_locked_until:
                return True
            else:
                # Lock has expired, clear it
                self.account_locked_until = None
                self.failed_login_attempts = 0
                self.save()
        return False

    def lock_account(self, duration_minutes=30):
        """Lock the account for specified duration"""
        self.account_locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save()


class Patient(models.Model):
    """Patient model for healthcare patients"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('U', 'Prefer not to say'),
    ]

    patient_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='patient_profile')
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    ssn = models.CharField(max_length=20, blank=True, unique=True, null=True)
    mrn = models.CharField(max_length=50, unique=True, help_text='Medical Record Number')
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    emergency_contact_name = models.CharField(max_length=255, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    primary_doctor = models.ForeignKey('Provider', on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_patients')
    insurance_provider = models.CharField(max_length=255, blank=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'patients'
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['mrn'], name='idx_patient_mrn'),
            models.Index(fields=['last_name', 'first_name'], name='idx_patient_name'),
        ]

    def __str__(self):
        return f"{self.last_name}, {self.first_name} (MRN: {self.mrn})"

    def get_full_name(self):
        """Return patient's full name"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def full_name(self):
        """Property for admin display"""
        return self.get_full_name()


class Provider(models.Model):
    """Provider model for healthcare providers (doctors)"""
    SPECIALTY_CHOICES = [
        ('Cardiology', 'Cardiology'),
        ('Dermatology', 'Dermatology'),
        ('Emergency Medicine', 'Emergency Medicine'),
        ('Family Medicine', 'Family Medicine'),
        ('Internal Medicine', 'Internal Medicine'),
        ('Neurology', 'Neurology'),
        ('Obstetrics and Gynecology', 'Obstetrics and Gynecology'),
        ('Orthopedic Surgery', 'Orthopedic Surgery'),
        ('Pediatrics', 'Pediatrics'),
        ('Psychiatry', 'Psychiatry'),
        ('Radiology', 'Radiology'),
        ('Surgery', 'Surgery'),
        ('Other', 'Other'),
    ]

    provider_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='provider_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100, choices=SPECIALTY_CHOICES)
    npi = models.CharField(max_length=20, unique=True, help_text='National Provider Identifier')
    license_number = models.CharField(max_length=100)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, related_name='providers')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='providers')
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'providers'
        verbose_name = 'Provider'
        verbose_name_plural = 'Providers'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['npi'], name='idx_provider_npi'),
        ]

    def __str__(self):
        return f"Dr. {self.last_name}, {self.first_name}"

    def get_full_name(self):
        """Return provider's full name with title"""
        return f"Dr. {self.first_name} {self.last_name}"

    def full_name(self):
        """Property for admin display"""
        return self.get_full_name()


class Nurse(models.Model):
    """Nurse model for healthcare nurses"""
    SPECIALTY_CHOICES = [
        ('Critical Care', 'Critical Care'),
        ('Emergency', 'Emergency'),
        ('Medical-Surgical', 'Medical-Surgical'),
        ('Pediatric', 'Pediatric'),
        ('Psychiatric', 'Psychiatric'),
        ('Geriatric', 'Geriatric'),
        ('Oncology', 'Oncology'),
        ('General', 'General'),
        ('Other', 'Other'),
    ]

    nurse_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='nurse_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100, choices=SPECIALTY_CHOICES)
    license_number = models.CharField(max_length=100, unique=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='nurses')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='nurses')
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'nurses'
        verbose_name = 'Nurse'
        verbose_name_plural = 'Nurses'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    def get_full_name(self):
        """Return nurse's full name"""
        return f"{self.first_name} {self.last_name}"

    def full_name(self):
        """Property for admin display"""
        return self.get_full_name()


class OfficeAdministrator(models.Model):
    """Office Administrator model for healthcare administrative staff"""
    admin_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='office_admin_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, default='Office Administrator')
    employee_id = models.CharField(max_length=50, unique=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='office_administrators')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='office_administrators')
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'office_administrators'
        verbose_name = 'Office Administrator'
        verbose_name_plural = 'Office Administrators'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    def get_full_name(self):
        """Return admin's full name"""
        return f"{self.first_name} {self.last_name}"

    def full_name(self):
        """Property for admin display"""
        return self.get_full_name()


class Encounter(models.Model):
    """Encounter model for patient visits"""
    ENCOUNTER_TYPE_CHOICES = [
        ('Emergency', 'Emergency'),
        ('Inpatient', 'Inpatient'),
        ('Outpatient', 'Outpatient'),
        ('Urgent Care', 'Urgent Care'),
        ('Virtual', 'Virtual'),
    ]

    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    encounter_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='encounters')
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, related_name='encounters')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='encounters')
    encounter_date = models.DateTimeField()
    encounter_type = models.CharField(max_length=50, choices=ENCOUNTER_TYPE_CHOICES)
    chief_complaint = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'encounters'
        verbose_name = 'Encounter'
        verbose_name_plural = 'Encounters'
        ordering = ['-encounter_date']
        indexes = [
            models.Index(fields=['-encounter_date'], name='idx_encounter_date'),
        ]

    def __str__(self):
        return f"Encounter {self.encounter_id} - {self.patient.get_full_name()} - {self.encounter_date.strftime('%Y-%m-%d')}"


class VitalSign(models.Model):
    """Vital signs model for patient vital measurements"""
    TEMPERATURE_UNITS = [
        ('F', 'Fahrenheit'),
        ('C', 'Celsius'),
    ]

    WEIGHT_UNITS = [
        ('lbs', 'Pounds'),
        ('kg', 'Kilograms'),
    ]

    vital_signs_id = models.AutoField(primary_key=True)
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name='vital_signs')
    recorded_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recorded_vitals')

    # Vital measurements
    blood_pressure_systolic = models.IntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True)
    heart_rate = models.IntegerField(null=True, blank=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature_unit = models.CharField(max_length=1, choices=TEMPERATURE_UNITS, default='F')
    respiratory_rate = models.IntegerField(null=True, blank=True)
    oxygen_saturation = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    weight_unit = models.CharField(max_length=3, choices=WEIGHT_UNITS, default='lbs')
    height_inches = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    bmi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    glucose = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text='Blood glucose level in mg/dL')

    # Additional fields
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'vital_signs'
        verbose_name = 'Vital Sign'
        verbose_name_plural = 'Vital Signs'
        ordering = ['-recorded_at']

    def __str__(self):
        return f"Vitals for {self.encounter.patient.get_full_name()} - {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"

    def blood_pressure(self):
        """Return formatted blood pressure"""
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"
        return "N/A"

    def temperature_value(self):
        """Return formatted temperature"""
        if self.temperature:
            return f"{self.temperature}°{self.temperature_unit}"
        return "N/A"


class Diagnosis(models.Model):
    """Diagnosis model for patient diagnoses"""
    DIAGNOSIS_TYPES = [
        ('Primary', 'Primary'),
        ('Secondary', 'Secondary'),
        ('Admitting', 'Admitting'),
        ('Discharge', 'Discharge'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Resolved', 'Resolved'),
        ('Chronic', 'Chronic'),
    ]

    diagnosis_id = models.AutoField(primary_key=True)
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name='diagnoses')
    diagnosis_description = models.TextField()
    icd10_code = models.CharField(max_length=20, blank=True)
    icd11_code = models.CharField(max_length=20, blank=True)
    diagnosis_type = models.CharField(max_length=20, choices=DIAGNOSIS_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    diagnosed_by = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, related_name='diagnoses')
    diagnosed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'diagnoses'
        verbose_name = 'Diagnosis'
        verbose_name_plural = 'Diagnoses'
        ordering = ['-diagnosed_at']

    def __str__(self):
        return f"{self.diagnosis_description} - {self.encounter.patient.get_full_name()}"


class Prescription(models.Model):
    """Prescription model for patient medications"""
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Discontinued', 'Discontinued'),
        ('Completed', 'Completed'),
    ]

    prescription_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, related_name='prescriptions')
    encounter = models.ForeignKey(Encounter, on_delete=models.SET_NULL, null=True, blank=True, related_name='prescriptions')
    medication_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    route = models.CharField(max_length=50, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    refills = models.IntegerField(default=0)
    quantity = models.IntegerField(null=True, blank=True)
    instructions = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'prescriptions'
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.medication_name} - {self.patient.get_full_name()}"


class Allergy(models.Model):
    """Allergy model for patient allergies"""
    ALLERGY_TYPES = [
        ('Medication', 'Medication'),
        ('Food', 'Food'),
        ('Environmental', 'Environmental'),
        ('Other', 'Other'),
    ]

    SEVERITY_CHOICES = [
        ('Mild', 'Mild'),
        ('Moderate', 'Moderate'),
        ('Severe', 'Severe'),
        ('Life-threatening', 'Life-threatening'),
    ]

    allergy_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='allergies')
    allergen = models.CharField(max_length=255)
    allergy_type = models.CharField(max_length=50, choices=ALLERGY_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    reaction = models.TextField(blank=True)
    onset_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'allergies'
        verbose_name = 'Allergy'
        verbose_name_plural = 'Allergies'
        ordering = ['-severity', 'allergen']

    def __str__(self):
        return f"{self.allergen} - {self.patient.get_full_name()}"


class MedicalHistory(models.Model):
    """Medical history model for patient past medical conditions"""
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Resolved', 'Resolved'),
        ('Chronic', 'Chronic'),
    ]

    medical_history_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_history')
    condition = models.CharField(max_length=255)
    diagnosis_date = models.DateField(null=True, blank=True)
    resolution_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    treatment_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'medical_history'
        verbose_name = 'Medical History'
        verbose_name_plural = 'Medical Histories'
        ordering = ['-diagnosis_date']

    def __str__(self):
        return f"{self.condition} - {self.patient.get_full_name()}"


class SocialHistory(models.Model):
    """Social history model for patient social history"""
    SMOKING_STATUS_CHOICES = [
        ('Never', 'Never'),
        ('Former', 'Former'),
        ('Current', 'Current'),
    ]

    ALCOHOL_USE_CHOICES = [
        ('Never', 'Never'),
        ('Occasional', 'Occasional'),
        ('Regular', 'Regular'),
        ('Heavy', 'Heavy'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Divorced', 'Divorced'),
        ('Widowed', 'Widowed'),
        ('Separated', 'Separated'),
    ]

    social_history_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='social_history')
    smoking_status = models.CharField(max_length=20, choices=SMOKING_STATUS_CHOICES, default='Never')
    alcohol_use = models.CharField(max_length=20, choices=ALCOHOL_USE_CHOICES, default='Never')
    drug_use = models.TextField(blank=True)
    occupation = models.CharField(max_length=255, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True)
    living_situation = models.TextField(blank=True)
    exercise = models.TextField(blank=True)
    diet = models.TextField(blank=True)
    recorded_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'social_history'
        verbose_name = 'Social History'
        verbose_name_plural = 'Social Histories'
        ordering = ['-recorded_date']

    def __str__(self):
        return f"Social History - {self.patient.get_full_name()}"


class FamilyHistory(models.Model):
    """Family history model for patient family medical history"""
    RELATIONSHIP_CHOICES = [
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Brother', 'Brother'),
        ('Sister', 'Sister'),
        ('Grandfather', 'Grandfather'),
        ('Grandmother', 'Grandmother'),
        ('Uncle', 'Uncle'),
        ('Aunt', 'Aunt'),
        ('Cousin', 'Cousin'),
        ('Child', 'Child'),
        ('Other', 'Other'),
    ]

    family_history_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='family_history')
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES)
    condition = models.CharField(max_length=255)
    age_at_diagnosis = models.IntegerField(null=True, blank=True)
    is_alive = models.BooleanField(default=True)
    age_at_death = models.IntegerField(null=True, blank=True)
    cause_of_death = models.CharField(max_length=255, blank=True)
    recorded_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'family_history'
        verbose_name = 'Family History'
        verbose_name_plural = 'Family Histories'
        ordering = ['-recorded_date']

    def __str__(self):
        return f"{self.relationship} - {self.condition} - {self.patient.get_full_name()}"


class Message(models.Model):
    """Message model for internal messaging between users"""
    message_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(default=timezone.now)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"From {self.sender.username} to {self.recipient.username} - {self.subject}"


class LabTest(models.Model):
    """Lab test model for patient laboratory tests"""
    STATUS_CHOICES = [
        ('Ordered', 'Ordered'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    lab_test_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_tests')
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, related_name='lab_tests')
    encounter = models.ForeignKey(Encounter, on_delete=models.SET_NULL, null=True, blank=True, related_name='lab_tests')
    test_name = models.CharField(max_length=255)
    test_code = models.CharField(max_length=50, blank=True)
    ordered_date = models.DateTimeField(auto_now_add=True)
    sample_collected_date = models.DateTimeField(null=True, blank=True)
    result_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ordered')
    result_value = models.TextField(blank=True)
    result_unit = models.CharField(max_length=50, blank=True)
    reference_range = models.CharField(max_length=100, blank=True)
    abnormal_flag = models.BooleanField(default=False)
    interpretation = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'lab_tests'
        verbose_name = 'Lab Test'
        verbose_name_plural = 'Lab Tests'
        ordering = ['-ordered_date']

    def __str__(self):
        return f"{self.test_name} - {self.patient.get_full_name()}"


class Notification(models.Model):
    """Notification model for user notifications"""
    NOTIFICATION_TYPES = [
        ('appointment', 'Appointment'),
        ('lab_result', 'Lab Result'),
        ('prescription', 'Prescription'),
        ('message', 'Message'),
        ('alert', 'Alert'),
        ('system', 'System'),
    ]

    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class InsuranceInformation(models.Model):
    """Insurance information model for patient insurance details"""
    insurance_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='insurance_information')
    provider_name = models.CharField(max_length=255)
    policy_number = models.CharField(max_length=100)
    group_number = models.CharField(max_length=100, blank=True)
    policyholder_name = models.CharField(max_length=255)
    policyholder_relationship = models.CharField(max_length=50)
    effective_date = models.DateField()
    termination_date = models.DateField(null=True, blank=True)
    is_primary = models.BooleanField(default=True)
    copay_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deductible_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'insurance_information'
        verbose_name = 'Insurance Information'
        verbose_name_plural = 'Insurance Information'
        ordering = ['-is_primary', '-effective_date']

    def __str__(self):
        return f"{self.provider_name} - {self.patient.get_full_name()}"


class Billing(models.Model):
    """Billing model for patient billing information"""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Partially Paid', 'Partially Paid'),
        ('Overdue', 'Overdue'),
        ('Cancelled', 'Cancelled'),
    ]

    billing_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='billings')
    encounter = models.ForeignKey(Encounter, on_delete=models.SET_NULL, null=True, blank=True, related_name='billings')
    invoice_number = models.CharField(max_length=100, unique=True)
    billing_date = models.DateField()
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'billings'
        verbose_name = 'Billing'
        verbose_name_plural = 'Billings'
        ordering = ['-billing_date']

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.patient.get_full_name()}"


class BillingItem(models.Model):
    """Billing item model for line items in billing"""
    item_id = models.AutoField(primary_key=True)
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, related_name='items')
    service_code = models.CharField(max_length=50)
    service_description = models.TextField()
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'billing_items'
        verbose_name = 'Billing Item'
        verbose_name_plural = 'Billing Items'

    def __str__(self):
        return f"{self.service_description} - {self.billing.invoice_number}"

    def save(self, *args, **kwargs):
        """Calculate total price before saving"""
        self.total_price = Decimal(str(self.quantity)) * self.unit_price
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment model for patient payments"""
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('Check', 'Check'),
        ('Insurance', 'Insurance'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Completed', 'Completed'),
        ('Pending', 'Pending'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]

    payment_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='payments')
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Completed')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment {self.payment_id} - {self.patient.get_full_name()} - ${self.amount}"


class Device(models.Model):
    """IoT Medical Device model for patient vital monitoring"""
    DEVICE_TYPES = [
        ('Watch', 'Watch'),
        ('Ring', 'Ring'),
        ('EarClip', 'EarClip'),
        ('Adapter', 'Adapter'),
        ('PulseGlucometer', 'PulseGlucometer'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Maintenance', 'Maintenance'),
        ('Retired', 'Retired'),
    ]

    device_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='devices')
    device_unique_id = models.CharField(max_length=255, unique=True)
    device_name = models.CharField(max_length=255)
    device_type = models.CharField(max_length=50, choices=DEVICE_TYPES)
    manufacturer = models.CharField(max_length=255, blank=True)
    model_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    firmware_version = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    registration_date = models.DateTimeField(auto_now_add=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    battery_level = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'devices'
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'
        ordering = ['-registration_date']
        indexes = [
            models.Index(fields=['device_unique_id'], name='idx_device_unique_id'),
        ]

    def __str__(self):
        return f"{self.device_name} - {self.patient.get_full_name()}"


class NotificationPreferences(models.Model):
    """Notification preferences for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')

    # Email notifications
    email_enabled = models.BooleanField(default=True, help_text='Enable email notifications')
    email_emergency = models.BooleanField(default=True, help_text='Emergency alerts via email')
    email_critical = models.BooleanField(default=True, help_text='Critical alerts via email')
    email_warning = models.BooleanField(default=True, help_text='Warning alerts via email')

    # SMS notifications
    sms_enabled = models.BooleanField(default=False, help_text='Enable SMS notifications')
    sms_emergency = models.BooleanField(default=True, help_text='Emergency alerts via SMS')
    sms_critical = models.BooleanField(default=True, help_text='Critical alerts via SMS')
    sms_warning = models.BooleanField(default=False, help_text='Warning alerts via SMS')

    # WhatsApp notifications
    whatsapp_enabled = models.BooleanField(default=False, help_text='Enable WhatsApp notifications')
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text='WhatsApp number with country code (e.g., +1234567890)')
    whatsapp_emergency = models.BooleanField(default=True, help_text='Emergency alerts via WhatsApp')
    whatsapp_critical = models.BooleanField(default=True, help_text='Critical alerts via WhatsApp')
    whatsapp_warning = models.BooleanField(default=False, help_text='Warning alerts via WhatsApp')

    # Quiet hours
    enable_quiet_hours = models.BooleanField(default=False, help_text='Enable quiet hours (emergency alerts still sent)')
    quiet_start_time = models.TimeField(null=True, blank=True, help_text='Start of quiet hours (e.g., 22:00)')
    quiet_end_time = models.TimeField(null=True, blank=True, help_text='End of quiet hours (e.g., 08:00)')

    # Digest mode
    digest_mode = models.BooleanField(default=False, help_text='Send summary of alerts instead of individual messages')
    digest_frequency_hours = models.IntegerField(default=24, help_text='How often to send digest (in hours)')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'

    def __str__(self):
        return f"Notification Preferences for {self.user.username}"


class VitalSignAlertResponse(models.Model):
    """
    Model to track patient responses to vital sign alerts and automated escalation
    """
    PATIENT_RESPONSE_CHOICES = [
        ('none', 'No Response'),
        ('ok', 'Patient Confirmed OK'),
        ('help_needed', 'Patient Needs Help'),
    ]

    ALERT_TYPE_CHOICES = [
        ('emergency', 'Emergency'),
        ('critical', 'Critical'),
        ('warning', 'Warning'),
    ]

    RESPONSE_METHOD_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
    ]

    alert_id = models.AutoField(primary_key=True)
    vital_sign = models.ForeignKey(VitalSign, on_delete=models.CASCADE, related_name='alert_responses')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vital_alert_responses')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)

    # Patient response tracking
    patient_response_status = models.CharField(max_length=20, choices=PATIENT_RESPONSE_CHOICES, default='none')
    patient_wants_doctor = models.BooleanField(default=False)
    patient_wants_nurse = models.BooleanField(default=False)
    patient_wants_ems = models.BooleanField(default=False)
    patient_response_time = models.DateTimeField(null=True, blank=True)
    patient_response_method = models.CharField(max_length=20, choices=RESPONSE_METHOD_CHOICES, blank=True)

    # Auto-escalation tracking
    timeout_minutes = models.IntegerField(default=15, help_text='Minutes to wait for patient response before auto-escalation')
    auto_escalated = models.BooleanField(default=False, help_text='Was this alert auto-escalated due to no response?')
    auto_escalation_time = models.DateTimeField(null=True, blank=True)

    # Notification tracking
    doctor_notified = models.BooleanField(default=False)
    nurse_notified = models.BooleanField(default=False)
    ems_notified = models.BooleanField(default=False)
    notifications_sent_at = models.DateTimeField(null=True, blank=True)

    # Response token for email/SMS links
    response_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # Vital signs that triggered the alert
    critical_vitals_json = models.JSONField(default=dict, help_text='JSON data of vital signs that triggered this alert')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'vital_sign_alert_responses'
        verbose_name = 'Vital Sign Alert Response'
        verbose_name_plural = 'Vital Sign Alert Responses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['response_token'], name='idx_response_token'),
            models.Index(fields=['patient_response_status'], name='idx_patient_response'),
            models.Index(fields=['auto_escalated'], name='idx_auto_escalated'),
        ]

    def __str__(self):
        return f"Alert {self.alert_id} - {self.patient.get_full_name()} - {self.get_alert_type_display()}"

    def record_patient_response(self, status, wants_doctor=False, wants_nurse=False, wants_ems=False, response_method='email'):
        """Record patient's response to the alert"""
        self.patient_response_status = status
        self.patient_wants_doctor = wants_doctor
        self.patient_wants_nurse = wants_nurse
        self.patient_wants_ems = wants_ems
        self.patient_response_time = timezone.now()
        self.patient_response_method = response_method
        self.save()

    def mark_auto_escalated(self):
        """Mark this alert as auto-escalated due to no response"""
        self.auto_escalated = True
        self.auto_escalation_time = timezone.now()
        self.save()

    def mark_notifications_sent(self, doctor=False, nurse=False, ems=False):
        """Mark which healthcare providers were notified"""
        self.doctor_notified = doctor
        self.nurse_notified = nurse
        self.ems_notified = ems
        self.notifications_sent_at = timezone.now()
        self.save()


class AIProposedTreatmentPlan(models.Model):
    """
    AI-generated treatment plan proposals
    Doctors can review, modify, and approve these plans
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('implemented', 'Implemented'),
    ]

    proposal_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='ai_treatment_proposals')
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, related_name='ai_treatment_proposals')

    # AI-generated treatment plan content
    proposed_treatment = models.TextField(help_text='AI-generated treatment plan')
    medications_suggested = models.TextField(blank=True, help_text='Medications suggested by AI')
    lifestyle_recommendations = models.TextField(blank=True, help_text='Lifestyle changes suggested by AI')
    follow_up_recommendations = models.TextField(blank=True, help_text='Follow-up recommendations')
    warnings_and_precautions = models.TextField(blank=True, help_text='Warnings and precautions')

    # Source data used for AI generation
    vital_signs_data = models.JSONField(default=dict, help_text='Vital signs data used for generation')
    diagnosis_data = models.JSONField(default=dict, help_text='Diagnosis data used for generation')
    lab_test_data = models.JSONField(default=dict, help_text='Lab test data used for generation')
    medical_history_data = models.JSONField(default=dict, help_text='Medical history used for generation')
    family_history_data = models.JSONField(default=dict, help_text='Family history used for generation')
    social_history_data = models.JSONField(default=dict, help_text='Social history used for generation')

    # AI model information
    ai_model_name = models.CharField(max_length=100, blank=True, help_text='Name of AI model used')
    ai_model_version = models.CharField(max_length=50, blank=True, help_text='Version of AI model')
    generation_time_seconds = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, help_text='Time taken to generate (in seconds)')
    prompt_tokens = models.IntegerField(null=True, blank=True, help_text='Number of tokens in prompt')
    completion_tokens = models.IntegerField(null=True, blank=True, help_text='Number of tokens in completion')

    # Doctor review
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    doctor_notes = models.TextField(blank=True, help_text='Doctor\'s notes and modifications')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'ai_proposed_treatment_plans'
        verbose_name = 'AI Proposed Treatment Plan'
        verbose_name_plural = 'AI Proposed Treatment Plans'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'status'], name='idx_ai_plan_patient_status'),
            models.Index(fields=['provider', 'status'], name='idx_ai_plan_provider_status'),
        ]

    def __str__(self):
        return f"AI Proposal #{self.proposal_id} - {self.patient.get_full_name()} - {self.get_status_display()}"

    def mark_reviewed(self, doctor_notes=''):
        """Mark this proposal as reviewed by a doctor"""
        self.status = 'reviewed'
        self.doctor_notes = doctor_notes
        self.reviewed_at = timezone.now()
        self.save()

    def approve(self, doctor_notes=''):
        """Approve this AI proposal"""
        self.status = 'approved'
        self.doctor_notes = doctor_notes
        self.reviewed_at = timezone.now()
        self.save()

    def reject(self, doctor_notes=''):
        """Reject this AI proposal"""
        self.status = 'rejected'
        self.doctor_notes = doctor_notes
        self.reviewed_at = timezone.now()
        self.save()


class DoctorTreatmentPlan(models.Model):
    """
    Doctor-created and approved treatment plans for patients
    Can be based on AI proposals or created from scratch
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    plan_id = models.AutoField(primary_key=True)
    plan_title = models.CharField(max_length=255, help_text='Title of the treatment plan')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='treatment_plans')
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, related_name='treatment_plans')
    encounter = models.ForeignKey(Encounter, on_delete=models.SET_NULL, null=True, blank=True, related_name='treatment_plans')

    # Link to AI proposal if this plan was based on one
    ai_proposal = models.ForeignKey(AIProposedTreatmentPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctor_plans')

    # Treatment plan details
    chief_complaint = models.TextField(blank=True, help_text='Patient\'s chief complaint')
    assessment = models.TextField(blank=True, help_text='Doctor\'s assessment')
    treatment_goals = models.TextField(help_text='Goals of this treatment plan')

    # Treatment components
    medications = models.TextField(blank=True, help_text='Prescribed medications with dosages and frequency')
    procedures = models.TextField(blank=True, help_text='Recommended medical procedures')
    lifestyle_modifications = models.TextField(blank=True, help_text='Lifestyle changes (exercise, diet, stress management)')
    dietary_recommendations = models.TextField(blank=True, help_text='Specific dietary guidelines')
    exercise_recommendations = models.TextField(blank=True, help_text='Exercise and physical activity recommendations')

    # Follow-up and monitoring
    follow_up_instructions = models.TextField(blank=True, help_text='Follow-up appointment schedule and instructions')
    warning_signs = models.TextField(blank=True, help_text='Warning signs to watch for')
    emergency_instructions = models.TextField(blank=True, help_text='When and how to seek emergency care')

    # Plan status and timeline
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    plan_start_date = models.DateField(help_text='Start date of the treatment plan')
    plan_end_date = models.DateField(null=True, blank=True, help_text='Expected end date (optional)')
    next_review_date = models.DateField(null=True, blank=True, help_text='Next review/follow-up date')

    # Patient visibility and interaction
    is_visible_to_patient = models.BooleanField(default=False, help_text='Is this plan visible to the patient in their portal?')
    patient_viewed_at = models.DateTimeField(null=True, blank=True, help_text='When patient first viewed this plan')
    patient_acknowledged_at = models.DateTimeField(null=True, blank=True, help_text='When patient acknowledged understanding the plan')
    patient_feedback = models.TextField(blank=True, help_text='Patient\'s feedback or questions')

    # Additional notes
    additional_notes = models.TextField(blank=True, help_text='Additional notes for internal use')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'doctor_treatment_plans'
        verbose_name = 'Doctor Treatment Plan'
        verbose_name_plural = 'Doctor Treatment Plans'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'status'], name='idx_treatment_plan_patient'),
            models.Index(fields=['provider', 'status'], name='idx_treatment_plan_provider'),
            models.Index(fields=['plan_start_date'], name='idx_treatment_plan_start'),
        ]

    def __str__(self):
        return f"{self.plan_title} - {self.patient.get_full_name()}"

    def publish_to_patient(self):
        """Make this treatment plan visible to the patient"""
        self.is_visible_to_patient = True
        if self.status == 'draft':
            self.status = 'active'
        self.save()

    def mark_patient_viewed(self):
        """Record when patient first viewed this plan"""
        if not self.patient_viewed_at:
            self.patient_viewed_at = timezone.now()
            self.save()

    def mark_patient_acknowledged(self):
        """Record when patient acknowledged understanding the plan"""
        if not self.patient_acknowledged_at:
            self.patient_acknowledged_at = timezone.now()
            self.save()


class APIKey(models.Model):
    """
    REST API Key model for external system integrations
    Managed by system administrators
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('revoked', 'Revoked'),
    ]

    api_key_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, help_text='Descriptive name for this API key')
    description = models.TextField(blank=True, null=True, help_text='Purpose and usage of this API key')

    # API Key credentials
    key = models.CharField(max_length=64, unique=True, help_text='API Key (auto-generated)')
    secret = models.CharField(max_length=128, help_text='API Secret (hashed)')

    # Permissions and scope
    permissions = models.JSONField(default=list, help_text='List of permitted API endpoints/actions')
    ip_whitelist = models.TextField(blank=True, null=True, help_text='Comma-separated list of allowed IP addresses')
    rate_limit = models.IntegerField(default=1000, help_text='Maximum requests per hour')

    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='api_keys_created')
    last_used_at = models.DateTimeField(null=True, blank=True, help_text='Last time this key was used')
    usage_count = models.IntegerField(default=0, help_text='Total number of API calls made')

    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True, help_text='Expiration date (optional)')

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'api_keys'
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['key'], name='idx_api_key'),
            models.Index(fields=['status'], name='idx_api_key_status'),
        ]

    def __str__(self):
        return f"{self.name} ({self.key[:8]}...)"

    @property
    def is_expired(self):
        """Check if the API key has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def revoke(self):
        """Revoke this API key"""
        self.status = 'revoked'
        self.save()

    def record_usage(self):
        """Record API key usage"""
        self.usage_count += 1
        self.last_used_at = timezone.now()
        self.save()

    @classmethod
    def generate_key(cls):
        """Generate a random API key"""
        import secrets
        return secrets.token_urlsafe(32)

    @classmethod
    def hash_secret(cls, secret):
        """Hash API secret for storage"""
        from django.contrib.auth.hashers import make_password
        return make_password(secret)

    @classmethod
    def verify_secret(cls, secret, hashed_secret):
        """Verify API secret against stored hash"""
        from django.contrib.auth.hashers import check_password
        return check_password(secret, hashed_secret)


class AuthenticationConfig(models.Model):
    """
    Authentication configuration model for managing different authentication methods
    Managed by system administrators via Django admin
    """
    AUTH_METHOD_CHOICES = [
        ('local', 'Local Authentication'),
        ('ldap', 'Active Directory / LDAP'),
        ('oauth2', 'OAuth 2.0'),
        ('openid', 'OpenID Connect'),
        ('azure_ad', 'Azure Active Directory'),
        ('cac', 'CAC (Common Access Card)'),
        ('saml', 'SAML 2.0'),
        ('sso', 'Single Sign-On (SSO)'),
    ]

    config_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, help_text='Descriptive name for this configuration')
    auth_method = models.CharField(max_length=50, choices=AUTH_METHOD_CHOICES, unique=True, help_text='Authentication method type')
    is_enabled = models.BooleanField(default=False, help_text='Enable this authentication method')
    is_primary = models.BooleanField(default=False, help_text='Set as primary authentication method')
    priority = models.IntegerField(default=0, help_text='Priority order (higher = checked first)')

    # General settings (applicable to most auth methods)
    configuration = models.JSONField(default=dict, help_text='Method-specific configuration settings (JSON)')

    # LDAP / Active Directory specific fields
    ldap_server = models.CharField(max_length=255, blank=True, help_text='LDAP server URL (e.g., ldap://server.domain.com)')
    ldap_port = models.IntegerField(null=True, blank=True, help_text='LDAP port (usually 389 or 636 for LDAPS)')
    ldap_bind_dn = models.CharField(max_length=255, blank=True, help_text='Bind DN for LDAP authentication')
    ldap_bind_password = models.CharField(max_length=255, blank=True, help_text='Bind password (encrypted)')
    ldap_search_base = models.CharField(max_length=255, blank=True, help_text='Base DN for user searches')
    ldap_user_filter = models.CharField(max_length=255, blank=True, default='(uid={username})', help_text='LDAP user filter')
    ldap_use_ssl = models.BooleanField(default=True, help_text='Use LDAPS (SSL/TLS)')

    # OAuth 2.0 specific fields
    oauth_client_id = models.CharField(max_length=255, blank=True, help_text='OAuth Client ID')
    oauth_client_secret = models.CharField(max_length=255, blank=True, help_text='OAuth Client Secret (encrypted)')
    oauth_authorization_url = models.URLField(blank=True, help_text='OAuth Authorization URL')
    oauth_token_url = models.URLField(blank=True, help_text='OAuth Token URL')
    oauth_userinfo_url = models.URLField(blank=True, help_text='OAuth UserInfo URL')
    oauth_scope = models.CharField(max_length=255, blank=True, default='openid profile email', help_text='OAuth scopes')

    # OpenID Connect specific fields
    openid_issuer = models.URLField(blank=True, help_text='OpenID Connect Issuer URL')
    openid_client_id = models.CharField(max_length=255, blank=True, help_text='OpenID Client ID')
    openid_client_secret = models.CharField(max_length=255, blank=True, help_text='OpenID Client Secret (encrypted)')
    openid_redirect_uri = models.URLField(blank=True, help_text='OpenID Redirect URI')

    # Azure AD specific fields
    azure_tenant_id = models.CharField(max_length=255, blank=True, help_text='Azure AD Tenant ID')
    azure_client_id = models.CharField(max_length=255, blank=True, help_text='Azure AD Application (Client) ID')
    azure_client_secret = models.CharField(max_length=255, blank=True, help_text='Azure AD Client Secret (encrypted)')
    azure_authority = models.URLField(blank=True, help_text='Azure AD Authority URL')

    # CAC (Common Access Card) specific fields
    cac_certificate_path = models.CharField(max_length=500, blank=True, help_text='Path to CAC certificate validation endpoint')
    cac_ca_bundle_path = models.CharField(max_length=500, blank=True, help_text='Path to CA bundle for certificate validation')
    cac_require_pin = models.BooleanField(default=True, help_text='Require PIN for CAC authentication')

    # SAML 2.0 specific fields
    saml_entity_id = models.CharField(max_length=255, blank=True, help_text='SAML Service Provider Entity ID')
    saml_idp_url = models.URLField(blank=True, help_text='SAML Identity Provider URL')
    saml_idp_metadata_url = models.URLField(blank=True, help_text='SAML IdP Metadata URL')
    saml_sp_cert = models.TextField(blank=True, help_text='SAML Service Provider Certificate')
    saml_sp_key = models.TextField(blank=True, help_text='SAML Service Provider Private Key (encrypted)')
    saml_attribute_mapping = models.JSONField(default=dict, blank=True, help_text='SAML attribute to user field mapping')

    # SSO specific fields
    sso_provider_name = models.CharField(max_length=255, blank=True, help_text='SSO Provider Name')
    sso_login_url = models.URLField(blank=True, help_text='SSO Login URL')
    sso_logout_url = models.URLField(blank=True, help_text='SSO Logout URL')
    sso_callback_url = models.URLField(blank=True, help_text='SSO Callback URL')

    # User provisioning settings
    auto_create_users = models.BooleanField(default=False, help_text='Automatically create users on first login')
    auto_update_users = models.BooleanField(default=True, help_text='Update user information from auth provider')
    default_user_role = models.CharField(max_length=20, blank=True, default='patient', help_text='Default role for auto-created users')

    # Advanced settings
    session_timeout_minutes = models.IntegerField(default=30, help_text='Session timeout in minutes')
    require_mfa = models.BooleanField(default=False, help_text='Require multi-factor authentication')
    allow_password_change = models.BooleanField(default=True, help_text='Allow users to change password')

    # Testing and debugging
    test_mode = models.BooleanField(default=False, help_text='Enable test mode (logs additional debug information)')
    debug_logging = models.BooleanField(default=False, help_text='Enable debug logging for this auth method')

    # Metadata
    description = models.TextField(blank=True, help_text='Description of this authentication configuration')
    notes = models.TextField(blank=True, help_text='Internal notes for administrators')

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='auth_configs_created')
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='auth_configs_modified')

    class Meta:
        db_table = 'authentication_config'
        verbose_name = 'Authentication Configuration'
        verbose_name_plural = 'Authentication Configurations'
        ordering = ['-priority', 'name']
        indexes = [
            models.Index(fields=['auth_method'], name='idx_auth_method'),
            models.Index(fields=['is_enabled'], name='idx_auth_enabled'),
            models.Index(fields=['-priority'], name='idx_auth_priority'),
        ]

    def __str__(self):
        status = '✓ Enabled' if self.is_enabled else '✗ Disabled'
        return f"{self.name} ({self.get_auth_method_display()}) - {status}"

    def clean(self):
        """Validate configuration based on auth method"""
        super().clean()

        # Ensure only one primary auth method
        if self.is_primary:
            other_primary = AuthenticationConfig.objects.filter(is_primary=True).exclude(pk=self.pk)
            if other_primary.exists():
                raise ValidationError('Only one authentication method can be set as primary.')

        # Validate method-specific required fields
        if self.is_enabled:
            if self.auth_method == 'ldap':
                if not all([self.ldap_server, self.ldap_search_base]):
                    raise ValidationError('LDAP configuration requires server URL and search base.')

            elif self.auth_method == 'oauth2':
                if not all([self.oauth_client_id, self.oauth_client_secret, self.oauth_authorization_url, self.oauth_token_url]):
                    raise ValidationError('OAuth 2.0 configuration requires client ID, secret, authorization URL, and token URL.')

            elif self.auth_method == 'openid':
                if not all([self.openid_issuer, self.openid_client_id, self.openid_client_secret]):
                    raise ValidationError('OpenID Connect configuration requires issuer, client ID, and client secret.')

            elif self.auth_method == 'azure_ad':
                if not all([self.azure_tenant_id, self.azure_client_id, self.azure_client_secret]):
                    raise ValidationError('Azure AD configuration requires tenant ID, client ID, and client secret.')

            elif self.auth_method == 'saml':
                if not all([self.saml_entity_id, self.saml_idp_url]):
                    raise ValidationError('SAML configuration requires entity ID and IdP URL.')

    def save(self, *args, **kwargs):
        """Custom save to handle primary auth method logic"""
        # If this is being set as primary, unset others
        if self.is_primary:
            AuthenticationConfig.objects.filter(is_primary=True).exclude(pk=self.pk).update(is_primary=False)

        # If no primary exists and this is enabled, make it primary
        if self.is_enabled and not AuthenticationConfig.objects.filter(is_primary=True).exclude(pk=self.pk).exists():
            self.is_primary = True

        super().save(*args, **kwargs)

    def test_connection(self):
        """Test the authentication configuration (method-specific implementation needed)"""
        # This would be implemented with method-specific connection tests
        pass

    def get_config_summary(self):
        """Return a summary of the configuration for display"""
        summary = {
            'method': self.get_auth_method_display(),
            'enabled': self.is_enabled,
            'primary': self.is_primary,
            'auto_create_users': self.auto_create_users,
        }

        if self.auth_method == 'ldap':
            summary['server'] = self.ldap_server
            summary['ssl'] = self.ldap_use_ssl
        elif self.auth_method in ['oauth2', 'openid']:
            summary['client_id'] = self.oauth_client_id or self.openid_client_id
        elif self.auth_method == 'azure_ad':
            summary['tenant'] = self.azure_tenant_id
        elif self.auth_method == 'saml':
            summary['entity_id'] = self.saml_entity_id

        return summary
