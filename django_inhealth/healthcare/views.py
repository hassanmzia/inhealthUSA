from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q, Sum
from django.utils import timezone
from .models import (
    Hospital, Patient, Provider, Encounter, VitalSign, Diagnosis,
    Prescription, Department, Allergy, MedicalHistory, SocialHistory,
    FamilyHistory, LabTest, Message, Notification, InsuranceInformation,
    Billing, BillingItem, Payment, Device
)
from .forms import UserRegistrationForm
from .permissions import (
    require_patient_access, require_patient_edit, require_role,
    require_provider_access, require_provider_edit, require_vital_edit,
    is_patient, is_doctor, is_office_admin, is_nurse, get_patient_for_user,
    get_provider_for_user, can_view_patient, can_edit_patient,
    can_view_provider, can_edit_provider, can_edit_vitals
)


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
    """List all patients - filtered by role"""
    # If user is a patient, redirect them to their own profile
    if is_patient(request.user):
        user_patient = get_patient_for_user(request.user)
        if user_patient:
            return redirect('patient_detail', patient_id=user_patient.patient_id)
        else:
            # Auto-create patient profile if it doesn't exist
            try:
                user_profile = request.user.profile
                patient = Patient.objects.create(
                    user=request.user,
                    first_name=request.user.first_name or 'Unknown',
                    last_name=request.user.last_name or 'Unknown',
                    date_of_birth=user_profile.date_of_birth or '2000-01-01',
                    gender='Other',
                    email=request.user.email,
                )
                messages.success(request, 'Your patient profile has been created. Please update your information.')
                return redirect('patient_detail', patient_id=patient.patient_id)
            except Exception as e:
                messages.error(request, f'Error creating patient profile: {str(e)}. Please contact administration.')
                return redirect('index')

    # Only doctors, nurses, and admins can see the full patient list
    if not (is_doctor(request.user) or is_nurse(request.user) or is_office_admin(request.user)):
        messages.error(request, 'You do not have permission to view the patient list.')
        return redirect('index')

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
@require_patient_access
def patient_detail(request, patient_id):
    """View patient details - with role-based access control"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    encounters = patient.encounters.all()[:10]
    prescriptions = patient.prescriptions.all()[:10]
    allergies = patient.allergies.filter(is_active=True)

    # Determine user role and permissions
    if is_patient(request.user):
        user_role = 'patient'
    elif is_doctor(request.user):
        user_role = 'doctor'
    elif is_nurse(request.user):
        user_role = 'nurse'
    else:
        user_role = 'admin'

    can_edit = can_edit_patient(request.user, patient)

    context = {
        'patient': patient,
        'encounters': encounters,
        'prescriptions': prescriptions,
        'allergies': allergies,
        'user_role': user_role,
        'can_edit': can_edit,
    }
    return render(request, 'healthcare/patients/show.html', context)


@login_required
@require_role('doctor', 'office_admin')
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
@require_patient_edit
def patient_edit(request, patient_id):
    """Edit patient with comprehensive medical records - only doctors and admins"""
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
@require_vital_edit
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
@require_vital_edit
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
    """List all physicians - filtered by role"""
    # If user is a doctor, redirect them to their own profile
    if is_doctor(request.user):
        user_provider = get_provider_for_user(request.user)
        if user_provider:
            return redirect('physician_detail', provider_id=user_provider.provider_id)
        else:
            # Auto-create provider profile if it doesn't exist
            try:
                provider = Provider.objects.create(
                    user=request.user,
                    first_name=request.user.first_name or 'Unknown',
                    last_name=request.user.last_name or 'Unknown',
                    npi=f'TEMP{request.user.id:010d}',  # Temporary NPI
                    email=request.user.email,
                )
                messages.success(request, 'Your provider profile has been created. Please update your information and NPI.')
                return redirect('physician_detail', provider_id=provider.provider_id)
            except Exception as e:
                messages.error(request, f'Error creating provider profile: {str(e)}. Please contact administration.')
                return redirect('index')

    # Patients cannot view physician list
    if is_patient(request.user):
        messages.error(request, 'You do not have permission to view the physician list.')
        return redirect('index')

    # Only office admins and nurses can see the full physician list
    if not (is_office_admin(request.user) or is_nurse(request.user)):
        messages.error(request, 'You do not have permission to view the physician list.')
        return redirect('index')

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
@require_provider_access
def physician_detail(request, provider_id):
    """View physician details - with role-based access control"""
    physician = get_object_or_404(Provider, provider_id=provider_id)
    encounters = physician.encounters.all()[:10]

    # Determine user role and permissions
    if is_patient(request.user):
        user_role = 'patient'
    elif is_doctor(request.user):
        user_role = 'doctor'
    elif is_nurse(request.user):
        user_role = 'nurse'
    else:
        user_role = 'admin'

    can_edit = can_edit_provider(request.user, physician)

    context = {
        'physician': physician,
        'encounters': encounters,
        'user_role': user_role,
        'can_edit': can_edit,
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

    # Check if user can edit vitals for this patient
    if not can_edit_vitals(request.user, encounter.patient):
        messages.error(request, 'You do not have permission to edit vital information.')
        return redirect('appointment_detail', encounter_id=encounter.encounter_id)

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

    # Check if user can edit vitals for this patient
    if not can_edit_vitals(request.user, encounter.patient):
        messages.error(request, 'You do not have permission to edit vital information.')
        return redirect('appointment_detail', encounter_id=encounter.encounter_id)

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

    # Check if user can edit vitals for this patient
    if not can_edit_vitals(request.user, appointment.patient):
        messages.error(request, 'You do not have permission to edit vital information.')
        return redirect('appointment_detail', encounter_id=appointment.encounter_id)

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
        patient_id = request.POST['patient_id']
        FamilyHistory.objects.create(
            patient_id=patient_id,
            relationship=request.POST['relationship'],
            condition=request.POST['condition'],
            age_at_diagnosis=request.POST.get('age_at_diagnosis') or None,
            is_alive='is_alive' in request.POST,
            age_at_death=request.POST.get('age_at_death') or None,
            cause_of_death=request.POST.get('cause_of_death', ''),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Family history record created successfully.')
        # Redirect back to patient edit page if patient_id is in POST
        return redirect('patient_edit', patient_id=patient_id)

    # Get patient_id from query parameter if provided
    pre_selected_patient_id = request.GET.get('patient_id')
    patients = Patient.objects.filter(is_active=True).order_by('last_name', 'first_name')
    context = {
        'patients': patients,
        'pre_selected_patient_id': pre_selected_patient_id,
    }
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


# Allergies Questionnaire
@login_required
def allergies_questionnaire(request):
    """Display and process comprehensive allergies questionnaire"""
    if request.method == 'POST':
        # TODO: In production, parse form data and create Allergy records for each allergy:
        # - Drug/medication allergies with severity and reactions
        # - Food allergies with onset time and symptoms
        # - Environmental allergies with seasonal patterns
        # - Insect allergies
        # - Latex allergy
        # - Metal and chemical allergies
        # - Anaphylaxis history
        # - EpiPen information
        # - Allergy testing history
        # - Current allergy medications
        # - etc.

        messages.success(request, 'Allergies questionnaire submitted successfully. Your allergy information has been recorded.')
        return redirect('index')

    # For GET requests, display the questionnaire form
    return render(request, 'healthcare/questionnaire/allergies.html')


# Insurance Information
@login_required
def insurance_information(request):
    """Display and process comprehensive insurance information form"""
    if request.method == 'POST':
        # TODO: In production, parse form data and create/update Insurance records:
        # Primary Insurance:
        # - Carrier name, plan type, member ID, group number
        # - BIN, PCN, RxGrp numbers for prescription coverage
        # - Coverage dates (effective and termination)
        # - Subscriber information (name, DOB, SSN, relationship)
        # - Employer information
        # - Contact information (customer service, claims, pre-auth phones)
        # - Coverage types (medical, prescription, dental, vision, etc.)
        # - Copay amounts (PCP, specialist, ER, urgent care, inpatient, outpatient)
        # - Deductible information (individual, family, amounts met)
        # - Out-of-pocket maximums
        # - Coinsurance percentage
        # - Referral and prior authorization requirements
        # - PCP information
        # - Insurance card images (front and back)
        #
        # Secondary Insurance (if applicable):
        # - Same fields as primary
        #
        # Tertiary Insurance (if applicable):
        # - Same fields as primary
        #
        # Coordination of Benefits:
        # - COB rules (birthday rule, active/working, court order)
        # - COB notes
        #
        # Special Coverage:
        # - Medicare information (number, parts enrolled, effective dates)
        # - Medicaid information
        # - Workers' compensation (claim number, injury date, carrier, adjuster info)
        # - Auto insurance for accidents (carrier, policy, claim info)
        #
        # Additional:
        # - Financial responsibility acceptance
        # - Assignment of benefits authorization
        # - Release of information authorization
        # - Preferred contact method
        # - Additional notes
        # - Referral source
        # - etc.

        messages.success(request, 'Insurance information submitted successfully. Your insurance details have been recorded and will be used for billing purposes.')
        return redirect('index')

    # For GET requests, display the insurance information form
    return render(request, 'healthcare/insurance_information.html')


# Billing Information
@login_required
def billing_information(request):
    """Display and process comprehensive billing information form"""
    if request.method == 'POST':
        # TODO: In production, parse form data and create/update Billing records:
        # Billing Contact:
        # - Name, email, phone, address
        #
        # Guarantor Information:
        # - Name, relationship, DOB, SSN, contact information
        # - Address (if different from billing)
        # - Employment information
        # - Income range and dependents (for financial assistance)
        #
        # Payment Methods:
        # - Preferred payment method (credit card, bank account, check, cash)
        # - Credit/debit card details (encrypted):
        #   * Cardholder name, card number, expiry, CVV, billing ZIP
        # - Bank account details (encrypted):
        #   * Account holder name, bank name, account type, routing number, account number
        #
        # Payment Preferences:
        # - Auto-pay settings
        # - Statement preference (email, mail, both, portal)
        # - Payment reminders (email, SMS, phone)
        # - Reminder timing
        #
        # Payment Plans & Financial Assistance:
        # - Interest in payment plan (yes/no)
        # - Selected payment plan (3-month, 6-month, 12-month, custom)
        # - Preferred monthly payment amount
        # - Financial assistance application
        # - Assistance reasons (income, unemployment, medical expenses, hardship)
        # - Additional assistance information
        # - Charity care program participation (Medicaid, SNAP, WIC, TANF, SSI, unemployment)
        #
        # Additional Information:
        # - Outstanding balance status
        # - Preferred contact time for billing questions
        # - Special billing instructions/notes
        # - Payment authorization
        # - Financial responsibility acknowledgment
        # - Payment policy agreement
        # - etc.

        messages.success(request, 'Billing information submitted successfully. Your billing details have been securely saved and will be used for payment processing.')
        return redirect('index')

    # For GET requests, display the billing information form
    return render(request, 'healthcare/billing_information.html')


# Payment History
@login_required
def payment_history(request):
    """Display comprehensive payment history, invoices, and statements"""
    # TODO: In production, fetch actual data from database:
    # - Patient's payment history records:
    #   * Payment date, invoice number, description
    #   * Payment method (last 4 digits of card/account)
    #   * Amount paid, status (paid, pending, failed, refunded)
    #   * Receipt number and download link
    #
    # - Outstanding invoices:
    #   * Invoice number, issue date, due date
    #   * Description of services
    #   * Total amount, amount paid, balance due
    #   * Status (unpaid, partial, paid, overdue)
    #
    # - Billing statements:
    #   * Monthly statements with period dates
    #   * Previous balance, new charges, payments, adjustments
    #   * Current balance
    #   * PDF generation and download links
    #
    # - Payment receipts:
    #   * Receipt number, payment date, invoice reference
    #   * Description, amount paid, payment method
    #   * PDF receipt generation
    #
    # - Account summary:
    #   * Current balance (total amount due)
    #   * Total paid year-to-date
    #   * Overdue amount
    #   * Last payment date and amount
    #
    # - Filtering and pagination:
    #   * Date range filters (last 30/90 days, 6 months, year, custom)
    #   * Status filters (paid, pending, failed, refunded)
    #   * Payment method filters
    #   * Search by invoice number or description
    #   * Pagination for large result sets
    #
    # - Quick actions:
    #   * Make a payment (redirect to payment portal)
    #   * View/download statements
    #   * Update payment settings
    #   * Contact billing department
    # - etc.

    # For now, render with sample data shown in template
    return render(request, 'healthcare/payment_history.html')


# Billing Information
@login_required
@require_patient_access
def patient_billing_list(request, patient_id):
    """Display billing information and invoices for a patient - with role-based access control"""
    patient = get_object_or_404(Patient, patient_id=patient_id)

    # Get all billings for the patient
    billings = Billing.objects.filter(patient=patient).prefetch_related('billing_items', 'payments', 'encounter').order_by('-billing_date')

    # Calculate summary statistics
    total_billed = sum(b.total_amount for b in billings)
    total_paid = sum(b.amount_paid for b in billings)
    total_due = sum(b.amount_due for b in billings)

    context = {
        'patient': patient,
        'billings': billings,
        'total_billed': total_billed,
        'total_paid': total_paid,
        'total_due': total_due,
    }

    return render(request, 'healthcare/billing/index.html', context)


@login_required
@require_patient_access
def patient_billing_detail(request, patient_id, billing_id):
    """Display detailed invoice view - with role-based access control"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    billing = get_object_or_404(Billing, billing_id=billing_id, patient=patient)
    billing_items = billing.billing_items.all()
    payments = billing.payments.all()

    context = {
        'patient': patient,
        'billing': billing,
        'billing_items': billing_items,
        'payments': payments,
    }

    return render(request, 'healthcare/billing/show.html', context)


