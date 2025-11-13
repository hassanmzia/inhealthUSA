from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),

    # Dashboard
    path('', views.index, name='index'),

    # Patient URLs
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/create/', views.patient_create, name='patient_create'),
    path('patients/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:patient_id>/edit/', views.patient_edit, name='patient_edit'),

    # Patient Vital Signs URLs
    path('patients/<int:patient_id>/vitals/create/', views.patient_vital_create, name='patient_vital_create'),
    path('patients/<int:patient_id>/vitals/<int:vital_signs_id>/edit/', views.patient_vital_edit, name='patient_vital_edit'),

    # Patient Diagnosis URLs
    path('patients/<int:patient_id>/diagnoses/create/', views.patient_diagnosis_create, name='patient_diagnosis_create'),
    path('patients/<int:patient_id>/diagnoses/<int:diagnosis_id>/edit/', views.patient_diagnosis_edit, name='patient_diagnosis_edit'),

    # Patient Prescription URLs
    path('patients/<int:patient_id>/prescriptions/create/', views.patient_prescription_create, name='patient_prescription_create'),
    path('patients/<int:patient_id>/prescriptions/<int:prescription_id>/edit/', views.patient_prescription_edit, name='patient_prescription_edit'),

    # Patient Medical History URLs
    path('patients/<int:patient_id>/medical-history/create/', views.patient_medical_history_create, name='patient_medical_history_create'),
    path('patients/<int:patient_id>/medical-history/<int:medical_history_id>/edit/', views.patient_medical_history_edit, name='patient_medical_history_edit'),

    # Patient Social History URLs
    path('patients/<int:patient_id>/social-history/create/', views.patient_social_history_create, name='patient_social_history_create'),
    path('patients/<int:patient_id>/social-history/<int:social_history_id>/edit/', views.patient_social_history_edit, name='patient_social_history_edit'),

    # Patient Allergy URLs
    path('patients/<int:patient_id>/allergies/create/', views.patient_allergy_create, name='patient_allergy_create'),
    path('patients/<int:patient_id>/allergies/<int:allergy_id>/edit/', views.patient_allergy_edit, name='patient_allergy_edit'),

    # Patient Lab Test URLs
    path('patients/<int:patient_id>/lab-tests/create/', views.patient_lab_test_create, name='patient_lab_test_create'),
    path('patients/<int:patient_id>/lab-tests/<int:lab_test_id>/edit/', views.patient_lab_test_edit, name='patient_lab_test_edit'),

    # Physician URLs
    path('physicians/', views.physician_list, name='physician_list'),
    path('physicians/<int:provider_id>/', views.physician_detail, name='physician_detail'),

    # Appointment URLs
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/create/', views.appointment_create, name='appointment_create'),
    path('appointments/<int:encounter_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:encounter_id>/edit/', views.appointment_edit, name='appointment_edit'),

    # Encounter Vital Signs URLs
    path('appointments/<int:encounter_id>/vitals/create/', views.encounter_vital_create, name='encounter_vital_create'),
    path('appointments/<int:encounter_id>/vitals/<int:vital_signs_id>/edit/', views.encounter_vital_edit, name='encounter_vital_edit'),

    # Encounter Diagnosis URLs
    path('appointments/<int:encounter_id>/diagnoses/create/', views.encounter_diagnosis_create, name='encounter_diagnosis_create'),
    path('appointments/<int:encounter_id>/diagnoses/<int:diagnosis_id>/edit/', views.encounter_diagnosis_edit, name='encounter_diagnosis_edit'),

    # Encounter Prescription URLs
    path('appointments/<int:encounter_id>/prescriptions/create/', views.encounter_prescription_create, name='encounter_prescription_create'),
    path('appointments/<int:encounter_id>/prescriptions/<int:prescription_id>/edit/', views.encounter_prescription_edit, name='encounter_prescription_edit'),

    # Vital Signs URLs (deprecated - use encounter URLs above)
    path('appointments/<int:encounter_id>/vital-signs/create/', views.vital_sign_create, name='vital_sign_create'),

    # Diagnosis URLs (deprecated - use encounter URLs above)
    path('appointments/<int:encounter_id>/diagnoses/create/', views.diagnosis_create, name='diagnosis_create'),

    # Prescription URLs
    path('prescriptions/', views.prescription_list, name='prescription_list'),
    path('prescriptions/create/', views.prescription_create, name='prescription_create'),
    path('prescriptions/<int:prescription_id>/', views.prescription_detail, name='prescription_detail'),

    # Hospital URLs
    path('hospitals/', views.hospital_list, name='hospital_list'),
    path('hospitals/<int:hospital_id>/', views.hospital_detail, name='hospital_detail'),

    # Family History URLs
    path('family-history/', views.family_history_list, name='family_history_list'),
    path('family-history/create/', views.family_history_create, name='family_history_create'),
    path('family-history/<int:family_history_id>/', views.family_history_detail, name='family_history_detail'),

    # Patient Billing URLs
    path('patients/<int:patient_id>/billing/', views.patient_billing_list, name='patient_billing_list'),
    path('patients/<int:patient_id>/billing/<int:billing_id>/', views.patient_billing_detail, name='patient_billing_detail'),

    # Patient Payment URLs
    path('patients/<int:patient_id>/payments/', views.patient_payment_list, name='patient_payment_list'),
    path('patients/<int:patient_id>/payments/<int:payment_id>/', views.patient_payment_detail, name='patient_payment_detail'),

    # Patient Insurance URLs
    path('patients/<int:patient_id>/insurance/', views.patient_insurance_list, name='patient_insurance_list'),
    path('patients/<int:patient_id>/insurance/<int:insurance_id>/', views.patient_insurance_detail, name='patient_insurance_detail'),

    # Patient Device URLs
    path('patients/<int:patient_id>/devices/', views.patient_device_list, name='patient_device_list'),
    path('patients/<int:patient_id>/devices/<int:device_id>/', views.patient_device_detail, name='patient_device_detail'),

    # Medical History Questionnaire
    path('questionnaire/medical-history/', views.medical_history_questionnaire, name='medical_history_questionnaire'),

    # Family History Questionnaire
    path('questionnaire/family-history/', views.family_history_questionnaire, name='family_history_questionnaire'),

    # Social History Questionnaire
    path('questionnaire/social-history/', views.social_history_questionnaire, name='social_history_questionnaire'),

    # Allergies Questionnaire
    path('questionnaire/allergies/', views.allergies_questionnaire, name='allergies_questionnaire'),

    # Insurance Information (Generic)
    path('insurance/', views.insurance_information, name='insurance_information'),

    # Billing Information (Generic)
    path('billing/', views.billing_information, name='billing_information'),

    # Payment History (Generic)
    path('payment-history/', views.payment_history, name='payment_history'),

    # Message URLs
    path('messages/inbox/', views.message_inbox, name='message_inbox'),
    path('messages/sent/', views.message_sent, name='message_sent'),
    path('messages/compose/', views.message_compose, name='message_compose'),
    path('messages/<int:message_id>/', views.message_show, name='message_show'),
    path('messages/<int:message_id>/delete/', views.message_delete, name='message_delete'),

    # Patient Profile URLs (for logged-in patients)
    path('profile/', views.patient_profile, name='patient_profile'),
    path('profile/edit/', views.patient_profile_edit, name='patient_profile_edit'),

    # Provider Profile URLs (for logged-in providers/doctors)
    path('provider/profile/', views.provider_profile, name='provider_profile'),
    path('provider/profile/edit/', views.provider_profile_edit, name='provider_profile_edit'),
]
