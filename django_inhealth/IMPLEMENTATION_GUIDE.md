# InHealth EHR - Role-Based System Implementation Guide

## Overview

This guide documents the implementation of a comprehensive role-based Electronic Health Records (EHR) system with three distinct user types: **Patients**, **Doctors**, and **Office Administrators**.

---

## Phase 1: Database Schema & Models ✅ COMPLETED

### What Was Implemented

#### 1. New Models Added

**Hospital Model**
- Represents medical facilities/hospitals
- Fields: name, address, city, state, zip_code, phone, email, website
- Serves as the parent entity for departments and providers

**UserProfile Model**
- Extends Django User model with role-based access
- Three roles: `patient`, `doctor`, `office_admin`
- Helper properties: `is_patient()`, `is_doctor()`, `is_office_admin()`
- Links Django authentication users to their EHR roles

**Message Model**
- Secure patient-doctor communication
- Supports threaded conversations (parent_message)
- Tracks read status and timestamps
- Enables HIPAA-compliant messaging

**LabTest Model**
- Lab order and result management
- Status tracking: Ordered → Collected → In Progress → Completed
- Abnormal flag for critical results
- Reference ranges and result values

**Notification Model**
- System alerts and reminders
- Types: appointment, lab_result, prescription, message, system
- Read status tracking
- User-specific notifications

#### 2. Relationship Updates

**Critical Foreign Keys Added:**
```python
# Patient assigned to primary doctor
Patient.primary_doctor → Provider

# Patient linked to user account
Patient.user → User (OneToOne)

# Provider affiliated with hospital
Provider.hospital → Hospital

# Provider linked to user account
Provider.user → User (OneToOne)

# Department belongs to hospital
Department.hospital → Hospital
```

**Enhanced Existing Relationships:**
```python
# Changed from integer to ForeignKey
VitalSign.recorded_by → Provider
Diagnosis.diagnosed_by → Provider
```

#### 3. Admin Panel Configuration

All models registered with:
- List displays showing relationships
- Search and filter capabilities
- raw_id_fields for performance optimization
- Date hierarchies for temporal data

### Database Schema Summary

```
hospitals
├── departments
│   └── providers (doctors)
│       └── patients (primary_patients)
│
user_profiles (role: patient/doctor/office_admin)
├── patients → user, primary_doctor
├── providers → user, hospital
│
encounters → patient, provider
├── vital_signs → recorded_by
├── diagnoses → diagnosed_by
├── prescriptions → patient, provider
└── lab_tests → patient, provider

messages → sender, recipient
notifications → user
```

---

## Phase 2: Database Migrations & Setup ⚠️ NEXT STEP

### Prerequisites

1. **Activate Virtual Environment:**
   ```bash
   cd /home/user/inhealthUSA/django_inhealth
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Database:**
   - Edit `inhealth/settings.py` if needed
   - Ensure PostgreSQL is running
   - Database credentials configured

### Migration Steps

```bash
# Generate migrations
python manage.py makemigrations

# Review migration files
python manage.py showmigrations

# Apply migrations
python manage.py migrate

# Create superuser for testing
python manage.py createsuperuser
```

### Sample Data Creation

```python
# Create via Django shell
python manage.py shell

from django.contrib.auth.models import User
from healthcare.models import Hospital, UserProfile, Provider, Patient, Department

# Create hospital
hospital = Hospital.objects.create(
    name="General Hospital",
    address="123 Medical Center Dr",
    city="Springfield",
    state="IL",
    zip_code="62701",
    phone="555-0100"
)

# Create department
dept = Department.objects.create(
    hospital=hospital,
    department_name="Family Medicine",
    location="Building A, Floor 2"
)

# Create doctor user
doctor_user = User.objects.create_user(
    username='dr.smith',
    email='smith@hospital.com',
    password='securepass',
    first_name='John',
    last_name='Smith'
)

# Create doctor profile
UserProfile.objects.create(
    user=doctor_user,
    role='doctor'
)

# Create provider record
provider = Provider.objects.create(
    user=doctor_user,
    hospital=hospital,
    department=dept,
    first_name='John',
    last_name='Smith',
    npi='1234567890',
    specialty='Family Medicine',
    email='smith@hospital.com'
)

