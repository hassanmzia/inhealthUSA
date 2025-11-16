from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Hospital(models.Model):
    """Hospital model"""
    hospital_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255, blank=True, null=True)
    website = models.URLField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hospitals'
        ordering = ['name']

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """User Profile model with role-based access"""
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('office_admin', 'Office Administrator'),
        ('admin', 'System Administrator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    # Multi-Factor Authentication fields
    mfa_enabled = models.BooleanField(default=False, help_text="Enable Two-Factor Authentication")
    mfa_secret = models.CharField(max_length=32, blank=True, null=True, help_text="TOTP Secret Key")
    backup_codes = models.JSONField(default=list, blank=True, help_text="Backup codes for MFA recovery")

    # Email Verification fields
    email_verified = models.BooleanField(default=False, help_text="Email address verified")
    email_verification_token = models.CharField(max_length=100, blank=True, null=True, help_text="Email verification token")
    email_verification_sent_at = models.DateTimeField(blank=True, null=True, help_text="When verification email was sent")

    # Profile Picture
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, help_text="User profile picture")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"

    @property
    def is_patient(self):
        return self.role == 'patient'

    @property
    def is_doctor(self):
        return self.role == 'doctor'

    @property
    def is_nurse(self):
        return self.role == 'nurse'

    @property
    def is_office_admin(self):
        return self.role == 'office_admin'

    @property
    def is_admin(self):
        return self.role == 'admin'


class Department(models.Model):
    """Department model"""
    department_id = models.AutoField(primary_key=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='departments', null=True, blank=True)
    department_name = models.CharField(max_length=200)
    location = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'departments'
        ordering = ['department_name']

    def __str__(self):
        if self.hospital:
            return f"{self.department_name} - {self.hospital.name}"
        return self.department_name


class Provider(models.Model):
    """Provider/Physician model"""
    provider_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile', null=True, blank=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, related_name='providers')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    npi = models.CharField(max_length=20, unique=True)
    specialty = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='providers')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'providers'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"Dr. {self.last_name}, {self.first_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Nurse(models.Model):
    """Nurse model"""
    nurse_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='nurse_profile', null=True, blank=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='nurses')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=100, unique=True)
    specialty = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='nurses')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'nurses'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name}, {self.first_name} (RN)"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class OfficeAdministrator(models.Model):
    """Office Administrator model"""
    admin_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='office_admin_profile', null=True, blank=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='office_administrators')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=100, unique=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='office_administrators')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'office_administrators'
        ordering = ['last_name', 'first_name']
        verbose_name = 'Office Administrator'
        verbose_name_plural = 'Office Administrators'

    def __str__(self):
        return f"{self.last_name}, {self.first_name} (Admin)"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Patient(models.Model):
    """Patient model representing patient demographic information"""
    patient_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile', null=True, blank=True)
    primary_doctor = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, related_name='primary_patients')
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ])
    ssn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=200, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    insurance_provider = models.CharField(max_length=200, blank=True, null=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'patients'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"


class Encounter(models.Model):
    """Encounter/Appointment model"""
    encounter_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='encounters')
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, related_name='encounters')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='encounters')
    encounter_date = models.DateTimeField()
    encounter_type = models.CharField(max_length=100, choices=[
        ('Office Visit', 'Office Visit'),
        ('Follow-up', 'Follow-up'),
        ('Annual Physical', 'Annual Physical'),
        ('Urgent Care', 'Urgent Care'),
        ('Consultation', 'Consultation'),
        ('Telemedicine', 'Telemedicine'),
        ('Emergency', 'Emergency'),
        ('Procedure', 'Procedure'),
        ('Lab Review', 'Lab Review'),
    ])
    chief_complaint = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='Scheduled', choices=[
        ('Scheduled', 'Scheduled'),
        ('Checked In', 'Checked In'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('No Show', 'No Show'),
    ])
    clinical_impression = models.TextField(blank=True, null=True)
    treatment_plan = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'encounters'
        ordering = ['-encounter_date']

    def __str__(self):
        return f"Encounter {self.encounter_id} - {self.patient.full_name} on {self.encounter_date.strftime('%Y-%m-%d')}"


