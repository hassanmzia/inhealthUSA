# Fix for Nurse Migration Error

## The Error
```
psycopg2.errors.DuplicateTable: relation "nurses" already exists
django.db.utils.ProgrammingError: relation "nurses" already exists
```

## Root Cause
The migration `0004_alter_userprofile_role_nurse` is trying to create the "nurses" table, but it already exists in your database. This happens when:
- The table was created manually
- The table was created by a previous migration that wasn't tracked
- Database and migration history are out of sync

## The Solution

### Option 1: Fake the Migration (Recommended)
This tells Django that the migration has been applied without running the SQL commands:

```bash
cd /home/zia/django_inhealth
source venv/bin/activate
python manage.py migrate healthcare 0004_alter_userprofile_role_nurse --fake
python manage.py migrate
```

### Option 2: Alternative - Skip and Mark as Applied
If Option 1 doesn't work, try this:

```bash
cd /home/zia/django_inhealth
source venv/bin/activate

# Mark the specific migration as applied
python manage.py migrate healthcare 0004_alter_userprofile_role_nurse --fake

# Run any remaining migrations
python manage.py migrate
```

### Option 3: If Table Structure Doesn't Match (Use with Caution)
Only use this if the existing table structure is incorrect or incomplete:

```bash
cd /home/zia/django_inhealth
source venv/bin/activate

# CAUTION: This will drop existing data in the nurses table!
# Backup your data first!
python manage.py dbshell
```

Then in the PostgreSQL shell:
```sql
-- Backup the table first (if it has data)
CREATE TABLE nurses_backup AS SELECT * FROM nurses;

-- Drop the existing table
DROP TABLE nurses CASCADE;

-- Exit the shell
\q
```

Then run migrations normally:
```bash
python manage.py migrate
```

## Recommended Steps

1. **First, try Option 1** - It's the safest and fastest
2. **Verify the migration status** after faking:
   ```bash
   python manage.py showmigrations healthcare
   ```
3. **Continue with remaining migrations**:
   ```bash
   python manage.py migrate
   ```

## Verification

After applying the fix, verify everything is working:

```bash
# Check migration status
python manage.py showmigrations healthcare

# All migrations should show [X] (applied)

# Test the application
python manage.py runserver
```

## Expected Output
After running the fake migration, you should see:
```
Operations to perform:
  Target specific migration: 0004_alter_userprofile_role_nurse, from healthcare
Running migrations:
  Rendering model states... DONE
  Applying healthcare.0004_alter_userprofile_role_nurse... FAKED
```

Then running `python manage.py migrate` should complete successfully.

## Status
✅ Solution provided - awaiting user confirmation
