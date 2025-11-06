# EHR Database Schema Documentation

## InTAM Health Inc - Electronic Medical Record System

### Overview

This MySQL database schema provides a comprehensive Electronic Health Record (EHR) system designed to support all aspects of patient care, from demographics to billing. The schema is normalized, scalable, and designed with healthcare standards in mind.

### Generated Files

- `generate_ehr_schema.py` - Python script to generate the MySQL schema
- `ehr_schema.sql` - Generated MySQL database schema (ready to execute)

### Quick Start

#### Generate the SQL Schema

```bash
python3 generate_ehr_schema.py > ehr_schema.sql
```

#### Execute the Schema in MySQL

```bash
mysql -u root -p < ehr_schema.sql
```

Or connect to MySQL and source the file:

```sql
mysql> source ehr_schema.sql;
```

### Database Structure

The database `ehr_database` contains 40+ tables organized into the following sections:

#### 1. Patient Demographics and Basic Information

- **patients** - Core patient demographics (name, DOB, gender, address, contact info)
- **emergency_contacts** - Emergency contact information for patients
- **insurance_information** - Patient insurance details and coverage

#### 2. Providers and Staff

- **providers** - Healthcare providers (physicians, nurses, specialists)
- **departments** - Hospital/clinic departments (Emergency, Cardiology, Lab, etc.)

#### 3. Encounters and Visits

- **encounters** - Patient visits and encounters (inpatient, outpatient, emergency, telehealth)

#### 4. Chief Complaint and History

- **chief_complaints** - Primary reason for patient visit
- **history_presenting_illness** - Detailed HPI (onset, location, duration, characteristics, etc.)
- **review_of_systems** - Comprehensive ROS checklist covering all body systems

#### 5. Patient History

- **social_history** - Tobacco, alcohol, drugs, occupation, lifestyle
- **past_medical_history** - Previous medical conditions and diagnoses
- **surgical_history** - Past surgical procedures
- **family_history** - Family medical conditions
- **allergies** - Medication, food, and environmental allergies

#### 6. Vital Signs and Physical Examination

- **vital_signs** - Temperature, BP, heart rate, respiratory rate, SpO2, weight, height, BMI
- **physical_examinations** - Physical exam findings by body system

#### 7. Orders and Procedures

- **physician_orders** - All provider orders (medications, labs, imaging, procedures)
- **medications** - Medication master list
- **order_medications** - Medications ordered for patients
- **procedures_tests** - Procedures and tests ordered

#### 8. Laboratory and Imaging

- **laboratory_tests** - Lab test orders, results, and interpretations
- **imaging_studies** - Radiology studies (X-ray, CT, MRI, ultrasound)

#### 9. Assessment and Diagnosis

- **diagnoses** - Patient diagnoses with ICD-10 and ICD-11 codes
- **clinical_impressions** - MDM (Medical Decision Making) and clinical assessment

#### 10. Treatment Plans

- **treatment_plans** - Comprehensive treatment plans and follow-up
- **prescriptions** - Pharmacy prescriptions with detailed instructions

#### 11. Billing

- **billing** - CPT codes, charges, payments, and billing status

#### 12. Nursing Evaluation

- **nursing_evaluations** - Nursing assessments and interventions

#### 13. Patient Tracker

- **patient_tracker** - Department-by-department patient tracking

#### 14. Audit and System Tables

- **audit_log** - System audit trail for changes
- **provider_signatures** - Electronic signatures for documentation

#### 15. Reference Data

- **icd10_codes** - ICD-10 diagnosis codes reference
- **cpt_codes** - CPT procedure codes reference

### Key Features

#### 1. Comprehensive Data Model

- Covers all aspects of the EMR template provided
- Properly normalized to reduce data redundancy
- Foreign key constraints ensure referential integrity

#### 2. Automated Calculations

**Triggers:**
- Auto-calculate BMI when vital signs are recorded
- Auto-update patient age based on date of birth

#### 3. Useful Views

Pre-built views for common queries:

- `v_patient_complete` - Complete patient demographics with insurance
- `v_active_encounters` - Active patient encounters
- `v_patient_allergies` - Patient allergy summary
- `v_active_prescriptions` - Active prescriptions
- `v_latest_vital_signs` - Latest vital signs per encounter
- `v_patient_tracker_summary` - Patient tracking summary

#### 4. Stored Procedures

- `sp_create_encounter` - Create new patient encounter
- `sp_get_patient_history` - Get complete patient medical history
- `sp_update_patient_ages` - Update all patient ages

#### 5. Performance Optimization

- Strategic indexes on frequently queried columns
- Composite indexes for common multi-column queries
- InnoDB engine for transaction support

#### 6. Audit Trail

- Complete audit logging for compliance
- Tracks all INSERT, UPDATE, DELETE operations
- Stores old and new values in JSON format

### Table Relationships

```
patients (1) -> (M) encounters
patients (1) -> (M) allergies
patients (1) -> (M) prescriptions
patients (1) -> (M) emergency_contacts
patients (1) -> (M) insurance_information

encounters (1) -> (1) chief_complaints
encounters (1) -> (1) history_presenting_illness
encounters (1) -> (1) review_of_systems
encounters (1) -> (M) vital_signs
encounters (1) -> (1) physical_examinations
encounters (1) -> (M) physician_orders
encounters (1) -> (M) diagnoses
encounters (1) -> (1) clinical_impressions
encounters (1) -> (1) treatment_plans
encounters (1) -> (M) patient_tracker

physician_orders (1) -> (M) order_medications
physician_orders (1) -> (M) procedures_tests
```