class VitalSign(models.Model):
    """Vital Signs model"""
    vital_signs_id = models.AutoField(primary_key=True)
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name='vital_signs')
    temperature_value = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    temperature_unit = models.CharField(max_length=1, choices=[('C', 'Celsius'), ('F', 'Fahrenheit')], blank=True, null=True)
    blood_pressure_systolic = models.IntegerField(blank=True, null=True)
    blood_pressure_diastolic = models.IntegerField(blank=True, null=True)
    heart_rate = models.IntegerField(blank=True, null=True)
    respiratory_rate = models.IntegerField(blank=True, null=True)
    oxygen_saturation = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    glucose = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)  # Blood glucose in mg/dL
    weight_value = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    weight_unit = models.CharField(max_length=3, choices=[('lbs', 'Pounds'), ('kg', 'Kilograms')], blank=True, null=True)
    height_value = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    height_unit = models.CharField(max_length=2, choices=[('in', 'Inches'), ('cm', 'Centimeters')], blank=True, null=True)
    bmi = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, blank=True)
    recorded_by_nurse = models.ForeignKey('Nurse', on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_vitals')
    data_source = models.CharField(max_length=10, choices=[('manual', 'Manual Entry'), ('device', 'IoT Device')], default='manual')
    device = models.ForeignKey('Device', on_delete=models.SET_NULL, null=True, blank=True, related_name='vitals_recorded')
    recorded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'vital_signs'
        ordering = ['-recorded_at']

    def __str__(self):
        return f"Vitals for Encounter {self.encounter_id} at {self.recorded_at}"

    @property
    def blood_pressure(self):
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"
        return "N/A"

    # Heart Rate (Pulse/HR) Color and Contact
    def get_heart_rate_status(self):
        """Returns (color, contact_level, is_critical) for heart rate"""
        if not self.heart_rate:
            return None, None, False
        hr = self.heart_rate
        if hr >= 150:
            return 'blue', 'Emergency', True
        elif 120 <= hr <= 149:
            return 'red', 'Doctor', True
        elif 100 <= hr <= 119:
            return 'orange', 'Nurse', True
        elif 50 <= hr <= 99:
            return 'green', 'Normal', False
        elif 40 <= hr <= 49:
            return 'orange', 'Nurse', True
        elif 30 <= hr <= 39:
            return 'red', 'Doctor', True
        else:  # < 30
            return 'blue', 'Emergency', True

    # Systolic Blood Pressure Color and Contact
    def get_sbp_status(self):
        """Returns (color, contact_level, is_critical) for systolic BP"""
        if not self.blood_pressure_systolic:
            return None, None, False
        sbp = self.blood_pressure_systolic
        if sbp > 220:
            return 'blue', 'Emergency', True
        elif 180 <= sbp <= 219:
            return 'red', 'Doctor', True
        elif 150 <= sbp <= 179:
            return 'orange', 'Nurse', True
        elif 100 <= sbp <= 149:
            return 'green', 'Normal', False
        elif 90 <= sbp <= 100:
            return 'orange', 'Nurse', True
        elif 80 <= sbp <= 89:
            return 'red', 'Doctor', True
        else:  # < 80
            return 'blue', 'Emergency', True

    # Diastolic Blood Pressure Color and Contact
    def get_dbp_status(self):
        """Returns (color, contact_level, is_critical) for diastolic BP"""
        if not self.blood_pressure_diastolic:
            return None, None, False
        dbp = self.blood_pressure_diastolic
        if dbp > 120:
            return 'blue', 'Emergency', True
        elif 110 <= dbp <= 119:
            return 'red', 'Doctor', True
        elif 100 <= dbp <= 109:
            return 'orange', 'Nurse', True
        elif 50 <= dbp <= 99:
            return 'green', 'Normal', False
        elif 40 <= dbp <= 49:
            return 'orange', 'Nurse', True
        elif 30 <= dbp <= 39:
            return 'red', 'Doctor', True
        else:  # < 30
            return 'blue', 'Emergency', True

    # Temperature Color and Contact
    def get_temperature_status(self):
        """Returns (color, contact_level, is_critical) for temperature (in Fahrenheit)"""
        if not self.temperature_value:
            return None, None, False
        # Convert to Fahrenheit if needed
        temp = float(self.temperature_value)
        if self.temperature_unit == 'C':
            temp = (temp * 9/5) + 32

        if temp > 105:
            return 'blue', 'Emergency', True
        elif 102 <= temp <= 104.9:
            return 'red', 'Doctor', True
        elif 100.4 <= temp <= 101.9:
            return 'orange', 'Nurse', True
        elif 97 <= temp <= 100.4:
            return 'green', 'Normal', False
        elif 95 <= temp <= 96.9:
            return 'orange', 'Nurse', True
        elif 93 <= temp <= 94.9:
            return 'red', 'Doctor', True
        else:  # < 93
            return 'blue', 'Emergency', True

    # Respiration Rate Color and Contact
    def get_respiratory_rate_status(self):
        """Returns (color, contact_level, is_critical) for respiration rate"""
        if not self.respiratory_rate:
            return None, None, False
        rr = self.respiratory_rate
        if rr > 50:
            return 'blue', 'Emergency', True
        elif 40 <= rr <= 49:
            return 'red', 'Doctor', True
        elif 30 <= rr <= 39:
            return 'orange', 'Nurse', True
        elif 12 <= rr <= 29:
            return 'green', 'Normal', False
        elif 9 <= rr <= 11:
            return 'orange', 'Nurse', True
        elif 7 <= rr <= 8:
            return 'red', 'Doctor', True
        else:  # < 6
            return 'blue', 'Emergency', True

    # O2 Saturation Color and Contact
    def get_oxygen_saturation_status(self):
        """Returns (color, contact_level, is_critical) for O2 saturation"""
        if not self.oxygen_saturation:
            return None, None, False
        o2 = float(self.oxygen_saturation)
        if 92 <= o2 <= 100:
            return 'green', 'Normal', False
        elif 88 <= o2 < 92:
            return 'orange', 'Nurse', True
        elif 81 <= o2 < 88:
            return 'red', 'Doctor', True
        else:  # < 80
            return 'blue', 'Emergency', True

    # Glucose Color and Contact
    def get_glucose_status(self):
        """Returns (color, contact_level, is_critical) for glucose (mg/dL)"""
        if not self.glucose:
            return None, None, False
        glc = float(self.glucose)
        if glc > 750:
            return 'blue', 'Emergency', True
        elif 400 <= glc <= 749:
            return 'red', 'Doctor', True
        elif 300 <= glc <= 399:
            return 'orange', 'Nurse', True
        elif 120 <= glc <= 299:
            return 'green', 'Normal', False
        elif 50 <= glc <= 119:
            return 'orange', 'Nurse', True
        elif 30 <= glc <= 49:
            return 'red', 'Doctor', True
        else:  # < 30
            return 'blue', 'Emergency', True

    def get_critical_vitals(self):
        """Returns a dictionary of all critical vitals with their status"""
        return {
            'heart_rate': {
                'value': self.heart_rate,
                'status': self.get_heart_rate_status(),
                'label': 'Pulse/HR',
                'unit': 'bpm'
            },
            'sbp': {
                'value': self.blood_pressure_systolic,
                'status': self.get_sbp_status(),
                'label': 'SBP',
                'unit': 'mmHg'
            },
            'dbp': {
                'value': self.blood_pressure_diastolic,
                'status': self.get_dbp_status(),
                'label': 'DBP',
                'unit': 'mmHg'
            },
            'temperature': {
                'value': self.temperature_value,
                'status': self.get_temperature_status(),
                'label': 'Temperature',
                'unit': f'°{self.temperature_unit}' if self.temperature_unit else '°F'
            },
            'respiratory_rate': {
                'value': self.respiratory_rate,
                'status': self.get_respiratory_rate_status(),
                'label': 'Respiration Rate',
                'unit': 'bpm'
            },
            'oxygen_saturation': {
                'value': self.oxygen_saturation,
                'status': self.get_oxygen_saturation_status(),
                'label': 'O2 Saturation',
                'unit': '%'
            },
            'glucose': {
                'value': self.glucose,
                'status': self.get_glucose_status(),
                'label': 'Glucose',
                'unit': 'mg/dL'
            }
        }

    def has_critical_values(self):
        """Check if any vital signs have critical values requiring immediate attention"""
        critical_vitals = self.get_critical_vitals()
        for vital_name, vital_data in critical_vitals.items():
            if vital_data['status'] and vital_data['status'][2]:  # is_critical flag
                return True
        return False

    def get_highest_alert_level(self):
        """Returns the highest alert level among all vitals (Emergency, Doctor, Nurse, Normal)"""
        critical_vitals = self.get_critical_vitals()
        alert_priority = {'Emergency': 4, 'Doctor': 3, 'Nurse': 2, 'Normal': 1}
        highest_level = 'Normal'
        highest_priority = 1

        for vital_name, vital_data in critical_vitals.items():
            if vital_data['status'] and vital_data['status'][1]:  # contact_level
                contact_level = vital_data['status'][1]
                priority = alert_priority.get(contact_level, 0)
                if priority > highest_priority:
                    highest_priority = priority
                    highest_level = contact_level

        return highest_level

    def get_data_source_display_with_name(self):
        """Returns the data source with the name of who/what recorded it"""
        if self.data_source == 'device' and self.device:
            return f"IoT Device: {self.device.device_name}"
        elif self.data_source == 'manual' and self.recorded_by_nurse:
            return f"Nurse: {self.recorded_by_nurse.full_name}"
        elif self.recorded_by:
            return f"Doctor: {self.recorded_by.full_name}"
        else:
            return "Unknown Source"


class Diagnosis(models.Model):
    """Diagnosis model"""
    diagnosis_id = models.AutoField(primary_key=True)
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name='diagnoses')
    diagnosis_description = models.TextField()
    icd10_code = models.CharField(max_length=20, blank=True, null=True)
    icd11_code = models.CharField(max_length=20, blank=True, null=True)
    diagnosis_type = models.CharField(max_length=50, choices=[
        ('Primary', 'Primary'),
        ('Secondary', 'Secondary'),
        ('Differential', 'Differential'),
    ])
    status = models.CharField(max_length=50, default='Active', choices=[
        ('Active', 'Active'),
        ('Resolved', 'Resolved'),
        ('Rule Out', 'Rule Out'),
    ])
    onset_date = models.DateField(blank=True, null=True)
    resolved_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    diagnosed_by = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, blank=True)
    diagnosed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'diagnoses'
        ordering = ['-diagnosed_at']

    def __str__(self):
        return f"{self.diagnosis_description} ({self.diagnosis_type})"


