# Fix for Primary Key Schema Mismatch

## Critical Issue

**Error**: `ProgrammingError: column user_profiles.profile_id does not exist`

This error indicates a fundamental schema mismatch between your database and Django models. The database tables were created with Django's default primary key name (`id`), but your models use custom primary key names (e.g., `profile_id`, `patient_id`, etc.).

## Problem Summary

All models in the InHealth EHR system use custom primary key names, but the database tables were created with the default `id` column. This causes Django to look for columns that don't exist.

### Affected Tables (30+ tables)

- `user_profiles` → expects `profile_id`
- `patients` → expects `patient_id`
- `providers` → expects `provider_id`
- `hospitals` → expects `hospital_id`
- `departments` → expects `department_id`
- `nurses` → expects `nurse_id`
- `office_administrators` → expects `admin_id`
- `encounters` → expects `encounter_id`
- `vital_signs` → expects `vital_signs_id`
- `diagnoses` → expects `diagnosis_id`
- `prescriptions` → expects `prescription_id`
- ... and 20+ more tables

## ⚠️ CRITICAL: Backup First

**DO NOT PROCEED WITHOUT A BACKUP!**

```bash
# Create a full database backup
pg_dump -h localhost -U inhealth_user inhealth_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Or with custom host/port
pg_dump -h your_host -p 5432 -U inhealth_user inhealth_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

## Solution Options

### Option 1: Automated Fix (Recommended)

This script fixes ALL tables at once and is idempotent (safe to run multiple times).

```bash
# 1. Backup your database (DO THIS FIRST!)
pg_dump -h localhost -U inhealth_user inhealth_db > backup_before_pk_fix.sql

# 2. Run the comprehensive fix script
psql -h localhost -U inhealth_user -d inhealth_db -f django_inhealth/fix_all_primary_keys.sql

# 3. Verify the changes
psql -h localhost -U inhealth_user -d inhealth_db -f django_inhealth/check_database_schema.sql
```

### Option 2: Manual Fix (Step by Step)

If you prefer to fix tables one at a time:

```bash
# 1. Backup first!
pg_dump -h localhost -U inhealth_user inhealth_db > backup_before_pk_fix.sql

# 2. Fix just the user_profiles table
psql -h localhost -U inhealth_user -d inhealth_db -f django_inhealth/fix_user_profiles_schema.sql

# 3. Test your application
# If it works, proceed with other tables using fix_all_primary_keys.sql
```

### Option 3: Interactive Fix

Connect to your database and run commands manually:

```bash
psql -h localhost -U inhealth_user -d inhealth_db
```

Then in the PostgreSQL prompt:

```sql
-- Backup reminder
\echo 'Have you backed up your database? (Press Ctrl+C to exit if not)'

-- Fix user_profiles table (example)
BEGIN;

ALTER TABLE user_profiles RENAME COLUMN id TO profile_id;
ALTER SEQUENCE user_profiles_id_seq RENAME TO user_profiles_profile_id_seq;

-- Verify the change
\d user_profiles

-- If everything looks good, commit
COMMIT;

-- If something went wrong, rollback
-- ROLLBACK;
```

## What the Fix Script Does

The `fix_all_primary_keys.sql` script:

1. **Creates a helper function** that safely renames primary key columns
2. **Checks each table** to see if renaming is needed
3. **Renames the column** from `id` to the custom name (e.g., `profile_id`)
4. **Renames the sequence** (e.g., `user_profiles_id_seq` → `user_profiles_profile_id_seq`)
5. **Skips tables** that already have the correct name
6. **Shows verification** results at the end

## Verification After Fix

### Check if fix was successful:

```sql
-- Connect to database
psql -h localhost -U inhealth_user -d inhealth_db

-- Check user_profiles table specifically
\d user_profiles

-- Check all primary keys
SELECT
    tc.table_name,
    kcu.column_name as primary_key_column
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.constraint_type = 'PRIMARY KEY'
    AND tc.table_name LIKE '%'
ORDER BY tc.table_name;
```

### Test your application:

1. Restart your Django application:
   ```bash
   sudo systemctl restart gunicorn
   # or
   sudo systemctl restart inhealth
   ```

2. Access the application:
   - Homepage: https://inhealth.eminencetechsolutions.com:8899/
   - MFA Setup: https://inhealth.eminencetechsolutions.com:8899/mfa/setup/
   - Admin: https://inhealth.eminencetechsolutions.com:8899/admin/

3. Check Django can query the tables:
   ```bash
   cd /home/zia/ihealth/inhealthUSA/django_inhealth
   source venv/bin/activate
   python manage.py shell
   ```

   ```python
   from healthcare.models import UserProfile, Patient, Provider

   # Test queries
   UserProfile.objects.count()  # Should work without errors
   Patient.objects.count()
   Provider.objects.count()
   ```

## Rollback (If Something Goes Wrong)

If you encounter issues after running the fix:

### Option A: Restore from backup

```bash
# Stop your application first
sudo systemctl stop gunicorn

# Drop and recreate the database
psql -h localhost -U postgres
```

```sql
-- In PostgreSQL prompt
DROP DATABASE inhealth_db;
CREATE DATABASE inhealth_db OWNER inhealth_user;
\q
```

```bash
# Restore from backup
psql -h localhost -U inhealth_user -d inhealth_db < backup_before_pk_fix.sql

# Restart application
sudo systemctl start gunicorn
```

### Option B: Manual rollback (if you know which tables were affected)

```sql
-- Example: Rollback user_profiles only
BEGIN;

ALTER TABLE user_profiles RENAME COLUMN profile_id TO id;
ALTER SEQUENCE user_profiles_profile_id_seq RENAME TO user_profiles_id_seq;

COMMIT;
```

## Why This Happened

This typically occurs when:

1. **Migrations were not run** - The database was created using an old schema
2. **Models were changed** - Primary key names were customized after initial migration
3. **Database was imported** - From another system with different naming conventions
4. **Manual table creation** - Tables were created manually without using Django migrations

## Prevention for Future

To avoid this issue in the future:

1. **Always run migrations** when deploying:
   ```bash
   python manage.py migrate
   ```

2. **Check migration status** before deployment:
   ```bash
   python manage.py showmigrations
   ```

3. **Use version control** for migration files

4. **Test in staging** before applying to production

## Files Included

- `fix_all_primary_keys.sql` - Comprehensive fix for all tables
- `fix_user_profiles_schema.sql` - Fix for user_profiles table only
- `check_database_schema.sql` - Diagnostic queries
- `FIX_PRIMARY_KEY_SCHEMA.md` - This documentation

## Support

If you encounter issues:

1. **Check the backup** - Make sure your backup is complete and valid
2. **Check logs** - Django and PostgreSQL logs for specific errors
3. **Verify database connection** - Ensure credentials and connection settings are correct
4. **Test queries** - Use the verification queries above

## Expected Outcome

After successfully applying the fix:

✅ Homepage loads without errors
✅ MFA setup works
✅ Admin panel accessible
✅ All CRUD operations work
✅ No `ProgrammingError` about missing columns

## Timeline

- **Backup**: 5-10 minutes (depending on database size)
- **Fix execution**: 1-2 minutes
- **Verification**: 2-3 minutes
- **Total**: ~15 minutes

## Next Steps

1. ✅ Create database backup
2. ✅ Run the fix script
3. ✅ Verify the changes
4. ✅ Test the application
5. ✅ Monitor for any errors
6. ✅ Apply the security fields fix from previous ticket (if not done)

---

**Remember**: Always backup before making schema changes!
