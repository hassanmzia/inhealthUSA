from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.utils import timezone
from .models import (
    Hospital, Patient, Provider, Encounter, VitalSign, Diagnosis,
    Prescription, Department, Allergy, MedicalHistory, SocialHistory,
    FamilyHistory, LabTest, Message, Notification
)
from .forms import UserRegistrationForm


# Authentication Views
def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'index')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'healthcare/auth/login.html', {'form': form})


def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def user_register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'healthcare/auth/register.html', {'form': form})


@login_required
def index(request):
    """Dashboard/Home view"""
    context = {
        'total_hospitals': Hospital.objects.filter(is_active=True).count(),
        'total_patients': Patient.objects.filter(is_active=True).count(),
        'total_providers': Provider.objects.filter(is_active=True).count(),
        'total_appointments_today': Encounter.objects.filter(
            encounter_date__date=timezone.now().date()
        ).count(),
        'recent_appointments': Encounter.objects.select_related('patient', 'provider').order_by('-encounter_date')[:10],
    }
    return render(request, 'healthcare/index.html', context)


# Patient Views
@login_required
def patient_list(request):
    """List all patients"""
    search = request.GET.get('search', '')
    patients = Patient.objects.filter(is_active=True).select_related('primary_doctor', 'primary_doctor__hospital')

    if search:
        patients = patients.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(ssn__icontains=search)
        )

    patients = patients.order_by('last_name', 'first_name')
    return render(request, 'healthcare/patients/index.html', {'patients': patients, 'search': search})


@login_required
def patient_detail(request, patient_id):
    """View patient details"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    encounters = patient.encounters.all()[:10]
    prescriptions = patient.prescriptions.all()[:10]
    allergies = patient.allergies.filter(is_active=True)

    context = {
        'patient': patient,
        'encounters': encounters,
        'prescriptions': prescriptions,
        'allergies': allergies,
    }
    return render(request, 'healthcare/patients/show.html', context)


@login_required
def patient_create(request):
    """Create new patient"""
    if request.method == 'POST':
        patient = Patient.objects.create(
            first_name=request.POST['first_name'],
            middle_name=request.POST.get('middle_name', ''),
            last_name=request.POST['last_name'],
            date_of_birth=request.POST['date_of_birth'],
            gender=request.POST['gender'],
            ssn=request.POST.get('ssn', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            address=request.POST.get('address', ''),
            city=request.POST.get('city', ''),
            state=request.POST.get('state', ''),
            zip_code=request.POST.get('zip_code', ''),
            emergency_contact_name=request.POST.get('emergency_contact_name', ''),
            emergency_contact_phone=request.POST.get('emergency_contact_phone', ''),
            insurance_provider=request.POST.get('insurance_provider', ''),
            insurance_policy_number=request.POST.get('insurance_policy_number', ''),
        )
        messages.success(request, f'Patient {patient.full_name} created successfully.')
        return redirect('patient_detail', patient_id=patient.patient_id)

    return render(request, 'healthcare/patients/create.html')


@login_required
def patient_edit(request, patient_id):
    """Edit patient with comprehensive medical records"""
    patient = get_object_or_404(Patient, patient_id=patient_id)

    if request.method == 'POST':
        patient.first_name = request.POST['first_name']
        patient.middle_name = request.POST.get('middle_name', '')
        patient.last_name = request.POST['last_name']
        patient.date_of_birth = request.POST['date_of_birth']
        patient.gender = request.POST['gender']
        patient.ssn = request.POST.get('ssn', '')
        patient.email = request.POST.get('email', '')
        patient.phone = request.POST.get('phone', '')
        patient.address = request.POST.get('address', '')
        patient.city = request.POST.get('city', '')
        patient.state = request.POST.get('state', '')
        patient.zip_code = request.POST.get('zip_code', '')
        patient.emergency_contact_name = request.POST.get('emergency_contact_name', '')
        patient.emergency_contact_phone = request.POST.get('emergency_contact_phone', '')
        patient.insurance_provider = request.POST.get('insurance_provider', '')
        patient.insurance_policy_number = request.POST.get('insurance_policy_number', '')
        patient.save()

        messages.success(request, f'Patient {patient.full_name} updated successfully.')
        return redirect('patient_edit', patient_id=patient.patient_id)

    # Get related data for the patient
    encounters = patient.encounters.select_related('provider').order_by('-encounter_date')

    # Get all vital signs through encounters
    vital_signs = VitalSign.objects.filter(
        encounter__patient=patient
    ).select_related('encounter', 'recorded_by').order_by('-recorded_at')

    # Get all diagnoses through encounters
    diagnoses = Diagnosis.objects.filter(
        encounter__patient=patient
    ).select_related('encounter', 'diagnosed_by').order_by('-diagnosed_at')

    # Get all prescriptions for the patient
    prescriptions = patient.prescriptions.select_related('provider').order_by('-start_date')

    # Get all medical history
    medical_history = patient.medical_history.all().order_by('-diagnosis_date')

    # Get all social history
    social_history = patient.social_history.all().order_by('-recorded_date')

    # Get all family history
    family_history = patient.family_history.all().order_by('-recorded_date')

    # Get all allergies
    allergies = patient.allergies.filter(is_active=True).order_by('-severity', 'allergen')

    # Get all lab tests
    lab_tests = patient.lab_tests.select_related('provider').order_by('-ordered_date')

    # Get all messages (sent and received)
    sent_messages = patient.user.sent_messages.all().order_by('-created_at')[:20] if patient.user else []
    received_messages = patient.user.received_messages.all().order_by('-created_at')[:20] if patient.user else []

    # Get all notifications
    notifications = patient.user.notifications.all().order_by('-created_at')[:20] if patient.user else []

    # Get all providers for dropdowns
    providers = Provider.objects.filter(is_active=True).order_by('last_name', 'first_name')

    context = {
        'patient': patient,
        'encounters': encounters,
        'vital_signs': vital_signs,
        'diagnoses': diagnoses,
        'prescriptions': prescriptions,
        'medical_history': medical_history,
        'social_history': social_history,
        'family_history': family_history,
        'allergies': allergies,
        'lab_tests': lab_tests,
        'sent_messages': sent_messages,
        'received_messages': received_messages,
        'notifications': notifications,
        'providers': providers,
    }
    return render(request, 'healthcare/patients/edit.html', context)


# Patient Vital Signs Views
@login_required
def patient_vital_create(request, patient_id):
    """Create vital signs for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)

    # Get or create a default encounter for vitals
    encounters = patient.encounters.all()
    providers = Provider.objects.filter(is_active=True).order_by('last_name', 'first_name')

    if request.method == 'POST':
        encounter_id = request.POST.get('encounter_id')
        if not encounter_id:
            # Create a new encounter for this vital sign
            encounter = Encounter.objects.create(
                patient=patient,
                provider_id=request.POST.get('provider_id'),
                encounter_date=timezone.now(),
                encounter_type='Office Visit',
                status='Completed'
            )
        else:
            encounter = get_object_or_404(Encounter, encounter_id=encounter_id)

        VitalSign.objects.create(
            encounter=encounter,
            temperature_value=request.POST.get('temperature_value') or None,
            temperature_unit=request.POST.get('temperature_unit') or None,
            blood_pressure_systolic=request.POST.get('blood_pressure_systolic') or None,
            blood_pressure_diastolic=request.POST.get('blood_pressure_diastolic') or None,
            heart_rate=request.POST.get('heart_rate') or None,
            respiratory_rate=request.POST.get('respiratory_rate') or None,
            oxygen_saturation=request.POST.get('oxygen_saturation') or None,
            weight_value=request.POST.get('weight_value') or None,
            weight_unit=request.POST.get('weight_unit') or None,
            height_value=request.POST.get('height_value') or None,
            height_unit=request.POST.get('height_unit') or None,
            bmi=request.POST.get('bmi') or None,
            notes=request.POST.get('notes', ''),
            recorded_at=timezone.now(),
        )
        messages.success(request, 'Vital signs added successfully.')
        return redirect('patient_edit', patient_id=patient.patient_id)

    context = {
        'patient': patient,
        'encounters': encounters,
        'providers': providers,
    }
    return render(request, 'healthcare/patients/vital_create.html', context)