class Prescription(models.Model):
    """Prescription model"""
    prescription_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, related_name='prescriptions')
    encounter = models.ForeignKey(Encounter, on_delete=models.SET_NULL, null=True, blank=True, related_name='prescriptions')
    medication_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    route = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    refills = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)
    pharmacy_name = models.CharField(max_length=200, blank=True, null=True)
    pharmacy_phone = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=50, default='Active', choices=[
        ('Active', 'Active'),
        ('Discontinued', 'Discontinued'),
        ('Completed', 'Completed'),
    ])

    class Meta:
        db_table = 'prescriptions'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.medication_name} - {self.dosage}"


class Allergy(models.Model):
    """Allergy model"""
    allergy_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='allergies')
    allergen = models.CharField(max_length=255)
    allergy_type = models.CharField(max_length=100, choices=[
        ('Drug', 'Drug'),
        ('Food', 'Food'),
        ('Environmental', 'Environmental'),
        ('Other', 'Other'),
    ])
    severity = models.CharField(max_length=50, choices=[
        ('Mild', 'Mild'),
        ('Moderate', 'Moderate'),
        ('Severe', 'Severe'),
    ], blank=True, null=True)
    reaction = models.TextField(blank=True, null=True)
    onset_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'allergies'
        ordering = ['-severity', 'allergen']

    def __str__(self):
        return f"{self.allergen} ({self.allergy_type})"