# Payment Information
@login_required
@require_patient_access
def patient_payment_list(request, patient_id):
    """Display payment history for a patient - with role-based access control"""
    patient = get_object_or_404(Patient, patient_id=patient_id)

    # Get all payments for the patient
    payments = Payment.objects.filter(patient=patient).select_related('billing').order_by('-payment_date')

    # Calculate statistics
    completed_payments = payments.filter(status='Completed')
    stats = {
        'total_payments': sum(p.amount for p in completed_payments),
        'payment_count': completed_payments.count(),
        'pending_payments': sum(p.amount for p in payments.filter(status='Pending')),
        'last_payment_date': completed_payments.first().payment_date if completed_payments.exists() else None,
    }

    context = {
        'patient': patient,
        'payments': payments,
        'stats': stats,
    }

    return render(request, 'healthcare/payments/index.html', context)


@login_required
@require_patient_access
def patient_payment_detail(request, patient_id, payment_id):
    """Display payment receipt - with role-based access control"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    payment = get_object_or_404(Payment, payment_id=payment_id, patient=patient)

    context = {
        'patient': patient,
        'payment': payment,
    }

    return render(request, 'healthcare/payments/show.html', context)


# Insurance Information
@login_required
@require_patient_access
def patient_insurance_list(request, patient_id):
    """Display insurance information for a patient - with role-based access control"""
    patient = get_object_or_404(Patient, patient_id=patient_id)

    # Get all insurance policies
    insurances = patient.insurance_policies.all().order_by('-is_primary', '-effective_date')
    primary_insurance = insurances.filter(is_primary=True).first()
    secondary_insurances = insurances.filter(is_primary=False)

    context = {
        'patient': patient,
        'insurances': insurances,
        'primary_insurance': primary_insurance,
        'secondary_insurances': secondary_insurances,
    }

    return render(request, 'healthcare/insurance/index.html', context)


@login_required
@require_patient_access
def patient_insurance_detail(request, patient_id, insurance_id):
    """Display detailed insurance policy view - with role-based access control"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    insurance = get_object_or_404(InsuranceInformation, insurance_id=insurance_id, patient=patient)

    context = {
        'patient': patient,
        'insurance': insurance,
    }

    return render(request, 'healthcare/insurance/show.html', context)


# Device Management
@login_required
@require_patient_access
def patient_device_list(request, patient_id):
    """Display devices for a patient - with role-based access control"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    devices = patient.devices.all().order_by('-created_at')

    context = {
        'patient': patient,
        'devices': devices,
    }

    return render(request, 'healthcare/devices/index.html', context)


@login_required
@require_patient_access
def patient_device_detail(request, patient_id, device_id):
    """Display device details - with role-based access control"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    device = get_object_or_404(Device, device_id=device_id, patient=patient)

    context = {
        'patient': patient,
        'device': device,
    }

    return render(request, 'healthcare/devices/show.html', context)


# Messaging Views
@login_required
def message_inbox(request):
    """Display inbox messages for the logged-in user"""
    messages_list = request.user.received_messages.all().order_by('-created_at')

    context = {
        'messages_list': messages_list,
        'unread_count': messages_list.filter(is_read=False).count(),
    }

    return render(request, 'healthcare/messages/inbox.html', context)


@login_required
def message_sent(request):
    """Display sent messages for the logged-in user"""
    messages_list = request.user.sent_messages.all().order_by('-created_at')

    context = {
        'messages_list': messages_list,
    }

    return render(request, 'healthcare/messages/sent.html', context)