# Create patient user
patient_user = User.objects.create_user(
    username='john.doe',
    email='john.doe@email.com',
    password='patientpass',
    first_name='John',
    last_name='Doe'
)

# Create patient profile
UserProfile.objects.create(
    user=patient_user,
    role='patient'
)

# Create patient record
patient = Patient.objects.create(
    user=patient_user,
    primary_doctor=provider,
    first_name='John',
    last_name='Doe',
    date_of_birth='1980-01-15',
    gender='Male',
    email='john.doe@email.com',
    phone='555-0123'
)
```

---

## Phase 3: Role-Based Authentication & Permissions 📋 TO DO

### Required Implementation

#### 1. Create Middleware (`healthcare/middleware.py`)

```python
from django.shortcuts import redirect
from django.urls import reverse

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            role = request.user.profile.role
            path = request.path

            # Patient portal: /patient/*
            if path.startswith('/patient/') and role != 'patient':
                return redirect('access_denied')

            # Doctor portal: /doctor/*
            if path.startswith('/doctor/') and role != 'doctor':
                return redirect('access_denied')

            # Admin portal: /admin-portal/*
            if path.startswith('/admin-portal/') and role != 'office_admin':
                return redirect('access_denied')

        response = self.get_response(request)
        return response
```

#### 2. Add Middleware to Settings

```python
# inhealth/settings.py
MIDDLEWARE = [
    # ... existing middleware ...
    'healthcare.middleware.RoleBasedAccessMiddleware',
]
```

#### 3. Create Custom Decorators (`healthcare/decorators.py`)

```python
from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def patient_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'patient':
            return redirect('access_denied')
        return view_func(request, *args, **kwargs)
    return wrapped_view

def doctor_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'doctor':
            return redirect('access_denied')
        return view_func(request, *args, **kwargs)
    return wrapped_view

def office_admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'office_admin':
            return redirect('access_denied')
        return view_func(request, *args, **kwargs)
    return wrapped_view
```

#### 4. Update Login View to Route by Role

```python
# healthcare/views.py
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Route based on role
            if hasattr(user, 'profile'):
                role = user.profile.role
                if role == 'patient':
                    return redirect('patient_dashboard')
                elif role == 'doctor':
                    return redirect('doctor_dashboard')
                elif role == 'office_admin':
                    return redirect('admin_dashboard')

            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'healthcare/auth/login.html', {'form': form})
```

---

## Phase 4: Patient Portal 📋 TO DO

### Functional Requirements

#### Dashboard (`/patient/dashboard/`)
- Display upcoming appointments
- Show recent lab results
- List active prescriptions
- Display primary doctor information
- Show recent messages
- Notification center

#### Medical Records (`/patient/records/`)
- View visit history
- View lab results
- View prescriptions
- View allergies
- View immunizations
- View medical history

#### Appointments (`/patient/appointments/`)
- Book new appointment with primary doctor
- View upcoming appointments
- View past appointments
- Cancel appointments
- Reschedule appointments

#### Messages (`/patient/messages/`)
- Inbox/outbox
- Send message to primary doctor
- View message threads
- Mark as read

#### Profile (`/patient/profile/`)
- View/edit personal information
- Update contact details
- Update emergency contacts
- View insurance information

### URL Configuration

```python
# healthcare/urls.py - Patient Portal URLs
urlpatterns = [
    # Patient Portal
    path('patient/dashboard/', patient_dashboard, name='patient_dashboard'),
    path('patient/records/', patient_records, name='patient_records'),
    path('patient/appointments/', patient_appointments, name='patient_appointments'),
    path('patient/appointments/book/', patient_book_appointment, name='patient_book_appointment'),
    path('patient/messages/', patient_messages, name='patient_messages'),
    path('patient/messages/compose/', patient_compose_message, name='patient_compose_message'),
    path('patient/profile/', patient_profile, name='patient_profile'),
    path('patient/lab-results/', patient_lab_results, name='patient_lab_results'),
]
```

### Sample View Implementation

```python
# healthcare/views.py
from healthcare.decorators import patient_required
from healthcare.models import Patient, Encounter, Prescription, LabTest, Message

