"""
AI Treatment Plan Generator using Ollama/Llama 3.2
Generates treatment plan proposals based on patient data
"""
import requests
import json
import time
from django.conf import settings
from django.utils import timezone
from .models import (
    Patient, AIProposedTreatmentPlan, VitalSign, Diagnosis,
    LabTest, MedicalHistory, FamilyHistory, SocialHistory
)


class OllamaAPIClient:
    """Client for interacting with Ollama API"""

    def __init__(self, base_url=None, model='llama3.2'):
        self.base_url = base_url or getattr(
            settings, 'OLLAMA_API_URL', 'http://localhost:11434'
        )
        self.model = model
        self.generate_endpoint = f"{self.base_url}/api/generate"
        self.chat_endpoint = f"{self.base_url}/api/chat"

    def generate(self, prompt, stream=False, options=None):
        """
        Generate text using Ollama API

        Args:
            prompt: Text prompt for generation
            stream: Whether to stream the response
            options: Dict of generation options (temperature, top_p, etc.)

        Returns:
            dict with 'response', 'tokens', and 'generation_time'
        """
        payload = {
            'model': self.model,
            'prompt': prompt,
            'stream': stream
        }

        if options:
            payload['options'] = options

        try:
            start_time = time.time()
            response = requests.post(
                self.generate_endpoint,
                json=payload,
                timeout=300  # 5 minute timeout
            )
            response.raise_for_status()
            end_time = time.time()

            result = response.json()

            return {
                'response': result.get('response', ''),
                'prompt_tokens': result.get('prompt_eval_count', 0),
                'completion_tokens': result.get('eval_count', 0),
                'generation_time': end_time - start_time,
                'model': result.get('model', self.model),
            }

        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API error: {str(e)}")

    def chat(self, messages, stream=False, options=None):
        """
        Chat using Ollama API

        Args:
            messages: List of message dicts with 'role' and 'content'
            stream: Whether to stream the response
            options: Dict of generation options

        Returns:
            dict with 'response', 'tokens', and 'generation_time'
        """
        payload = {
            'model': self.model,
            'messages': messages,
            'stream': stream
        }

        if options:
            payload['options'] = options

        try:
            start_time = time.time()
            response = requests.post(
                self.chat_endpoint,
                json=payload,
                timeout=300
            )
            response.raise_for_status()
            end_time = time.time()

            result = response.json()
            message = result.get('message', {})

            return {
                'response': message.get('content', ''),
                'prompt_tokens': result.get('prompt_eval_count', 0),
                'completion_tokens': result.get('eval_count', 0),
                'generation_time': end_time - start_time,
                'model': result.get('model', self.model),
            }

        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API error: {str(e)}")