### Sample Department Data

The schema automatically populates the following departments:

- Emergency Department (ED)
- Cardiology (CARDIO)
- Radiology (RAD)
- Laboratory (LAB)
- Orthopedics (ORTHO)
- Internal Medicine (IM)
- Pediatrics (PEDS)
- Surgery (SURG)
- Neurology (NEURO)
- Pharmacy (PHARM)
- Nursing (NURSE)
- Primary Care (PC)

### Usage Examples

#### Create a New Patient

```sql
INSERT INTO patients (first_name, last_name, date_of_birth, gender, address_street, address_city, address_state, address_zip, phone_number, email)
VALUES ('John', 'Doe', '1980-05-15', 'Male', '123 Main St', 'Chicago', 'IL', '60601', '555-0100', 'john.doe@email.com');
```

#### Add Emergency Contact

```sql
INSERT INTO emergency_contacts (patient_id, contact_name, relationship, phone_number, is_primary)
VALUES (1, 'Jane Doe', 'Spouse', '555-0101', TRUE);
```

#### Create a New Encounter

```sql
CALL sp_create_encounter(1, 1, 'Outpatient', 6, @encounter_id);
SELECT @encounter_id;
```

#### Record Vital Signs

```sql
INSERT INTO vital_signs (encounter_id, temperature_value, temperature_unit, blood_pressure_systolic, blood_pressure_diastolic, heart_rate, respiratory_rate, oxygen_saturation, weight_value, weight_unit, height_value, height_unit)
VALUES (1, 98.6, 'F', 120, 80, 72, 16, 98.0, 180, 'lbs', 70, 'in');
```

#### Add a Diagnosis

```sql
INSERT INTO diagnoses (encounter_id, diagnosis_description, icd10_code, diagnosis_type, status, diagnosed_by)
VALUES (1, 'Essential hypertension', 'I10', 'Primary', 'Active', 1);
```

#### Query Active Patient Encounters

```sql
SELECT * FROM v_active_encounters WHERE patient_name LIKE '%Doe%';
```

#### Get Patient Complete History

```sql
CALL sp_get_patient_history(1);
```

### Integration Points

The schema includes placeholders for future integrations:

1. **ICD-10/ICD-11 API Integration**
   - Tables: `icd10_codes`, `diagnoses.icd11_code`
   - Connect to external ICD code databases

2. **Pharmacopeia and Pharmacy API**
   - Tables: `medications`, `prescriptions`
   - Fields include pharmacy details for e-prescribing

3. **CPT Code Integration**
   - Table: `cpt_codes`, `billing`
   - Connect to CPT code reference systems

4. **clinGPT AI Suggestions**
   - Fields: `clinical_impressions.clingpt_suggestions`, `treatment_plans.clingpt_suggestions`
   - Integrate AI-powered clinical decision support

### Security Considerations

1. **Audit Trail** - All changes are logged in `audit_log` table
2. **Soft Deletes** - Use `is_active` flags instead of hard deletes where appropriate
3. **Data Encryption** - Consider encrypting sensitive fields at application level
4. **Access Control** - Implement role-based access control at application level
5. **HIPAA Compliance** - Ensure all PHI is properly protected

### Performance Tips

1. **Indexes** - The schema includes strategic indexes; monitor query performance and add more as needed
2. **Partitioning** - Consider partitioning large tables (e.g., `encounters`, `vital_signs`) by date
3. **Archiving** - Implement archiving strategy for old encounters and related data
4. **Query Optimization** - Use EXPLAIN to analyze slow queries
5. **Connection Pooling** - Use connection pooling in your application

### Maintenance

#### Regular Tasks

1. **Update Patient Ages**
   ```sql
   CALL sp_update_patient_ages();
   ```

2. **Clean Old Audit Logs** (older than 7 years for compliance)
   ```sql
   DELETE FROM audit_log WHERE changed_at < DATE_SUB(NOW(), INTERVAL 7 YEAR);
   ```

3. **Archive Completed Encounters** (older than 1 year)
   ```sql
   -- Move to archive database/table
   ```

### Backup and Recovery

1. **Daily Backups**
   ```bash
   mysqldump -u root -p ehr_database > ehr_backup_$(date +%Y%m%d).sql
   ```

2. **Point-in-Time Recovery**
   - Enable MySQL binary logging
   - Keep transaction logs for required retention period

### Extending the Schema

To add new features:

1. Create migration scripts
2. Update the Python generator script
3. Regenerate the schema
4. Test thoroughly before production deployment

### Support and Compliance

This schema is designed to support:

- **HIPAA** - Health Insurance Portability and Accountability Act
- **HL7** - Health Level 7 standards (data can be mapped to HL7 FHIR)
- **ICD-10/ICD-11** - International Classification of Diseases
- **CPT** - Current Procedural Terminology
- **LOINC** - Logical Observation Identifiers Names and Codes (for lab tests)

### Version Information

- **Database Version**: 1.0
- **MySQL Version**: 5.7+ or 8.0+
- **Character Set**: utf8mb4
- **Collation**: utf8mb4_unicode_ci
- **Storage Engine**: InnoDB

### Contact

For questions or support regarding this EHR database schema, please contact InTAM Health Inc.

---

**Generated**: Auto-generated using `generate_ehr_schema.py`

**Last Updated**: 2025-11-06