@login_required
def message_compose(request):
    """Compose a new message"""
    from django.contrib.auth.models import User

    # Get potential recipients (all users except current user)
    potential_recipients = User.objects.exclude(id=request.user.id).order_by('last_name', 'first_name')

    # Check if this is a reply
    reply_to_id = request.GET.get('reply_to')
    reply_to_message = None
    if reply_to_id:
        reply_to_message = get_object_or_404(Message, message_id=reply_to_id)

    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        parent_message_id = request.POST.get('parent_message_id')

        # Validate required fields
        if not recipient_id or not subject or not body:
            messages.error(request, 'All fields are required.')
            return redirect('message_compose')

        try:
            recipient = User.objects.get(id=recipient_id)

            # Create message
            message = Message.objects.create(
                sender=request.user,
                recipient=recipient,
                subject=subject,
                body=body,
                parent_message=Message.objects.get(message_id=parent_message_id) if parent_message_id else None
            )

            messages.success(request, 'Message sent successfully!')
            return redirect('message_sent')
        except User.DoesNotExist:
            messages.error(request, 'Invalid recipient.')
            return redirect('message_compose')

    context = {
        'recipients': potential_recipients,
        'reply_to': reply_to_message,
    }

    return render(request, 'healthcare/messages/compose.html', context)


@login_required
def message_show(request, message_id):
    """Display a specific message"""
    message = get_object_or_404(Message, message_id=message_id)

    # Check if user has access to this message
    if message.sender != request.user and message.recipient != request.user:
        messages.error(request, 'You do not have permission to view this message.')
        return redirect('message_inbox')

    # Mark as read if user is the recipient
    if message.recipient == request.user and not message.is_read:
        message.is_read = True
        message.read_at = timezone.now()
        message.save()

    context = {
        'message': message,
        'replies': message.replies.all().order_by('created_at'),
    }

    return render(request, 'healthcare/messages/show.html', context)


@login_required
def message_delete(request, message_id):
    """Delete a message (only sender can delete)"""
    message = get_object_or_404(Message, message_id=message_id)

    # Only sender can delete
    if message.sender != request.user:
        messages.error(request, 'You can only delete messages you sent.')
        return redirect('message_inbox')

    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Message deleted successfully!')
        return redirect('message_sent')

    return redirect('message_show', message_id=message_id)


# ============================================================================
# DOCTOR MESSAGING AND ALERT SYSTEM
# ============================================================================

@login_required
@require_role('doctor')
def doctor_inbox(request):
    """Doctor-specific inbox with filtering and alert capabilities"""
    try:
        provider = request.user.provider_profile
    except:
        messages.error(request, 'No provider profile found for your account.')
        return redirect('index')

    # Get received messages
    messages_list = request.user.received_messages.select_related('sender').order_by('-created_at')

    # Get notifications/alerts
    notifications_list = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]

    # Get unread counts
    unread_messages = messages_list.filter(is_read=False).count()
    unread_notifications = notifications_list.filter(is_read=False).count()

    context = {
        'provider': provider,
        'messages_list': messages_list[:20],
        'notifications_list': notifications_list,
        'unread_messages': unread_messages,
        'unread_notifications': unread_notifications,
    }

    return render(request, 'healthcare/providers/inbox.html', context)


@login_required
@require_role('doctor')
def doctor_compose_message(request):
    """Doctor compose message - can only message their patients"""
    try:
        provider = request.user.provider_profile
    except:
        messages.error(request, 'No provider profile found for your account.')
        return redirect('index')

    # Get only this doctor's patients
    patients = Patient.objects.filter(
        primary_doctor=provider,
        is_active=True
    ).select_related('user').order_by('last_name', 'first_name')

    # Filter patients who have user accounts
    patient_users = [p.user for p in patients if p.user]

    # Check if this is a reply
    reply_to_id = request.GET.get('reply_to')
    reply_to_message = None
    if reply_to_id:
        reply_to_message = get_object_or_404(Message, message_id=reply_to_id)

    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        send_email = request.POST.get('send_email') == 'on'
        send_sms = request.POST.get('send_sms') == 'on'
        parent_message_id = request.POST.get('parent_message_id')

        # Validate required fields
        if not recipient_id or not subject or not body:
            messages.error(request, 'Subject and message body are required.')
            return redirect('doctor_compose_message')

        try:
            from django.contrib.auth.models import User
            recipient = User.objects.get(id=recipient_id)

            # Verify recipient is this doctor's patient
            if not Patient.objects.filter(primary_doctor=provider, user=recipient, is_active=True).exists():
                messages.error(request, 'You can only message your own patients.')
                return redirect('doctor_compose_message')

            # Create message
            message = Message.objects.create(
                sender=request.user,
                recipient=recipient,
                subject=subject,
                body=body,
                parent_message=Message.objects.get(message_id=parent_message_id) if parent_message_id else None
            )

            # Create notification for the recipient
            Notification.objects.create(
                user=recipient,
                title=f'New message from Dr. {provider.full_name}',
                message=f'Subject: {subject[:50]}...' if len(subject) > 50 else f'Subject: {subject}',
                notification_type='message'
            )

            # Send email if requested (placeholder for actual email sending)
            if send_email:
                try:
                    patient = Patient.objects.get(user=recipient)
                    if patient.email:
                        # TODO: Implement actual email sending using Django's email backend
                        # Example: send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [patient.email])
                        messages.info(request, f'Email notification queued to {patient.email}')
                except Exception as e:
                    messages.warning(request, f'Could not queue email notification: {str(e)}')

            # Send SMS if requested (placeholder for actual SMS sending)
            if send_sms:
                try:
                    patient = Patient.objects.get(user=recipient)
                    if patient.phone:
                        # TODO: Implement actual SMS sending using Twilio or similar service
                        messages.info(request, f'SMS notification queued to {patient.phone}')
                except Exception as e:
                    messages.warning(request, f'Could not queue SMS notification: {str(e)}')

            messages.success(request, 'Message sent successfully!')
            return redirect('doctor_inbox')

        except User.DoesNotExist:
            messages.error(request, 'Invalid recipient.')
            return redirect('doctor_compose_message')

    context = {
        'provider': provider,
        'patients': patient_users,
        'reply_to': reply_to_message,
    }

    return render(request, 'healthcare/providers/compose_message.html', context)


@login_required
@require_role('doctor')
def doctor_notifications(request):
    """View all notifications/alerts for the doctor"""
    # Get all notifications for the doctor
    notifications_list = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Mark notifications as read if requested
    if request.method == 'POST':
        notification_ids = request.POST.getlist('mark_read')
        if notification_ids:
            Notification.objects.filter(
                notification_id__in=notification_ids,
                user=request.user
            ).update(is_read=True, read_at=timezone.now())
            messages.success(request, 'Notifications marked as read.')
            return redirect('doctor_notifications')

    context = {
        'notifications_list': notifications_list,
        'unread_count': notifications_list.filter(is_read=False).count(),
    }

    return render(request, 'healthcare/providers/notifications.html', context)


@login_required
@require_role('doctor')
def mark_notification_read(request, notification_id):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, notification_id=notification_id, user=request.user)
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()
    messages.success(request, 'Notification marked as read.')
    return redirect('doctor_notifications')


@login_required
@require_role('doctor')
def doctor_view_all_vitals(request):
    """View all vital signs for doctor's patients - latest to oldest"""
    try:
        provider = request.user.provider_profile
    except:
        messages.error(request, 'No provider profile found for your account.')
        return redirect('index')

    # Get all patients for this provider
    patients = Patient.objects.filter(primary_doctor=provider, is_active=True)
    patient_ids = patients.values_list('patient_id', flat=True)

    # Get all vital signs for these patients, ordered by latest first
    vitals_list = VitalSign.objects.filter(
        encounter__patient_id__in=patient_ids
    ).select_related(
        'encounter__patient',
        'encounter__provider',
        'recorded_by'
    ).order_by('-recorded_at')

    # Pagination (optional, but recommended for large datasets)
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(vitals_list, 50)  # Show 50 vitals per page
    page = request.GET.get('page')

    try:
        vitals = paginator.page(page)
    except PageNotAnInteger:
        vitals = paginator.page(1)
    except EmptyPage:
        vitals = paginator.page(paginator.num_pages)

    # Get statistics
    total_vitals = vitals_list.count()
    critical_vitals = sum(1 for v in vitals_list if v.has_critical_values())

    context = {
        'provider': provider,
        'vitals': vitals,
        'total_vitals': total_vitals,
        'critical_vitals': critical_vitals,
    }

    return render(request, 'healthcare/providers/all_vitals.html', context)


