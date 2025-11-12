# Deployment Instructions - Fix Patient and Doctor Profiles

This guide will help you create the missing Patient and Provider profiles for users in your Django application.

## Prerequisites

- PostgreSQL database must be running
- Virtual environment activated
- Django project properly configured

## Step 1: Start PostgreSQL (if not already running)

```bash
# On Linux/Ubuntu
sudo service postgresql start

# On macOS
brew services start postgresql

# On Windows
# Start PostgreSQL from Services or pgAdmin
```

## Step 2: Navigate to Project Directory

```bash
cd /home/user/inhealthUSA/django_inhealth
```

## Step 3: Activate Virtual Environment

```bash
source ../venv/bin/activate
```

## Step 4: Run Database Migrations

This will add the 'nurse' role to the database and create new tables for billing, payments, insurance, and devices.

```bash
python manage.py migrate
```

Expected output:
```
Running migrations:
  Applying healthcare.0003_billing_alter_userprofile_role_payment_and_more... OK
```

## Step 5: Create Missing Patient/Provider Profiles

You have **three options** to create the missing profiles:

### Option A: Use the Django Management Command (Recommended)

```bash
# Preview what will be created (dry run)
python manage.py fix_patient_profiles --dry-run

# Actually create the profiles
python manage.py fix_patient_profiles
```

### Option B: Use the Standalone Script

```bash
cd /home/user/inhealthUSA
python create_profiles.py
```

### Option C: Use Django Shell Manually

```bash
cd /home/user/inhealthUSA/django_inhealth
python manage.py shell
```

Then paste this code:

```python
from django.contrib.auth.models import User
from healthcare.models import UserProfile, Patient, Provider

# Get all users with patient role but no Patient record
for profile in UserProfile.objects.filter(role='patient'):
    user = profile.user
    if not hasattr(user, 'patient_profile') or user.patient_profile is None:
        patient = Patient.objects.create(
            user=user,
            first_name=user.first_name or 'Unknown',
            last_name=user.last_name or 'Unknown',
            date_of_birth=profile.date_of_birth or '2000-01-01',
            gender='Other',
            email=user.email,
        )
        print(f"Created Patient profile for {user.username}")

# Get all users with doctor role but no Provider record
for profile in UserProfile.objects.filter(role='doctor'):
    user = profile.user
    if not hasattr(user, 'provider_profile') or user.provider_profile is None:
        provider = Provider.objects.create(
            user=user,
            first_name=user.first_name or 'Unknown',
            last_name=user.last_name or 'Unknown',
            npi=f'TEMP{user.id:010d}',  # Temporary NPI
            email=user.email,
        )
        print(f"Created Provider profile for {user.username} with temporary NPI: {provider.npi}")

print("Done!")
```

## Step 6: Verify Profiles Were Created

```bash
python manage.py shell
```

Then run:

```python
from django.contrib.auth.models import User
from healthcare.models import Patient, Provider

# Check patients
print(f"Total patients: {Patient.objects.count()}")
for patient in Patient.objects.all():
    print(f"  - {patient.full_name} (User: {patient.user.username if patient.user else 'No user'})")

# Check providers
print(f"\nTotal providers: {Provider.objects.count()}")
for provider in Provider.objects.all():
    print(f"  - Dr. {provider.full_name} (User: {provider.user.username if provider.user else 'No user'}, NPI: {provider.npi})")
```

## Step 7: Update Temporary NPIs (Important!)

For any doctors that were created, they will have a temporary NPI like `TEMP0000000001`. You need to update these with real NPI numbers:

### Using Django Admin:
1. Go to `http://your-domain/admin/`
2. Click on "Providers"
3. Find the provider with temporary NPI
4. Click on their name
5. Update the NPI field with the real NPI
6. Save

### Using Django Shell:
```python
from healthcare.models import Provider

# Find provider with temporary NPI
provider = Provider.objects.get(npi='TEMP0000000001')  # Replace with actual temp NPI

# Update with real NPI
provider.npi = '1234567890'  # Replace with real NPI
provider.save()

print(f"Updated NPI for Dr. {provider.full_name}")
```

## Step 8: Restart Django Server

```bash
# If using runserver
python manage.py runserver

# If using gunicorn (production)
sudo systemctl restart gunicorn
# or
gunicorn inhealth.wsgi:application --bind 0.0.0.0:8000
```

## Testing

1. **As a Patient:**
   - Log in with a patient account
   - Click on "Patients" in the dashboard
   - You should be redirected to your patient profile
   - No error message should appear

2. **As a Doctor:**
   - Log in with a doctor account
   - Click on "Doctors" in the dashboard
   - You should be redirected to your provider profile
   - No error message should appear

## Troubleshooting

### Error: "connection to server at localhost... failed"
- PostgreSQL is not running. Start it using the commands in Step 1.

### Error: "relation 'patients' does not exist"
- Migrations haven't been run. Go back to Step 4.

### Error: "UNIQUE constraint failed: providers.npi"
- Two doctors are trying to use the same NPI. Each doctor must have a unique NPI.
- Update the NPIs as described in Step 7.

### Profiles still not appearing
- Clear your browser cache and restart the Django server
- Check the Django logs for errors
- Run the verification commands in Step 6

## What Changed in the Code

1. **Added nurse role** to `UserProfile.ROLE_CHOICES`
2. **Created signals** to auto-create Patient/Provider records when UserProfile is created
3. **Updated views** to auto-create profiles if missing instead of showing error
4. **Created management command** `fix_patient_profiles` to fix existing users
5. **Added migrations** for new models (Billing, Payment, Insurance, Device)

## Need Help?

If you encounter any issues:
1. Check the Django logs: `tail -f /path/to/django/logs/debug.log`
2. Check PostgreSQL logs: `tail -f /var/log/postgresql/postgresql-*.log`
3. Run Django check: `python manage.py check`
4. Test database connection: `python manage.py dbshell`