class MedicalHistory(models.Model):
    """Medical History model"""
    medical_history_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_history')
    condition = models.CharField(max_length=255)
    diagnosis_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=[
        ('Active', 'Active'),
        ('Resolved', 'Resolved'),
        ('Chronic', 'Chronic'),
    ], default='Active')
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'medical_history'
        ordering = ['-diagnosis_date']

    def __str__(self):
        return f"{self.condition} - {self.status}"


class SocialHistory(models.Model):
    """Social History model"""
    social_history_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='social_history')
    smoking_status = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('Never', 'Never'),
        ('Former', 'Former'),
        ('Current', 'Current'),
    ])
    alcohol_use = models.CharField(max_length=50, blank=True, null=True)
    drug_use = models.CharField(max_length=50, blank=True, null=True)
    occupation = models.CharField(max_length=200, blank=True, null=True)
    marital_status = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Divorced', 'Divorced'),
        ('Widowed', 'Widowed'),
    ])
    notes = models.TextField(blank=True, null=True)
    recorded_date = models.DateField(default=timezone.now)

    class Meta:
        db_table = 'social_history'
        ordering = ['-recorded_date']

    def __str__(self):
        return f"Social History for Patient {self.patient_id}"


class Message(models.Model):
    """Message model for patient-doctor communication"""
    message_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.sender.get_full_name()} to {self.recipient.get_full_name()}: {self.subject}"


class LabTest(models.Model):
    """Lab Test model"""
    lab_test_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_tests')
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, related_name='ordered_lab_tests')
    encounter = models.ForeignKey(Encounter, on_delete=models.SET_NULL, null=True, blank=True, related_name='lab_tests')
    test_name = models.CharField(max_length=255)
    test_code = models.CharField(max_length=50, blank=True, null=True)
    ordered_date = models.DateTimeField(default=timezone.now)
    collection_date = models.DateTimeField(null=True, blank=True)
    result_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, default='Ordered', choices=[
        ('Ordered', 'Ordered'),
        ('Collected', 'Collected'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ])
    result = models.TextField(blank=True, null=True)
    result_value = models.CharField(max_length=100, blank=True, null=True)
    result_unit = models.CharField(max_length=50, blank=True, null=True)
    reference_range = models.CharField(max_length=100, blank=True, null=True)
    abnormal_flag = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'lab_tests'
        ordering = ['-ordered_date']

    def __str__(self):
        return f"{self.test_name} for {self.patient.full_name} - {self.status}"


class FamilyHistory(models.Model):
    """Family History model"""
    family_history_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='family_history')
    relationship = models.CharField(max_length=100, choices=[
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Brother', 'Brother'),
        ('Sister', 'Sister'),
        ('Grandfather', 'Grandfather'),
        ('Grandmother', 'Grandmother'),
        ('Uncle', 'Uncle'),
        ('Aunt', 'Aunt'),
        ('Son', 'Son'),
        ('Daughter', 'Daughter'),
        ('Other', 'Other'),
    ])
    condition = models.CharField(max_length=255)
    age_at_diagnosis = models.IntegerField(blank=True, null=True)
    is_alive = models.BooleanField(default=True)
    age_at_death = models.IntegerField(blank=True, null=True)
    cause_of_death = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    recorded_date = models.DateField(default=timezone.now)

    class Meta:
        db_table = 'family_history'
        ordering = ['-recorded_date']

    def __str__(self):
        return f"{self.relationship} - {self.condition} (Patient: {self.patient.full_name})"


class Notification(models.Model):
    """Notification model for system alerts"""
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=[
        ('appointment', 'Appointment'),
        ('lab_result', 'Lab Result'),
        ('prescription', 'Prescription'),
        ('message', 'Message'),
        ('vital_alert', 'Vital Sign Alert'),
        ('system', 'System'),
    ])
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.get_full_name()}: {self.title}"


class InsuranceInformation(models.Model):
    """Insurance Information model"""
    insurance_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='insurance_policies')
    provider_name = models.CharField(max_length=200)
    plan_type = models.CharField(max_length=100, blank=True, null=True)
    policy_number = models.CharField(max_length=100)
    group_number = models.CharField(max_length=100, blank=True, null=True)
    subscriber_name = models.CharField(max_length=200)
    subscriber_relationship = models.CharField(max_length=50, choices=[
        ('Self', 'Self'),
        ('Spouse', 'Spouse'),
        ('Parent', 'Parent'),
        ('Child', 'Child'),
        ('Other', 'Other'),
    ])
    effective_date = models.DateField()
    termination_date = models.DateField(blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'insurance_information'
        ordering = ['-is_primary', '-effective_date']

    def __str__(self):
        return f"{self.provider_name} - {self.policy_number} ({'Primary' if self.is_primary else 'Secondary'})"


class Billing(models.Model):
    """Billing model for patient invoices"""
    billing_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='billings')
    encounter = models.ForeignKey(Encounter, on_delete=models.SET_NULL, null=True, blank=True, related_name='billings')
    invoice_number = models.CharField(max_length=50, unique=True)
    billing_date = models.DateField()
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Pending', choices=[
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Partial', 'Partial'),
        ('Overdue', 'Overdue'),
        ('Cancelled', 'Cancelled'),
    ])
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'billings'
        ordering = ['-billing_date']

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.patient.full_name} - ${self.total_amount}"