@login_required
@require_role('doctor')
def patient_vitals_chart(request, patient_id):
    """View patient's vital signs with charts, graphs, and historical data"""
    try:
        provider = request.user.provider_profile
    except:
        messages.error(request, 'No provider profile found for your account.')
        return redirect('index')

    # Get the patient
    patient = get_object_or_404(Patient, patient_id=patient_id)

    # Verify this is the doctor's patient
    if patient.primary_doctor != provider:
        messages.error(request, 'You do not have access to this patient.')
        return redirect('provider_dashboard')

    # Get date range from query params (default: last 30 days)
    from datetime import datetime, timedelta
    from django.utils import timezone

    days = request.GET.get('days', '30')
    try:
        days = int(days)
    except:
        days = 30

    start_date = timezone.now() - timedelta(days=days)

    # Get all vitals for this patient within date range
    vitals_list = VitalSign.objects.filter(
        encounter__patient=patient,
        recorded_at__gte=start_date
    ).select_related(
        'encounter',
        'recorded_by'
    ).order_by('recorded_at')

    # Get all vitals (no date filter) for total count
    all_vitals = VitalSign.objects.filter(
        encounter__patient=patient
    ).order_by('-recorded_at')

    # Prepare data for charts
    chart_data = {
        'dates': [],
        'heart_rate': [],
        'sbp': [],
        'dbp': [],
        'temperature': [],
        'respiratory_rate': [],
        'oxygen_saturation': [],
        'glucose': [],
        'heart_rate_colors': [],
        'sbp_colors': [],
        'dbp_colors': [],
        'temperature_colors': [],
        'respiratory_rate_colors': [],
        'oxygen_saturation_colors': [],
        'glucose_colors': [],
    }

    # Color mapping
    color_map = {
        'blue': 'rgba(33, 150, 243, 0.8)',  # Emergency
        'red': 'rgba(244, 67, 54, 0.8)',    # Doctor
        'orange': 'rgba(255, 152, 0, 0.8)', # Nurse
        'green': 'rgba(76, 175, 80, 0.8)',  # Normal
    }

    for vital in vitals_list:
        date_str = vital.recorded_at.strftime('%Y-%m-%d %H:%M')
        chart_data['dates'].append(date_str)

        # Heart Rate
        if vital.heart_rate:
            chart_data['heart_rate'].append(float(vital.heart_rate))
            status = vital.get_heart_rate_status()
            chart_data['heart_rate_colors'].append(color_map.get(status[0], color_map['green']))
        else:
            chart_data['heart_rate'].append(None)
            chart_data['heart_rate_colors'].append(color_map['green'])

        # SBP
        if vital.blood_pressure_systolic:
            chart_data['sbp'].append(float(vital.blood_pressure_systolic))
            status = vital.get_sbp_status()
            chart_data['sbp_colors'].append(color_map.get(status[0], color_map['green']))
        else:
            chart_data['sbp'].append(None)
            chart_data['sbp_colors'].append(color_map['green'])

        # DBP
        if vital.blood_pressure_diastolic:
            chart_data['dbp'].append(float(vital.blood_pressure_diastolic))
            status = vital.get_dbp_status()
            chart_data['dbp_colors'].append(color_map.get(status[0], color_map['green']))
        else:
            chart_data['dbp'].append(None)
            chart_data['dbp_colors'].append(color_map['green'])

        # Temperature (convert to Fahrenheit for display if needed)
        if vital.temperature_value:
            temp = float(vital.temperature_value)
            if vital.temperature_unit == 'C':
                temp = (temp * 9/5) + 32  # Convert to Fahrenheit
            chart_data['temperature'].append(temp)
            status = vital.get_temperature_status()
            chart_data['temperature_colors'].append(color_map.get(status[0], color_map['green']))
        else:
            chart_data['temperature'].append(None)
            chart_data['temperature_colors'].append(color_map['green'])

        # Respiratory Rate
        if vital.respiratory_rate:
            chart_data['respiratory_rate'].append(float(vital.respiratory_rate))
            status = vital.get_respiratory_rate_status()
            chart_data['respiratory_rate_colors'].append(color_map.get(status[0], color_map['green']))
        else:
            chart_data['respiratory_rate'].append(None)
            chart_data['respiratory_rate_colors'].append(color_map['green'])

        # Oxygen Saturation
        if vital.oxygen_saturation:
            chart_data['oxygen_saturation'].append(float(vital.oxygen_saturation))
            status = vital.get_oxygen_saturation_status()
            chart_data['oxygen_saturation_colors'].append(color_map.get(status[0], color_map['green']))
        else:
            chart_data['oxygen_saturation'].append(None)
            chart_data['oxygen_saturation_colors'].append(color_map['green'])

        # Glucose
        if vital.glucose:
            chart_data['glucose'].append(float(vital.glucose))
            status = vital.get_glucose_status()
            chart_data['glucose_colors'].append(color_map.get(status[0], color_map['green']))
        else:
            chart_data['glucose'].append(None)
            chart_data['glucose_colors'].append(color_map['green'])

    # Calculate statistics
    total_readings = all_vitals.count()
    critical_readings = sum(1 for v in vitals_list if v.has_critical_values())

    # Get latest vital
    latest_vital = all_vitals.first() if all_vitals.exists() else None

    import json
    context = {
        'provider': provider,
        'patient': patient,
        'vitals_list': vitals_list,
        'all_vitals': all_vitals[:100],  # Show last 100 for table
        'chart_data_json': json.dumps(chart_data),
        'total_readings': total_readings,
        'critical_readings': critical_readings,
        'latest_vital': latest_vital,
        'days': days,
    }

    return render(request, 'healthcare/providers/patient_vitals_chart.html', context)


@login_required
def patient_profile(request):
    """Patient profile view - shows patient's own information"""
    # Get the patient associated with the logged-in user
    try:
        patient = request.user.patient_profile
    except:
        messages.error(request, 'No patient profile found for your account.')
        return redirect('index')

    # Get all patient-related information
    appointments = Encounter.objects.filter(patient=patient).order_by('-encounter_date')[:10]
    vitals = VitalSign.objects.filter(encounter__patient=patient).order_by('-recorded_at')[:10]
    diagnoses = Diagnosis.objects.filter(encounter__patient=patient).order_by('-diagnosed_at')[:10]
    prescriptions = Prescription.objects.filter(encounter__patient=patient).order_by('-start_date')[:10]
    allergies = Allergy.objects.filter(patient=patient).order_by('-allergy_id')
    medical_history = MedicalHistory.objects.filter(patient=patient).order_by('-diagnosis_date')
    social_history = SocialHistory.objects.filter(patient=patient).first()
    lab_tests = LabTest.objects.filter(patient=patient).order_by('-ordered_date')[:10]
    billings = Billing.objects.filter(patient=patient).order_by('-billing_date')[:10]
    payments = Payment.objects.filter(patient=patient).order_by('-payment_date')[:10]
    insurance_info = InsuranceInformation.objects.filter(patient=patient, is_primary=True).first()
    devices = Device.objects.filter(patient=patient).order_by('-created_at')

    context = {
        'patient': patient,
        'appointments': appointments,
        'vitals': vitals,
        'diagnoses': diagnoses,
        'prescriptions': prescriptions,
        'allergies': allergies,
        'medical_history': medical_history,
        'social_history': social_history,
        'lab_tests': lab_tests,
        'billings': billings,
        'payments': payments,
        'insurance_info': insurance_info,
        'devices': devices,
    }

    return render(request, 'healthcare/patients/profile.html', context)


@login_required
def patient_profile_edit(request):
    """Edit patient profile - patients can edit their own information"""
    try:
        patient = request.user.patient_profile
    except:
        messages.error(request, 'No patient profile found for your account.')
        return redirect('index')

    if request.method == 'POST':
        # Update patient information
        patient.phone = request.POST.get('phone', patient.phone)
        patient.email = request.POST.get('email', patient.email)
        patient.address = request.POST.get('address', patient.address)
        patient.city = request.POST.get('city', patient.city)
        patient.state = request.POST.get('state', patient.state)
        patient.zip_code = request.POST.get('zip_code', patient.zip_code)
        patient.emergency_contact_name = request.POST.get('emergency_contact_name', patient.emergency_contact_name)
        patient.emergency_contact_phone = request.POST.get('emergency_contact_phone', patient.emergency_contact_phone)

        try:
            patient.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('patient_profile')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')

    context = {
        'patient': patient,
    }

    return render(request, 'healthcare/patients/profile_edit.html', context)


