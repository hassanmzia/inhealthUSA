-- SQL script to fix ALL primary key column names to match Django models
-- This script renames primary keys from 'id' to the custom names used in the models

-- CRITICAL: BACKUP YOUR DATABASE FIRST!
-- pg_dump -h localhost -U inhealth_user inhealth_db > backup_before_primary_key_fix.sql

-- This script is idempotent - it can be run multiple times safely

BEGIN;

-- Function to rename primary key column if needed
CREATE OR REPLACE FUNCTION rename_primary_key(
    p_table_name TEXT,
    p_new_pk_name TEXT
) RETURNS VOID AS $$
DECLARE
    v_old_pk_name TEXT;
    v_constraint_name TEXT;
    v_sequence_old TEXT;
    v_sequence_new TEXT;
BEGIN
    -- Get current primary key column name
    SELECT kcu.column_name, tc.constraint_name
    INTO v_old_pk_name, v_constraint_name
    FROM information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
    WHERE tc.table_name = p_table_name
        AND tc.constraint_type = 'PRIMARY KEY'
    LIMIT 1;

    -- If primary key column name is different from target, rename it
    IF v_old_pk_name IS NOT NULL AND v_old_pk_name != p_new_pk_name THEN
        -- Rename the column
        EXECUTE format('ALTER TABLE %I RENAME COLUMN %I TO %I',
            p_table_name, v_old_pk_name, p_new_pk_name);

        -- Try to rename the sequence
        v_sequence_old := p_table_name || '_' || v_old_pk_name || '_seq';
        v_sequence_new := p_table_name || '_' || p_new_pk_name || '_seq';

        IF EXISTS (SELECT 1 FROM pg_class WHERE relname = v_sequence_old AND relkind = 'S') THEN
            EXECUTE format('ALTER SEQUENCE %I RENAME TO %I',
                v_sequence_old, v_sequence_new);
            RAISE NOTICE 'Renamed % primary key: % -> % (and sequence)', p_table_name, v_old_pk_name, p_new_pk_name;
        ELSE
            RAISE NOTICE 'Renamed % primary key: % -> %', p_table_name, v_old_pk_name, p_new_pk_name;
        END IF;
    ELSE
        RAISE NOTICE 'Table % already has correct primary key name: %', p_table_name, p_new_pk_name;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Fix all tables with custom primary keys
SELECT rename_primary_key('hospitals', 'hospital_id');
SELECT rename_primary_key('departments', 'department_id');
SELECT rename_primary_key('user_profiles', 'profile_id');
SELECT rename_primary_key('patients', 'patient_id');
SELECT rename_primary_key('providers', 'provider_id');
SELECT rename_primary_key('nurses', 'nurse_id');
SELECT rename_primary_key('office_administrators', 'admin_id');
SELECT rename_primary_key('encounters', 'encounter_id');
SELECT rename_primary_key('vital_signs', 'vital_signs_id');
SELECT rename_primary_key('diagnoses', 'diagnosis_id');
SELECT rename_primary_key('prescriptions', 'prescription_id');
SELECT rename_primary_key('allergies', 'allergy_id');
SELECT rename_primary_key('medical_history', 'medical_history_id');
SELECT rename_primary_key('social_history', 'social_history_id');
SELECT rename_primary_key('family_history', 'family_history_id');
SELECT rename_primary_key('messages', 'message_id');
SELECT rename_primary_key('lab_tests', 'lab_test_id');
SELECT rename_primary_key('notifications', 'notification_id');
SELECT rename_primary_key('insurance_information', 'insurance_id');
SELECT rename_primary_key('billings', 'billing_id');
SELECT rename_primary_key('billing_items', 'item_id');
SELECT rename_primary_key('payments', 'payment_id');
SELECT rename_primary_key('devices', 'device_id');
SELECT rename_primary_key('notification_preferences', 'id'); -- This one uses default Django 'id'
SELECT rename_primary_key('vital_sign_alert_responses', 'alert_id');
SELECT rename_primary_key('ai_proposed_treatment_plans', 'proposal_id');
SELECT rename_primary_key('doctor_treatment_plans', 'plan_id');
SELECT rename_primary_key('api_keys', 'api_key_id');
SELECT rename_primary_key('authentication_config', 'config_id');

-- Drop the helper function
DROP FUNCTION rename_primary_key(TEXT, TEXT);

COMMIT;

-- Verification: Show all primary keys
\echo '\n=== VERIFICATION: All Primary Keys ==='

SELECT
    tc.table_name,
    kcu.column_name as primary_key_column
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.constraint_type = 'PRIMARY KEY'
    AND tc.table_name IN (
        'hospitals', 'departments', 'user_profiles', 'patients', 'providers',
        'nurses', 'office_administrators', 'encounters', 'vital_signs',
        'diagnoses', 'prescriptions', 'allergies', 'medical_history',
        'social_history', 'family_history', 'messages', 'lab_tests',
        'notifications', 'insurance_information', 'billings', 'billing_items',
        'payments', 'devices', 'notification_preferences',
        'vital_sign_alert_responses', 'ai_proposed_treatment_plans',
        'doctor_treatment_plans', 'api_keys', 'authentication_config'
    )
ORDER BY tc.table_name;

\echo '\nDone! All primary keys have been fixed to match Django models.'
