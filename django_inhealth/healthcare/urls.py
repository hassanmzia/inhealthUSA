from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.index, name='index'),

    # Patient URLs
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/create/', views.patient_create, name='patient_create'),
    path('patients/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:patient_id>/edit/', views.patient_edit, name='patient_edit'),

    # Physician URLs
    path('physicians/', views.physician_list, name='physician_list'),
    path('physicians/<int:provider_id>/', views.physician_detail, name='physician_detail'),

    # Appointment URLs
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/create/', views.appointment_create, name='appointment_create'),
    path('appointments/<int:encounter_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:encounter_id>/edit/', views.appointment_edit, name='appointment_edit'),

    # Vital Signs URLs
    path('appointments/<int:encounter_id>/vital-signs/create/', views.vital_sign_create, name='vital_sign_create'),

    # Diagnosis URLs
    path('appointments/<int:encounter_id>/diagnoses/create/', views.diagnosis_create, name='diagnosis_create'),

    # Prescription URLs
    path('prescriptions/', views.prescription_list, name='prescription_list'),
    path('prescriptions/create/', views.prescription_create, name='prescription_create'),
    path('prescriptions/<int:prescription_id>/', views.prescription_detail, name='prescription_detail'),
]