@patient_required
def patient_dashboard(request):
    patient = request.user.patient_profile

    context = {
        'patient': patient,
        'primary_doctor': patient.primary_doctor,
        'upcoming_appointments': Encounter.objects.filter(
            patient=patient,
            encounter_date__gte=timezone.now(),
            status='Scheduled'
        ).order_by('encounter_date')[:5],
        'recent_labs': LabTest.objects.filter(
            patient=patient,
            status='Completed'
        ).order_by('-result_date')[:5],
        'active_prescriptions': Prescription.objects.filter(
            patient=patient,
            status='Active'
        ).order_by('-start_date')[:5],
        'unread_messages': Message.objects.filter(
            recipient=request.user,
            is_read=False
        ).count(),
        'notifications': request.user.notifications.filter(
            is_read=False
        ).order_by('-created_at')[:5],
    }
    return render(request, 'healthcare/patient/dashboard.html', context)
```

---

## Phase 5: Doctor Portal 📋 TO DO

### Functional Requirements

#### Dashboard (`/doctor/dashboard/`)
- Today's appointment schedule
- Patient list overview
- Pending lab results
- Unread messages
- Task summary

#### Patient List (`/doctor/patients/`)
- View all assigned patients
- Search patients
- Quick access to patient records
- Filter by various criteria

#### Patient Details (`/doctor/patient/<id>/`)
- Complete health history
- All encounters
- Lab results
- Prescriptions
- Clinical notes
- Allergies and medical history

#### Appointments (`/doctor/appointments/`)
- Calendar view
- Schedule management
- Appointment details
- Check-in patients
- Update appointment status

#### Clinical Documentation (`/doctor/encounter/<id>/`)
- Document visit notes
- Add diagnoses
- Order lab tests
- Write prescriptions
- Record vital signs
- Create treatment plans

#### Lab Management (`/doctor/labs/`)
- Order new lab tests
- Review pending results
- View completed results
- Flag abnormal results

#### Messages (`/doctor/messages/`)
- Secure communication with patients
- Reply to patient inquiries
- Inbox management

### URL Configuration

```python
# healthcare/urls.py - Doctor Portal URLs
urlpatterns = [
    # Doctor Portal
    path('doctor/dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('doctor/patients/', doctor_patient_list, name='doctor_patient_list'),
    path('doctor/patient/<int:patient_id>/', doctor_patient_detail, name='doctor_patient_detail'),
    path('doctor/appointments/', doctor_appointments, name='doctor_appointments'),
    path('doctor/encounter/<int:encounter_id>/', doctor_encounter, name='doctor_encounter'),
    path('doctor/encounter/<int:encounter_id>/vitals/', doctor_add_vitals, name='doctor_add_vitals'),
    path('doctor/encounter/<int:encounter_id>/diagnosis/', doctor_add_diagnosis, name='doctor_add_diagnosis'),
    path('doctor/labs/', doctor_labs, name='doctor_labs'),
    path('doctor/labs/order/<int:patient_id>/', doctor_order_lab, name='doctor_order_lab'),
    path('doctor/messages/', doctor_messages, name='doctor_messages'),
]
```

### Permission Logic

```python
# Ensure doctors can only access their assigned patients
@doctor_required
def doctor_patient_detail(request, patient_id):
    provider = request.user.provider_profile
    patient = get_object_or_404(Patient, patient_id=patient_id)

    # Check if this patient is assigned to this doctor
    if patient.primary_doctor != provider:
        return render(request, 'healthcare/access_denied.html', {
            'message': 'You do not have access to this patient\'s records.'
        })

    # ... continue with view logic
```

---

## Phase 6: Office Administrator Portal 📋 TO DO

### Functional Requirements

#### Dashboard (`/admin-portal/dashboard/`)
- System-wide statistics
- User activity overview
- Pending tasks
- System alerts

#### User Management (`/admin-portal/users/`)
- Create patient accounts
- Create doctor accounts
- Edit user profiles
- Assign patients to doctors
- Assign doctors to hospitals
- Reset passwords
- Deactivate accounts

#### Hospital Management (`/admin-portal/hospitals/`)
- Add/edit hospitals
- Manage departments
- View hospital statistics

#### Assignment Management (`/admin-portal/assignments/`)
- Assign patients to primary doctors
- Reassign patients
- View assignment history

#### Reporting (`/admin-portal/reports/`)
- Hospital capacity reports
- Appointment statistics
- User activity logs
- Compliance reports

#### Audit Logs (`/admin-portal/audit/`)
- User login history
- Data access logs
- System changes
- Security events

### URL Configuration

```python
# healthcare/urls.py - Admin Portal URLs
urlpatterns = [
    # Office Admin Portal
    path('admin-portal/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-portal/users/', admin_user_list, name='admin_user_list'),
    path('admin-portal/users/create/', admin_create_user, name='admin_create_user'),
    path('admin-portal/users/<int:user_id>/edit/', admin_edit_user, name='admin_edit_user'),
    path('admin-portal/assignments/', admin_assignments, name='admin_assignments'),
    path('admin-portal/hospitals/', admin_hospitals, name='admin_hospitals'),
    path('admin-portal/reports/', admin_reports, name='admin_reports'),
    path('admin-portal/audit/', admin_audit_logs, name='admin_audit_logs'),
]
```

### Sample View Implementation

```python
@office_admin_required
def admin_create_user(request):
    if request.method == 'POST':
        # Get form data
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        role = request.POST['role']
        password = request.POST['password']

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        # Create profile
        UserProfile.objects.create(user=user, role=role)

        # Create role-specific record
        if role == 'patient':
            primary_doctor_id = request.POST.get('primary_doctor')
            patient = Patient.objects.create(
                user=user,
                primary_doctor_id=primary_doctor_id,
                first_name=first_name,
                last_name=last_name,
                # ... other fields from form
            )
        elif role == 'doctor':
            hospital_id = request.POST.get('hospital')
            provider = Provider.objects.create(
                user=user,
                hospital_id=hospital_id,
                first_name=first_name,
                last_name=last_name,
                # ... other fields from form
            )

        messages.success(request, f'User {username} created successfully.')
        return redirect('admin_user_list')

    # GET request - show form
    context = {
        'hospitals': Hospital.objects.filter(is_active=True),
        'doctors': Provider.objects.filter(is_active=True),
    }
    return render(request, 'healthcare/admin/create_user.html', context)
```

---

## Phase 7: Messaging System 📋 TO DO

### Implementation Steps

#### 1. Create Message Views

```python
# healthcare/views.py
from healthcare.models import Message

@login_required
def message_inbox(request):
    messages = Message.objects.filter(
        recipient=request.user
    ).order_by('-created_at')

    unread_count = messages.filter(is_read=False).count()

    return render(request, 'healthcare/messages/inbox.html', {
        'messages': messages,
        'unread_count': unread_count
    })

@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, message_id=message_id)

    # Check permissions
    if message.recipient != request.user and message.sender != request.user:
        return redirect('access_denied')

    # Mark as read
    if message.recipient == request.user and not message.is_read:
        message.is_read = True
        message.read_at = timezone.now()
        message.save()

    # Get thread
    if message.parent_message:
        thread = Message.objects.filter(
            models.Q(message_id=message.parent_message_id) |
            models.Q(parent_message=message.parent_message)
        ).order_by('created_at')
    else:
        thread = Message.objects.filter(
            models.Q(message_id=message_id) |
            models.Q(parent_message_id=message_id)
        ).order_by('created_at')

    return render(request, 'healthcare/messages/detail.html', {
        'message': message,
        'thread': thread
    })

