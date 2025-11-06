-- =====================================================
-- InTAM Health Inc - Electronic Health Records (EHR)
-- MySQL Database Schema
-- =====================================================

-- Drop database if exists (use with caution in production)
-- DROP DATABASE IF EXISTS intam_ehr;

-- Create database
CREATE DATABASE IF NOT EXISTS intam_ehr
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE intam_ehr;

-- =====================================================
-- PATIENT INFORMATION TABLES
-- =====================================================

-- Patients table (Demographics)
CREATE TABLE patients (
    patient_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    date_of_birth DATE NOT NULL,
    age INT GENERATED ALWAYS AS (TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE())) STORED,
    gender ENUM('Male', 'Female', 'Other', 'Prefer not to say') NOT NULL,
    ssn VARCHAR(11),
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'USA',
    phone_primary VARCHAR(20),
    phone_secondary VARCHAR(20),
    email VARCHAR(100),
    preferred_language VARCHAR(50) DEFAULT 'English',
    marital_status ENUM('Single', 'Married', 'Divorced', 'Widowed', 'Separated', 'Domestic Partner'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_last_name (last_name),
    INDEX idx_dob (date_of_birth),
    INDEX idx_phone (phone_primary)
) ENGINE=InnoDB;

-- Emergency Contacts
CREATE TABLE emergency_contacts (
    contact_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    contact_name VARCHAR(200) NOT NULL,
    relationship VARCHAR(100),
    phone_primary VARCHAR(20) NOT NULL,
    phone_secondary VARCHAR(20),
    email VARCHAR(100),
    address VARCHAR(500),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient (patient_id)
) ENGINE=InnoDB;

-- Insurance Information
CREATE TABLE insurance_information (
    insurance_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    provider_name VARCHAR(200) NOT NULL,
    plan_type VARCHAR(100),
    policy_number VARCHAR(100) NOT NULL,
    group_number VARCHAR(100),
    subscriber_name VARCHAR(200),
    subscriber_relationship VARCHAR(50),
    subscriber_dob DATE,
    effective_date DATE,
    expiration_date DATE,
    is_primary BOOLEAN DEFAULT TRUE,
    copay_amount DECIMAL(10, 2),
    deductible_amount DECIMAL(10, 2),
    phone VARCHAR(20),
    address VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient (patient_id),
    INDEX idx_policy (policy_number)
) ENGINE=InnoDB;

-- =====================================================
-- PROVIDER INFORMATION
-- =====================================================

-- Healthcare Providers
CREATE TABLE providers (
    provider_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    title VARCHAR(50),
    specialty VARCHAR(100),
    license_number VARCHAR(100),
    npi_number VARCHAR(20) UNIQUE,
    phone VARCHAR(20),
    email VARCHAR(100),
    department VARCHAR(100),
    signature_path VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_specialty (specialty),
    INDEX idx_last_name (last_name)
) ENGINE=InnoDB;

-- =====================================================
-- ENCOUNTER/VISIT TABLES
-- =====================================================