class TreatmentPlanGenerator:
    """Generate AI treatment plan proposals for patients"""

    def __init__(self, model='llama3.2'):
        self.ollama_client = OllamaAPIClient(model=model)
        self.model = model

    def gather_patient_data(self, patient):
        """
        Gather all relevant patient data for treatment plan generation

        Args:
            patient: Patient model instance

        Returns:
            dict with all patient data
        """
        data = {
            'patient_info': {
                'name': patient.full_name,
                'age': patient.age if hasattr(patient, 'age') else 'Unknown',
                'gender': patient.gender if hasattr(patient, 'gender') else 'Unknown',
                'date_of_birth': str(patient.date_of_birth) if hasattr(patient, 'date_of_birth') else 'Unknown',
            },
            'vital_signs': [],
            'diagnoses': [],
            'lab_tests': [],
            'medical_history': [],
            'family_history': [],
            'social_history': [],
        }

        # Get recent vital signs (last 10)
        recent_vitals = VitalSign.objects.filter(
            encounter__patient=patient
        ).order_by('-recorded_at')[:10]

        for vital in recent_vitals:
            data['vital_signs'].append({
                'date': str(vital.recorded_at.date()) if hasattr(vital, 'recorded_at') else 'Unknown',
                'heart_rate': vital.heart_rate,
                'blood_pressure': f"{vital.blood_pressure_systolic}/{vital.blood_pressure_diastolic}",
                'temperature': f"{vital.temperature_value}°{vital.temperature_unit}" if hasattr(vital, 'temperature_value') else None,
                'respiratory_rate': vital.respiratory_rate,
                'oxygen_saturation': vital.oxygen_saturation,
                'glucose': vital.glucose,
                'weight': f"{vital.weight} {vital.weight_unit}" if hasattr(vital, 'weight') and vital.weight else None,
            })

        # Get diagnoses
        diagnoses = Diagnosis.objects.filter(encounter__patient=patient).order_by('-encounter__encounter_date')[:10]
        for diagnosis in diagnoses:
            data['diagnoses'].append({
                'condition': diagnosis.condition_name if hasattr(diagnosis, 'condition_name') else str(diagnosis),
                'date': str(diagnosis.encounter.encounter_date) if hasattr(diagnosis, 'encounter') else 'Unknown',
                'icd_code': diagnosis.icd_code if hasattr(diagnosis, 'icd_code') else None,
                'status': diagnosis.status if hasattr(diagnosis, 'status') else None,
            })

        # Get lab tests
        lab_tests = LabTest.objects.filter(patient=patient).order_by('-test_date')[:15]
        for lab in lab_tests:
            data['lab_tests'].append({
                'test_name': lab.test_name if hasattr(lab, 'test_name') else str(lab),
                'date': str(lab.test_date) if hasattr(lab, 'test_date') else 'Unknown',
                'result': lab.result if hasattr(lab, 'result') else None,
                'unit': lab.unit if hasattr(lab, 'unit') else None,
                'reference_range': lab.reference_range if hasattr(lab, 'reference_range') else None,
                'status': lab.status if hasattr(lab, 'status') else None,
            })

        # Get medical history
        medical_histories = MedicalHistory.objects.filter(patient=patient)
        for history in medical_histories:
            data['medical_history'].append({
                'condition': history.condition if hasattr(history, 'condition') else str(history),
                'onset_date': str(history.onset_date) if hasattr(history, 'onset_date') and history.onset_date else 'Unknown',
                'status': history.status if hasattr(history, 'status') else None,
                'notes': history.notes if hasattr(history, 'notes') else None,
            })

        # Get family history
        family_histories = FamilyHistory.objects.filter(patient=patient)
        for history in family_histories:
            data['family_history'].append({
                'relationship': history.relationship if hasattr(history, 'relationship') else 'Unknown',
                'condition': history.condition if hasattr(history, 'condition') else str(history),
                'age_at_diagnosis': history.age_at_diagnosis if hasattr(history, 'age_at_diagnosis') else None,
                'notes': history.notes if hasattr(history, 'notes') else None,
            })

        # Get social history
        try:
            social_history = SocialHistory.objects.filter(patient=patient).first()
            if social_history:
                data['social_history'].append({
                    'smoking_status': social_history.smoking_status if hasattr(social_history, 'smoking_status') else None,
                    'alcohol_use': social_history.alcohol_use if hasattr(social_history, 'alcohol_use') else None,
                    'drug_use': social_history.drug_use if hasattr(social_history, 'drug_use') else None,
                    'exercise_frequency': social_history.exercise_frequency if hasattr(social_history, 'exercise_frequency') else None,
                    'diet': social_history.diet if hasattr(social_history, 'diet') else None,
                    'occupation': social_history.occupation if hasattr(social_history, 'occupation') else None,
                })
        except:
            pass

        return data

    def build_treatment_prompt(self, patient_data):
        """
        Build a comprehensive prompt for treatment plan generation

        Args:
            patient_data: dict with patient data from gather_patient_data()

        Returns:
            str: Formatted prompt for AI
        """
        prompt = """You are an experienced medical AI assistant helping doctors create treatment plans. Based on the patient data provided, generate a comprehensive treatment plan proposal.

**IMPORTANT INSTRUCTIONS:**
1. This is a PROPOSAL to assist the doctor - the doctor will review and modify it
2. Be specific and evidence-based
3. Include medication names, dosages, and frequencies when appropriate
4. Suggest lifestyle modifications and preventive care
5. Identify warning signs that require immediate attention
6. Recommend appropriate follow-up schedule
7. Format your response in clear sections

**PATIENT INFORMATION:**
"""

        # Patient demographics
        patient_info = patient_data['patient_info']
        prompt += f"\nPatient: {patient_info['name']}\n"
        prompt += f"Age: {patient_info['age']}\n"
        prompt += f"Gender: {patient_info['gender']}\n"
        prompt += f"Date of Birth: {patient_info['date_of_birth']}\n"

        # Recent vital signs
        if patient_data['vital_signs']:
            prompt += "\n**RECENT VITAL SIGNS:**\n"
            for i, vital in enumerate(patient_data['vital_signs'][:5], 1):
                prompt += f"\n{i}. Date: {vital['date']}\n"
                if vital['heart_rate']:
                    prompt += f"   - Heart Rate: {vital['heart_rate']} bpm\n"
                if vital['blood_pressure']:
                    prompt += f"   - Blood Pressure: {vital['blood_pressure']} mmHg\n"
                if vital['temperature']:
                    prompt += f"   - Temperature: {vital['temperature']}\n"
                if vital['respiratory_rate']:
                    prompt += f"   - Respiratory Rate: {vital['respiratory_rate']} breaths/min\n"
                if vital['oxygen_saturation']:
                    prompt += f"   - Oxygen Saturation: {vital['oxygen_saturation']}%\n"
                if vital['glucose']:
                    prompt += f"   - Blood Glucose: {vital['glucose']} mg/dL\n"
                if vital['weight']:
                    prompt += f"   - Weight: {vital['weight']}\n"

        # Diagnoses
        if patient_data['diagnoses']:
            prompt += "\n**CURRENT/RECENT DIAGNOSES:**\n"
            for i, diagnosis in enumerate(patient_data['diagnoses'], 1):
                prompt += f"{i}. {diagnosis['condition']}"
                if diagnosis['icd_code']:
                    prompt += f" (ICD: {diagnosis['icd_code']})"
                if diagnosis['status']:
                    prompt += f" - Status: {diagnosis['status']}"
                prompt += f" - Date: {diagnosis['date']}\n"

        # Lab results
        if patient_data['lab_tests']:
            prompt += "\n**RECENT LAB RESULTS:**\n"
            for i, lab in enumerate(patient_data['lab_tests'][:10], 1):
                prompt += f"{i}. {lab['test_name']} ({lab['date']}): {lab['result']}"
                if lab['unit']:
                    prompt += f" {lab['unit']}"
                if lab['reference_range']:
                    prompt += f" (Ref: {lab['reference_range']})"
                prompt += "\n"

        # Medical history
        if patient_data['medical_history']:
            prompt += "\n**MEDICAL HISTORY:**\n"
            for i, history in enumerate(patient_data['medical_history'], 1):
                prompt += f"{i}. {history['condition']}"
                if history['onset_date'] and history['onset_date'] != 'Unknown':
                    prompt += f" (Since: {history['onset_date']})"
                if history['status']:
                    prompt += f" - {history['status']}"
                prompt += "\n"

        # Family history
        if patient_data['family_history']:
            prompt += "\n**FAMILY HISTORY:**\n"
            for i, history in enumerate(patient_data['family_history'], 1):
                prompt += f"{i}. {history['relationship']}: {history['condition']}"
                if history['age_at_diagnosis']:
                    prompt += f" (Age: {history['age_at_diagnosis']})"
                prompt += "\n"

        # Social history
        if patient_data['social_history']:
            prompt += "\n**SOCIAL HISTORY:**\n"
            for history in patient_data['social_history']:
                if history['smoking_status']:
                    prompt += f"- Smoking: {history['smoking_status']}\n"
                if history['alcohol_use']:
                    prompt += f"- Alcohol: {history['alcohol_use']}\n"
                if history['drug_use']:
                    prompt += f"- Drug Use: {history['drug_use']}\n"
                if history['exercise_frequency']:
                    prompt += f"- Exercise: {history['exercise_frequency']}\n"
                if history['diet']:
                    prompt += f"- Diet: {history['diet']}\n"
                if history['occupation']:
                    prompt += f"- Occupation: {history['occupation']}\n"

        # Request structured output
        prompt += """

**PLEASE PROVIDE A TREATMENT PLAN IN THE FOLLOWING FORMAT:**

## CLINICAL ASSESSMENT
[Provide summary of patient's current health status and key concerns]

## TREATMENT GOALS
[List 3-5 specific, measurable treatment goals]

## MEDICATIONS
[List recommended medications with dosages, frequencies, and duration]

## LIFESTYLE MODIFICATIONS
[Specific lifestyle changes recommended - diet, exercise, sleep, stress management]

## FOLLOW-UP CARE
[Recommended follow-up schedule and monitoring]

## WARNING SIGNS
[Symptoms that require immediate medical attention]

## ADDITIONAL PRECAUTIONS
[Any special precautions or considerations]

Please be specific, evidence-based, and practical in your recommendations."""

        return prompt

    def parse_ai_response(self, ai_response):
        """
        Parse AI response into structured sections

        Args:
            ai_response: Raw text response from AI

        Returns:
            dict with parsed sections
        """
        sections = {
            'proposed_treatment': ai_response,  # Full response
            'medications_suggested': '',
            'lifestyle_recommendations': '',
            'follow_up_recommendations': '',
            'warnings_and_precautions': '',
        }

        # Try to extract sections
        response_lower = ai_response.lower()

        # Extract medications section
        if '## medications' in response_lower or '##medications' in response_lower:
            start = ai_response.lower().find('## medications')
            if start == -1:
                start = ai_response.lower().find('##medications')

            # Find next section
            end = len(ai_response)
            next_sections = ['## lifestyle', '## follow-up', '## warning', '## additional']
            for next_sec in next_sections:
                pos = ai_response.lower().find(next_sec, start + 1)
                if pos != -1 and pos < end:
                    end = pos

            sections['medications_suggested'] = ai_response[start:end].strip()

        # Extract lifestyle section
        if '## lifestyle' in response_lower:
            start = ai_response.lower().find('## lifestyle')
            end = len(ai_response)
            next_sections = ['## follow-up', '## warning', '## additional']
            for next_sec in next_sections:
                pos = ai_response.lower().find(next_sec, start + 1)
                if pos != -1 and pos < end:
                    end = pos

            sections['lifestyle_recommendations'] = ai_response[start:end].strip()

        # Extract follow-up section
        if '## follow-up' in response_lower:
            start = ai_response.lower().find('## follow-up')
            end = len(ai_response)
            next_sections = ['## warning', '## additional']
            for next_sec in next_sections:
                pos = ai_response.lower().find(next_sec, start + 1)
                if pos != -1 and pos < end:
                    end = pos

            sections['follow_up_recommendations'] = ai_response[start:end].strip()

        # Extract warnings section
        if '## warning' in response_lower:
            start = ai_response.lower().find('## warning')
            end = len(ai_response)
            next_sections = ['## additional']
            for next_sec in next_sections:
                pos = ai_response.lower().find(next_sec, start + 1)
                if pos != -1 and pos < end:
                    end = pos

            # Also include additional precautions in warnings
            if '## additional' in response_lower:
                additional_start = ai_response.lower().find('## additional')
                warnings_and_additional = ai_response[start:].strip()
                sections['warnings_and_precautions'] = warnings_and_additional
            else:
                sections['warnings_and_precautions'] = ai_response[start:end].strip()

        return sections

    def generate_treatment_plan(self, patient, provider=None):
        """
        Generate AI treatment plan proposal for a patient

        Args:
            patient: Patient model instance
            provider: Provider (doctor) requesting the plan

        Returns:
            AIProposedTreatmentPlan instance
        """
        # Gather patient data
        patient_data = self.gather_patient_data(patient)

        # Build prompt
        prompt = self.build_treatment_prompt(patient_data)

        # Generate using Ollama
        print(f"Generating AI treatment plan for {patient.full_name}...")
        result = self.ollama_client.generate(
            prompt=prompt,
            options={
                'temperature': 0.7,  # Balanced creativity and consistency
                'top_p': 0.9,
                'top_k': 40,
            }
        )

        # Parse response
        parsed_sections = self.parse_ai_response(result['response'])

        # Create AIProposedTreatmentPlan record
        proposal = AIProposedTreatmentPlan.objects.create(
            patient=patient,
            provider=provider,
            vital_signs_data=patient_data['vital_signs'],
            diagnosis_data=patient_data['diagnoses'],
            lab_test_data=patient_data['lab_tests'],
            medical_history_data=patient_data['medical_history'],
            family_history_data=patient_data['family_history'],
            social_history_data=patient_data['social_history'],
            proposed_treatment=parsed_sections['proposed_treatment'],
            medications_suggested=parsed_sections['medications_suggested'],
            lifestyle_recommendations=parsed_sections['lifestyle_recommendations'],
            follow_up_recommendations=parsed_sections['follow_up_recommendations'],
            warnings_and_precautions=parsed_sections['warnings_and_precautions'],
            ai_model_name=self.model,
            ai_model_version=result.get('model', self.model),
            generation_time_seconds=result['generation_time'],
            prompt_tokens=result['prompt_tokens'],
            completion_tokens=result['completion_tokens'],
            status='pending',
        )

        print(f"AI treatment plan generated successfully (ID: {proposal.proposal_id})")
        print(f"Generation time: {result['generation_time']:.2f}s")
        print(f"Tokens: {result['prompt_tokens']} prompt + {result['completion_tokens']} completion")

        return proposal


# Convenience function for easy use
def generate_ai_treatment_plan(patient_id, provider_id=None, model='llama3.2'):
    """
    Generate AI treatment plan for a patient

    Args:
        patient_id: Patient ID
        provider_id: Provider ID (optional)
        model: AI model name (default: llama3.2)

    Returns:
        AIProposedTreatmentPlan instance
    """
    from .models import Patient, Provider

    patient = Patient.objects.get(patient_id=patient_id)
    provider = None
    if provider_id:
        provider = Provider.objects.get(provider_id=provider_id)

    generator = TreatmentPlanGenerator(model=model)
    return generator.generate_treatment_plan(patient, provider)
