from django.db import models
from django.utils import timezone


class Patient(models.Model):
    """Patient model representing patient demographic information"""
    patient_id = models.AutoField(primary_key=True)
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


class Department(models.Model):
    """Department model"""
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=200)
    location = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'departments'
        ordering = ['department_name']

    def __str__(self):
        return self.department_name


class Provider(models.Model):
    """Provider/Physician model"""
    provider_id = models.AutoField(primary_key=True)
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
        return f"Encounter {self.encounter_id} - {self.patient.full_name} on {self.encounter_date.strftime('%Y-%m-d')}"


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
    weight_value = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    weight_unit = models.CharField(max_length=3, choices=[('lbs', 'Pounds'), ('kg', 'Kilograms')], blank=True, null=True)
    height_value = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    height_unit = models.CharField(max_length=2, choices=[('in', 'Inches'), ('cm', 'Centimeters')], blank=True, null=True)
    bmi = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    recorded_by = models.IntegerField(blank=True, null=True)  # Provider ID
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
    diagnosed_by = models.IntegerField(blank=True, null=True)  # Provider ID
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
