-- SQL script to fix user_profiles table schema mismatch
-- This script renames the primary key from 'id' to 'profile_id' to match the Django model

-- IMPORTANT: Back up your database before running this script!
-- pg_dump -h localhost -U inhealth_user inhealth_db > backup_before_schema_fix.sql

BEGIN;

-- Step 1: Check if we need to rename the primary key column
DO $$
BEGIN
    -- If 'id' column exists and 'profile_id' doesn't, rename it
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles' AND column_name = 'id'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles' AND column_name = 'profile_id'
    ) THEN
        -- Rename the primary key column from 'id' to 'profile_id'
        ALTER TABLE user_profiles RENAME COLUMN id TO profile_id;

        RAISE NOTICE 'Renamed primary key column from id to profile_id';
    ELSE
        RAISE NOTICE 'Column already correctly named or both exist - manual intervention needed';
    END IF;
END $$;

-- Step 2: Ensure the column is the primary key
DO $$
BEGIN
    -- Check if profile_id is the primary key
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_name = 'user_profiles'
            AND tc.constraint_type = 'PRIMARY KEY'
            AND kcu.column_name = 'profile_id'
    ) THEN
        -- Drop old primary key constraint if it exists
        IF EXISTS (
            SELECT 1 FROM information_schema.table_constraints
            WHERE table_name = 'user_profiles' AND constraint_type = 'PRIMARY KEY'
        ) THEN
            EXECUTE (
                SELECT 'ALTER TABLE user_profiles DROP CONSTRAINT ' || constraint_name || ';'
                FROM information_schema.table_constraints
                WHERE table_name = 'user_profiles' AND constraint_type = 'PRIMARY KEY'
            );
        END IF;

        -- Add profile_id as primary key
        ALTER TABLE user_profiles ADD PRIMARY KEY (profile_id);

        RAISE NOTICE 'Set profile_id as primary key';
    END IF;
END $$;

-- Step 3: Ensure the sequence is correctly named (if it exists)
DO $$
BEGIN
    -- Rename sequence if it exists with old name
    IF EXISTS (
        SELECT 1 FROM pg_class
        WHERE relname = 'user_profiles_id_seq' AND relkind = 'S'
    ) AND NOT EXISTS (
        SELECT 1 FROM pg_class
        WHERE relname = 'user_profiles_profile_id_seq' AND relkind = 'S'
    ) THEN
        ALTER SEQUENCE user_profiles_id_seq RENAME TO user_profiles_profile_id_seq;
        RAISE NOTICE 'Renamed sequence from user_profiles_id_seq to user_profiles_profile_id_seq';
    END IF;
END $$;

-- Step 4: Update any foreign key references from other tables
-- (These will be handled automatically by PostgreSQL if using CASCADE)

COMMIT;

-- Verification queries
\echo '\n=== VERIFICATION ==='
\echo 'Current user_profiles table structure:'

SELECT
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'user_profiles'
ORDER BY ordinal_position;

\echo '\nPrimary key constraints:'

SELECT
    tc.constraint_name,
    kcu.column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.table_name = 'user_profiles'
    AND tc.constraint_type = 'PRIMARY KEY';

\echo '\nSequences:'

SELECT
    relname as sequence_name
FROM pg_class
WHERE relname LIKE 'user_profiles%_seq'
    AND relkind = 'S';