@login_required
@require_role('patient')
def patient_dashboard(request):
    """Patient Dashboard - personalized health overview"""
    try:
        patient = request.user.patient_profile
    except:
        messages.error(request, 'No patient profile found for your account.')
        return redirect('index')

    # Get statistics
    stats = {
        'total_appointments': Encounter.objects.filter(patient=patient).count(),
        'upcoming_appointments': Encounter.objects.filter(
            patient=patient,
            encounter_date__gte=timezone.now(),
            status='Scheduled'
        ).count(),
        'total_prescriptions': Prescription.objects.filter(patient=patient, status='Active').count(),
        'pending_bills': Billing.objects.filter(
            patient=patient,
            status__in=['Pending', 'Partially Paid']
        ).count(),
        'total_allergies': Allergy.objects.filter(patient=patient, is_active=True).count(),
        'unread_messages': request.user.received_messages.filter(is_read=False).count(),
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
    }

    # Recent and upcoming data
    upcoming_appointments = Encounter.objects.filter(
        patient=patient,
        encounter_date__gte=timezone.now(),
        status='Scheduled'
    ).select_related('provider').order_by('encounter_date')[:5]

    recent_appointments = Encounter.objects.filter(
        patient=patient,
        encounter_date__lt=timezone.now()
    ).select_related('provider').order_by('-encounter_date')[:5]

    recent_vitals = VitalSign.objects.filter(
        encounter__patient=patient
    ).select_related('encounter').order_by('-recorded_at')[:5]

    active_prescriptions = Prescription.objects.filter(
        patient=patient,
        status='Active'
    ).select_related('provider').order_by('-start_date')[:10]

    recent_lab_tests = LabTest.objects.filter(
        patient=patient
    ).order_by('-ordered_date')[:5]

    pending_billings = Billing.objects.filter(
        patient=patient,
        status__in=['Pending', 'Partially Paid']
    ).order_by('-billing_date')[:5]

    allergies = Allergy.objects.filter(
        patient=patient,
        is_active=True
    ).order_by('-severity', 'allergen')

    context = {
        'patient': patient,
        'stats': stats,
        'upcoming_appointments': upcoming_appointments,
        'recent_appointments': recent_appointments,
        'recent_vitals': recent_vitals,
        'active_prescriptions': active_prescriptions,
        'recent_lab_tests': recent_lab_tests,
        'pending_billings': pending_billings,
        'allergies': allergies,
    }

    return render(request, 'healthcare/patients/dashboard.html', context)


# ============================================================================
# PATIENT MESSAGING AND ALERT SYSTEM
# ============================================================================

@login_required
@require_role('patient')
def patient_inbox(request):
    """Patient-specific inbox with filtering and alert capabilities"""
    try:
        patient = request.user.patient_profile
    except:
        messages.error(request, 'No patient profile found for your account.')
        return redirect('index')

    # Get received messages
    messages_list = request.user.received_messages.select_related('sender').order_by('-created_at')

    # Get notifications/alerts
    notifications_list = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]

    # Get unread counts
    unread_messages = messages_list.filter(is_read=False).count()
    unread_notifications = notifications_list.filter(is_read=False).count()

    context = {
        'patient': patient,
        'messages_list': messages_list[:20],
        'notifications_list': notifications_list,
        'unread_messages': unread_messages,
        'unread_notifications': unread_notifications,
    }

    return render(request, 'healthcare/patients/inbox.html', context)


@login_required
@require_role('patient')
def patient_compose_message(request):
    """Patient compose message - can only message their primary doctor"""
    try:
        patient = request.user.patient_profile
    except:
        messages.error(request, 'No patient profile found for your account.')
        return redirect('index')

    # Get patient's primary doctor
    doctors = []
    if patient.primary_doctor and patient.primary_doctor.user:
        doctors = [patient.primary_doctor.user]

    # Check if this is a reply
    reply_to_id = request.GET.get('reply_to')
    reply_to_message = None
    if reply_to_id:
        reply_to_message = get_object_or_404(Message, message_id=reply_to_id)

    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        send_email = request.POST.get('send_email') == 'on'
        send_sms = request.POST.get('send_sms') == 'on'
        parent_message_id = request.POST.get('parent_message_id')

        # Validate required fields
        if not recipient_id or not subject or not body:
            messages.error(request, 'Subject and message body are required.')
            return redirect('patient_compose_message')

        try:
            from django.contrib.auth.models import User
            recipient = User.objects.get(id=recipient_id)

            # Verify recipient is this patient's primary doctor
            if patient.primary_doctor and patient.primary_doctor.user:
                if recipient.id != patient.primary_doctor.user.id:
                    messages.error(request, 'You can only message your primary doctor.')
                    return redirect('patient_compose_message')
            else:
                messages.error(request, 'You do not have a primary doctor assigned.')
                return redirect('patient_compose_message')

            # Create message
            message = Message.objects.create(
                sender=request.user,
                recipient=recipient,
                subject=subject,
                body=body,
                parent_message=Message.objects.get(message_id=parent_message_id) if parent_message_id else None
            )

            # Create notification for the recipient
            Notification.objects.create(
                user=recipient,
                title=f'New message from patient {patient.full_name}',
                message=f'Subject: {subject[:50]}...' if len(subject) > 50 else f'Subject: {subject}',
                notification_type='message'
            )

            # Send email if requested (placeholder for actual email sending)
            if send_email:
                try:
                    if patient.primary_doctor.email:
                        # TODO: Implement actual email sending using Django's email backend
                        messages.info(request, f'Email notification queued to {patient.primary_doctor.email}')
                except Exception as e:
                    messages.warning(request, f'Could not queue email notification: {str(e)}')

            # Send SMS if requested (placeholder for actual SMS sending)
            if send_sms:
                try:
                    if patient.primary_doctor.phone:
                        # TODO: Implement actual SMS sending using Twilio or similar service
                        messages.info(request, f'SMS notification queued to {patient.primary_doctor.phone}')
                except Exception as e:
                    messages.warning(request, f'Could not queue SMS notification: {str(e)}')

            messages.success(request, 'Message sent successfully!')
            return redirect('patient_inbox')

        except User.DoesNotExist:
            messages.error(request, 'Invalid recipient.')
            return redirect('patient_compose_message')

    context = {
        'patient': patient,
        'doctors': doctors,
        'reply_to': reply_to_message,
    }

    return render(request, 'healthcare/patients/compose_message.html', context)


@login_required
@require_role('patient')
def patient_notifications(request):
    """View all notifications/alerts for the patient"""
    # Get all notifications for the patient
    notifications_list = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Mark notifications as read if requested
    if request.method == 'POST':
        notification_ids = request.POST.getlist('mark_read')
        if notification_ids:
            Notification.objects.filter(
                notification_id__in=notification_ids,
                user=request.user
            ).update(is_read=True, read_at=timezone.now())
            messages.success(request, 'Notifications marked as read.')
            return redirect('patient_notifications')

    context = {
        'notifications_list': notifications_list,
        'unread_count': notifications_list.filter(is_read=False).count(),
    }

    return render(request, 'healthcare/patients/notifications.html', context)


@login_required
@require_role('patient')
def patient_mark_notification_read(request, notification_id):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, notification_id=notification_id, user=request.user)
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()
    messages.success(request, 'Notification marked as read.')
    return redirect('patient_notifications')