@login_required
def message_compose(request):
    if request.method == 'POST':
        recipient_id = request.POST['recipient']
        subject = request.POST['subject']
        body = request.POST['body']
        parent_message_id = request.POST.get('parent_message')

        message = Message.objects.create(
            sender=request.user,
            recipient_id=recipient_id,
            subject=subject,
            body=body,
            parent_message_id=parent_message_id
        )

        # Create notification
        Notification.objects.create(
            user_id=recipient_id,
            title='New Message',
            message=f'You have a new message from {request.user.get_full_name()}',
            notification_type='message'
        )

        messages.success(request, 'Message sent successfully.')
        return redirect('message_inbox')

    # Get allowed recipients based on role
    if hasattr(request.user, 'profile'):
        if request.user.profile.is_patient:
            # Patient can only message their primary doctor
            patient = request.user.patient_profile
            recipients = [patient.primary_doctor.user] if patient.primary_doctor and patient.primary_doctor.user else []
        elif request.user.profile.is_doctor:
            # Doctor can message their patients
            provider = request.user.provider_profile
            recipients = [p.user for p in provider.primary_patients.all() if p.user]
        else:
            recipients = []

    return render(request, 'healthcare/messages/compose.html', {
        'recipients': recipients
    })
```

#### 2. Create Message Templates

Create these template files:
- `healthcare/templates/healthcare/messages/inbox.html`
- `healthcare/templates/healthcare/messages/detail.html`
- `healthcare/templates/healthcare/messages/compose.html`

---

## Phase 8: Appointment Booking 📋 TO DO

### Patient Appointment Booking

```python
@patient_required
def patient_book_appointment(request):
    patient = request.user.patient_profile

    if request.method == 'POST':
        encounter_date = request.POST['encounter_date']
        encounter_type = request.POST['encounter_type']
        chief_complaint = request.POST.get('chief_complaint', '')

        # Create appointment with primary doctor
        encounter = Encounter.objects.create(
            patient=patient,
            provider=patient.primary_doctor,
            encounter_date=encounter_date,
            encounter_type=encounter_type,
            chief_complaint=chief_complaint,
            status='Scheduled'
        )

        # Create notification for doctor
        if patient.primary_doctor and patient.primary_doctor.user:
            Notification.objects.create(
                user=patient.primary_doctor.user,
                title='New Appointment Request',
                message=f'{patient.full_name} has requested an appointment for {encounter_date}',
                notification_type='appointment'
            )

        messages.success(request, 'Appointment booked successfully.')
        return redirect('patient_appointments')

    return render(request, 'healthcare/patient/book_appointment.html', {
        'patient': patient,
        'encounter_types': Encounter._meta.get_field('encounter_type').choices
    })
