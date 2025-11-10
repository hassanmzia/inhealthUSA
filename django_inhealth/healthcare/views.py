from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import (
    Patient, Provider, Encounter, VitalSign, Diagnosis,
    Prescription, Department, Allergy, MedicalHistory, SocialHistory
)


def index(request):
    """Dashboard/Home view"""
    context = {
        'total_patients': Patient.objects.filter(is_active=True).count(),
        'total_providers': Provider.objects.filter(is_active=True).count(),
        'total_appointments_today': Encounter.objects.filter(
            encounter_date__date=timezone.now().date()
        ).count(),
        'recent_appointments': Encounter.objects.select_related('patient', 'provider').order_by('-encounter_date')[:10],
    }
    return render(request, 'healthcare/index.html', context)


# Patient Views
def patient_list(request):
    """List all patients"""
    search = request.GET.get('search', '')
    patients = Patient.objects.filter(is_active=True)

    if search:
        patients = patients.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(ssn__icontains=search)
        )

    patients = patients.order_by('last_name', 'first_name')
    return render(request, 'healthcare/patients/index.html', {'patients': patients, 'search': search})


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


def patient_edit(request, patient_id):
    """Edit patient"""
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
        return redirect('patient_detail', patient_id=patient.patient_id)

    return render(request, 'healthcare/patients/edit.html', {'patient': patient})


# Physician (Provider) Views
def physician_list(request):
    """List all physicians"""
    search = request.GET.get('search', '')
    physicians = Provider.objects.filter(is_active=True)

    if search:
        physicians = physicians.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(npi__icontains=search) |
            Q(specialty__icontains=search)
        )

    physicians = physicians.order_by('last_name', 'first_name')
    return render(request, 'healthcare/physicians/index.html', {'physicians': physicians, 'search': search})


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
def appointment_list(request):
    """List all appointments"""
    status = request.GET.get('status', '')
    appointments = Encounter.objects.select_related('patient', 'provider', 'department')

    if status:
        appointments = appointments.filter(status=status)

    appointments = appointments.order_by('-encounter_date')
    return render(request, 'healthcare/appointments/index.html', {'appointments': appointments, 'status': status})


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


def appointment_edit(request, encounter_id):
    """Edit appointment"""
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
        return redirect('appointment_detail', encounter_id=appointment.encounter_id)

    physicians = Provider.objects.filter(is_active=True).order_by('last_name', 'first_name')
    departments = Department.objects.filter(is_active=True).order_by('department_name')

    context = {
        'appointment': appointment,
        'physicians': physicians,
        'departments': departments,
    }
    return render(request, 'healthcare/appointments/edit.html', context)


# Vital Signs Views
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
def prescription_list(request):
    """List all prescriptions"""
    status = request.GET.get('status', '')
    prescriptions = Prescription.objects.select_related('patient', 'provider')

    if status:
        prescriptions = prescriptions.filter(status=status)

    prescriptions = prescriptions.order_by('-start_date')
    return render(request, 'healthcare/prescriptions/index.html', {'prescriptions': prescriptions, 'status': status})


def prescription_detail(request, prescription_id):
    """View prescription details"""
    prescription = get_object_or_404(Prescription, prescription_id=prescription_id)
    return render(request, 'healthcare/prescriptions/show.html', {'prescription': prescription})


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
