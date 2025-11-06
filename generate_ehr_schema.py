#!/usr/bin/env python3
"""
EHR Database Schema Generator for MySQL
InTAM Health Inc - Electronic Medical Record System

This script generates a comprehensive MySQL database schema for an
Electronic Health Record (EHR) system.

Usage:
    python generate_ehr_schema.py > ehr_schema.sql
"""

from datetime import datetime


def generate_schema():
    """Generate the complete EHR database schema SQL script"""

    sql_script = f"""-- ============================================================================
-- EHR Database Schema for MySQL
-- InTAM Health Inc - Electronic Medical Record System
-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- ============================================================================

-- Drop database if exists and create new
DROP DATABASE IF EXISTS ehr_database;
CREATE DATABASE ehr_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ehr_database;

-- ============================================================================
-- SECTION 1: PATIENT DEMOGRAPHICS AND BASIC INFORMATION
-- ============================================================================

-- Patients table - Core patient demographics
CREATE TABLE patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    date_of_birth DATE NOT NULL,
    age INT,
    gender ENUM('Male', 'Female', 'Other', 'Unknown') NOT NULL,
    address_street VARCHAR(255),
    address_city VARCHAR(100),
    address_state VARCHAR(50),
    address_zip VARCHAR(20),
    phone_number VARCHAR(20),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_last_name (last_name),
    INDEX idx_date_of_birth (date_of_birth),
    INDEX idx_phone (phone_number)
) ENGINE=InnoDB;

-- Emergency contacts for patients
CREATE TABLE emergency_contacts (
    contact_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    contact_name VARCHAR(200) NOT NULL,
    relationship VARCHAR(100),
    phone_number VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient (patient_id)
) ENGINE=InnoDB;

-- Insurance information for patients
CREATE TABLE insurance_information (
    insurance_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    provider_name VARCHAR(200) NOT NULL,
    plan_type VARCHAR(100),
    policy_number VARCHAR(100) NOT NULL,
    group_number VARCHAR(100),
    subscriber_name VARCHAR(200),
    subscriber_relationship VARCHAR(50),
    effective_date DATE,
    termination_date DATE,
    is_primary BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient (patient_id),
    INDEX idx_policy_number (policy_number)
) ENGINE=InnoDB;

-- ============================================================================
-- SECTION 2: PROVIDERS AND STAFF
-- ============================================================================

-- Healthcare providers
CREATE TABLE providers (
    provider_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    specialty VARCHAR(200),
    license_number VARCHAR(100),
    npi_number VARCHAR(20),
    phone VARCHAR(20),
    email VARCHAR(255),
    signature_image LONGBLOB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_last_name (last_name),
    INDEX idx_npi (npi_number)
) ENGINE=InnoDB;

-- Departments
CREATE TABLE departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(200) NOT NULL,
    department_code VARCHAR(50),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================================
-- SECTION 3: ENCOUNTERS AND VISITS
-- ============================================================================

-- Patient encounters/visits
CREATE TABLE encounters (
    encounter_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    provider_id INT,
    encounter_date DATETIME NOT NULL,
    encounter_type ENUM('Inpatient', 'Outpatient', 'Emergency', 'Telehealth', 'Follow-up') NOT NULL,
    status ENUM('Scheduled', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
    department_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (provider_id) REFERENCES providers(provider_id) ON DELETE SET NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL,
    INDEX idx_patient (patient_id),
    INDEX idx_encounter_date (encounter_date),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- ============================================================================
-- SECTION 4: CHIEF COMPLAINT AND HISTORY
-- ============================================================================

-- Chief complaints
CREATE TABLE chief_complaints (
    complaint_id INT AUTO_INCREMENT PRIMARY KEY,
    encounter_id INT NOT NULL,
    chief_complaint TEXT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    INDEX idx_encounter (encounter_id)
) ENGINE=InnoDB;

-- History of Presenting Illness (HPI)
CREATE TABLE history_presenting_illness (
    hpi_id INT AUTO_INCREMENT PRIMARY KEY,
    encounter_id INT NOT NULL,
    onset TEXT,
    location TEXT,
    duration TEXT,
    characteristics TEXT,
    aggravating_factors TEXT,
    relieving_factors TEXT,
    severity ENUM('Mild', 'Moderate', 'Severe'),
    associated_symptoms TEXT,
    context TEXT,
    prior_treatments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    UNIQUE KEY unique_encounter (encounter_id)
) ENGINE=InnoDB;

-- Review of Systems (ROS)
CREATE TABLE review_of_systems (
    ros_id INT AUTO_INCREMENT PRIMARY KEY,
    encounter_id INT NOT NULL,
    -- General
    general_fever BOOLEAN DEFAULT FALSE,
    general_weight_loss BOOLEAN DEFAULT FALSE,
    general_fatigue BOOLEAN DEFAULT FALSE,
    general_night_sweats BOOLEAN DEFAULT FALSE,
    general_chills BOOLEAN DEFAULT FALSE,
    general_notes TEXT,
    -- Cardiovascular
    cardio_chest_pain BOOLEAN DEFAULT FALSE,
    cardio_palpitations BOOLEAN DEFAULT FALSE,
    cardio_orthopnea BOOLEAN DEFAULT FALSE,
    cardio_edema BOOLEAN DEFAULT FALSE,
    cardio_notes TEXT,
    -- Respiratory
    resp_cough BOOLEAN DEFAULT FALSE,
    resp_shortness_of_breath BOOLEAN DEFAULT FALSE,
    resp_wheezing BOOLEAN DEFAULT FALSE,
    resp_hemoptysis BOOLEAN DEFAULT FALSE,
    resp_notes TEXT,
    -- Gastrointestinal
    gi_nausea BOOLEAN DEFAULT FALSE,
    gi_vomiting BOOLEAN DEFAULT FALSE,
    gi_diarrhea BOOLEAN DEFAULT FALSE,
    gi_constipation BOOLEAN DEFAULT FALSE,
    gi_abdominal_pain BOOLEAN DEFAULT FALSE,
    gi_notes TEXT,
    -- Genitourinary
    gu_dysuria BOOLEAN DEFAULT FALSE,
    gu_hematuria BOOLEAN DEFAULT FALSE,
    gu_frequency BOOLEAN DEFAULT FALSE,
    gu_incontinence BOOLEAN DEFAULT FALSE,
    gu_notes TEXT,
    -- Musculoskeletal
    musculo_joint_pain BOOLEAN DEFAULT FALSE,
    musculo_swelling BOOLEAN DEFAULT FALSE,
    musculo_stiffness BOOLEAN DEFAULT FALSE,
    musculo_notes TEXT,
    -- Neurological
    neuro_headaches BOOLEAN DEFAULT FALSE,
    neuro_dizziness BOOLEAN DEFAULT FALSE,
    neuro_fainting BOOLEAN DEFAULT FALSE,
    neuro_numbness BOOLEAN DEFAULT FALSE,
    neuro_weakness BOOLEAN DEFAULT FALSE,
    neuro_notes TEXT,
    -- Endocrine
    endo_polyuria BOOLEAN DEFAULT FALSE,
    endo_polydipsia BOOLEAN DEFAULT FALSE,
    endo_heat_intolerance BOOLEAN DEFAULT FALSE,
    endo_weight_changes BOOLEAN DEFAULT FALSE,
    endo_notes TEXT,
    -- Integumentary
    integ_rashes BOOLEAN DEFAULT FALSE,
    integ_itching BOOLEAN DEFAULT FALSE,
    integ_skin_changes BOOLEAN DEFAULT FALSE,
    integ_notes TEXT,
    -- Psychiatric
    psych_depression BOOLEAN DEFAULT FALSE,
    psych_anxiety BOOLEAN DEFAULT FALSE,
    psych_mood_changes BOOLEAN DEFAULT FALSE,
    psych_sleep_disturbances BOOLEAN DEFAULT FALSE,
    psych_notes TEXT,
    -- Hematologic/Lymphatic
    hema_easy_bruising BOOLEAN DEFAULT FALSE,
    hema_bleeding BOOLEAN DEFAULT FALSE,
    hema_lymphadenopathy BOOLEAN DEFAULT FALSE,
    hema_notes TEXT,
    -- Allergic/Immunologic
    allergic_seasonal_allergies BOOLEAN DEFAULT FALSE,
    allergic_asthma BOOLEAN DEFAULT FALSE,
    allergic_immunodeficiency BOOLEAN DEFAULT FALSE,
    allergic_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    UNIQUE KEY unique_encounter (encounter_id)
) ENGINE=InnoDB;

-- ============================================================================
-- SECTION 5: PATIENT HISTORY
-- ============================================================================

-- Social history
CREATE TABLE social_history (
    social_history_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    tobacco_use ENUM('Current', 'Former', 'Never') DEFAULT 'Never',
    tobacco_frequency VARCHAR(200),
    alcohol_use ENUM('Current', 'Former', 'Never') DEFAULT 'Never',
    alcohol_frequency VARCHAR(200),
    drug_use TEXT,
    sexual_history TEXT,
    occupation VARCHAR(200),
    living_situation TEXT,
    exercise_frequency VARCHAR(200),
    diet_habits TEXT,
    sleep_quality VARCHAR(200),
    sleep_duration VARCHAR(50),
    hobbies TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient (patient_id)
) ENGINE=InnoDB;

-- Past medical history
CREATE TABLE past_medical_history (
    pmh_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    condition_name VARCHAR(200) NOT NULL,
    icd10_code VARCHAR(20),
    diagnosis_date DATE,
    status ENUM('Active', 'Resolved', 'Chronic', 'In Remission') DEFAULT 'Active',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient (patient_id)
) ENGINE=InnoDB;

-- Surgical history
CREATE TABLE surgical_history (
    surgery_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    procedure_name VARCHAR(300) NOT NULL,
    surgery_date DATE,
    surgeon_name VARCHAR(200),
    hospital VARCHAR(200),
    complications TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient (patient_id)
) ENGINE=InnoDB;

-- Family history
CREATE TABLE family_history (
    family_history_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    relationship VARCHAR(100) NOT NULL,
    condition_name VARCHAR(200) NOT NULL,
    age_of_onset INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient (patient_id)
) ENGINE=InnoDB;

-- Allergies
CREATE TABLE allergies (
    allergy_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    allergen_name VARCHAR(200) NOT NULL,
    allergy_type ENUM('Medication', 'Food', 'Environmental', 'Other') NOT NULL,
    reaction TEXT,
    severity ENUM('Mild', 'Moderate', 'Severe', 'Life-threatening'),
    onset_date DATE,
    status ENUM('Active', 'Inactive') DEFAULT 'Active',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient (patient_id),
    INDEX idx_type (allergy_type)
) ENGINE=InnoDB;

-- ============================================================================
-- SECTION 6: VITAL SIGNS AND PHYSICAL EXAMINATION
-- ============================================================================

-- Vital signs
CREATE TABLE vital_signs (
    vital_signs_id INT AUTO_INCREMENT PRIMARY KEY,
    encounter_id INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    temperature_value DECIMAL(4,1),
    temperature_unit ENUM('C', 'F') DEFAULT 'F',
    blood_pressure_systolic INT,
    blood_pressure_diastolic INT,
    heart_rate INT,
    respiratory_rate INT,
    oxygen_saturation DECIMAL(5,2),
    weight_value DECIMAL(6,2),
    weight_unit ENUM('lbs', 'kg') DEFAULT 'lbs',
    height_value DECIMAL(6,2),
    height_unit ENUM('in', 'cm') DEFAULT 'in',
    bmi DECIMAL(4,1),
    notes TEXT,
    recorded_by INT,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by) REFERENCES providers(provider_id) ON DELETE SET NULL,
    INDEX idx_encounter (encounter_id),
    INDEX idx_recorded_at (recorded_at)
) ENGINE=InnoDB;

-- Physical examination findings
CREATE TABLE physical_examinations (
    exam_id INT AUTO_INCREMENT PRIMARY KEY,
    encounter_id INT NOT NULL,
    general_appearance TEXT,
    heent_findings TEXT,
    neck_findings TEXT,
    cardiovascular_findings TEXT,
    respiratory_findings TEXT,
    gastrointestinal_findings TEXT,
    genitourinary_findings TEXT,
    musculoskeletal_findings TEXT,
    neurological_findings TEXT,
    integumentary_findings TEXT,
    psychiatric_findings TEXT,
    performed_by INT,
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (performed_by) REFERENCES providers(provider_id) ON DELETE SET NULL,
    UNIQUE KEY unique_encounter (encounter_id)
) ENGINE=InnoDB;

-- ============================================================================
-- SECTION 7: ORDERS AND PROCEDURES
-- ============================================================================

-- Physician orders
CREATE TABLE physician_orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    encounter_id INT NOT NULL,
    provider_id INT NOT NULL,
    order_type ENUM('Medication', 'Lab', 'Imaging', 'Procedure', 'Consultation', 'Other') NOT NULL,
    order_description TEXT NOT NULL,
    priority ENUM('Routine', 'Urgent', 'STAT') DEFAULT 'Routine',
    status ENUM('Ordered', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Ordered',
    ordered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scheduled_datetime DATETIME,
    completed_at TIMESTAMP NULL,
    notes TEXT,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (provider_id) REFERENCES providers(provider_id) ON DELETE CASCADE,
    INDEX idx_encounter (encounter_id),
    INDEX idx_order_type (order_type),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- Medications master list
CREATE TABLE medications (
    medication_id INT AUTO_INCREMENT PRIMARY KEY,
    medication_name VARCHAR(300) NOT NULL,
    generic_name VARCHAR(300),
    drug_class VARCHAR(200),
    ndc_code VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_name (medication_name),
    INDEX idx_generic (generic_name)
) ENGINE=InnoDB;

-- Ordered medications (linked to physician orders)
CREATE TABLE order_medications (
    order_medication_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    medication_id INT,
    medication_name VARCHAR(300) NOT NULL,
    dosage VARCHAR(200) NOT NULL,
    frequency VARCHAR(200) NOT NULL,
    duration VARCHAR(200),
    route VARCHAR(100),
    special_instructions TEXT,
    FOREIGN KEY (order_id) REFERENCES physician_orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (medication_id) REFERENCES medications(medication_id) ON DELETE SET NULL,
    INDEX idx_order (order_id)
) ENGINE=InnoDB;

-- Procedures and tests
CREATE TABLE procedures_tests (
    procedure_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    procedure_name VARCHAR(300) NOT NULL,
    cpt_code VARCHAR(20),
    scheduled_datetime DATETIME,
    location VARCHAR(200),
    status ENUM('Scheduled', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
    result TEXT,
    performed_by INT,
    notes TEXT,
    FOREIGN KEY (order_id) REFERENCES physician_orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (performed_by) REFERENCES providers(provider_id) ON DELETE SET NULL,
    INDEX idx_order (order_id),
    INDEX idx_scheduled (scheduled_datetime)
) ENGINE=InnoDB;

-- ============================================================================
-- SECTION 8: LABORATORY AND IMAGING
-- ============================================================================

-- Laboratory tests
CREATE TABLE laboratory_tests (
    lab_test_id INT AUTO_INCREMENT PRIMARY KEY,
    encounter_id INT NOT NULL,
    order_id INT,
    test_name VARCHAR(300) NOT NULL,
    test_code VARCHAR(50),
    specimen_type VARCHAR(100),
    collected_at TIMESTAMP NULL,
    resulted_at TIMESTAMP NULL,
    status ENUM('Ordered', 'Collected', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Ordered',
    result_value VARCHAR(500),
    result_unit VARCHAR(50),
    reference_range VARCHAR(200),
    abnormal_flag ENUM('Normal', 'Abnormal', 'Critical'),
    interpretation TEXT,
    performed_by_lab VARCHAR(200),
    notes TEXT,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES physician_orders(order_id) ON DELETE SET NULL,
    INDEX idx_encounter (encounter_id),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- Imaging studies
CREATE TABLE imaging_studies (
    imaging_id INT AUTO_INCREMENT PRIMARY KEY,
    encounter_id INT NOT NULL,
    order_id INT,
    study_type VARCHAR(200) NOT NULL,
    modality ENUM('X-ray', 'CT', 'MRI', 'Ultrasound', 'PET', 'Nuclear Medicine', 'Other'),
    body_part VARCHAR(200),
    ordered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    performed_at TIMESTAMP NULL,
    status ENUM('Ordered', 'Scheduled', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Ordered',
    findings TEXT,
    impression TEXT,
    radiologist_id INT,
    image_location VARCHAR(500),
    notes TEXT,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES physician_orders(order_id) ON DELETE SET NULL,
    FOREIGN KEY (radiologist_id) REFERENCES providers(provider_id) ON DELETE SET NULL,
    INDEX idx_encounter (encounter_id),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- ============================================================================
-- SECTION 9: ASSESSMENT AND DIAGNOSIS
-- ============================================================================

-- Diagnoses with ICD codes
CREATE TABLE diagnoses (
    diagnosis_id INT AUTO_INCREMENT PRIMARY KEY,
    encounter_id INT NOT NULL,
    diagnosis_description TEXT NOT NULL,
    icd10_code VARCHAR(20),
    icd11_code VARCHAR(20),
    diagnosis_type ENUM('Primary', 'Secondary', 'Differential') NOT NULL,
    status ENUM('Active', 'Resolved', 'Rule Out') DEFAULT 'Active',
    onset_date DATE,
    resolved_date DATE,
    notes TEXT,
    diagnosed_by INT,
    diagnosed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (diagnosed_by) REFERENCES providers(provider_id) ON DELETE SET NULL,
    INDEX idx_encounter (encounter_id),
    INDEX idx_icd10 (icd10_code),
    INDEX idx_type (diagnosis_type)
) ENGINE=InnoDB;

-- MDM (Medical Decision Making) and Clinical Impression
CREATE TABLE clinical_impressions (
    impression_id INT AUTO_INCREMENT PRIMARY KEY,
    encounter_id INT NOT NULL,
    patient_evaluation_summary TEXT,
    clinical_impression TEXT,
    differential_diagnoses TEXT,
    clinical_considerations TEXT,
    clingpt_suggestions TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES providers(provider_id) ON DELETE SET NULL,
    UNIQUE KEY unique_encounter (encounter_id)
) ENGINE=InnoDB;

-- ============================================================================
-- SECTION 10: TREATMENT PLANS
-- ============================================================================

-- Treatment plans
CREATE TABLE treatment_plans (
    plan_id INT AUTO_INCREMENT PRIMARY KEY,
    encounter_id INT NOT NULL,
    plan_description TEXT NOT NULL,
    diagnostic_workup TEXT,
    treatment_details TEXT,
    patient_education TEXT,
    follow_up_instructions TEXT,
    prevention_measures TEXT,
    clingpt_suggestions TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES providers(provider_id) ON DELETE SET NULL,
    UNIQUE KEY unique_encounter (encounter_id)
) ENGINE=InnoDB;

-- Prescriptions (Pharmacy Connect)
CREATE TABLE prescriptions (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    encounter_id INT NOT NULL,
    patient_id INT NOT NULL,
    provider_id INT NOT NULL,
    medication_id INT,
    medication_name VARCHAR(300) NOT NULL,
    dosage VARCHAR(200) NOT NULL,
    frequency VARCHAR(200) NOT NULL,
    duration VARCHAR(200),
    quantity INT,
    refills INT DEFAULT 0,
    route VARCHAR(100),
    instructions TEXT,
    pharmacy_name VARCHAR(200),
    pharmacy_address VARCHAR(500),
    pharmacy_phone VARCHAR(20),
    prescribed_date DATE NOT NULL,
    start_date DATE,
    end_date DATE,
    status ENUM('Active', 'Completed', 'Discontinued', 'Cancelled') DEFAULT 'Active',
    notes TEXT,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (provider_id) REFERENCES providers(provider_id) ON DELETE CASCADE,
    FOREIGN KEY (medication_id) REFERENCES medications(medication_id) ON DELETE SET NULL,
    INDEX idx_encounter (encounter_id),
    INDEX idx_patient (patient_id),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- ============================================================================
-- SECTION 11: BILLING
-- ============================================================================

-- Billing information
CREATE TABLE billing (
    billing_id INT AUTO_INCREMENT PRIMARY KEY,
    encounter_id INT NOT NULL,
    patient_id INT NOT NULL,
    provider_id INT NOT NULL,
    service_date DATE NOT NULL,
    cpt_code VARCHAR(20),
    cpt_description TEXT,
    modifiers VARCHAR(100),
    hcpcs_code VARCHAR(20),
    units INT DEFAULT 1,
    charge_amount DECIMAL(10,2),
    allowed_amount DECIMAL(10,2),
    insurance_payment DECIMAL(10,2),
    patient_responsibility DECIMAL(10,2),
    status ENUM('Pending', 'Submitted', 'Paid', 'Denied', 'Appealed') DEFAULT 'Pending',
    billing_date DATE,
    payment_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (provider_id) REFERENCES providers(provider_id) ON DELETE CASCADE,
    INDEX idx_encounter (encounter_id),
    INDEX idx_patient (patient_id),
    INDEX idx_status (status),
    INDEX idx_service_date (service_date)
) ENGINE=InnoDB;

-- ============================================================================
-- SECTION 12: NURSING EVALUATION
-- ============================================================================

-- Nursing evaluations
CREATE TABLE nursing_evaluations (
    nursing_eval_id INT AUTO_INCREMENT PRIMARY KEY,
    encounter_id INT NOT NULL,
    nurse_id INT,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Initial Assessment
    pain_level INT CHECK (pain_level BETWEEN 0 AND 10),
    functional_status ENUM('Ambulatory', 'Bed-bound', 'Requires Assistance', 'Independent'),
    psychosocial_status TEXT,
    skin_integrity TEXT,
    cognitive_memory ENUM('Alert', 'Oriented', 'Confused', 'Memory Issues', 'Impaired'),
    mobility_status TEXT,
    breathing_effort ENUM('Normal', 'Labored', 'Use of Accessory Muscles', 'Distressed'),
    hydration_nutrition TEXT,
    -- Nursing Interventions
    vital_signs_monitoring VARCHAR(200),
    pain_management TEXT,
    wound_care TEXT,
    patient_education TEXT,
    mobilization TEXT,
    fluid_management TEXT,
    mental_health_support TEXT,
    discharge_planning TEXT,
    additional_notes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (nurse_id) REFERENCES providers(provider_id) ON DELETE SET NULL,
    INDEX idx_encounter (encounter_id)
) ENGINE=InnoDB;

-- ============================================================================
-- SECTION 13: PATIENT TRACKER (DEPARTMENT TRACKING)
-- ============================================================================

-- Patient tracker - department by department
CREATE TABLE patient_tracker (
    tracker_id INT AUTO_INCREMENT PRIMARY KEY,
    encounter_id INT NOT NULL,
    patient_id INT NOT NULL,
    department_id INT NOT NULL,
    task_description VARCHAR(500) NOT NULL,
    task_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Pending', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Pending',
    comments TEXT,
    follow_up_instructions TEXT,
    completed_at TIMESTAMP NULL,
    assigned_to INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES providers(provider_id) ON DELETE SET NULL,
    INDEX idx_encounter (encounter_id),
    INDEX idx_patient (patient_id),
    INDEX idx_department (department_id),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- ============================================================================
-- SECTION 14: AUDIT AND SYSTEM TABLES
-- ============================================================================

-- Audit log for tracking changes
CREATE TABLE audit_log (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INT NOT NULL,
    action ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    user_id INT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    INDEX idx_table_record (table_name, record_id),
    INDEX idx_changed_at (changed_at)
) ENGINE=InnoDB;

-- Provider signatures table for storing electronic signatures
CREATE TABLE provider_signatures (
    signature_id INT AUTO_INCREMENT PRIMARY KEY,
    encounter_id INT NOT NULL,
    provider_id INT NOT NULL,
    signature_type ENUM('Provider', 'Attending', 'Co-Signature', 'Nurse', 'Other') NOT NULL,
    signed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    signature_data LONGBLOB,
    signature_text VARCHAR(500),
    ip_address VARCHAR(45),
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (provider_id) REFERENCES providers(provider_id) ON DELETE CASCADE,
    INDEX idx_encounter (encounter_id),
    INDEX idx_provider (provider_id)
) ENGINE=InnoDB;

-- ============================================================================
-- SECTION 15: REFERENCE DATA AND LOOKUP TABLES
-- ============================================================================

-- ICD-10 codes reference (can be populated from external source)
CREATE TABLE icd10_codes (
    icd10_id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_code (code),
    INDEX idx_category (category)
) ENGINE=InnoDB;

-- CPT codes reference (can be populated from external source)
CREATE TABLE cpt_codes (
    cpt_id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category VARCHAR(200),
    base_charge DECIMAL(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_code (code),
    INDEX idx_category (category)
) ENGINE=InnoDB;

-- ============================================================================
-- SECTION 16: SAMPLE DATA FOR DEPARTMENTS
-- ============================================================================

-- Insert common departments
INSERT INTO departments (department_name, department_code, description) VALUES
('Emergency Department', 'ED', 'Emergency medical services'),
('Cardiology', 'CARDIO', 'Heart and cardiovascular services'),
('Radiology', 'RAD', 'Medical imaging services'),
('Laboratory', 'LAB', 'Clinical laboratory services'),
('Orthopedics', 'ORTHO', 'Bone and joint services'),
('Internal Medicine', 'IM', 'General internal medicine'),
('Pediatrics', 'PEDS', 'Children healthcare services'),
('Surgery', 'SURG', 'Surgical services'),
('Neurology', 'NEURO', 'Neurological services'),
('Pharmacy', 'PHARM', 'Pharmaceutical services'),
('Nursing', 'NURSE', 'Nursing services'),
('Primary Care', 'PC', 'Primary care services');

-- ============================================================================
-- SECTION 17: VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Complete patient demographics with insurance
CREATE VIEW v_patient_complete AS
SELECT
    p.patient_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    p.date_of_birth,
    p.age,
    p.gender,
    CONCAT(p.address_street, ', ', p.address_city, ', ', p.address_state, ' ', p.address_zip) AS full_address,
    p.phone_number,
    p.email,
    ec.contact_name AS emergency_contact_name,
    ec.phone_number AS emergency_contact_phone,
    i.provider_name AS insurance_provider,
    i.policy_number,
    i.plan_type
FROM patients p
LEFT JOIN emergency_contacts ec ON p.patient_id = ec.patient_id AND ec.is_primary = TRUE
LEFT JOIN insurance_information i ON p.patient_id = i.patient_id AND i.is_primary = TRUE
WHERE p.is_active = TRUE;

-- View: Active encounters with patient and provider info
CREATE VIEW v_active_encounters AS
SELECT
    e.encounter_id,
    e.encounter_date,
    e.encounter_type,
    e.status,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    p.date_of_birth,
    CONCAT(pr.first_name, ' ', pr.last_name) AS provider_name,
    pr.specialty,
    d.department_name
FROM encounters e
INNER JOIN patients p ON e.patient_id = p.patient_id
LEFT JOIN providers pr ON e.provider_id = pr.provider_id
LEFT JOIN departments d ON e.department_id = d.department_id
WHERE e.status IN ('Scheduled', 'In Progress');

-- View: Patient allergies summary
CREATE VIEW v_patient_allergies AS
SELECT
    p.patient_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    a.allergen_name,
    a.allergy_type,
    a.reaction,
    a.severity,
    a.status
FROM patients p
INNER JOIN allergies a ON p.patient_id = a.patient_id
WHERE a.status = 'Active';

-- View: Active prescriptions
CREATE VIEW v_active_prescriptions AS
SELECT
    pr.prescription_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    p.patient_id,
    pr.medication_name,
    pr.dosage,
    pr.frequency,
    pr.prescribed_date,
    pr.refills,
    CONCAT(prov.first_name, ' ', prov.last_name) AS provider_name,
    pr.pharmacy_name
FROM prescriptions pr
INNER JOIN patients p ON pr.patient_id = p.patient_id
INNER JOIN providers prov ON pr.provider_id = prov.provider_id
WHERE pr.status = 'Active';

-- View: Latest vital signs per encounter
CREATE VIEW v_latest_vital_signs AS
SELECT
    v.*,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name
FROM vital_signs v
INNER JOIN encounters e ON v.encounter_id = e.encounter_id
INNER JOIN patients p ON e.patient_id = p.patient_id
INNER JOIN (
    SELECT encounter_id, MAX(recorded_at) AS max_recorded
    FROM vital_signs
    GROUP BY encounter_id
) latest ON v.encounter_id = latest.encounter_id AND v.recorded_at = latest.max_recorded;

-- View: Patient tracker summary
CREATE VIEW v_patient_tracker_summary AS
SELECT
    pt.tracker_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    d.department_name,
    pt.task_description,
    pt.task_datetime,
    pt.status,
    pt.comments,
    CONCAT(prov.first_name, ' ', prov.last_name) AS assigned_to_name
FROM patient_tracker pt
INNER JOIN patients p ON pt.patient_id = p.patient_id
INNER JOIN departments d ON pt.department_id = d.department_id
LEFT JOIN providers prov ON pt.assigned_to = prov.provider_id
ORDER BY pt.task_datetime DESC;

-- ============================================================================
-- SECTION 18: STORED PROCEDURES
-- ============================================================================

DELIMITER //

-- Procedure: Create new patient encounter
CREATE PROCEDURE sp_create_encounter(
    IN p_patient_id INT,
    IN p_provider_id INT,
    IN p_encounter_type VARCHAR(50),
    IN p_department_id INT,
    OUT p_encounter_id INT
)
BEGIN
    INSERT INTO encounters (patient_id, provider_id, encounter_date, encounter_type, department_id, status)
    VALUES (p_patient_id, p_provider_id, NOW(), p_encounter_type, p_department_id, 'In Progress');

    SET p_encounter_id = LAST_INSERT_ID();
END //

-- Procedure: Get patient complete medical history
CREATE PROCEDURE sp_get_patient_history(IN p_patient_id INT)
BEGIN
    -- Patient demographics
    SELECT * FROM patients WHERE patient_id = p_patient_id;

    -- Allergies
    SELECT * FROM allergies WHERE patient_id = p_patient_id AND status = 'Active';

    -- Past medical history
    SELECT * FROM past_medical_history WHERE patient_id = p_patient_id;

    -- Surgical history
    SELECT * FROM surgical_history WHERE patient_id = p_patient_id;

    -- Family history
    SELECT * FROM family_history WHERE patient_id = p_patient_id;

    -- Social history
    SELECT * FROM social_history WHERE patient_id = p_patient_id ORDER BY updated_at DESC LIMIT 1;

    -- Active prescriptions
    SELECT * FROM prescriptions WHERE patient_id = p_patient_id AND status = 'Active';
END //

-- Procedure: Update patient age based on DOB
CREATE PROCEDURE sp_update_patient_ages()
BEGIN
    UPDATE patients
    SET age = TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE());
END //

DELIMITER ;

-- ============================================================================
-- SECTION 19: TRIGGERS
-- ============================================================================

DELIMITER //

-- Trigger: Automatically calculate BMI when vital signs are inserted
CREATE TRIGGER trg_calculate_bmi_insert
BEFORE INSERT ON vital_signs
FOR EACH ROW
BEGIN
    IF NEW.weight_value IS NOT NULL AND NEW.height_value IS NOT NULL THEN
        -- Convert to metric if needed and calculate BMI
        SET @weight_kg = IF(NEW.weight_unit = 'lbs', NEW.weight_value * 0.453592, NEW.weight_value);
        SET @height_m = IF(NEW.height_unit = 'in', NEW.height_value * 0.0254, NEW.height_value / 100);
        SET NEW.bmi = @weight_kg / (@height_m * @height_m);
    END IF;
END //

-- Trigger: Automatically calculate BMI when vital signs are updated
CREATE TRIGGER trg_calculate_bmi_update
BEFORE UPDATE ON vital_signs
FOR EACH ROW
BEGIN
    IF NEW.weight_value IS NOT NULL AND NEW.height_value IS NOT NULL THEN
        SET @weight_kg = IF(NEW.weight_unit = 'lbs', NEW.weight_value * 0.453592, NEW.weight_value);
        SET @height_m = IF(NEW.height_unit = 'in', NEW.height_value * 0.0254, NEW.height_value / 100);
        SET NEW.bmi = @weight_kg / (@height_m * @height_m);
    END IF;
END //

-- Trigger: Update patient age when DOB is changed
CREATE TRIGGER trg_update_patient_age
BEFORE UPDATE ON patients
FOR EACH ROW
BEGIN
    IF NEW.date_of_birth != OLD.date_of_birth OR NEW.age IS NULL THEN
        SET NEW.age = TIMESTAMPDIFF(YEAR, NEW.date_of_birth, CURDATE());
    END IF;
END //

-- Trigger: Set patient age on insert
CREATE TRIGGER trg_set_patient_age
BEFORE INSERT ON patients
FOR EACH ROW
BEGIN
    IF NEW.age IS NULL THEN
        SET NEW.age = TIMESTAMPDIFF(YEAR, NEW.date_of_birth, CURDATE());
    END IF;
END //

DELIMITER ;

-- ============================================================================
-- SECTION 20: INDEXES FOR PERFORMANCE OPTIMIZATION
-- ============================================================================

-- Additional composite indexes for common queries
CREATE INDEX idx_encounter_patient_date ON encounters(patient_id, encounter_date);
CREATE INDEX idx_diagnosis_patient ON diagnoses(encounter_id, diagnosis_type);
CREATE INDEX idx_prescription_patient_status ON prescriptions(patient_id, status);
CREATE INDEX idx_billing_patient_date ON billing(patient_id, service_date);
CREATE INDEX idx_lab_encounter_status ON laboratory_tests(encounter_id, status);
CREATE INDEX idx_imaging_encounter_status ON imaging_studies(encounter_id, status);

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

SELECT '========================================' AS '';
SELECT 'EHR Database Schema Created Successfully' AS '';
SELECT '========================================' AS '';
SELECT CONCAT('Database: ehr_database') AS '';
SELECT CONCAT('Total Tables: ', COUNT(*)) AS ''
FROM information_schema.tables
WHERE table_schema = 'ehr_database' AND table_type = 'BASE TABLE';
SELECT '========================================' AS '';
"""

    return sql_script


def main():
    """Main function to generate and output the schema"""
    print(generate_schema())


if __name__ == "__main__":
    main()