class BillingItem(models.Model):
    """Billing Item model for individual service charges"""
    item_id = models.AutoField(primary_key=True)
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, related_name='billing_items')
    service_code = models.CharField(max_length=50)
    service_description = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'billing_items'
        ordering = ['item_id']

    def __str__(self):
        return f"{self.service_code} - {self.service_description} - ${self.total_price}"


class Payment(models.Model):
    """Payment model for tracking patient payments"""
    payment_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='payments')
    billing = models.ForeignKey(Billing, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    payment_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='Cash', choices=[
        ('Cash', 'Cash'),
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('Check', 'Check'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Insurance', 'Insurance'),
        ('Other', 'Other'),
    ])
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default='Completed', choices=[
        ('Completed', 'Completed'),
        ('Pending', 'Pending'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ])
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment #{self.payment_id} - {self.patient.full_name} - ${self.amount} ({self.status})"


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
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    device_name = models.CharField(max_length=200)
    manufacturer = models.CharField(max_length=200, blank=True, null=True)
    model_number = models.CharField(max_length=100, blank=True, null=True)
    firmware_version = models.CharField(max_length=50, blank=True, null=True)
    capabilities = models.JSONField(blank=True, null=True)  # List of capabilities
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    battery_level = models.IntegerField(blank=True, null=True)  # 0-100 percentage
    last_sync = models.DateTimeField(blank=True, null=True)
    registration_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'devices'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.device_name} ({self.device_type}) - {self.patient.full_name}"

    @property
    def battery_color(self):
        """Get battery status color"""
        if self.battery_level is None:
            return 'gray'
        if self.battery_level >= 70:
            return 'green'
        if self.battery_level >= 30:
            return 'yellow'
        return 'red'

    @property
    def capabilities_list(self):
        """Get capabilities as a list"""
        if isinstance(self.capabilities, list):
            return self.capabilities
        return []


