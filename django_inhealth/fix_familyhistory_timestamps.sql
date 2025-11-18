-- SQL script to add missing timestamp fields to family_history table
-- This fixes the migration error for created_at and updated_at fields

BEGIN;

-- Add created_at field with default value of current timestamp
-- For existing rows, this will set them to the current time
ALTER TABLE family_history
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE
DEFAULT CURRENT_TIMESTAMP NOT NULL;

-- Add updated_at field with default value of current timestamp
-- This will be automatically updated by Django on each save
ALTER TABLE family_history
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE
DEFAULT CURRENT_TIMESTAMP NOT NULL;

-- After adding the columns, we can remove the default for created_at
-- because auto_now_add will handle new records
ALTER TABLE family_history
ALTER COLUMN created_at DROP DEFAULT;

-- Keep the default for updated_at since auto_now needs it
-- (Django updates this value on each save)

COMMIT;

-- Verification
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'family_history'
    AND column_name IN ('created_at', 'updated_at')
ORDER BY column_name;