-- Patient Encounters/Visits
CREATE TABLE encounters (
    encounter_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    provider_id BIGINT NOT NULL,
    encounter_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    encounter_type ENUM('Inpatient', 'Outpatient', 'Emergency', 'Telemedicine', 'Home Visit') NOT NULL,
    department VARCHAR(100),
    location VARCHAR(200),
    status ENUM('Scheduled', 'In Progress', 'Completed', 'Cancelled', 'No Show') DEFAULT 'Scheduled',
    chief_complaint TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (provider_id) REFERENCES providers(provider_id),
    INDEX idx_patient (patient_id),
    INDEX idx_provider (provider_id),
    INDEX idx_date (encounter_date),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- History of Presenting Illness (HPI)
CREATE TABLE hpi (
    hpi_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    encounter_id BIGINT NOT NULL,
    onset VARCHAR(200),
    location VARCHAR(200),
    duration VARCHAR(200),
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
    INDEX idx_encounter (encounter_id)
) ENGINE=InnoDB;

-- Review of Systems (ROS)
CREATE TABLE review_of_systems (
    ros_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    encounter_id BIGINT NOT NULL,
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
    msk_joint_pain BOOLEAN DEFAULT FALSE,
    msk_swelling BOOLEAN DEFAULT FALSE,
    msk_stiffness BOOLEAN DEFAULT FALSE,
    msk_notes TEXT,
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
    heme_easy_bruising BOOLEAN DEFAULT FALSE,
    heme_bleeding BOOLEAN DEFAULT FALSE,
    heme_lymphadenopathy BOOLEAN DEFAULT FALSE,
    heme_notes TEXT,
    -- Allergic/Immunologic
    allergic_seasonal_allergies BOOLEAN DEFAULT FALSE,
    allergic_asthma BOOLEAN DEFAULT FALSE,
    allergic_immunodeficiency BOOLEAN DEFAULT FALSE,
    allergic_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    INDEX idx_encounter (encounter_id)
) ENGINE=InnoDB;

-- Vital Signs
CREATE TABLE vital_signs (
    vital_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    encounter_id BIGINT NOT NULL,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    temperature DECIMAL(5, 2),
    temp_unit ENUM('C', 'F') DEFAULT 'F',
    blood_pressure_systolic INT,
    blood_pressure_diastolic INT,
    heart_rate INT,
    respiratory_rate INT,
    oxygen_saturation DECIMAL(5, 2),
    weight DECIMAL(6, 2),
    weight_unit ENUM('kg', 'lbs') DEFAULT 'lbs',
    height DECIMAL(6, 2),
    height_unit ENUM('cm', 'in') DEFAULT 'in',
    bmi DECIMAL(5, 2) GENERATED ALWAYS AS (
        CASE
            WHEN weight_unit = 'kg' AND height_unit = 'cm' THEN weight / POWER(height / 100, 2)
            WHEN weight_unit = 'lbs' AND height_unit = 'in' THEN (weight / POWER(height, 2)) * 703
            ELSE NULL
        END
    ) STORED,
    pain_scale INT CHECK (pain_scale BETWEEN 0 AND 10),
    recorded_by_provider_id BIGINT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by_provider_id) REFERENCES providers(provider_id),
    INDEX idx_encounter (encounter_id),
    INDEX idx_recorded_at (recorded_at)
) ENGINE=InnoDB;

-- Physical Examination
CREATE TABLE physical_examinations (
    exam_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    encounter_id BIGINT NOT NULL,
    general_appearance TEXT,
    heent TEXT,
    neck TEXT,
    cardiovascular TEXT,
    respiratory TEXT,
    gastrointestinal TEXT,
    genitourinary TEXT,
    musculoskeletal TEXT,
    neurological TEXT,
    integumentary TEXT,
    psychiatric TEXT,
    other_findings TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    INDEX idx_encounter (encounter_id)
) ENGINE=InnoDB;

-- =====================================================
-- MEDICAL HISTORY TABLES
-- =====================================================

-- Past Medical History
CREATE TABLE medical_history (
    history_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    condition_name VARCHAR(200) NOT NULL,
    diagnosis_date DATE,
    is_chronic BOOLEAN DEFAULT FALSE,
    status ENUM('Active', 'Resolved', 'In Remission') DEFAULT 'Active',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient (patient_id)
) ENGINE=InnoDB;

-- Surgical History
CREATE TABLE surgical_history (
    surgery_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    procedure_name VARCHAR(200) NOT NULL,
    surgery_date DATE,
    surgeon_name VARCHAR(200),
    hospital VARCHAR(200),
    complications TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient (patient_id)
) ENGINE=InnoDB;

-- Family History
CREATE TABLE family_history (
    family_history_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    relationship VARCHAR(100) NOT NULL,
    condition_name VARCHAR(200) NOT NULL,
    age_of_onset INT,
    is_alive BOOLEAN,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient (patient_id)
) ENGINE=InnoDB;

-- Social History
CREATE TABLE social_history (
    social_history_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    tobacco_use ENUM('Current', 'Former', 'Never') DEFAULT 'Never',
    tobacco_frequency VARCHAR(100),
    tobacco_quit_date DATE,
    alcohol_use ENUM('Current', 'Former', 'Never') DEFAULT 'Never',
    alcohol_frequency VARCHAR(100),
    alcohol_quit_date DATE,
    drug_use ENUM('Current', 'Former', 'Never') DEFAULT 'Never',
    drug_type VARCHAR(200),
    drug_frequency VARCHAR(100),
    sexual_history TEXT,
    occupation VARCHAR(200),
    living_situation TEXT,
    exercise_frequency VARCHAR(100),
    exercise_type VARCHAR(200),
    diet_description TEXT,
    diet_restrictions TEXT,
    sleep_quality VARCHAR(100),
    sleep_duration VARCHAR(50),
    hobbies TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient (patient_id)
) ENGINE=InnoDB;