@login_required
def provider_profile(request):
    """Provider profile view - shows provider's own information and ALL patient data"""
    try:
        provider = request.user.provider_profile
    except:
        messages.error(request, 'No provider profile found for your account.')
        return redirect('index')

    # Get unique patients for this provider
    patients = Patient.objects.filter(encounters__provider=provider).distinct().order_by('last_name', 'first_name')
    patient_ids = patients.values_list('patient_id', flat=True)

    # Get all provider-related information
    appointments = Encounter.objects.filter(provider=provider).select_related('patient', 'department').order_by('-encounter_date')[:20]

    # Get prescriptions written by this provider
    prescriptions = Prescription.objects.filter(provider=provider).select_related('patient', 'encounter').order_by('-start_date')[:20]

    # Get diagnoses made by this provider
    diagnoses = Diagnosis.objects.filter(diagnosed_by=provider).select_related('encounter__patient').order_by('-diagnosed_at')[:20]

    # Get recent vital signs for provider's patients
    vitals = VitalSign.objects.filter(encounter__provider=provider).select_related('encounter__patient').order_by('-recorded_at')[:20]

    # Get ALL information about provider's patients
    allergies = Allergy.objects.filter(patient__in=patients).select_related('patient').order_by('patient__last_name', '-severity')

    medical_history = MedicalHistory.objects.filter(patient__in=patients).select_related('patient').order_by('patient__last_name', '-diagnosis_date')[:30]

    social_history = SocialHistory.objects.filter(patient__in=patients).select_related('patient').order_by('patient__last_name')[:20]

    lab_tests = LabTest.objects.filter(patient__in=patients).select_related('patient').order_by('-ordered_date')[:30]

    billings = Billing.objects.filter(patient__in=patients).select_related('patient').order_by('-billing_date')[:30]

    payments = Payment.objects.filter(patient__in=patients).select_related('patient').order_by('-payment_date')[:30]

    insurance_info = InsuranceInformation.objects.filter(patient__in=patients).select_related('patient').order_by('patient__last_name', '-is_primary')[:20]

    devices = Device.objects.filter(patient__in=patients).select_related('patient').order_by('-created_at')[:20]

    # Get statistics
    total_patients = patients.count()
    total_appointments = appointments.count()
    upcoming_appointments = Encounter.objects.filter(
        provider=provider,
        encounter_date__gte=timezone.now(),
        status='Scheduled'
    ).count()

    context = {
        'provider': provider,
        'appointments': appointments,
        'patients': patients,
        'prescriptions': prescriptions,
        'diagnoses': diagnoses,
        'vitals': vitals,
        'allergies': allergies,
        'medical_history': medical_history,
        'social_history': social_history,
        'lab_tests': lab_tests,
        'billings': billings,
        'payments': payments,
        'insurance_info': insurance_info,
        'devices': devices,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'upcoming_appointments': upcoming_appointments,
    }

    return render(request, 'healthcare/providers/profile.html', context)


@login_required
def provider_profile_edit(request):
    """Provider profile edit view - allows providers to update contact information"""
    try:
        provider = request.user.provider_profile
    except:
        messages.error(request, 'No provider profile found for your account.')
        return redirect('index')

    if request.method == 'POST':
        # Update only contact information
        provider.phone = request.POST.get('phone', provider.phone)
        provider.email = request.POST.get('email', provider.email)
        provider.save()

        # Update user email as well
        request.user.email = provider.email
        request.user.save()

        messages.success(request, 'Your contact information has been updated successfully.')
        return redirect('provider_profile')

    context = {
        'provider': provider,
    }

    return render(request, 'healthcare/providers/profile_edit.html', context)


@login_required
@require_role('doctor')
def provider_dashboard(request):
    """Provider/Doctor Dashboard - comprehensive patient care overview"""
    try:
        provider = request.user.provider_profile
    except:
        messages.error(request, 'No provider profile found for your account.')
        return redirect('index')

    # Get all patients for this provider
    patients = Patient.objects.filter(primary_doctor=provider, is_active=True)
    patient_ids = patients.values_list('patient_id', flat=True)

    # Get statistics
    stats = {
        'total_patients': patients.count(),
        'appointments_today': Encounter.objects.filter(
            provider=provider,
            encounter_date__date=timezone.now().date()
        ).count(),
        'appointments_upcoming': Encounter.objects.filter(
            provider=provider,
            encounter_date__gt=timezone.now(),
            status='Scheduled'
        ).count(),
        'diagnoses_this_month': Diagnosis.objects.filter(
            diagnosed_by=provider,
            diagnosed_at__month=timezone.now().month,
            diagnosed_at__year=timezone.now().year
        ).count(),
        'prescriptions_active': Prescription.objects.filter(
            provider=provider,
            status='Active'
        ).count(),
        'unread_messages': request.user.received_messages.filter(is_read=False).count(),
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
    }

    # Today's appointments
    todays_appointments = Encounter.objects.filter(
        provider=provider,
        encounter_date__date=timezone.now().date()
    ).select_related('patient').order_by('encounter_date')

    # Upcoming appointments
    upcoming_appointments = Encounter.objects.filter(
        provider=provider,
        encounter_date__gt=timezone.now(),
        status='Scheduled'
    ).select_related('patient').order_by('encounter_date')[:10]

    # Recent appointments
    recent_appointments = Encounter.objects.filter(
        provider=provider,
        encounter_date__lt=timezone.now()
    ).select_related('patient').order_by('-encounter_date')[:10]

    # Recent diagnoses
    recent_diagnoses = Diagnosis.objects.filter(
        diagnosed_by=provider
    ).select_related('encounter__patient').order_by('-diagnosed_at')[:10]

    # Recent prescriptions
    recent_prescriptions = Prescription.objects.filter(
        provider=provider
    ).select_related('patient').order_by('-start_date')[:10]

    # Recent vitals from provider's patients
    recent_vitals = VitalSign.objects.filter(
        encounter__provider=provider
    ).select_related('encounter__patient').order_by('-recorded_at')[:10]

    # Patients needing attention (recent vitals with abnormal values)
    critical_patients = Patient.objects.filter(
        patient_id__in=VitalSign.objects.filter(
            encounter__provider=provider,
            recorded_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).filter(
            Q(blood_pressure_systolic__gt=140) | Q(blood_pressure_diastolic__gt=90) |
            Q(heart_rate__gt=100) | Q(heart_rate__lt=60) |
            Q(temperature_value__gt=100.4)
        ).values_list('encounter__patient_id', flat=True)
    ).distinct()[:5]

    context = {
        'provider': provider,
        'stats': stats,
        'todays_appointments': todays_appointments,
        'upcoming_appointments': upcoming_appointments,
        'recent_appointments': recent_appointments,
        'recent_diagnoses': recent_diagnoses,
        'recent_prescriptions': recent_prescriptions,
        'recent_vitals': recent_vitals,
        'critical_patients': critical_patients,
    }

    return render(request, 'healthcare/providers/dashboard.html', context)


# ============================================================================
# OFFICE ADMINISTRATOR VIEWS
# ============================================================================

@login_required
@require_role('office_admin')
def admin_dashboard(request):
    """Office Administrator Dashboard - comprehensive management overview"""
    # Get statistics
    stats = {
        'total_patients': Patient.objects.filter(is_active=True).count(),
        'total_providers': Provider.objects.filter(is_active=True).count(),
        'total_hospitals': Hospital.objects.filter(is_active=True).count(),
        'total_appointments_today': Encounter.objects.filter(
            encounter_date__date=timezone.now().date()
        ).count(),
        'total_appointments_upcoming': Encounter.objects.filter(
            encounter_date__gt=timezone.now(),
            status='Scheduled'
        ).count(),
        'total_pending_billing': Billing.objects.filter(
            status='Pending'
        ).aggregate(total=Sum('amount_due'))['total'] or 0,
        'total_unpaid_billing': Billing.objects.filter(
            status__in=['Pending', 'Partially Paid']
        ).aggregate(total=Sum('amount_due'))['total'] or 0,
    }

    # Recent activity
    recent_patients = Patient.objects.filter(is_active=True).order_by('-patient_id')[:5]
    recent_appointments = Encounter.objects.select_related('patient', 'provider').order_by('-encounter_date')[:10]
    recent_billings = Billing.objects.select_related('patient').order_by('-created_at')[:10]
    upcoming_appointments = Encounter.objects.filter(
        encounter_date__gte=timezone.now(),
        status='Scheduled'
    ).select_related('patient', 'provider').order_by('encounter_date')[:10]

    context = {
        'stats': stats,
        'recent_patients': recent_patients,
        'recent_appointments': recent_appointments,
        'recent_billings': recent_billings,
        'upcoming_appointments': upcoming_appointments,
    }

    return render(request, 'healthcare/admin/dashboard.html', context)


# ============================================================================
# ADMIN - PROVIDER MANAGEMENT
# ============================================================================

@login_required
@require_role('office_admin')
def admin_provider_create(request):
    """Admin: Create new provider"""
    if request.method == 'POST':
        provider = Provider.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            npi=request.POST['npi'],
            specialty=request.POST.get('specialty', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            license_number=request.POST.get('license_number', ''),
            hospital_id=request.POST.get('hospital_id') or None,
            department_id=request.POST.get('department_id') or None,
        )
        messages.success(request, f'Provider {provider.full_name} created successfully.')
        return redirect('physician_detail', provider_id=provider.provider_id)

    hospitals = Hospital.objects.filter(is_active=True).order_by('name')
    departments = Department.objects.filter(is_active=True).order_by('department_name')

    context = {
        'hospitals': hospitals,
        'departments': departments,
    }
    return render(request, 'healthcare/admin/provider_create.html', context)