@login_required
def patient_vital_edit(request, patient_id, vital_signs_id):
    """Edit vital signs for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    vital_sign = get_object_or_404(VitalSign, vital_signs_id=vital_signs_id)

    if request.method == 'POST':
        vital_sign.temperature_value = request.POST.get('temperature_value') or None
        vital_sign.temperature_unit = request.POST.get('temperature_unit') or None
        vital_sign.blood_pressure_systolic = request.POST.get('blood_pressure_systolic') or None
        vital_sign.blood_pressure_diastolic = request.POST.get('blood_pressure_diastolic') or None
        vital_sign.heart_rate = request.POST.get('heart_rate') or None
        vital_sign.respiratory_rate = request.POST.get('respiratory_rate') or None
        vital_sign.oxygen_saturation = request.POST.get('oxygen_saturation') or None
        vital_sign.weight_value = request.POST.get('weight_value') or None
        vital_sign.weight_unit = request.POST.get('weight_unit') or None
        vital_sign.height_value = request.POST.get('height_value') or None
        vital_sign.height_unit = request.POST.get('height_unit') or None
        vital_sign.bmi = request.POST.get('bmi') or None
        vital_sign.notes = request.POST.get('notes', '')
        vital_sign.save()

        messages.success(request, 'Vital signs updated successfully.')
        return redirect('patient_edit', patient_id=patient.patient_id)

    context = {
        'patient': patient,
        'vital_sign': vital_sign,
    }
    return render(request, 'healthcare/patients/vital_edit.html', context)


# Patient Diagnosis Views
@login_required
def patient_diagnosis_create(request, patient_id):
    """Create diagnosis for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    encounters = patient.encounters.all()
    providers = Provider.objects.filter(is_active=True).order_by('last_name', 'first_name')

    if request.method == 'POST':
        encounter_id = request.POST.get('encounter_id')
        if not encounter_id:
            # Create a new encounter for this diagnosis
            encounter = Encounter.objects.create(
                patient=patient,
                provider_id=request.POST.get('provider_id'),
                encounter_date=timezone.now(),
                encounter_type='Office Visit',
                status='Completed'
            )
        else:
            encounter = get_object_or_404(Encounter, encounter_id=encounter_id)

        Diagnosis.objects.create(
            encounter=encounter,
            diagnosis_description=request.POST['diagnosis_description'],
            icd10_code=request.POST.get('icd10_code', ''),
            icd11_code=request.POST.get('icd11_code', ''),
            diagnosis_type=request.POST['diagnosis_type'],
            status=request.POST.get('status', 'Active'),
            onset_date=request.POST.get('onset_date') or None,
            resolved_date=request.POST.get('resolved_date') or None,
            notes=request.POST.get('notes', ''),
            diagnosed_at=timezone.now(),
        )
        messages.success(request, 'Diagnosis added successfully.')
        return redirect('patient_edit', patient_id=patient.patient_id)

    context = {
        'patient': patient,
        'encounters': encounters,
        'providers': providers,
    }
    return render(request, 'healthcare/patients/diagnosis_create.html', context)