-- Allergies
CREATE TABLE allergies (
    allergy_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    allergen VARCHAR(200) NOT NULL,
    allergy_type ENUM('Medication', 'Food', 'Environmental', 'Other') NOT NULL,
    reaction TEXT,
    severity ENUM('Mild', 'Moderate', 'Severe', 'Life-threatening'),
    onset_date DATE,
    status ENUM('Active', 'Resolved', 'Unconfirmed') DEFAULT 'Active',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient (patient_id),
    INDEX idx_type (allergy_type)
) ENGINE=InnoDB;

-- =====================================================
-- DIAGNOSTIC AND TREATMENT TABLES
-- =====================================================

-- Laboratory Tests
CREATE TABLE lab_orders (
    lab_order_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    encounter_id BIGINT NOT NULL,
    test_name VARCHAR(200) NOT NULL,
    test_code VARCHAR(50),
    ordered_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    ordered_by_provider_id BIGINT NOT NULL,
    priority ENUM('Routine', 'Urgent', 'STAT') DEFAULT 'Routine',
    status ENUM('Ordered', 'Collected', 'In Process', 'Completed', 'Cancelled') DEFAULT 'Ordered',
    specimen_type VARCHAR(100),
    collection_date DATETIME,
    notes TEXT,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (ordered_by_provider_id) REFERENCES providers(provider_id),
    INDEX idx_encounter (encounter_id),
    INDEX idx_status (status)
) ENGINE=InnoDB;

CREATE TABLE lab_results (
    result_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    lab_order_id BIGINT NOT NULL,
    test_component VARCHAR(200),
    result_value VARCHAR(200),
    unit VARCHAR(50),
    reference_range VARCHAR(100),
    abnormal_flag ENUM('Normal', 'High', 'Low', 'Critical High', 'Critical Low'),
    result_date DATETIME,
    performed_by VARCHAR(200),
    verified_by_provider_id BIGINT,
    comments TEXT,
    FOREIGN KEY (lab_order_id) REFERENCES lab_orders(lab_order_id) ON DELETE CASCADE,
    FOREIGN KEY (verified_by_provider_id) REFERENCES providers(provider_id),
    INDEX idx_lab_order (lab_order_id)
) ENGINE=InnoDB;

-- Imaging Studies
CREATE TABLE imaging_orders (
    imaging_order_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    encounter_id BIGINT NOT NULL,
    study_type VARCHAR(200) NOT NULL,
    study_code VARCHAR(50),
    body_part VARCHAR(100),
    ordered_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    ordered_by_provider_id BIGINT NOT NULL,
    priority ENUM('Routine', 'Urgent', 'STAT') DEFAULT 'Routine',
    status ENUM('Ordered', 'Scheduled', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Ordered',
    scheduled_date DATETIME,
    modality VARCHAR(50),
    contrast_used BOOLEAN DEFAULT FALSE,
    clinical_indication TEXT,
    notes TEXT,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (ordered_by_provider_id) REFERENCES providers(provider_id),
    INDEX idx_encounter (encounter_id),
    INDEX idx_status (status)
) ENGINE=InnoDB;

CREATE TABLE imaging_results (
    imaging_result_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    imaging_order_id BIGINT NOT NULL,
    performed_date DATETIME,
    radiologist_name VARCHAR(200),
    findings TEXT,
    impression TEXT,
    result_status ENUM('Normal', 'Abnormal', 'Critical') DEFAULT 'Normal',
    images_path VARCHAR(500),
    report_path VARCHAR(500),
    verified_by_provider_id BIGINT,
    verified_date DATETIME,
    FOREIGN KEY (imaging_order_id) REFERENCES imaging_orders(imaging_order_id) ON DELETE CASCADE,
    FOREIGN KEY (verified_by_provider_id) REFERENCES providers(provider_id),
    INDEX idx_imaging_order (imaging_order_id)
) ENGINE=InnoDB;

-- Diagnoses (ICD-10)
CREATE TABLE diagnoses (
    diagnosis_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    encounter_id BIGINT NOT NULL,
    icd10_code VARCHAR(20) NOT NULL,
    description VARCHAR(500) NOT NULL,
    diagnosis_type ENUM('Primary', 'Secondary', 'Differential') DEFAULT 'Primary',
    diagnosis_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    diagnosed_by_provider_id BIGINT NOT NULL,
    status ENUM('Active', 'Resolved', 'Ruled Out') DEFAULT 'Active',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (diagnosed_by_provider_id) REFERENCES providers(provider_id),
    INDEX idx_encounter (encounter_id),
    INDEX idx_icd10 (icd10_code)
) ENGINE=InnoDB;

-- Clinical Impressions / MDM
CREATE TABLE clinical_impressions (
    impression_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    encounter_id BIGINT NOT NULL,
    evaluation_summary TEXT,
    clinical_impression TEXT,
    differential_diagnoses TEXT,
    additional_findings TEXT,
    clingpt_suggestion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    INDEX idx_encounter (encounter_id)
) ENGINE=InnoDB;

-- Treatment Plans
CREATE TABLE treatment_plans (
    plan_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    encounter_id BIGINT NOT NULL,
    diagnostic_workup TEXT,
    treatment_description TEXT,
    patient_education TEXT,
    follow_up_instructions TEXT,
    prevention_measures TEXT,
    clingpt_suggestion TEXT,
    created_by_provider_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by_provider_id) REFERENCES providers(provider_id),
    INDEX idx_encounter (encounter_id)
) ENGINE=InnoDB;