```

---

## Phase 9: Testing & Security 📋 TO DO

### Security Checklist

- [ ] HIPAA compliance audit
- [ ] Data encryption at rest and in transit
- [ ] Secure password policies
- [ ] Session timeout implementation
- [ ] Audit logging for all data access
- [ ] SQL injection prevention (Django ORM)
- [ ] XSS prevention (template escaping)
- [ ] CSRF protection (enabled by default)
- [ ] Role-based access control testing
- [ ] Data backup procedures
- [ ] Disaster recovery plan

### Testing Requirements

1. **Unit Tests**
   - Model tests
   - View tests
   - Form tests
   - Permission tests

2. **Integration Tests**
   - User workflows
   - Role-based access
   - Messaging system
   - Appointment booking

3. **Security Tests**
   - Authorization testing
   - Authentication testing
   - Data access control
   - SQL injection attempts
   - XSS attempts

---

## Installation & Deployment

### Development Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd inhealthUSA/django_inhealth

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Production Deployment

Follow the installation scripts:
- For Ubuntu 24: `./install_ubuntu24.sh`
- For Rocky Linux 9: `./install_rocky9.sh`

---

## Summary of Current Status

### ✅ Completed
- Database schema design with all relationships
- Models for Hospital, UserProfile, Message, LabTest, Notification
- Updated Patient and Provider models with relationships
- Admin panel configuration
- Git commit and push of changes

### 📋 Next Steps (In Priority Order)
1. Run database migrations
2. Create sample data for testing
3. Implement role-based authentication middleware
4. Build Patient portal (views + templates)
5. Build Doctor portal (views + templates)
6. Build Office Administrator portal (views + templates)
7. Implement messaging system
8. Implement appointment booking
9. Add security features and audit logging
10. Comprehensive testing
11. HIPAA compliance review
12. Production deployment

---

## Questions & Support

For implementation questions or issues, please refer to:
- Django Documentation: https://docs.djangoproject.com/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- HIPAA Compliance Guide: https://www.hhs.gov/hipaa/

---

**Last Updated:** 2024-11-11
**Version:** 1.0
**Status:** Phase 1 Complete - Database Schema Implemented