@login_required
@require_role('office_admin')
def admin_provider_edit(request, provider_id):
    """Admin: Edit provider"""
    provider = get_object_or_404(Provider, provider_id=provider_id)

    if request.method == 'POST':
        provider.first_name = request.POST['first_name']
        provider.last_name = request.POST['last_name']
        provider.npi = request.POST['npi']
        provider.specialty = request.POST.get('specialty', '')
        provider.email = request.POST.get('email', '')
        provider.phone = request.POST.get('phone', '')
        provider.license_number = request.POST.get('license_number', '')
        provider.hospital_id = request.POST.get('hospital_id') or None
        provider.department_id = request.POST.get('department_id') or None
        provider.is_active = request.POST.get('is_active', 'on') == 'on'
        provider.save()

        messages.success(request, f'Provider {provider.full_name} updated successfully.')
        return redirect('physician_detail', provider_id=provider.provider_id)

    hospitals = Hospital.objects.filter(is_active=True).order_by('name')
    departments = Department.objects.filter(is_active=True).order_by('department_name')

    context = {
        'provider': provider,
        'hospitals': hospitals,
        'departments': departments,
    }
    return render(request, 'healthcare/admin/provider_edit.html', context)


# ============================================================================
# ADMIN - HOSPITAL MANAGEMENT
# ============================================================================

@login_required
@require_role('office_admin')
def admin_hospital_create(request):
    """Admin: Create new hospital"""
    if request.method == 'POST':
        hospital = Hospital.objects.create(
            name=request.POST['name'],
            address=request.POST['address'],
            city=request.POST['city'],
            state=request.POST['state'],
            zip_code=request.POST['zip_code'],
            phone=request.POST['phone'],
            email=request.POST.get('email', ''),
            website=request.POST.get('website', ''),
        )
        messages.success(request, f'Hospital {hospital.name} created successfully.')
        return redirect('hospital_detail', hospital_id=hospital.hospital_id)

    return render(request, 'healthcare/admin/hospital_create.html')


@login_required
@require_role('office_admin')
def admin_hospital_edit(request, hospital_id):
    """Admin: Edit hospital"""
    hospital = get_object_or_404(Hospital, hospital_id=hospital_id)

    if request.method == 'POST':
        hospital.name = request.POST['name']
        hospital.address = request.POST['address']
        hospital.city = request.POST['city']
        hospital.state = request.POST['state']
        hospital.zip_code = request.POST['zip_code']
        hospital.phone = request.POST['phone']
        hospital.email = request.POST.get('email', '')
        hospital.website = request.POST.get('website', '')
        hospital.is_active = request.POST.get('is_active', 'on') == 'on'
        hospital.save()

        messages.success(request, f'Hospital {hospital.name} updated successfully.')
        return redirect('hospital_detail', hospital_id=hospital.hospital_id)

    context = {
        'hospital': hospital,
    }
    return render(request, 'healthcare/admin/hospital_edit.html', context)


# ============================================================================
# ADMIN - INSURANCE MANAGEMENT
# ============================================================================

@login_required
@require_role('office_admin')
def admin_insurance_create(request, patient_id):
    """Admin: Create insurance for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)

    if request.method == 'POST':
        insurance = InsuranceInformation.objects.create(
            patient=patient,
            insurance_company=request.POST['insurance_company'],
            policy_number=request.POST['policy_number'],
            group_number=request.POST.get('group_number', ''),
            subscriber_name=request.POST['subscriber_name'],
            subscriber_relationship=request.POST.get('subscriber_relationship', ''),
            subscriber_dob=request.POST.get('subscriber_dob') or None,
            effective_date=request.POST.get('effective_date') or None,
            termination_date=request.POST.get('termination_date') or None,
            copay_amount=request.POST.get('copay_amount') or None,
            deductible_amount=request.POST.get('deductible_amount') or None,
            is_primary=request.POST.get('is_primary', 'off') == 'on',
        )
        messages.success(request, f'Insurance policy created successfully for {patient.full_name}.')
        return redirect('patient_insurance_list', patient_id=patient.patient_id)

    context = {
        'patient': patient,
    }
    return render(request, 'healthcare/admin/insurance_create.html', context)


@login_required
@require_role('office_admin')
def admin_insurance_edit(request, patient_id, insurance_id):
    """Admin: Edit insurance for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    insurance = get_object_or_404(InsuranceInformation, insurance_id=insurance_id, patient=patient)

    if request.method == 'POST':
        insurance.insurance_company = request.POST['insurance_company']
        insurance.policy_number = request.POST['policy_number']
        insurance.group_number = request.POST.get('group_number', '')
        insurance.subscriber_name = request.POST['subscriber_name']
        insurance.subscriber_relationship = request.POST.get('subscriber_relationship', '')
        insurance.subscriber_dob = request.POST.get('subscriber_dob') or None
        insurance.effective_date = request.POST.get('effective_date') or None
        insurance.termination_date = request.POST.get('termination_date') or None
        insurance.copay_amount = request.POST.get('copay_amount') or None
        insurance.deductible_amount = request.POST.get('deductible_amount') or None
        insurance.is_primary = request.POST.get('is_primary', 'off') == 'on'
        insurance.save()

        messages.success(request, f'Insurance policy updated successfully for {patient.full_name}.')
        return redirect('patient_insurance_list', patient_id=patient.patient_id)

    context = {
        'patient': patient,
        'insurance': insurance,
    }
    return render(request, 'healthcare/admin/insurance_edit.html', context)


# ============================================================================
# ADMIN - BILLING MANAGEMENT
# ============================================================================

@login_required
@require_role('office_admin')
def admin_billing_create(request, patient_id):
    """Admin: Create billing for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    encounters = patient.encounters.all().order_by('-encounter_date')

    if request.method == 'POST':
        billing = Billing.objects.create(
            patient=patient,
            encounter_id=request.POST.get('encounter_id') or None,
            billing_date=request.POST['billing_date'],
            total_amount=request.POST['total_amount'],
            insurance_amount=request.POST.get('insurance_amount', 0),
            patient_responsibility=request.POST.get('patient_responsibility', 0),
            amount_paid=request.POST.get('amount_paid', 0),
            amount_due=request.POST.get('amount_due', 0),
            status=request.POST.get('status', 'Pending'),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, f'Billing created successfully for {patient.full_name}.')
        return redirect('patient_billing_detail', patient_id=patient.patient_id, billing_id=billing.billing_id)

    context = {
        'patient': patient,
        'encounters': encounters,
    }
    return render(request, 'healthcare/admin/billing_create.html', context)


@login_required
@require_role('office_admin')
def admin_billing_edit(request, patient_id, billing_id):
    """Admin: Edit billing for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    billing = get_object_or_404(Billing, billing_id=billing_id, patient=patient)

    if request.method == 'POST':
        billing.billing_date = request.POST['billing_date']
        billing.total_amount = request.POST['total_amount']
        billing.insurance_amount = request.POST.get('insurance_amount', 0)
        billing.patient_responsibility = request.POST.get('patient_responsibility', 0)
        billing.amount_paid = request.POST.get('amount_paid', 0)
        billing.amount_due = request.POST.get('amount_due', 0)
        billing.status = request.POST.get('status', 'Pending')
        billing.notes = request.POST.get('notes', '')
        billing.save()

        messages.success(request, f'Billing updated successfully for {patient.full_name}.')
        return redirect('patient_billing_detail', patient_id=patient.patient_id, billing_id=billing.billing_id)

    context = {
        'patient': patient,
        'billing': billing,
    }
    return render(request, 'healthcare/admin/billing_edit.html', context)


# ============================================================================
# ADMIN - PAYMENT MANAGEMENT
# ============================================================================