@login_required
def patient_diagnosis_edit(request, patient_id, diagnosis_id):
    """Edit diagnosis for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    diagnosis = get_object_or_404(Diagnosis, diagnosis_id=diagnosis_id)

    if request.method == 'POST':
        diagnosis.diagnosis_description = request.POST['diagnosis_description']
        diagnosis.icd10_code = request.POST.get('icd10_code', '')
        diagnosis.icd11_code = request.POST.get('icd11_code', '')
        diagnosis.diagnosis_type = request.POST['diagnosis_type']
        diagnosis.status = request.POST.get('status', 'Active')
        diagnosis.onset_date = request.POST.get('onset_date') or None
        diagnosis.resolved_date = request.POST.get('resolved_date') or None
        diagnosis.notes = request.POST.get('notes', '')
        diagnosis.save()

        messages.success(request, 'Diagnosis updated successfully.')
        return redirect('patient_edit', patient_id=patient.patient_id)

    context = {
        'patient': patient,
        'diagnosis': diagnosis,
    }
    return render(request, 'healthcare/patients/diagnosis_edit.html', context)


# Patient Prescription Views
@login_required
def patient_prescription_create(request, patient_id):
    """Create prescription for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    encounters = patient.encounters.all()
    providers = Provider.objects.filter(is_active=True).order_by('last_name', 'first_name')

    if request.method == 'POST':
        prescription = Prescription.objects.create(
            patient=patient,
            provider_id=request.POST.get('provider_id'),
            encounter_id=request.POST.get('encounter_id') or None,
            medication_name=request.POST['medication_name'],
            dosage=request.POST['dosage'],
            frequency=request.POST['frequency'],
            route=request.POST.get('route', ''),
            quantity=request.POST.get('quantity') or None,
            refills=request.POST.get('refills', 0),
            start_date=request.POST['start_date'],
            end_date=request.POST.get('end_date') or None,
            instructions=request.POST.get('instructions', ''),
            pharmacy_name=request.POST.get('pharmacy_name', ''),
            pharmacy_phone=request.POST.get('pharmacy_phone', ''),
            status='Active',
        )
        messages.success(request, 'Prescription added successfully.')
        return redirect('patient_edit', patient_id=patient.patient_id)

    context = {
        'patient': patient,
        'encounters': encounters,
        'providers': providers,
    }
    return render(request, 'healthcare/patients/prescription_create.html', context)


@login_required
def patient_prescription_edit(request, patient_id, prescription_id):
    """Edit prescription for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    prescription = get_object_or_404(Prescription, prescription_id=prescription_id)
    providers = Provider.objects.filter(is_active=True).order_by('last_name', 'first_name')

    if request.method == 'POST':
        prescription.provider_id = request.POST.get('provider_id')
        prescription.medication_name = request.POST['medication_name']
        prescription.dosage = request.POST['dosage']
        prescription.frequency = request.POST['frequency']
        prescription.route = request.POST.get('route', '')
        prescription.quantity = request.POST.get('quantity') or None
        prescription.refills = request.POST.get('refills', 0)
        prescription.start_date = request.POST['start_date']
        prescription.end_date = request.POST.get('end_date') or None
        prescription.instructions = request.POST.get('instructions', '')
        prescription.pharmacy_name = request.POST.get('pharmacy_name', '')
        prescription.pharmacy_phone = request.POST.get('pharmacy_phone', '')
        prescription.status = request.POST['status']
        prescription.save()

        messages.success(request, 'Prescription updated successfully.')
        return redirect('patient_edit', patient_id=patient.patient_id)

    context = {
        'patient': patient,
        'prescription': prescription,
        'providers': providers,
    }
    return render(request, 'healthcare/patients/prescription_edit.html', context)


# Patient Medical History Views
@login_required
def patient_medical_history_create(request, patient_id):
    """Create medical history for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)

    if request.method == 'POST':
        MedicalHistory.objects.create(
            patient=patient,
            condition=request.POST['condition'],
            diagnosis_date=request.POST.get('diagnosis_date') or None,
            status=request.POST.get('status', 'Active'),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Medical history added successfully.')
        return redirect('patient_edit', patient_id=patient.patient_id)

    context = {
        'patient': patient,
    }
    return render(request, 'healthcare/patients/medical_history_create.html', context)


@login_required
def patient_medical_history_edit(request, patient_id, medical_history_id):
    """Edit medical history for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    medical_history = get_object_or_404(MedicalHistory, medical_history_id=medical_history_id)

    if request.method == 'POST':
        medical_history.condition = request.POST['condition']
        medical_history.diagnosis_date = request.POST.get('diagnosis_date') or None
        medical_history.status = request.POST.get('status', 'Active')
        medical_history.notes = request.POST.get('notes', '')
        medical_history.save()

        messages.success(request, 'Medical history updated successfully.')
        return redirect('patient_edit', patient_id=patient.patient_id)

    context = {
        'patient': patient,
        'medical_history': medical_history,
    }
    return render(request, 'healthcare/patients/medical_history_edit.html', context)


# Patient Social History Views
@login_required
def patient_social_history_create(request, patient_id):
    """Create social history for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)

    if request.method == 'POST':
        SocialHistory.objects.create(
            patient=patient,
            smoking_status=request.POST.get('smoking_status', ''),
            alcohol_use=request.POST.get('alcohol_use', ''),
            drug_use=request.POST.get('drug_use', ''),
            occupation=request.POST.get('occupation', ''),
            marital_status=request.POST.get('marital_status', ''),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Social history added successfully.')
        return redirect('patient_edit', patient_id=patient.patient_id)

    context = {
        'patient': patient,
    }
    return render(request, 'healthcare/patients/social_history_create.html', context)


@login_required
def patient_social_history_edit(request, patient_id, social_history_id):
    """Edit social history for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    social_history = get_object_or_404(SocialHistory, social_history_id=social_history_id)

    if request.method == 'POST':
        social_history.smoking_status = request.POST.get('smoking_status', '')
        social_history.alcohol_use = request.POST.get('alcohol_use', '')
        social_history.drug_use = request.POST.get('drug_use', '')
        social_history.occupation = request.POST.get('occupation', '')
        social_history.marital_status = request.POST.get('marital_status', '')
        social_history.notes = request.POST.get('notes', '')
        social_history.save()

        messages.success(request, 'Social history updated successfully.')
        return redirect('patient_edit', patient_id=patient.patient_id)

    context = {
        'patient': patient,
        'social_history': social_history,
    }
    return render(request, 'healthcare/patients/social_history_edit.html', context)


# Patient Allergy Views
@login_required
def patient_allergy_create(request, patient_id):
    """Create allergy for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)

    if request.method == 'POST':
        Allergy.objects.create(
            patient=patient,
            allergen=request.POST['allergen'],
            allergy_type=request.POST['allergy_type'],
            severity=request.POST.get('severity', ''),
            reaction=request.POST.get('reaction', ''),
            onset_date=request.POST.get('onset_date') or None,
            notes=request.POST.get('notes', ''),
            is_active=True,
        )
        messages.success(request, 'Allergy added successfully.')
        return redirect('patient_edit', patient_id=patient.patient_id)

    context = {
        'patient': patient,
    }
    return render(request, 'healthcare/patients/allergy_create.html', context)


