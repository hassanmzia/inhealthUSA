# AI-Powered Treatment Plan System with Ollama/Llama 3.2

## Overview

This system uses local Ollama with Llama 3.2 model to generate intelligent treatment plan proposals for doctors. The AI analyzes patient data including vital signs, diagnoses, lab results, and medical history to create comprehensive treatment recommendations.

**Key Features:**
- AI-generated treatment proposals (doctors only)
- Doctor's final treatment plans (visible to patients)
- Complete patient data integration
- Ollama/Llama 3.2 local AI model
- Privacy-focused (AI proposals never shown to patients)

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Models](#models)
3. [Ollama Integration](#ollama-integration)
4. [Treatment Plan Generation](#treatment-plan-generation)
5. [Setup and Configuration](#setup-and-configuration)
6. [Usage Examples](#usage-examples)
7. [Views and URLs](#views-and-urls)
8. [Templates](#templates)
9. [API Reference](#api-reference)
10. [Troubleshooting](#troubleshooting)

---

## System Architecture

### Data Flow

```
Patient Data → AI Proposal Generator → Ollama/Llama 3.2 → AI Proposed Treatment Plan
                                                                      ↓
                                                            Doctor Reviews & Modifies
                                                                      ↓
                                                            Doctor's Treatment Plan
                                                                      ↓
                                                            Published to Patient
```

### Key Components

1. **AIProposedTreatmentPlan Model**
   - Stores AI-generated proposals
   - Only visible to doctors
   - Tracks review status and doctor feedback

2. **DoctorTreatmentPlan Model**
   - Doctor's final treatment plan
   - Visible to patients when published
   - Can be linked to AI proposal

3. **TreatmentPlanGenerator**
   - Gathers patient data
   - Builds AI prompts
   - Interfaces with Ollama API
   - Parses AI responses

4. **OllamaAPIClient**
   - Handles Ollama API communication
   - Manages timeouts and errors
   - Tracks generation metrics

---

## Models

### AIProposedTreatmentPlan

**Purpose:** Store AI-generated treatment proposals for doctor review

**Key Fields:**
```python
- patient: FK to Patient
- provider: FK to Provider (doctor who requested)
- proposed_treatment: Full AI-generated text
- medications_suggested: Parsed medications section
- lifestyle_recommendations: Parsed lifestyle section
- follow_up_recommendations: Parsed follow-up section
- warnings_and_precautions: Parsed warnings section
- ai_model_name: 'llama3.2'
- generation_time_seconds: How long it took
- status: pending/reviewed/accepted/modified/rejected
- doctor_notes: Doctor's feedback on proposal
```

**Methods:**
```python
mark_as_reviewed(doctor_notes=None)
mark_as_accepted(doctor_notes=None)
mark_as_modified(doctor_notes=None)
mark_as_rejected(doctor_notes=None)
```

### DoctorTreatmentPlan

**Purpose:** Doctor's final treatment plan visible to patients

**Key Fields:**
```python
- patient: FK to Patient
- provider: FK to Provider (doctor)
- encounter: FK to Encounter (optional)
- ai_proposal: FK to AIProposedTreatmentPlan (optional link)
- plan_title: Title of treatment plan
- assessment: Doctor's clinical assessment
- treatment_goals: Treatment objectives
- medications: Prescribed medications
- lifestyle_modifications: Lifestyle changes
- follow_up_instructions: Follow-up care
- status: draft/active/completed/cancelled/superseded
- is_visible_to_patient: Boolean
- patient_viewed_at: When patient first viewed
- patient_acknowledged_at: When patient acknowledged
```

**Methods:**
```python
publish_to_patient()  # Make visible to patient
mark_patient_viewed()  # Track when patient views
mark_patient_acknowledged()  # Track acknowledgment
supersede()  # Mark as replaced by newer plan
is_current()  # Check if currently active
```

---

## Ollama Integration

### OllamaAPIClient Class

**Location:** `healthcare/ai_treatment_generator.py`

**Configuration:**
```python
# Default settings
base_url = 'http://localhost:11434'  # Ollama default port
model = 'llama3.2'
```

**Methods:**

1. **generate(prompt, stream=False, options=None)**
   - Generates text from prompt
   - Returns dict with response, tokens, generation time

2. **chat(messages, stream=False, options=None)**
   - Chat-based generation
   - Accepts list of messages

**Example:**
```python
from healthcare.ai_treatment_generator import OllamaAPIClient

client = OllamaAPIClient(model='llama3.2')
result = client.generate(
    prompt="Generate a treatment plan...",
    options={
        'temperature': 0.7,
        'top_p': 0.9,
        'top_k': 40
    }
)

print(f"Response: {result['response']}")
print(f"Time: {result['generation_time']}s")
print(f"Tokens: {result['prompt_tokens']} + {result['completion_tokens']}")
```

---

## Treatment Plan Generation

### TreatmentPlanGenerator Class

**Location:** `healthcare/ai_treatment_generator.py`

**Process:**

1. **Gather Patient Data**
   ```python
   def gather_patient_data(patient):
       # Collects:
       - Demographics (age, gender, DOB)
       - Recent vital signs (last 10)
       - Diagnoses (last 10)
       - Lab tests (last 15)
       - Medical history (all)
       - Family history (all)
       - Social history (smoking, alcohol, exercise, etc.)
   ```

2. **Build Treatment Prompt**
   ```python
   def build_treatment_prompt(patient_data):
       # Creates comprehensive prompt with:
       - Patient information
       - All vital signs formatted
       - All diagnoses with ICD codes
       - Lab results with reference ranges
       - Medical and family history
       - Social factors
       - Instructions for AI to follow
       - Output format specification
   ```

3. **Generate with Ollama**
   ```python
   def generate_treatment_plan(patient, provider=None):
       # Generates AI proposal
       - Gathers data
       - Builds prompt
       - Calls Ollama API
       - Parses response
       - Creates AIProposedTreatmentPlan record
       - Returns proposal object
   ```

**Example Usage:**
```python
from healthcare.ai_treatment_generator import TreatmentPlanGenerator
from healthcare.models import Patient, Provider

# Create generator
generator = TreatmentPlanGenerator(model='llama3.2')

# Get patient and doctor
patient = Patient.objects.get(patient_id=123)
doctor = Provider.objects.get(provider_id=456)

# Generate AI proposal
proposal = generator.generate_treatment_plan(patient, doctor)

print(f"Proposal ID: {proposal.proposal_id}")
print(f"Status: {proposal.status}")
print(f"Generated in: {proposal.generation_time_seconds}s")
print(f"\n{proposal.proposed_treatment}")
```

**Convenience Function:**
```python
from healthcare.ai_treatment_generator import generate_ai_treatment_plan

# Simple one-liner
proposal = generate_ai_treatment_plan(
    patient_id=123,
    provider_id=456,
    model='llama3.2'
)
```

---

## Setup and Configuration

### 1. Install Ollama

```bash
# Install Ollama (macOS/Linux)
curl https://ollama.ai/install.sh | sh

# Or download from https://ollama.ai
```

### 2. Download Llama 3.2 Model

```bash
ollama pull llama3.2
```

### 3. Verify Ollama is Running

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Should return list of installed models
```

### 4. Configure Django Settings

Add to `settings.py` or `.env`:
```python
# Ollama Configuration
OLLAMA_API_URL = 'http://localhost:11434'  # Default
OLLAMA_MODEL = 'llama3.2'  # Default model
OLLAMA_TIMEOUT = 300  # 5 minutes for generation
```

### 5. Run Migration

```bash
cd django_inhealth
python manage.py migrate healthcare
```

This creates:
- `ai_proposed_treatment_plans` table
- `doctor_treatment_plans` table
- All necessary indexes

### 6. Test Ollama Connection

```python
python manage.py shell

from healthcare.ai_treatment_generator import OllamaAPIClient

client = OllamaAPIClient()
result = client.generate("Test prompt: Say 'Hello World'")
print(result['response'])
```

---

## Usage Examples

### For Doctors

#### 1. Generate AI Treatment Proposal

```python
# In view or management command
from healthcare.models import Patient, Provider
from healthcare.ai_treatment_generator import TreatmentPlanGenerator

def generate_proposal_for_patient(request, patient_id):
    patient = Patient.objects.get(patient_id=patient_id)
    doctor = request.user.profile.provider  # Current logged-in doctor

    # Generate AI proposal
    generator = TreatmentPlanGenerator()
    proposal = generator.generate_treatment_plan(patient, doctor)

    # Proposal is now in database with status='pending'
    return proposal
```

#### 2. Review AI Proposal

```python
from healthcare.models import AIProposedTreatmentPlan

# Get proposal
proposal = AIProposedTreatmentPlan.objects.get(proposal_id=789)

# Review the AI suggestions
print(f"Proposed Treatment:\n{proposal.proposed_treatment}")
print(f"\nMedications:\n{proposal.medications_suggested}")
print(f"\nLifestyle:\n{proposal.lifestyle_recommendations}")

# Doctor decides to accept it
proposal.mark_as_accepted("This looks good, I'll use it as a base")

# Or modify
proposal.mark_as_modified("I adjusted the medication dosages")

# Or reject
proposal.mark_as_rejected("Not appropriate for this patient")
```

#### 3. Create Doctor's Treatment Plan (Based on AI Proposal)

```python
from healthcare.models import DoctorTreatmentPlan, AIProposedTreatmentPlan

# Get AI proposal
ai_proposal = AIProposedTreatmentPlan.objects.get(proposal_id=789)

# Create doctor's treatment plan based on AI proposal
plan = DoctorTreatmentPlan.objects.create(
    patient=ai_proposal.patient,
    provider=ai_proposal.provider,
    ai_proposal=ai_proposal,  # Link to AI proposal
    plan_title="Hypertension Management Plan",
    assessment="Patient has uncontrolled hypertension...",
    treatment_goals="1. Reduce BP to <130/80\n2. Improve medication compliance",
    medications=ai_proposal.medications_suggested,  # Use AI suggestion
    lifestyle_modifications="Based on AI: " + ai_proposal.lifestyle_recommendations,
    follow_up_instructions="Follow up in 2 weeks for BP check",
    status='draft'
)

# Review and publish to patient
plan.publish_to_patient()  # Sets status='active' and is_visible_to_patient=True
```

#### 4. Create Treatment Plan from Scratch

```python
# Without using AI proposal
plan = DoctorTreatmentPlan.objects.create(
    patient=patient,
    provider=doctor,
    plan_title="Diabetes Management Plan",
    assessment="Type 2 diabetes, A1C 8.5%",
    treatment_goals="Lower A1C to <7.0%",
    medications="Metformin 1000mg BID\nGlipizide 5mg daily",
    lifestyle_modifications="Low carb diet, 30min exercise daily",
    dietary_recommendations="Limit carbs to 150g/day, avoid sugary drinks",
    exercise_recommendations="Walk 30 minutes after meals",
    follow_up_instructions="Lab work in 3 months, office visit in 1 month",
    warning_signs="Severe hypoglycemia, DKA symptoms",
    emergency_instructions="Call 911 if unconscious or blood sugar <50",
    status='draft'
)

# Publish when ready
plan.publish_to_patient()
```

### For Patients

#### 1. View Treatment Plans

```python
from healthcare.models import DoctorTreatmentPlan

# Get current active treatment plans
patient = request.user.profile.patient
active_plans = DoctorTreatmentPlan.objects.filter(
    patient=patient,
    is_visible_to_patient=True,
    status='active'
).order_by('-created_at')

for plan in active_plans:
    print(f"Plan: {plan.plan_title}")
    print(f"Doctor: {plan.provider.full_name}")
    print(f"Start Date: {plan.plan_start_date}")

    # Mark as viewed
    plan.mark_patient_viewed()
```

#### 2. Acknowledge Treatment Plan

```python
plan = DoctorTreatmentPlan.objects.get(plan_id=456)

# Patient acknowledges understanding
plan.mark_patient_acknowledged()

# Add feedback
plan.patient_feedback = "I have a question about the medication schedule"
plan.save()
```

### Management Commands

#### Generate Proposals for All Patients with Recent Critical Vitals

```python
# management/commands/generate_treatment_proposals.py
from django.core.management.base import BaseCommand
from healthcare.models import VitalSign, Patient
from healthcare.ai_treatment_generator import generate_ai_treatment_plan
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Generate AI treatment proposals for patients with critical vitals'

    def handle(self, *args, **options):
        # Get patients with critical vitals in last 24 hours
        yesterday = timezone.now() - timedelta(days=1)

        critical_vitals = VitalSign.objects.filter(
            recorded_at__gte=yesterday
        ).filter(
            # Critical conditions
            Q(blood_pressure_systolic__gte=180) |
            Q(heart_rate__gte=120) |
            Q(oxygen_saturation__lte=90)
        ).select_related('encounter__patient', 'encounter__provider')

        for vital in critical_vitals:
            patient = vital.encounter.patient
            doctor = vital.encounter.provider

            # Check if proposal already exists for today
            today = timezone.now().date()
            existing = AIProposedTreatmentPlan.objects.filter(
                patient=patient,
                created_at__date=today
            ).exists()

            if not existing:
                self.stdout.write(f"Generating proposal for {patient.full_name}...")
                proposal = generate_ai_treatment_plan(
                    patient_id=patient.patient_id,
                    provider_id=doctor.provider_id if doctor else None
                )
                self.stdout.write(self.style.SUCCESS(f"✓ Created proposal {proposal.proposal_id}"))
```

---

## Views and URLs

### Recommended View Structure

#### views.py

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Patient, AIProposedTreatmentPlan, DoctorTreatmentPlan
from .ai_treatment_generator import TreatmentPlanGenerator
from .permissions import require_role

# Doctor Views

@login_required
@require_role('doctor')
def doctor_ai_proposals(request):
    """List all AI proposals for doctor's patients"""
    doctor = request.user.profile.provider
    proposals = AIProposedTreatmentPlan.objects.filter(
        provider=doctor
    ).select_related('patient').order_by('-created_at')

    context = {
        'proposals': proposals,
        'pending_count': proposals.filter(status='pending').count(),
    }
    return render(request, 'healthcare/doctor/ai_proposals_list.html', context)


@login_required
@require_role('doctor')
def doctor_view_ai_proposal(request, proposal_id):
    """View detailed AI proposal"""
    proposal = get_object_or_404(AIProposedTreatmentPlan, proposal_id=proposal_id)

    # Check permission
    if proposal.provider != request.user.profile.provider:
        messages.error(request, 'You do not have permission to view this proposal.')
        return redirect('doctor_dashboard')

    return render(request, 'healthcare/doctor/ai_proposal_detail.html', {'proposal': proposal})


@login_required
@require_role('doctor')
def doctor_generate_ai_proposal(request, patient_id):
    """Generate new AI treatment proposal for patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    doctor = request.user.profile.provider

    if request.method == 'POST':
        try:
            generator = TreatmentPlanGenerator()
            proposal = generator.generate_treatment_plan(patient, doctor)

            messages.success(request, f'AI treatment proposal generated successfully! (ID: {proposal.proposal_id})')
            return redirect('doctor_view_ai_proposal', proposal_id=proposal.proposal_id)
        except Exception as e:
            messages.error(request, f'Error generating proposal: {str(e)}')
            return redirect('doctor_patients_list')

    return render(request, 'healthcare/doctor/generate_ai_proposal.html', {'patient': patient})


@login_required
@require_role('doctor')
def doctor_treatment_plans(request):
    """List all treatment plans created by doctor"""
    doctor = request.user.profile.provider
    plans = DoctorTreatmentPlan.objects.filter(
        provider=doctor
    ).select_related('patient').order_by('-created_at')

    context = {
        'plans': plans,
        'draft_count': plans.filter(status='draft').count(),
        'active_count': plans.filter(status='active').count(),
    }
    return render(request, 'healthcare/doctor/treatment_plans_list.html', context)


@login_required
@require_role('doctor')
def doctor_create_treatment_plan(request, patient_id, proposal_id=None):
    """Create new treatment plan (optionally from AI proposal)"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    doctor = request.user.profile.provider
    ai_proposal = None

    if proposal_id:
        ai_proposal = get_object_or_404(AIProposedTreatmentPlan, proposal_id=proposal_id)

    if request.method == 'POST':
        # Handle form submission
        plan = DoctorTreatmentPlan.objects.create(
            patient=patient,
            provider=doctor,
            ai_proposal=ai_proposal,
            plan_title=request.POST.get('plan_title'),
            assessment=request.POST.get('assessment'),
            treatment_goals=request.POST.get('treatment_goals'),
            medications=request.POST.get('medications'),
            lifestyle_modifications=request.POST.get('lifestyle_modifications'),
            follow_up_instructions=request.POST.get('follow_up_instructions'),
            status='draft'
        )

        if request.POST.get('publish'):
            plan.publish_to_patient()
            messages.success(request, 'Treatment plan created and published to patient!')
        else:
            messages.success(request, 'Treatment plan saved as draft.')

        if ai_proposal:
            ai_proposal.mark_as_used()

        return redirect('doctor_treatment_plans')

    context = {
        'patient': patient,
        'ai_proposal': ai_proposal,
    }
    return render(request, 'healthcare/doctor/create_treatment_plan.html', context)


# Patient Views

@login_required
@require_role('patient')
def patient_treatment_plans(request):
    """List treatment plans for patient"""
    patient = request.user.profile.patient
    plans = DoctorTreatmentPlan.objects.filter(
        patient=patient,
        is_visible_to_patient=True
    ).select_related('provider').order_by('-created_at')

    return render(request, 'healthcare/patient/treatment_plans_list.html', {'plans': plans})


@login_required
@require_role('patient')
def patient_view_treatment_plan(request, plan_id):
    """View treatment plan detail"""
    patient = request.user.profile.patient
    plan = get_object_or_404(
        DoctorTreatmentPlan,
        plan_id=plan_id,
        patient=patient,
        is_visible_to_patient=True
    )

    # Mark as viewed
    plan.mark_patient_viewed()

    if request.method == 'POST':
        if 'acknowledge' in request.POST:
            plan.mark_patient_acknowledged()
            messages.success(request, 'Thank you for acknowledging your treatment plan.')

        if 'feedback' in request.POST:
            plan.patient_feedback = request.POST.get('feedback_text')
            plan.save()
            messages.success(request, 'Your feedback has been sent to your doctor.')

        return redirect('patient_view_treatment_plan', plan_id=plan_id)

    return render(request, 'healthcare/patient/treatment_plan_detail.html', {'plan': plan})
```

#### urls.py

```python
from django.urls import path
from . import views

urlpatterns = [
    # ... existing patterns ...

    # Doctor - AI Proposals
    path('doctor/ai-proposals/', views.doctor_ai_proposals, name='doctor_ai_proposals'),
    path('doctor/ai-proposals/<int:proposal_id>/', views.doctor_view_ai_proposal, name='doctor_view_ai_proposal'),
    path('doctor/patients/<int:patient_id>/generate-ai-proposal/', views.doctor_generate_ai_proposal, name='doctor_generate_ai_proposal'),

    # Doctor - Treatment Plans
    path('doctor/treatment-plans/', views.doctor_treatment_plans, name='doctor_treatment_plans'),
    path('doctor/patients/<int:patient_id>/create-treatment-plan/', views.doctor_create_treatment_plan, name='doctor_create_treatment_plan'),
    path('doctor/patients/<int:patient_id>/create-treatment-plan/<int:proposal_id>/', views.doctor_create_treatment_plan, name='doctor_create_treatment_plan_from_proposal'),

    # Patient - Treatment Plans
    path('patient/treatment-plans/', views.patient_treatment_plans, name='patient_treatment_plans'),
    path('patient/treatment-plans/<int:plan_id>/', views.patient_view_treatment_plan, name='patient_view_treatment_plan'),
]
```

---

## Templates

### Doctor Dashboard - AI Proposals Section

Add to `healthcare/templates/healthcare/doctor/dashboard.html`:

```html
<!-- AI Treatment Proposals Section -->
<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5><i class="fas fa-robot"></i> AI Treatment Proposals</h5>
            </div>
            <div class="card-body">
                {% if ai_proposals %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Patient</th>
                                <th>Status</th>
                                <th>Generated</th>
                                <th>Time</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for proposal in ai_proposals %}
                            <tr>
                                <td>{{ proposal.patient.full_name }}</td>
                                <td>
                                    <span class="badge bg-{% if proposal.status == 'pending' %}warning{% elif proposal.status == 'accepted' %}success{% elif proposal.status == 'rejected' %}danger{% else %}info{% endif %}">
                                        {{ proposal.get_status_display }}
                                    </span>
                                </td>
                                <td>{{ proposal.created_at|date:"M d, Y" }}</td>
                                <td>{{ proposal.generation_time_seconds|floatformat:1 }}s</td>
                                <td>
                                    <a href="{% url 'doctor_view_ai_proposal' proposal.proposal_id %}" class="btn btn-sm btn-primary">
                                        <i class="fas fa-eye"></i> Review
                                    </a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                <a href="{% url 'doctor_ai_proposals' %}" class="btn btn-outline-primary">View All Proposals</a>
                {% else %}
                <p class="text-muted">No AI proposals yet. Generate one from a patient's page.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
```

### Patient Dashboard - Treatment Plans Section

Add to `healthcare/templates/healthcare/patient/dashboard.html`:

```html
<!-- Treatment Plans Section -->
<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5><i class="fas fa-notes-medical"></i> My Treatment Plans</h5>
            </div>
            <div class="card-body">
                {% if treatment_plans %}
                <div class="list-group">
                    {% for plan in treatment_plans %}
                    <a href="{% url 'patient_view_treatment_plan' plan.plan_id %}" class="list-group-item list-group-item-action">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">{{ plan.plan_title }}</h6>
                            <small>{{ plan.plan_start_date|date:"M d, Y" }}</small>
                        </div>
                        <p class="mb-1 text-muted">Dr. {{ plan.provider.full_name }}</p>
                        <small>
                            {% if not plan.patient_viewed_at %}
                                <span class="badge bg-info">New</span>
                            {% endif %}
                            {% if plan.patient_acknowledged_at %}
                                <span class="badge bg-success">Acknowledged</span>
                            {% endif %}
                        </small>
                    </a>
                    {% endfor %}
                </div>
                {% else %}
                <p class="text-muted">No treatment plans available yet.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
```

---

## API Reference

### TreatmentPlanGenerator

```python
class TreatmentPlanGenerator:
    def __init__(self, model='llama3.2'):
        """Initialize with AI model name"""

    def gather_patient_data(self, patient):
        """
        Gather all relevant patient data
        Returns: dict with patient info, vitals, diagnoses, labs, history
        """

    def build_treatment_prompt(self, patient_data):
        """
        Build comprehensive prompt for AI
        Returns: str - formatted prompt
        """

    def parse_ai_response(self, ai_response):
        """
        Parse AI response into sections
        Returns: dict with parsed sections
        """

    def generate_treatment_plan(self, patient, provider=None):
        """
        Generate complete AI treatment proposal
        Returns: AIProposedTreatmentPlan instance
        """
```

### OllamaAPIClient

```python
class OllamaAPIClient:
    def __init__(self, base_url=None, model='llama3.2'):
        """Initialize with Ollama URL and model"""

    def generate(self, prompt, stream=False, options=None):
        """
        Generate text from prompt
        Returns: dict with 'response', 'prompt_tokens', 'completion_tokens', 'generation_time'
        """

    def chat(self, messages, stream=False, options=None):
        """
        Chat-based generation
        Returns: dict with response and metadata
        """
```

---

## Troubleshooting

### Ollama Not Responding

**Problem:** `Connection refused to localhost:11434`

**Solutions:**
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve

# Or restart
pkill ollama && ollama serve
```

### Model Not Found

**Problem:** `model 'llama3.2' not found`

**Solution:**
```bash
# Pull the model
ollama pull llama3.2

# Verify installation
ollama list
```

### Slow Generation Times

**Problem:** Treatment plan takes too long to generate

**Solutions:**
1. **Use smaller model:**
   ```python
   generator = TreatmentPlanGenerator(model='llama3.2:7b')  # Smaller variant
   ```

2. **Reduce patient data:**
   ```python
   # Limit vital signs to last 5 instead of 10
   recent_vitals = VitalSign.objects.filter(
       encounter__patient=patient
   ).order_by('-recorded_at')[:5]
   ```

3. **Adjust generation parameters:**
   ```python
   result = client.generate(
       prompt=prompt,
       options={
           'temperature': 0.5,  # Lower for faster, more deterministic
           'num_predict': 1000,  # Limit output length
       }
   )
   ```

### Error: No Patient Data

**Problem:** "Insufficient patient data for treatment plan"

**Solution:**
- Ensure patient has recent vital signs
- Check diagnosis records exist
- Verify medical history is populated
- Add minimum data requirements check

### Memory Issues

**Problem:** Server runs out of memory during generation

**Solutions:**
```bash
# Allocate more memory to Ollama
OLLAMA_NUM_THREADS=4 ollama serve

# Or use smaller model
ollama pull llama3.2:7b-instruct-q4_0  # Quantized version
```

---

## Best Practices

### 1. Data Quality

**Ensure comprehensive patient data:**
```python
def validate_patient_data_for_ai(patient):
    """Check if patient has enough data for AI generation"""
    checks = {
        'vitals': VitalSign.objects.filter(encounter__patient=patient).count() >= 3,
        'diagnoses': Diagnosis.objects.filter(encounter__patient=patient).exists(),
        'medical_history': MedicalHistory.objects.filter(patient=patient).exists(),
    }
    return all(checks.values()), checks
```

### 2. Doctor Review Required

**Always require doctor review before using AI proposals:**
```python
def create_plan_from_ai(proposal):
    """Enforce doctor review before creating treatment plan"""
    if proposal.status == 'pending':
        raise ValueError("AI proposal must be reviewed by doctor first")

    # Proceed with creating plan
    ...
```

### 3. Audit Trail

**Track all AI generations and doctor modifications:**
```python
class TreatmentPlanAuditLog(models.Model):
    plan = models.ForeignKey(DoctorTreatmentPlan, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)  # 'created', 'modified', 'published'
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changes = models.JSONField()  # What was changed
    timestamp = models.DateTimeField(auto_now_add=True)
```

### 4. Patient Privacy

**Never show AI proposals to patients:**
```python
# In patient views, filter out AI proposals
treatment_data = {
    'plans': DoctorTreatmentPlan.objects.filter(
        patient=patient,
        is_visible_to_patient=True
    ),
    # DO NOT include ai_treatment_proposals
}
```

### 5. Error Handling

**Gracefully handle AI generation failures:**
```python
try:
    proposal = generator.generate_treatment_plan(patient, doctor)
except requests.exceptions.Timeout:
    messages.error(request, "AI generation timed out. Please try again.")
except Exception as e:
    logger.error(f"AI generation failed: {str(e)}")
    messages.error(request, "Unable to generate AI proposal. Please create plan manually.")
```

---

## Security Considerations

1. **API Access Control**
   - Only doctors can generate AI proposals
   - Only doctors can view AI proposals
   - Patients never see AI proposals

2. **Data Privacy**
   - AI proposals contain PHI
   - Implement proper access controls
   - Audit all AI generations

3. **Local Processing**
   - Ollama runs locally (no data sent to cloud)
   - Patient data never leaves your server
   - HIPAA-compliant architecture

4. **Input Validation**
   - Sanitize patient data before sending to AI
   - Validate AI responses before saving
   - Prevent prompt injection attacks

---

## Performance Optimization

### 1. Async Generation

```python
from celery import shared_task

@shared_task
def generate_treatment_plan_async(patient_id, provider_id):
    """Generate AI proposal asynchronously"""
    patient = Patient.objects.get(patient_id=patient_id)
    provider = Provider.objects.get(provider_id=provider_id)

    generator = TreatmentPlanGenerator()
    proposal = generator.generate_treatment_plan(patient, provider)

    # Send notification to doctor
    notify_doctor_proposal_ready(provider, proposal)

    return proposal.proposal_id
```

### 2. Caching

```python
from django.core.cache import cache

def get_or_generate_proposal(patient_id, force=False):
    """Cache proposals to avoid regeneration"""
    cache_key = f"ai_proposal_{patient_id}"

    if not force:
        cached = cache.get(cache_key)
        if cached:
            return cached

    # Generate new
    proposal = generate_ai_treatment_plan(patient_id)
    cache.set(cache_key, proposal, timeout=3600)  # 1 hour

    return proposal
```

### 3. Batch Processing

```python
def generate_proposals_batch(patient_ids):
    """Generate multiple proposals efficiently"""
    generator = TreatmentPlanGenerator()

    for patient_id in patient_ids:
        patient = Patient.objects.get(patient_id=patient_id)
        try:
            proposal = generator.generate_treatment_plan(patient)
            print(f"✓ Generated for {patient.full_name}")
        except Exception as e:
            print(f"✗ Failed for {patient.full_name}: {e}")
```

---

## Future Enhancements

1. **Multi-Model Support**
   - Support multiple AI models (GPT-4, Claude, Mistral)
   - A/B testing of different models
   - Model performance comparison

2. **Fine-Tuning**
   - Fine-tune Llama on medical literature
   - Train on successful treatment outcomes
   - Specialty-specific models

3. **Feedback Loop**
   - Track treatment plan outcomes
   - Learn from doctor modifications
   - Improve AI suggestions over time

4. **Advanced Features**
   - Drug interaction checking
   - Evidence-based medicine references
   - Clinical decision support

5. **Integration**
   - HL7 FHIR compatibility
   - EHR system integration
   - Pharmacy system integration

---

## License and Disclaimer

**IMPORTANT MEDICAL DISCLAIMER:**

This AI treatment plan system is a **clinical decision support tool** and should NOT replace professional medical judgment. All AI-generated proposals must be reviewed and approved by licensed healthcare providers before use in patient care.

- AI proposals are suggestions only
- Doctors are responsible for final treatment decisions
- System should not be used for emergency medical decisions
- Regular review and validation of AI outputs is required

---

## Support and Contributing

For issues, questions, or contributions:

1. Check documentation first
2. Review troubleshooting section
3. Check system logs: `tail -f logs/django.log`
4. Contact technical support

---

## Changelog

### Version 1.0 (2025-11-16)

- ✅ AI treatment proposal generation with Ollama/Llama 3.2
- ✅ Doctor treatment plan creation and management
- ✅ Patient treatment plan viewing
- ✅ Comprehensive patient data integration
- ✅ Privacy-focused architecture (AI proposals for doctors only)
- ✅ Full admin interface
- ✅ Audit trail and tracking

---

## Quick Reference

### Generate AI Proposal
```python
from healthcare.ai_treatment_generator import generate_ai_treatment_plan
proposal = generate_ai_treatment_plan(patient_id=123, provider_id=456)
```

### Create Treatment Plan
```python
from healthcare.models import DoctorTreatmentPlan
plan = DoctorTreatmentPlan.objects.create(
    patient=patient,
    provider=doctor,
    plan_title="...",
    assessment="...",
    ...
)
plan.publish_to_patient()
```

### Patient View Plans
```python
plans = DoctorTreatmentPlan.objects.filter(
    patient=patient,
    is_visible_to_patient=True,
    status='active'
)
```

---

**End of Documentation**