-- =====================================================
-- MEDICATION AND PHARMACY TABLES
-- =====================================================

-- Medications/Prescriptions
CREATE TABLE prescriptions (
    prescription_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    encounter_id BIGINT NOT NULL,
    patient_id BIGINT NOT NULL,
    medication_name VARCHAR(200) NOT NULL,
    medication_code VARCHAR(50),
    dosage VARCHAR(100) NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    route VARCHAR(50),
    duration VARCHAR(100),
    quantity INT,
    refills INT DEFAULT 0,
    start_date DATE,
    end_date DATE,
    special_instructions TEXT,
    prescribed_by_provider_id BIGINT NOT NULL,
    prescribed_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Active', 'Completed', 'Discontinued', 'On Hold') DEFAULT 'Active',
    pharmacy_id BIGINT,
    pharmacopia_code VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (prescribed_by_provider_id) REFERENCES providers(provider_id),
    INDEX idx_encounter (encounter_id),
    INDEX idx_patient (patient_id),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- Pharmacy Information
CREATE TABLE pharmacies (
    pharmacy_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pharmacy_name VARCHAR(200) NOT NULL,
    phone VARCHAR(20),
    fax VARCHAR(20),
    email VARCHAR(100),
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    is_24_hour BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (pharmacy_name)
) ENGINE=InnoDB;

-- Add foreign key to prescriptions after pharmacy table is created
ALTER TABLE prescriptions
ADD FOREIGN KEY (pharmacy_id) REFERENCES pharmacies(pharmacy_id);

-- =====================================================
-- ORDERS AND PROCEDURES
-- =====================================================

-- Physician Orders
CREATE TABLE physician_orders (
    order_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    encounter_id BIGINT NOT NULL,
    order_type ENUM('Medication', 'Procedure', 'Test', 'Consultation', 'Other') NOT NULL,
    order_description TEXT NOT NULL,
    ordered_by_provider_id BIGINT NOT NULL,
    ordered_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    scheduled_date DATETIME,
    priority ENUM('Routine', 'Urgent', 'STAT') DEFAULT 'Routine',
    status ENUM('Ordered', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Ordered',
    location VARCHAR(200),
    special_instructions TEXT,
    completed_date DATETIME,
    completed_by VARCHAR(200),
    notes TEXT,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (ordered_by_provider_id) REFERENCES providers(provider_id),
    INDEX idx_encounter (encounter_id),
    INDEX idx_type (order_type),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- Consultations/Referrals
CREATE TABLE consultations (
    consultation_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    encounter_id BIGINT NOT NULL,
    patient_id BIGINT NOT NULL,
    referring_provider_id BIGINT NOT NULL,
    consulting_provider_id BIGINT,
    specialty VARCHAR(100) NOT NULL,
    reason TEXT NOT NULL,
    urgency ENUM('Routine', 'Urgent', 'Emergency') DEFAULT 'Routine',
    requested_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    scheduled_date DATETIME,
    consultation_date DATETIME,
    status ENUM('Requested', 'Scheduled', 'Completed', 'Cancelled') DEFAULT 'Requested',
    findings TEXT,
    recommendations TEXT,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (referring_provider_id) REFERENCES providers(provider_id),
    FOREIGN KEY (consulting_provider_id) REFERENCES providers(provider_id),
    INDEX idx_encounter (encounter_id),
    INDEX idx_patient (patient_id),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- =====================================================
-- NURSING DOCUMENTATION
-- =====================================================

-- Nursing Evaluations
CREATE TABLE nursing_evaluations (
    evaluation_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    encounter_id BIGINT NOT NULL,
    nurse_id BIGINT NOT NULL,
    evaluation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    -- Initial Assessment
    pain_level INT CHECK (pain_level BETWEEN 0 AND 10),
    functional_status ENUM('Ambulatory', 'Bed-bound', 'Requires Assistance', 'Independent'),
    psychosocial_status TEXT,
    skin_integrity TEXT,
    cognitive_memory ENUM('Alert', 'Oriented', 'Confused', 'Memory Issues', 'Impaired'),
    mobility TEXT,
    breathing_effort ENUM('Normal', 'Labored', 'Use of Accessory Muscles', 'Distressed'),
    hydration_nutrition TEXT,
    -- Additional Notes
    assessment_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (nurse_id) REFERENCES providers(provider_id),
    INDEX idx_encounter (encounter_id)
) ENGINE=InnoDB;

-- Nursing Interventions
CREATE TABLE nursing_interventions (
    intervention_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    evaluation_id BIGINT NOT NULL,
    encounter_id BIGINT NOT NULL,
    intervention_type VARCHAR(100) NOT NULL,
    intervention_description TEXT NOT NULL,
    performed_by_nurse_id BIGINT NOT NULL,
    performed_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    frequency VARCHAR(100),
    outcome TEXT,
    notes TEXT,
    FOREIGN KEY (evaluation_id) REFERENCES nursing_evaluations(evaluation_id) ON DELETE CASCADE,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (performed_by_nurse_id) REFERENCES providers(provider_id),
    INDEX idx_evaluation (evaluation_id),
    INDEX idx_encounter (encounter_id)
) ENGINE=InnoDB;

-- =====================================================
-- BILLING TABLES
-- =====================================================

-- Billing Information
CREATE TABLE billing (
    billing_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    encounter_id BIGINT NOT NULL,
    patient_id BIGINT NOT NULL,
    billing_date DATE DEFAULT (CURRENT_DATE),
    total_charge DECIMAL(10, 2),
    insurance_payment DECIMAL(10, 2),
    patient_payment DECIMAL(10, 2),
    balance DECIMAL(10, 2),
    status ENUM('Pending', 'Submitted', 'Paid', 'Partially Paid', 'Denied', 'Appealed') DEFAULT 'Pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_encounter (encounter_id),
    INDEX idx_patient (patient_id),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- CPT Codes
CREATE TABLE cpt_codes (
    cpt_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    billing_id BIGINT NOT NULL,
    cpt_code VARCHAR(20) NOT NULL,
    description VARCHAR(500),
    modifier VARCHAR(10),
    units INT DEFAULT 1,
    charge_amount DECIMAL(10, 2),
    FOREIGN KEY (billing_id) REFERENCES billing(billing_id) ON DELETE CASCADE,
    INDEX idx_billing (billing_id),
    INDEX idx_code (cpt_code)
) ENGINE=InnoDB;

-- HCPCS Codes
CREATE TABLE hcpcs_codes (
    hcpcs_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    billing_id BIGINT NOT NULL,
    hcpcs_code VARCHAR(20) NOT NULL,
    description VARCHAR(500),
    modifier VARCHAR(10),
    units INT DEFAULT 1,
    charge_amount DECIMAL(10, 2),
    FOREIGN KEY (billing_id) REFERENCES billing(billing_id) ON DELETE CASCADE,
    INDEX idx_billing (billing_id),
    INDEX idx_code (hcpcs_code)
) ENGINE=InnoDB;

-- =====================================================
-- DEPARTMENT TRACKING
-- =====================================================

-- Departments
CREATE TABLE departments (
    department_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    department_code VARCHAR(20),
    description TEXT,
    phone VARCHAR(20),
    location VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Patient Tracker
CREATE TABLE patient_tracker (
    tracker_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    encounter_id BIGINT NOT NULL,
    patient_id BIGINT NOT NULL,
    department_id BIGINT NOT NULL,
    task_description VARCHAR(500) NOT NULL,
    task_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Pending', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Pending',
    result ENUM('Normal', 'Abnormal', 'Critical', 'Pending', 'N/A') DEFAULT 'Pending',
    comments TEXT,
    follow_up_instructions TEXT,
    assigned_to_provider_id BIGINT,
    completed_date DATETIME,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (assigned_to_provider_id) REFERENCES providers(provider_id),
    INDEX idx_encounter (encounter_id),
    INDEX idx_patient (patient_id),
    INDEX idx_department (department_id),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- =====================================================
-- AUDIT AND LOGGING TABLES
-- =====================================================

-- Audit Log for tracking changes
CREATE TABLE audit_log (
    audit_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id BIGINT NOT NULL,
    action ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    user_id BIGINT,
    changed_data JSON,
    ip_address VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_table_record (table_name, record_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB;

-- Document Attachments
CREATE TABLE documents (
    document_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    encounter_id BIGINT,
    document_type VARCHAR(100) NOT NULL,
    document_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    uploaded_by_provider_id BIGINT,
    uploaded_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by_provider_id) REFERENCES providers(provider_id),
    INDEX idx_patient (patient_id),
    INDEX idx_encounter (encounter_id)
) ENGINE=InnoDB;

-- =====================================================
-- INSERT SAMPLE DEPARTMENTS
-- =====================================================

INSERT INTO departments (department_name, department_code, phone) VALUES
('Emergency Department', 'ED', '555-0100'),
('Cardiology', 'CARDIO', '555-0200'),
('Radiology', 'RAD', '555-0300'),
('Laboratory', 'LAB', '555-0400'),
('Orthopedics', 'ORTHO', '555-0500'),
('Internal Medicine', 'IM', '555-0600'),
('Pediatrics', 'PEDS', '555-0700'),
('Obstetrics & Gynecology', 'OBGYN', '555-0800'),
('Surgery', 'SURG', '555-0900'),
('Pharmacy', 'PHARM', '555-1000');

-- =====================================================
-- CREATE VIEWS FOR COMMON QUERIES
-- =====================================================

-- Patient Summary View
CREATE VIEW vw_patient_summary AS
SELECT
    p.patient_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    p.date_of_birth,
    p.age,
    p.gender,
    p.phone_primary,
    p.email,
    COUNT(DISTINCT e.encounter_id) AS total_encounters,
    MAX(e.encounter_date) AS last_visit_date
FROM patients p
LEFT JOIN encounters e ON p.patient_id = e.patient_id
WHERE p.is_active = TRUE
GROUP BY p.patient_id;

-- Active Prescriptions View
CREATE VIEW vw_active_prescriptions AS
SELECT
    pr.prescription_id,
    p.patient_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    pr.medication_name,
    pr.dosage,
    pr.frequency,
    pr.start_date,
    pr.end_date,
    pr.refills,
    CONCAT(prov.first_name, ' ', prov.last_name) AS prescribed_by,
    ph.pharmacy_name
FROM prescriptions pr
JOIN patients p ON pr.patient_id = p.patient_id
JOIN providers prov ON pr.prescribed_by_provider_id = prov.provider_id
LEFT JOIN pharmacies ph ON pr.pharmacy_id = ph.pharmacy_id
WHERE pr.status = 'Active';

-- Pending Lab Results View
CREATE VIEW vw_pending_labs AS
SELECT
    lo.lab_order_id,
    e.encounter_id,
    p.patient_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    lo.test_name,
    lo.ordered_date,
    lo.status,
    CONCAT(prov.first_name, ' ', prov.last_name) AS ordered_by
FROM lab_orders lo
JOIN encounters e ON lo.encounter_id = e.encounter_id
JOIN patients p ON e.patient_id = p.patient_id
JOIN providers prov ON lo.ordered_by_provider_id = prov.provider_id
WHERE lo.status IN ('Ordered', 'Collected', 'In Process');

-- =====================================================
-- END OF SCHEMA
-- =====================================================