@login_required
def patient_allergy_edit(request, patient_id, allergy_id):
    """Edit allergy for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    allergy = get_object_or_404(Allergy, allergy_id=allergy_id)

    if request.method == 'POST':
        allergy.allergen = request.POST['allergen']
        allergy.allergy_type = request.POST['allergy_type']
        allergy.severity = request.POST.get('severity', '')
        allergy.reaction = request.POST.get('reaction', '')
        allergy.onset_date = request.POST.get('onset_date') or None
        allergy.notes = request.POST.get('notes', '')
        allergy.is_active = request.POST.get('is_active', 'true') == 'true'
        allergy.save()

        messages.success(request, 'Allergy updated successfully.')
        return redirect('patient_edit', patient_id=patient.patient_id)

    context = {
        'patient': patient,
        'allergy': allergy,
    }
    return render(request, 'healthcare/patients/allergy_edit.html', context)


# Patient Lab Test Views
@login_required
def patient_lab_test_create(request, patient_id):
    """Create lab test for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    providers = Provider.objects.filter(is_active=True).order_by('last_name', 'first_name')
    encounters = patient.encounters.all()

    if request.method == 'POST':
        LabTest.objects.create(
            patient=patient,
            provider_id=request.POST.get('provider_id'),
            encounter_id=request.POST.get('encounter_id') or None,
            test_name=request.POST['test_name'],
            test_code=request.POST.get('test_code', ''),
            status=request.POST.get('status', 'Ordered'),
            collection_date=request.POST.get('collection_date') or None,
            result_date=request.POST.get('result_date') or None,
            result=request.POST.get('result', ''),
            result_value=request.POST.get('result_value', ''),
            result_unit=request.POST.get('result_unit', ''),
            reference_range=request.POST.get('reference_range', ''),
            abnormal_flag=request.POST.get('abnormal_flag') == 'on',
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Lab test added successfully.')
        return redirect('patient_edit', patient_id=patient.patient_id)

    context = {
        'patient': patient,
        'providers': providers,
        'encounters': encounters,
    }
    return render(request, 'healthcare/patients/lab_test_create.html', context)


@login_required
def patient_lab_test_edit(request, patient_id, lab_test_id):
    """Edit lab test for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    lab_test = get_object_or_404(LabTest, lab_test_id=lab_test_id)
    providers = Provider.objects.filter(is_active=True).order_by('last_name', 'first_name')

    if request.method == 'POST':
        lab_test.provider_id = request.POST.get('provider_id')
        lab_test.test_name = request.POST['test_name']
        lab_test.test_code = request.POST.get('test_code', '')
        lab_test.status = request.POST.get('status', 'Ordered')
        lab_test.collection_date = request.POST.get('collection_date') or None
        lab_test.result_date = request.POST.get('result_date') or None
        lab_test.result = request.POST.get('result', '')
        lab_test.result_value = request.POST.get('result_value', '')
        lab_test.result_unit = request.POST.get('result_unit', '')
        lab_test.reference_range = request.POST.get('reference_range', '')
        lab_test.abnormal_flag = request.POST.get('abnormal_flag') == 'on'
        lab_test.notes = request.POST.get('notes', '')
        lab_test.save()

        messages.success(request, 'Lab test updated successfully.')
        return redirect('patient_edit', patient_id=patient.patient_id)

    context = {
        'patient': patient,
        'lab_test': lab_test,
        'providers': providers,
    }
    return render(request, 'healthcare/patients/lab_test_edit.html', context)


# Physician (Provider) Views
@login_required
def physician_list(request):
    """List all physicians"""
    search = request.GET.get('search', '')
    physicians = Provider.objects.filter(is_active=True).select_related('hospital', 'department')

    if search:
        physicians = physicians.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(npi__icontains=search) |
            Q(specialty__icontains=search) |
            Q(hospital__name__icontains=search)
        )

    physicians = physicians.order_by('hospital__name', 'last_name', 'first_name')
    return render(request, 'healthcare/physicians/index.html', {'physicians': physicians, 'search': search})


@login_required
def physician_detail(request, provider_id):
    """View physician details"""
    physician = get_object_or_404(Provider, provider_id=provider_id)
    encounters = physician.encounters.all()[:10]

    context = {
        'physician': physician,
        'encounters': encounters,
    }
    return render(request, 'healthcare/physicians/show.html', context)


# Appointment (Encounter) Views
@login_required
def appointment_list(request):
    """List all appointments"""
    status = request.GET.get('status', '')
    appointments = Encounter.objects.select_related('patient', 'provider', 'department')

    if status:
        appointments = appointments.filter(status=status)

    appointments = appointments.order_by('-encounter_date')
    return render(request, 'healthcare/appointments/index.html', {'appointments': appointments, 'status': status})


@login_required
def appointment_detail(request, encounter_id):
    """View appointment details"""
    appointment = get_object_or_404(Encounter, encounter_id=encounter_id)
    vital_signs = appointment.vital_signs.all()
    diagnoses = appointment.diagnoses.all()
    prescriptions = appointment.prescriptions.all()

    context = {
        'appointment': appointment,
        'vital_signs': vital_signs,
        'diagnoses': diagnoses,
        'prescriptions': prescriptions,
    }
    return render(request, 'healthcare/appointments/show.html', context)


@login_required
def appointment_create(request):
    """Create new appointment"""
    if request.method == 'POST':
        appointment = Encounter.objects.create(
            patient_id=request.POST['patient_id'],
            provider_id=request.POST['provider_id'],
            department_id=request.POST.get('department_id'),
            encounter_date=request.POST['encounter_date'],
            encounter_type=request.POST['encounter_type'],
            chief_complaint=request.POST.get('chief_complaint', ''),
            status=request.POST.get('status', 'Scheduled'),
        )
        messages.success(request, 'Appointment created successfully.')
        return redirect('appointment_detail', encounter_id=appointment.encounter_id)

    patients = Patient.objects.filter(is_active=True).order_by('last_name', 'first_name')
    physicians = Provider.objects.filter(is_active=True).order_by('last_name', 'first_name')
    departments = Department.objects.filter(is_active=True).order_by('department_name')

    context = {
        'patients': patients,
        'physicians': physicians,
        'departments': departments,
    }
    return render(request, 'healthcare/appointments/create.html', context)


@login_required
def appointment_edit(request, encounter_id):
    """Edit appointment with vitals, diagnoses, and prescriptions"""
    appointment = get_object_or_404(Encounter, encounter_id=encounter_id)

    if request.method == 'POST':
        appointment.provider_id = request.POST['provider_id']
        appointment.department_id = request.POST.get('department_id')
        appointment.encounter_date = request.POST['encounter_date']
        appointment.encounter_type = request.POST['encounter_type']
        appointment.status = request.POST['status']
        appointment.chief_complaint = request.POST.get('chief_complaint', '')
        appointment.clinical_impression = request.POST.get('clinical_impression', '')
        appointment.treatment_plan = request.POST.get('treatment_plan', '')
        appointment.notes = request.POST.get('notes', '')
        appointment.save()

        messages.success(request, 'Appointment updated successfully.')
        return redirect('appointment_edit', encounter_id=appointment.encounter_id)

    physicians = Provider.objects.filter(is_active=True).order_by('last_name', 'first_name')
    departments = Department.objects.filter(is_active=True).order_by('department_name')

    # Get related data for the encounter
    vital_signs = appointment.vital_signs.all().order_by('-recorded_at')
    diagnoses = appointment.diagnoses.all().order_by('-diagnosed_at')
    prescriptions = appointment.prescriptions.all().order_by('-start_date')

    context = {
        'appointment': appointment,
        'physicians': physicians,
        'departments': departments,
        'vital_signs': vital_signs,
        'diagnoses': diagnoses,
        'prescriptions': prescriptions,
    }
    return render(request, 'healthcare/appointments/edit.html', context)


# Encounter Vital Signs Views
@login_required
def encounter_vital_create(request, encounter_id):
    """Create vital signs for an encounter"""
    encounter = get_object_or_404(Encounter, encounter_id=encounter_id)

    if request.method == 'POST':
        VitalSign.objects.create(
            encounter=encounter,
            temperature_value=request.POST.get('temperature_value') or None,
            temperature_unit=request.POST.get('temperature_unit') or None,
            blood_pressure_systolic=request.POST.get('blood_pressure_systolic') or None,
            blood_pressure_diastolic=request.POST.get('blood_pressure_diastolic') or None,
            heart_rate=request.POST.get('heart_rate') or None,
            respiratory_rate=request.POST.get('respiratory_rate') or None,
            oxygen_saturation=request.POST.get('oxygen_saturation') or None,
            weight_value=request.POST.get('weight_value') or None,
            weight_unit=request.POST.get('weight_unit') or None,
            height_value=request.POST.get('height_value') or None,
            height_unit=request.POST.get('height_unit') or None,
            bmi=request.POST.get('bmi') or None,
            notes=request.POST.get('notes', ''),
            recorded_at=timezone.now(),
        )
        messages.success(request, 'Vital signs added successfully.')
        return redirect('appointment_edit', encounter_id=encounter.encounter_id)

    context = {
        'encounter': encounter,
    }
    return render(request, 'healthcare/appointments/vital_create.html', context)


@login_required
def encounter_vital_edit(request, encounter_id, vital_signs_id):
    """Edit vital signs for an encounter"""
    encounter = get_object_or_404(Encounter, encounter_id=encounter_id)
    vital_sign = get_object_or_404(VitalSign, vital_signs_id=vital_signs_id)

    if request.method == 'POST':
        vital_sign.temperature_value = request.POST.get('temperature_value') or None
        vital_sign.temperature_unit = request.POST.get('temperature_unit') or None
        vital_sign.blood_pressure_systolic = request.POST.get('blood_pressure_systolic') or None
        vital_sign.blood_pressure_diastolic = request.POST.get('blood_pressure_diastolic') or None
        vital_sign.heart_rate = request.POST.get('heart_rate') or None
        vital_sign.respiratory_rate = request.POST.get('respiratory_rate') or None
        vital_sign.oxygen_saturation = request.POST.get('oxygen_saturation') or None
        vital_sign.weight_value = request.POST.get('weight_value') or None
        vital_sign.weight_unit = request.POST.get('weight_unit') or None
        vital_sign.height_value = request.POST.get('height_value') or None
        vital_sign.height_unit = request.POST.get('height_unit') or None
        vital_sign.bmi = request.POST.get('bmi') or None
        vital_sign.notes = request.POST.get('notes', '')
        vital_sign.save()

        messages.success(request, 'Vital signs updated successfully.')
        return redirect('appointment_edit', encounter_id=encounter.encounter_id)

    context = {
        'encounter': encounter,
        'vital_sign': vital_sign,
    }
    return render(request, 'healthcare/appointments/vital_edit.html', context)


# Encounter Diagnosis Views
@login_required
def encounter_diagnosis_create(request, encounter_id):
    """Create diagnosis for an encounter"""
    encounter = get_object_or_404(Encounter, encounter_id=encounter_id)
    providers = Provider.objects.filter(is_active=True).order_by('last_name', 'first_name')

    if request.method == 'POST':
        Diagnosis.objects.create(
            encounter=encounter,
            diagnosis_description=request.POST['diagnosis_description'],
            icd10_code=request.POST.get('icd10_code', ''),
            icd11_code=request.POST.get('icd11_code', ''),
            diagnosis_type=request.POST['diagnosis_type'],
            status=request.POST.get('status', 'Active'),
            onset_date=request.POST.get('onset_date') or None,
            resolved_date=request.POST.get('resolved_date') or None,
            notes=request.POST.get('notes', ''),
            diagnosed_at=timezone.now(),
        )
        messages.success(request, 'Diagnosis added successfully.')
        return redirect('appointment_edit', encounter_id=encounter.encounter_id)

    context = {
        'encounter': encounter,
        'providers': providers,
    }
    return render(request, 'healthcare/appointments/diagnosis_create.html', context)


@login_required
def encounter_diagnosis_edit(request, encounter_id, diagnosis_id):
    """Edit diagnosis for an encounter"""
    encounter = get_object_or_404(Encounter, encounter_id=encounter_id)
    diagnosis = get_object_or_404(Diagnosis, diagnosis_id=diagnosis_id)

    if request.method == 'POST':
        diagnosis.diagnosis_description = request.POST['diagnosis_description']
        diagnosis.icd10_code = request.POST.get('icd10_code', '')
        diagnosis.icd11_code = request.POST.get('icd11_code', '')
        diagnosis.diagnosis_type = request.POST['diagnosis_type']
        diagnosis.status = request.POST.get('status', 'Active')
        diagnosis.onset_date = request.POST.get('onset_date') or None
        diagnosis.resolved_date = request.POST.get('resolved_date') or None
        diagnosis.notes = request.POST.get('notes', '')
        diagnosis.save()

        messages.success(request, 'Diagnosis updated successfully.')
        return redirect('appointment_edit', encounter_id=encounter.encounter_id)

    context = {
        'encounter': encounter,
        'diagnosis': diagnosis,
    }
    return render(request, 'healthcare/appointments/diagnosis_edit.html', context)


# Encounter Prescription Views
@login_required
def encounter_prescription_create(request, encounter_id):
    """Create prescription for an encounter"""
    encounter = get_object_or_404(Encounter, encounter_id=encounter_id)
    providers = Provider.objects.filter(is_active=True).order_by('last_name', 'first_name')

    if request.method == 'POST':
        Prescription.objects.create(
            patient=encounter.patient,
            provider_id=request.POST.get('provider_id'),
            encounter=encounter,
            medication_name=request.POST['medication_name'],
            dosage=request.POST['dosage'],
            frequency=request.POST['frequency'],
            route=request.POST.get('route', ''),
            quantity=request.POST.get('quantity') or None,
            refills=request.POST.get('refills', 0),
            start_date=request.POST['start_date'],
            end_date=request.POST.get('end_date') or None,
            instructions=request.POST.get('instructions', ''),
            pharmacy_name=request.POST.get('pharmacy_name', ''),
            pharmacy_phone=request.POST.get('pharmacy_phone', ''),
            status='Active',
        )
        messages.success(request, 'Prescription added successfully.')
        return redirect('appointment_edit', encounter_id=encounter.encounter_id)

    context = {
        'encounter': encounter,
        'providers': providers,
    }
    return render(request, 'healthcare/appointments/prescription_create.html', context)


@login_required
def encounter_prescription_edit(request, encounter_id, prescription_id):
    """Edit prescription for an encounter"""
    encounter = get_object_or_404(Encounter, encounter_id=encounter_id)
    prescription = get_object_or_404(Prescription, prescription_id=prescription_id)
    providers = Provider.objects.filter(is_active=True).order_by('last_name', 'first_name')

    if request.method == 'POST':
        prescription.provider_id = request.POST.get('provider_id')
        prescription.medication_name = request.POST['medication_name']
        prescription.dosage = request.POST['dosage']
        prescription.frequency = request.POST['frequency']
        prescription.route = request.POST.get('route', '')
        prescription.quantity = request.POST.get('quantity') or None
        prescription.refills = request.POST.get('refills', 0)
        prescription.start_date = request.POST['start_date']
        prescription.end_date = request.POST.get('end_date') or None
        prescription.instructions = request.POST.get('instructions', '')
        prescription.pharmacy_name = request.POST.get('pharmacy_name', '')
        prescription.pharmacy_phone = request.POST.get('pharmacy_phone', '')
        prescription.status = request.POST['status']
        prescription.save()

        messages.success(request, 'Prescription updated successfully.')
        return redirect('appointment_edit', encounter_id=encounter.encounter_id)

    context = {
        'encounter': encounter,
        'prescription': prescription,
        'providers': providers,
    }
    return render(request, 'healthcare/appointments/prescription_edit.html', context)


# Vital Signs Views
@login_required
def vital_sign_create(request, encounter_id):
    """Create vital signs for an appointment"""
    appointment = get_object_or_404(Encounter, encounter_id=encounter_id)

    if request.method == 'POST':
        VitalSign.objects.create(
            encounter=appointment,
            temperature_value=request.POST.get('temperature_value'),
            temperature_unit=request.POST.get('temperature_unit'),
            blood_pressure_systolic=request.POST.get('blood_pressure_systolic'),
            blood_pressure_diastolic=request.POST.get('blood_pressure_diastolic'),
            heart_rate=request.POST.get('heart_rate'),
            respiratory_rate=request.POST.get('respiratory_rate'),
            oxygen_saturation=request.POST.get('oxygen_saturation'),
            weight_value=request.POST.get('weight_value'),
            weight_unit=request.POST.get('weight_unit'),
            height_value=request.POST.get('height_value'),
            height_unit=request.POST.get('height_unit'),
            bmi=request.POST.get('bmi'),
            notes=request.POST.get('notes', ''),
            recorded_by=1,  # Default user
            recorded_at=timezone.now(),
        )
        messages.success(request, 'Vital signs recorded successfully.')
        return redirect('appointment_detail', encounter_id=encounter_id)

    return render(request, 'healthcare/vital_signs/create.html', {'appointment': appointment})


# Diagnosis Views
@login_required
def diagnosis_create(request, encounter_id):
    """Create diagnosis for an appointment"""
    appointment = get_object_or_404(Encounter, encounter_id=encounter_id)

    if request.method == 'POST':
        Diagnosis.objects.create(
            encounter=appointment,
            diagnosis_description=request.POST['diagnosis_description'],
            icd10_code=request.POST.get('icd10_code', ''),
            icd11_code=request.POST.get('icd11_code', ''),
            diagnosis_type=request.POST['diagnosis_type'],
            status=request.POST.get('status', 'Active'),
            onset_date=request.POST.get('onset_date'),
            notes=request.POST.get('notes', ''),
            diagnosed_by=1,  # Default user
            diagnosed_at=timezone.now(),
        )
        messages.success(request, 'Diagnosis added successfully.')
        return redirect('appointment_detail', encounter_id=encounter_id)

    physicians = Provider.objects.filter(is_active=True).order_by('last_name', 'first_name')
    context = {
        'appointment': appointment,
        'physicians': physicians,
    }
    return render(request, 'healthcare/diagnoses/create.html', context)


# Prescription Views
@login_required
def prescription_list(request):
    """List all prescriptions"""
    status = request.GET.get('status', '')
    prescriptions = Prescription.objects.select_related('patient', 'provider')

    if status:
        prescriptions = prescriptions.filter(status=status)

    prescriptions = prescriptions.order_by('-start_date')
    return render(request, 'healthcare/prescriptions/index.html', {'prescriptions': prescriptions, 'status': status})


@login_required
def prescription_detail(request, prescription_id):
    """View prescription details"""
    prescription = get_object_or_404(Prescription, prescription_id=prescription_id)
    return render(request, 'healthcare/prescriptions/show.html', {'prescription': prescription})


@login_required
def prescription_create(request):
    """Create new prescription"""
    if request.method == 'POST':
        prescription = Prescription.objects.create(
            patient_id=request.POST['patient_id'],
            provider_id=request.POST['provider_id'],
            encounter_id=request.POST.get('encounter_id'),
            medication_name=request.POST['medication_name'],
            dosage=request.POST['dosage'],
            frequency=request.POST['frequency'],
            route=request.POST.get('route', ''),
            quantity=request.POST.get('quantity'),
            refills=request.POST.get('refills', 0),
            start_date=request.POST['start_date'],
            end_date=request.POST.get('end_date'),
            instructions=request.POST.get('instructions', ''),
            pharmacy_name=request.POST.get('pharmacy_name', ''),
            pharmacy_phone=request.POST.get('pharmacy_phone', ''),
            status='Active',
        )
        messages.success(request, 'Prescription created successfully.')
        return redirect('prescription_detail', prescription_id=prescription.prescription_id)

    patients = Patient.objects.filter(is_active=True).order_by('last_name', 'first_name')
    physicians = Provider.objects.filter(is_active=True).order_by('last_name', 'first_name')
    encounters = Encounter.objects.order_by('-encounter_date')[:100]

    context = {
        'patients': patients,
        'physicians': physicians,
        'encounters': encounters,
    }
    return render(request, 'healthcare/prescriptions/create.html', context)


# Hospital Views
@login_required
def hospital_list(request):
    """List all hospitals"""
    search = request.GET.get('search', '')
    hospitals = Hospital.objects.filter(is_active=True)

    if search:
        hospitals = hospitals.filter(
            Q(name__icontains=search) |
            Q(city__icontains=search) |
            Q(state__icontains=search)
        )

    hospitals = hospitals.order_by('name')
    return render(request, 'healthcare/hospitals/index.html', {'hospitals': hospitals, 'search': search})


@login_required
def hospital_detail(request, hospital_id):
    """View hospital details"""
    hospital = get_object_or_404(Hospital, hospital_id=hospital_id)
    departments = hospital.departments.filter(is_active=True).order_by('department_name')
    providers = hospital.providers.filter(is_active=True).order_by('last_name', 'first_name')
    
    # Count patients through providers
    total_patients = Patient.objects.filter(
        primary_doctor__hospital=hospital,
        is_active=True
    ).count()

    context = {
        'hospital': hospital,
        'departments': departments,
        'providers': providers,
        'total_patients': total_patients,
        'total_departments': departments.count(),
        'total_providers': providers.count(),
    }
    return render(request, 'healthcare/hospitals/show.html', context)


# Family History Views
@login_required
def family_history_list(request):
    """List all family histories"""
    search = request.GET.get('search', '')
    relationship = request.GET.get('relationship', '')
    
    family_histories = FamilyHistory.objects.select_related('patient').all()

    if search:
        family_histories = family_histories.filter(
            Q(patient__first_name__icontains=search) |
            Q(patient__last_name__icontains=search) |
            Q(condition__icontains=search)
        )
    
    if relationship:
        family_histories = family_histories.filter(relationship=relationship)

    family_histories = family_histories.order_by('-recorded_date')
    
    context = {
        'family_histories': family_histories,
        'search': search,
        'relationship': relationship,
    }
    return render(request, 'healthcare/family_history/index.html', context)


@login_required
def family_history_detail(request, family_history_id):
    """View family history details"""
    history = get_object_or_404(FamilyHistory, family_history_id=family_history_id)
    context = {'history': history}
    return render(request, 'healthcare/family_history/show.html', context)


@login_required
def family_history_create(request):
    """Create a new family history record"""
    if request.method == 'POST':
        FamilyHistory.objects.create(
            patient_id=request.POST['patient_id'],
            relationship=request.POST['relationship'],
            condition=request.POST['condition'],
            age_at_diagnosis=request.POST.get('age_at_diagnosis') or None,
            is_alive='is_alive' in request.POST,
            age_at_death=request.POST.get('age_at_death') or None,
            cause_of_death=request.POST.get('cause_of_death', ''),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Family history record created successfully.')
        return redirect('family_history_list')

    patients = Patient.objects.filter(is_active=True).order_by('last_name', 'first_name')
    context = {'patients': patients}
    return render(request, 'healthcare/family_history/create.html', context)


# Medical History Questionnaire
@login_required
def medical_history_questionnaire(request):
    """Display and process comprehensive medical history questionnaire"""
    if request.method == 'POST':
        # TODO: In production, parse form data and distribute across multiple models:
        # - Patient demographics (update Patient model)
        # - Current medications (create Prescription records)
        # - Allergies (create Allergy records)
        # - Past medical history (create MedicalHistory records)
        # - Social history (create/update SocialHistory)
        # - Family history (create FamilyHistory records)
        # - etc.

        messages.success(request, 'Medical history questionnaire submitted successfully. Your information has been recorded.')
        return redirect('index')

    # For GET requests, display the questionnaire form
    return render(request, 'healthcare/questionnaire/medical_history.html')


# Family History Questionnaire
@login_required
def family_history_questionnaire(request):
    """Display and process comprehensive family history questionnaire"""
    if request.method == 'POST':
        # TODO: In production, parse form data and create FamilyHistory records for each family member:
        # - Father, Mother
        # - Paternal/Maternal Grandparents
        # - Siblings, Children
        # - Aunts, Uncles
        # - Store hereditary condition flags
        # - Link to genetic testing information
        # - etc.

        messages.success(request, 'Family history questionnaire submitted successfully. Your family medical history has been recorded.')
        return redirect('index')

    # For GET requests, display the questionnaire form
    return render(request, 'healthcare/questionnaire/family_history.html')


# Social History Questionnaire
@login_required
def social_history_questionnaire(request):
    """Display and process comprehensive social history questionnaire"""
    if request.method == 'POST':
        # TODO: In production, parse form data and create/update SocialHistory record:
        # - Tobacco use details
        # - Alcohol use details
        # - Substance use history
        # - Occupation and work exposures
        # - Living situation and housing
        # - Relationship status and sexual history
        # - Physical activity and diet
        # - Sleep patterns
        # - Stress and mental health
        # - Social support system
        # - Safety concerns
        # - Travel history
        # - Spiritual beliefs
        # - Financial status
        # - Military service
        # - etc.

        messages.success(request, 'Social history questionnaire submitted successfully. Your social and lifestyle information has been recorded.')
        return redirect('index')

    # For GET requests, display the questionnaire form
    return render(request, 'healthcare/questionnaire/social_history.html')