@login_required
@require_role('office_admin')
def admin_payment_create(request, patient_id):
    """Admin: Create payment for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    billings = Billing.objects.filter(patient=patient).order_by('-billing_date')

    if request.method == 'POST':
        payment = Payment.objects.create(
            patient=patient,
            billing_id=request.POST.get('billing_id') or None,
            payment_date=request.POST['payment_date'],
            amount=request.POST['amount'],
            payment_method=request.POST.get('payment_method', 'Cash'),
            transaction_id=request.POST.get('transaction_id', ''),
            status=request.POST.get('status', 'Completed'),
            notes=request.POST.get('notes', ''),
        )

        # Update billing amount_paid if billing is selected
        if payment.billing:
            billing = payment.billing
            billing.amount_paid = float(billing.amount_paid or 0) + float(payment.amount)
            billing.amount_due = float(billing.total_amount) - float(billing.amount_paid)
            if billing.amount_due <= 0:
                billing.status = 'Paid'
            elif billing.amount_paid > 0:
                billing.status = 'Partially Paid'
            billing.save()

        messages.success(request, f'Payment recorded successfully for {patient.full_name}.')
        return redirect('patient_payment_list', patient_id=patient.patient_id)

    context = {
        'patient': patient,
        'billings': billings,
    }
    return render(request, 'healthcare/admin/payment_create.html', context)


@login_required
@require_role('office_admin')
def admin_payment_edit(request, patient_id, payment_id):
    """Admin: Edit payment for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    payment = get_object_or_404(Payment, payment_id=payment_id, patient=patient)
    billings = Billing.objects.filter(patient=patient).order_by('-billing_date')

    if request.method == 'POST':
        old_amount = payment.amount
        old_billing = payment.billing

        payment.billing_id = request.POST.get('billing_id') or None
        payment.payment_date = request.POST['payment_date']
        payment.amount = request.POST['amount']
        payment.payment_method = request.POST.get('payment_method', 'Cash')
        payment.transaction_id = request.POST.get('transaction_id', '')
        payment.status = request.POST.get('status', 'Completed')
        payment.notes = request.POST.get('notes', '')
        payment.save()

        # Update billing amounts
        if old_billing:
            old_billing.amount_paid = float(old_billing.amount_paid or 0) - float(old_amount)
            old_billing.amount_due = float(old_billing.total_amount) - float(old_billing.amount_paid)
            if old_billing.amount_due <= 0:
                old_billing.status = 'Paid'
            elif old_billing.amount_paid > 0:
                old_billing.status = 'Partially Paid'
            else:
                old_billing.status = 'Pending'
            old_billing.save()

        if payment.billing:
            billing = payment.billing
            billing.amount_paid = float(billing.amount_paid or 0) + float(payment.amount)
            billing.amount_due = float(billing.total_amount) - float(billing.amount_paid)
            if billing.amount_due <= 0:
                billing.status = 'Paid'
            elif billing.amount_paid > 0:
                billing.status = 'Partially Paid'
            billing.save()

        messages.success(request, f'Payment updated successfully for {patient.full_name}.')
        return redirect('patient_payment_list', patient_id=patient.patient_id)

    context = {
        'patient': patient,
        'payment': payment,
        'billings': billings,
    }
    return render(request, 'healthcare/admin/payment_edit.html', context)


@login_required
@require_role('office_admin')
def admin_profile(request):
    """Office Administrator profile view - shows admin's own information"""
    admin_profile = request.user.profile

    # Get recent activity statistics
    stats = {
        'total_patients': Patient.objects.filter(is_active=True).count(),
        'total_providers': Provider.objects.filter(is_active=True).count(),
        'total_appointments_today': Encounter.objects.filter(
            encounter_date__date=timezone.now().date()
        ).count(),
        'pending_billings': Billing.objects.filter(
            status__in=['Pending', 'Partially Paid']
        ).count(),
    }

    # Recent actions
    recent_patients = Patient.objects.filter(is_active=True).order_by('-patient_id')[:10]
    recent_appointments = Encounter.objects.select_related('patient', 'provider').order_by('-encounter_date')[:10]
    recent_billings = Billing.objects.select_related('patient').order_by('-billing_date')[:10]

    context = {
        'admin_profile': admin_profile,
        'stats': stats,
        'recent_patients': recent_patients,
        'recent_appointments': recent_appointments,
        'recent_billings': recent_billings,
    }

    return render(request, 'healthcare/admin/profile.html', context)


@login_required
@require_role('office_admin')
def admin_profile_edit(request):
    """Edit office administrator profile - admins can edit their own information"""
    admin_profile = request.user.profile

    if request.method == 'POST':
        # Update user information
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.email = request.POST.get('email', request.user.email)
        request.user.save()

        # Update profile information
        admin_profile.phone = request.POST.get('phone', admin_profile.phone)
        admin_profile.date_of_birth = request.POST.get('date_of_birth') or admin_profile.date_of_birth
        admin_profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('admin_profile')

    context = {
        'admin_profile': admin_profile,
    }

    return render(request, 'healthcare/admin/profile_edit.html', context)


# ============================================================================
# NURSE VIEWS
# ============================================================================

@login_required
@require_role('nurse')
def nurse_dashboard(request):
    """Nurse Dashboard - view patients, appointments, and vitals management"""
    # Get statistics
    stats = {
        'total_patients': Patient.objects.filter(is_active=True).count(),
        'total_appointments_today': Encounter.objects.filter(
            encounter_date__date=timezone.now().date()
        ).count(),
        'total_appointments_upcoming': Encounter.objects.filter(
            encounter_date__gt=timezone.now(),
            status='Scheduled'
        ).count(),
        'total_vitals_recorded_today': VitalSign.objects.filter(
            recorded_at__date=timezone.now().date()
        ).count(),
    }

    # Recent activity
    recent_patients = Patient.objects.filter(is_active=True).order_by('-patient_id')[:10]
    upcoming_appointments = Encounter.objects.filter(
        encounter_date__gte=timezone.now(),
        status='Scheduled'
    ).select_related('patient', 'provider').order_by('encounter_date')[:10]

    recent_vitals = VitalSign.objects.select_related(
        'encounter__patient', 'encounter__provider'
    ).order_by('-recorded_at')[:10]

    # Today's appointments
    todays_appointments = Encounter.objects.filter(
        encounter_date__date=timezone.now().date()
    ).select_related('patient', 'provider').order_by('encounter_date')

    context = {
        'stats': stats,
        'recent_patients': recent_patients,
        'upcoming_appointments': upcoming_appointments,
        'recent_vitals': recent_vitals,
        'todays_appointments': todays_appointments,
    }

    return render(request, 'healthcare/nurse/dashboard.html', context)


@login_required
@require_role('nurse')
def nurse_profile(request):
    """Nurse profile view - shows nurse's own information"""
    nurse_profile = request.user.profile

    # Get recent vitals recorded (recent activity)
    recent_vitals = VitalSign.objects.select_related(
        'encounter__patient', 'encounter__provider'
    ).order_by('-recorded_at')[:20]

    # Get statistics for nurse's work
    stats = {
        'patients_seen_today': Encounter.objects.filter(
            encounter_date__date=timezone.now().date()
        ).values('patient').distinct().count(),
        'vitals_recorded_today': VitalSign.objects.filter(
            recorded_at__date=timezone.now().date()
        ).count(),
        'appointments_today': Encounter.objects.filter(
            encounter_date__date=timezone.now().date()
        ).count(),
    }

    context = {
        'nurse_profile': nurse_profile,
        'recent_vitals': recent_vitals,
        'stats': stats,
    }

    return render(request, 'healthcare/nurse/profile.html', context)


@login_required
@require_role('nurse')
def nurse_profile_edit(request):
    """Edit nurse profile - nurses can edit their own information"""
    nurse_profile = request.user.profile

    if request.method == 'POST':
        # Update user information
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.email = request.POST.get('email', request.user.email)
        request.user.save()

        # Update profile information
        nurse_profile.phone = request.POST.get('phone', nurse_profile.phone)
        nurse_profile.date_of_birth = request.POST.get('date_of_birth') or nurse_profile.date_of_birth
        nurse_profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('nurse_profile')

    context = {
        'nurse_profile': nurse_profile,
    }

    return render(request, 'healthcare/nurse/profile_edit.html', context)


@login_required
@require_role('nurse')
def nurse_patients_list(request):
    """Nurse view of all patients - with quick access to add vitals"""
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

    context = {
        'patients': patients,
        'search': search,
    }

    return render(request, 'healthcare/nurse/patients_list.html', context)


@login_required
@require_role('nurse')
def nurse_vitals_list(request):
    """Nurse view of all recent vital signs"""
    # Filter options
    date_filter = request.GET.get('date', '')
    patient_search = request.GET.get('patient', '')

    vitals = VitalSign.objects.select_related(
        'encounter__patient', 'encounter__provider', 'recorded_by'
    ).order_by('-recorded_at')

    if date_filter == 'today':
        vitals = vitals.filter(recorded_at__date=timezone.now().date())
    elif date_filter == 'week':
        from datetime import timedelta
        week_ago = timezone.now() - timedelta(days=7)
        vitals = vitals.filter(recorded_at__gte=week_ago)
    elif date_filter == 'month':
        from datetime import timedelta
        month_ago = timezone.now() - timedelta(days=30)
        vitals = vitals.filter(recorded_at__gte=month_ago)

    if patient_search:
        vitals = vitals.filter(
            Q(encounter__patient__first_name__icontains=patient_search) |
            Q(encounter__patient__last_name__icontains=patient_search)
        )

    # Paginate results
    vitals = vitals[:100]  # Limit to recent 100

    context = {
        'vitals': vitals,
        'date_filter': date_filter,
        'patient_search': patient_search,
    }

    return render(request, 'healthcare/nurse/vitals_list.html', context)
