# Fix for Migration Errors (Nurses & Office Administrators)

## The Errors
```
psycopg2.errors.DuplicateTable: relation "nurses" already exists
django.db.utils.ProgrammingError: relation "nurses" already exists
```

```
psycopg2.errors.DuplicateTable: relation "office_administrators" already exists
django.db.utils.ProgrammingError: relation "office_administrators" already exists
```

## Root Cause
The migrations `0004_alter_userprofile_role_nurse` and `0005_officeadministrator` are trying to create tables that already exist in your database. This happens when:
- The tables were created manually
- The tables were created by previous migrations that weren't tracked
- Database and migration history are out of sync

## The Solution

### Option 1: Fake the Migrations (Recommended - Use Script)
Use the automated script:

```bash
cd /home/zia/django_inhealth
./fix_nurse_migration.sh
```

### Option 2: Manual Fix
This tells Django that the migrations have been applied without running the SQL commands:

```bash
cd /home/zia/django_inhealth
source venv/bin/activate
python manage.py migrate healthcare 0004_alter_userprofile_role_nurse --fake
python manage.py migrate healthcare 0005_officeadministrator --fake
python manage.py migrate
```

### Option 3: If Table Structure Doesn't Match (Use with Caution)
Only use this if the existing table structure is incorrect or incomplete:

```bash
cd /home/zia/django_inhealth
source venv/bin/activate

# CAUTION: This will drop existing data in the tables!
# Backup your data first!
python manage.py dbshell
```

Then in the PostgreSQL shell:
```sql
-- Backup the tables first (if they have data)
CREATE TABLE nurses_backup AS SELECT * FROM nurses;
CREATE TABLE office_administrators_backup AS SELECT * FROM office_administrators;

-- Drop the existing tables
DROP TABLE nurses CASCADE;
DROP TABLE office_administrators CASCADE;

-- Exit the shell
\q
```

Then run migrations normally:
```bash
python manage.py migrate
```

## Recommended Steps

1. **First, try Option 1 (automated script)** - It's the safest and fastest
2. **Verify the migration status** after running the script:
   ```bash
   cd /home/zia/django_inhealth
   source venv/bin/activate
   python manage.py showmigrations healthcare
   ```
3. **Test the application**:
   ```bash
   python manage.py runserver
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
After running the fix script, you should see:
```
✓ Successfully faked migration 0004_alter_userprofile_role_nurse
✓ Successfully faked migration 0005_officeadministrator
✓ All migrations completed successfully!
```

## Status
✅ Solution ready - run ./fix_nurse_migration.sh to apply the fix