class NotificationPreferences(models.Model):
    """
    Notification preferences for vital sign alerts
    Allows users to control how they receive vital sign alerts
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')

    # Email notifications
    email_enabled = models.BooleanField(default=True, help_text="Receive email notifications")
    email_emergency = models.BooleanField(default=True, help_text="Receive emergency alerts via email")
    email_critical = models.BooleanField(default=True, help_text="Receive critical alerts via email")
    email_warning = models.BooleanField(default=True, help_text="Receive warning alerts via email")

    # SMS notifications
    sms_enabled = models.BooleanField(default=False, help_text="Receive SMS notifications")
    sms_emergency = models.BooleanField(default=True, help_text="Receive emergency alerts via SMS")
    sms_critical = models.BooleanField(default=True, help_text="Receive critical alerts via SMS")
    sms_warning = models.BooleanField(default=False, help_text="Receive warning alerts via SMS")

    # WhatsApp notifications
    whatsapp_enabled = models.BooleanField(default=False, help_text="Receive WhatsApp notifications")
    whatsapp_emergency = models.BooleanField(default=True, help_text="Receive emergency alerts via WhatsApp")
    whatsapp_critical = models.BooleanField(default=True, help_text="Receive critical alerts via WhatsApp")
    whatsapp_warning = models.BooleanField(default=True, help_text="Receive warning alerts via WhatsApp")
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True, help_text="WhatsApp number with country code (e.g., +1234567890)")

    # Quiet hours (optional)
    enable_quiet_hours = models.BooleanField(default=False, help_text="Enable quiet hours (no non-emergency alerts)")
    quiet_start_time = models.TimeField(null=True, blank=True, help_text="Quiet hours start time")
    quiet_end_time = models.TimeField(null=True, blank=True, help_text="Quiet hours end time")

    # Advanced settings
    digest_mode = models.BooleanField(default=False, help_text="Send digest emails instead of individual alerts")
    digest_frequency_hours = models.IntegerField(default=6, help_text="How often to send digest emails (in hours)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'

    def __str__(self):
        return f"Notification preferences for {self.user.get_full_name() or self.user.username}"

    def should_send_email(self, alert_type):
        """
        Check if email notification should be sent for this alert type
        alert_type: 'emergency', 'doctor', or 'nurse'
        """
        if not self.email_enabled:
            return False

        if alert_type == 'emergency':
            return self.email_emergency
        elif alert_type == 'doctor':
            return self.email_critical
        elif alert_type == 'nurse':
            return self.email_warning

        return True  # Default to sending

    def should_send_sms(self, alert_type):
        """
        Check if SMS notification should be sent for this alert type
        alert_type: 'emergency', 'doctor', or 'nurse'
        """
        if not self.sms_enabled:
            return False

        if alert_type == 'emergency':
            return self.sms_emergency
        elif alert_type == 'doctor':
            return self.sms_critical
        elif alert_type == 'nurse':
            return self.sms_warning

        return False  # Default to not sending SMS for unknown types

    def should_send_whatsapp(self, alert_type):
        """
        Check if WhatsApp notification should be sent for this alert type
        alert_type: 'emergency', 'doctor', or 'nurse'
        """
        if not self.whatsapp_enabled:
            return False

        if alert_type == 'emergency':
            return self.whatsapp_emergency
        elif alert_type == 'doctor':
            return self.whatsapp_critical
        elif alert_type == 'nurse':
            return self.whatsapp_warning

        return False  # Default to not sending WhatsApp for unknown types

    def is_quiet_hours(self):
        """Check if current time is within quiet hours"""
        if not self.enable_quiet_hours or not self.quiet_start_time or not self.quiet_end_time:
            return False

        from datetime import datetime
        now = datetime.now().time()

        # Handle overnight quiet hours
        if self.quiet_start_time <= self.quiet_end_time:
            return self.quiet_start_time <= now <= self.quiet_end_time
        else:
            return now >= self.quiet_start_time or now <= self.quiet_end_time


class VitalSignAlertResponse(models.Model):
    """
    Tracks patient responses to critical vital sign alerts
    Implements two-stage alerting: Patient permission → Provider notification
    """
    STATUS_CHOICES = [
        ('pending', 'Waiting for Patient Response'),
        ('approved_doctor', 'Patient Approved - Notify Doctor'),
        ('approved_nurse', 'Patient Approved - Notify Nurse'),
        ('approved_ems', 'Patient Approved - Notify EMS'),
        ('approved_all', 'Patient Approved - Notify All'),
        ('declined', 'Patient Declined Notification'),
        ('timeout', 'No Response - Auto-escalated'),
        ('completed', 'Notifications Sent'),
    ]

    alert_id = models.AutoField(primary_key=True)
    vital_sign = models.ForeignKey('VitalSign', on_delete=models.CASCADE, related_name='alert_responses')
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='vital_alert_responses')

    # Alert details
    alert_type = models.CharField(max_length=20, help_text="emergency, doctor, or nurse")
    critical_vitals_json = models.JSONField(help_text="JSON array of critical vital signs")

    # Patient response
    patient_response_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    patient_wants_doctor = models.BooleanField(default=False, help_text="Patient wants to contact doctor")
    patient_wants_nurse = models.BooleanField(default=False, help_text="Patient wants to contact nurse")
    patient_wants_ems = models.BooleanField(default=False, help_text="Patient wants to contact EMS")
    patient_response_time = models.DateTimeField(null=True, blank=True, help_text="When patient responded")
    patient_response_method = models.CharField(max_length=20, null=True, blank=True, help_text="email, sms, or whatsapp")

    # Auto-escalation
    timeout_minutes = models.IntegerField(default=15, help_text="Minutes before auto-escalation")
    auto_escalated = models.BooleanField(default=False, help_text="Alert was auto-escalated due to timeout")
    auto_escalation_time = models.DateTimeField(null=True, blank=True, help_text="When auto-escalation occurred")

    # Notifications sent
    doctor_notified = models.BooleanField(default=False)
    nurse_notified = models.BooleanField(default=False)
    ems_notified = models.BooleanField(default=False)
    notifications_sent_at = models.DateTimeField(null=True, blank=True)

    # Response tracking
    response_token = models.CharField(max_length=100, unique=True, help_text="Unique token for response links")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vital_sign_alert_responses'
        verbose_name = 'Vital Sign Alert Response'
        verbose_name_plural = 'Vital Sign Alert Responses'
        ordering = ['-created_at']

    def __str__(self):
        return f"Alert {self.alert_id} - {self.patient.full_name} - {self.patient_response_status}"

    def is_pending(self):
        """Check if alert is still waiting for patient response"""
        return self.patient_response_status == 'pending'

    def is_timeout_exceeded(self):
        """Check if the timeout period has been exceeded"""
        if self.patient_response_status != 'pending':
            return False

        from datetime import timedelta
        timeout_threshold = self.created_at + timedelta(minutes=self.timeout_minutes)
        return timezone.now() > timeout_threshold

    def should_auto_escalate(self):
        """Determine if alert should be auto-escalated"""
        return self.is_pending() and self.is_timeout_exceeded() and not self.auto_escalated

    def get_response_url(self, action):
        """
        Generate response URL for email/SMS/WhatsApp
        action: 'approve_doctor', 'approve_nurse', 'approve_ems', 'approve_all', 'decline'
        """
        from django.urls import reverse
        from django.conf import settings

        base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        path = reverse('vital_alert_response', kwargs={'token': self.response_token, 'action': action})
        return f"{base_url}{path}"

    def process_patient_response(self, action, response_method='web'):
        """
        Process patient's response to alert
        action: 'approve_doctor', 'approve_nurse', 'approve_ems', 'approve_all', 'decline'
        """
        if not self.is_pending():
            return False, "Alert has already been responded to"

        self.patient_response_time = timezone.now()
        self.patient_response_method = response_method

        if action == 'decline':
            self.patient_response_status = 'declined'
            self.save()
            return True, "Patient declined notification. No providers will be contacted."

        elif action == 'approve_doctor':
            self.patient_wants_doctor = True
            self.patient_response_status = 'approved_doctor'

        elif action == 'approve_nurse':
            self.patient_wants_nurse = True
            self.patient_response_status = 'approved_nurse'

        elif action == 'approve_ems':
            self.patient_wants_ems = True
            self.patient_response_status = 'approved_ems'

        elif action == 'approve_all':
            self.patient_wants_doctor = True
            self.patient_wants_nurse = True
            self.patient_wants_ems = True
            self.patient_response_status = 'approved_all'

        else:
            return False, "Invalid action"

        self.save()

        # Send notifications to approved providers
        self._send_provider_notifications()

        return True, f"Notifications will be sent as requested."

    def _send_provider_notifications(self):
        """Send notifications to providers based on patient approval"""
        from .vital_alerts import send_alert_to_providers

        send_alert_to_providers(
            vital_sign=self.vital_sign,
            patient=self.patient,
            alert_type=self.alert_type,
            critical_vitals=self.critical_vitals_json,
            notify_doctor=self.patient_wants_doctor,
            notify_nurse=self.patient_wants_nurse,
            notify_ems=self.patient_wants_ems
        )

        self.doctor_notified = self.patient_wants_doctor
        self.nurse_notified = self.patient_wants_nurse
        self.ems_notified = self.patient_wants_ems
        self.notifications_sent_at = timezone.now()
        self.patient_response_status = 'completed'
        self.save()

    def auto_escalate(self):
        """Auto-escalate alert when timeout is exceeded"""
        if not self.should_auto_escalate():
            return False

        self.auto_escalated = True
        self.auto_escalation_time = timezone.now()
        self.patient_response_status = 'timeout'

        # For emergencies, notify everyone
        if self.alert_type == 'emergency':
            self.patient_wants_doctor = True
            self.patient_wants_nurse = True
            self.patient_wants_ems = True
        # For critical, notify doctor and nurse
        elif self.alert_type == 'doctor':
            self.patient_wants_doctor = True
            self.patient_wants_nurse = True
        # For warnings, notify nurse
        else:
            self.patient_wants_nurse = True

        self.save()

        # Send notifications
        self._send_provider_notifications()

        return True


class AIProposedTreatmentPlan(models.Model):
    """
    AI-generated treatment plan proposals using Ollama/Llama
    Only visible to doctors - patients cannot see these proposals
    """
    proposal_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(
        'Patient',
        on_delete=models.CASCADE,
        related_name='ai_treatment_proposals',
        help_text='Patient for whom the treatment plan is proposed'
    )
    provider = models.ForeignKey(
        'Provider',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_treatment_proposals',
        help_text='Doctor who requested the AI proposal'
    )

    # Data used for generating the proposal
    vital_signs_data = models.JSONField(
        help_text='Vital signs data used for proposal',
        blank=True,
        null=True
    )
    diagnosis_data = models.JSONField(
        help_text='Diagnosis information used for proposal',
        blank=True,
        null=True
    )
    lab_test_data = models.JSONField(
        help_text='Lab test results used for proposal',
        blank=True,
        null=True
    )
    medical_history_data = models.JSONField(
        help_text='Medical history used for proposal',
        blank=True,
        null=True
    )
    family_history_data = models.JSONField(
        help_text='Family history used for proposal',
        blank=True,
        null=True
    )
    social_history_data = models.JSONField(
        help_text='Social history used for proposal',
        blank=True,
        null=True
    )

    # AI-generated content
    proposed_treatment = models.TextField(
        help_text='AI-generated treatment plan proposal'
    )
    medications_suggested = models.TextField(
        blank=True,
        null=True,
        help_text='AI-suggested medications'
    )
    lifestyle_recommendations = models.TextField(
        blank=True,
        null=True,
        help_text='AI-suggested lifestyle changes'
    )
    follow_up_recommendations = models.TextField(
        blank=True,
        null=True,
        help_text='AI-suggested follow-up care'
    )
    warnings_and_precautions = models.TextField(
        blank=True,
        null=True,
        help_text='AI-generated warnings and precautions'
    )

    # AI model metadata
    ai_model_name = models.CharField(
        max_length=100,
        default='llama3.2',
        help_text='Name of AI model used'
    )
    ai_model_version = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Version of AI model'
    )
    generation_time_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text='Time taken to generate proposal'
    )
    prompt_tokens = models.IntegerField(
        null=True,
        blank=True,
        help_text='Number of tokens in prompt'
    )
    completion_tokens = models.IntegerField(
        null=True,
        blank=True,
        help_text='Number of tokens in completion'
    )

    # Doctor actions
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('modified', 'Modified and Used'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Doctor review status'
    )
    doctor_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Doctor's notes on the AI proposal"
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When doctor reviewed the proposal'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_proposed_treatment_plans'
        verbose_name = 'AI Proposed Treatment Plan'
        verbose_name_plural = 'AI Proposed Treatment Plans'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', '-created_at'], name='idx_ai_proposal_patient'),
            models.Index(fields=['provider', '-created_at'], name='idx_ai_proposal_provider'),
            models.Index(fields=['status'], name='idx_ai_proposal_status'),
        ]

    def __str__(self):
        return f"AI Proposal for {self.patient.full_name} - {self.created_at.strftime('%Y-%m-%d')}"

    def mark_as_reviewed(self, doctor_notes=None):
        """Mark proposal as reviewed by doctor"""
        self.status = 'reviewed'
        self.reviewed_at = timezone.now()
        if doctor_notes:
            self.doctor_notes = doctor_notes
        self.save()

    def mark_as_accepted(self, doctor_notes=None):
        """Mark proposal as accepted by doctor"""
        self.status = 'accepted'
        self.reviewed_at = timezone.now()
        if doctor_notes:
            self.doctor_notes = doctor_notes
        self.save()

    def mark_as_modified(self, doctor_notes=None):
        """Mark proposal as modified and used by doctor"""
        self.status = 'modified'
        self.reviewed_at = timezone.now()
        if doctor_notes:
            self.doctor_notes = doctor_notes
        self.save()

    def mark_as_rejected(self, doctor_notes=None):
        """Mark proposal as rejected by doctor"""
        self.status = 'rejected'
        self.reviewed_at = timezone.now()
        if doctor_notes:
            self.doctor_notes = doctor_notes
        self.save()


class DoctorTreatmentPlan(models.Model):
    """
    Doctor's final treatment plan for patient
    This is what patients can see - the official treatment plan written by the doctor
    """
    plan_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(
        'Patient',
        on_delete=models.CASCADE,
        related_name='treatment_plans',
        help_text='Patient receiving the treatment plan'
    )
    provider = models.ForeignKey(
        'Provider',
        on_delete=models.SET_NULL,
        null=True,
        related_name='treatment_plans_created',
        help_text='Doctor who created the treatment plan'
    )
    encounter = models.ForeignKey(
        'Encounter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='treatment_plans',
        help_text='Related encounter/visit'
    )

    # Link to AI proposal (if doctor used it)
    ai_proposal = models.ForeignKey(
        'AIProposedTreatmentPlan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctor_treatment_plans',
        help_text='AI proposal that influenced this plan (if any)'
    )

    # Treatment plan content
    plan_title = models.CharField(
        max_length=255,
        help_text='Title/summary of treatment plan'
    )
    chief_complaint = models.TextField(
        blank=True,
        null=True,
        help_text='Primary complaint being addressed'
    )
    assessment = models.TextField(
        help_text="Doctor's clinical assessment"
    )
    treatment_goals = models.TextField(
        help_text='Goals of the treatment plan'
    )
    medications = models.TextField(
        blank=True,
        null=True,
        help_text='Prescribed medications with dosage and instructions'
    )
    procedures = models.TextField(
        blank=True,
        null=True,
        help_text='Recommended procedures or interventions'
    )
    lifestyle_modifications = models.TextField(
        blank=True,
        null=True,
        help_text='Lifestyle changes recommended'
    )
    dietary_recommendations = models.TextField(
        blank=True,
        null=True,
        help_text='Diet and nutrition recommendations'
    )
    exercise_recommendations = models.TextField(
        blank=True,
        null=True,
        help_text='Exercise and physical activity recommendations'
    )
    follow_up_instructions = models.TextField(
        help_text='Follow-up care instructions'
    )
    warning_signs = models.TextField(
        blank=True,
        null=True,
        help_text='Warning signs to watch for'
    )
    emergency_instructions = models.TextField(
        blank=True,
        null=True,
        help_text='When to seek emergency care'
    )
    additional_notes = models.TextField(
        blank=True,
        null=True,
        help_text='Any additional notes or instructions'
    )

    # Status and visibility
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('superseded', 'Superseded by Newer Plan'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text='Status of treatment plan'
    )
    is_visible_to_patient = models.BooleanField(
        default=False,
        help_text='Whether patient can view this plan'
    )

    # Dates
    plan_start_date = models.DateField(
        default=timezone.now,
        help_text='Start date of treatment plan'
    )
    plan_end_date = models.DateField(
        null=True,
        blank=True,
        help_text='Expected end date of treatment plan'
    )
    next_review_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date for next review of plan'
    )

    # Patient acknowledgment
    patient_viewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When patient first viewed the plan'
    )
    patient_acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When patient acknowledged understanding'
    )
    patient_feedback = models.TextField(
        blank=True,
        null=True,
        help_text='Patient feedback or questions'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'doctor_treatment_plans'
        verbose_name = "Doctor's Treatment Plan"
        verbose_name_plural = "Doctor's Treatment Plans"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', '-created_at'], name='idx_treatment_plan_patient'),
            models.Index(fields=['provider', '-created_at'], name='idx_treatment_plan_provider'),
            models.Index(fields=['status'], name='idx_treatment_plan_status'),
            models.Index(fields=['is_visible_to_patient'], name='idx_treatment_plan_visible'),
        ]

    def __str__(self):
        return f"{self.plan_title} - {self.patient.full_name}"

    def publish_to_patient(self):
        """Make the treatment plan visible to patient"""
        self.is_visible_to_patient = True
        self.status = 'active'
        self.save()

    def mark_patient_viewed(self):
        """Record when patient first viewed the plan"""
        if not self.patient_viewed_at:
            self.patient_viewed_at = timezone.now()
            self.save()

    def mark_patient_acknowledged(self):
        """Record when patient acknowledged the plan"""
        if not self.patient_acknowledged_at:
            self.patient_acknowledged_at = timezone.now()
            self.save()

    def supersede(self):
        """Mark this plan as superseded by a newer one"""
        self.status = 'superseded'
        self.save()

    def is_current(self):
        """Check if plan is currently active"""
        return self.status == 'active' and self.is_visible_to_patient

    def get_duration_days(self):
        """Calculate duration of treatment plan"""
        if self.plan_end_date:
            return (self.plan_end_date - self.plan_start_date).days
        return None
