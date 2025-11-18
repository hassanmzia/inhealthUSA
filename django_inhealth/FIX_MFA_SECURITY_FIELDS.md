# Fix for MFA Setup Error - Missing Security Fields

## Problem
When accessing `/mfa/setup/`, you encounter the error:
```
ProgrammingError: column "failed_login_attempts" of relation "user_profiles" does not exist
```

## Root Cause
The `user_profiles` table in the database is missing several security-related columns that were added to the `UserProfile` model:
- `failed_login_attempts`
- `account_locked_until`
- `password_reset_token`
- `password_reset_token_expires`
- `last_password_change`
- `email_verification_token`
- `email_verified`
- `email_verified_at`
- `auth_provider`
- `external_id`
- `mfa_backup_codes` (renamed from `backup_codes`)

## Solution

### Option 1: Run SQL Script (Recommended for Production)

1. Connect to your PostgreSQL database:
   ```bash
   psql -h localhost -U inhealth_user -d inhealth_db
   ```

2. Run the SQL script:
   ```bash
   \i /path/to/django_inhealth/add_security_fields.sql
   ```

   Or run it directly:
   ```bash
   psql -h localhost -U inhealth_user -d inhealth_db -f django_inhealth/add_security_fields.sql
   ```

3. Verify the columns were added:
   ```sql
   \d user_profiles
   ```

### Option 2: Run Django Migration

1. Activate your virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Run the migration:
   ```bash
   python manage.py migrate healthcare 0016_add_security_fields
   ```

3. Verify the migration was applied:
   ```bash
   python manage.py showmigrations healthcare
   ```

### Option 3: Manual SQL Commands (Quick Fix)

If you prefer to run the SQL commands manually, execute these in your PostgreSQL database:

```sql
BEGIN;

ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0 NOT NULL;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS account_locked_until TIMESTAMP WITH TIME ZONE NULL;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR(255) NULL;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS password_reset_token_expires TIMESTAMP WITH TIME ZONE NULL;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS last_password_change TIMESTAMP WITH TIME ZONE NULL;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(255) NULL;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE NOT NULL;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP WITH TIME ZONE NULL;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(50) NULL;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS external_id VARCHAR(255) NULL;

COMMIT;
```

Note: PostgreSQL versions before 9.6 don't support `IF NOT EXISTS` for `ADD COLUMN`. If you're using an older version, use the provided `add_security_fields.sql` script instead.

## Verification

After applying the fix, verify that:

1. The MFA setup page loads without errors:
   ```
   https://your-domain.com/mfa/setup/
   ```

2. All columns are present in the database:
   ```sql
   SELECT column_name FROM information_schema.columns
   WHERE table_name = 'user_profiles'
   ORDER BY ordinal_position;
   ```

## Files Created

- `healthcare/migrations/0016_add_security_fields.py` - Django migration file
- `add_security_fields.sql` - SQL script for direct database update
- `FIX_MFA_SECURITY_FIELDS.md` - This documentation file

## Next Steps

After the fix is applied:
1. Test the MFA setup functionality
2. Test user login and authentication
3. Monitor logs for any additional errors
4. Consider running `python manage.py check` to identify any other issues

## Notes

- The SQL script is idempotent - it can be run multiple times safely
- The migration file (0016) should be committed to version control
- If you have a staging environment, test there first before applying to production
