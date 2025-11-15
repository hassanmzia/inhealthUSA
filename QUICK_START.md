# Quick Start - Enterprise Authentication

## Fix: ModuleNotFoundError: No module named 'allauth'

If you're seeing this error, it means the enterprise authentication packages need to be installed in your virtual environment.

### Solution

**1. Activate your virtual environment:**

```bash
cd /path/to/inhealthUSA
source django_inhealth/venv/bin/activate
# or if your venv is elsewhere:
# source venv/bin/activate
```

**2. Install the required packages:**

Option A - Using the installation script:
```bash
./install_auth_packages.sh
```

Option B - Manual installation:
```bash
pip install -r requirements.txt
```

Option C - Install only critical auth packages:
```bash
pip install django-allauth mozilla-django-oidc python3-saml django-axes msal psycopg2-binary
```

**3. Run migrations:**

```bash
cd django_inhealth
python manage.py migrate
```

**4. Create Site object (required for django-allauth):**

```bash
python manage.py shell
```

Then in the Python shell:
```python
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
site.domain = 'localhost:8000'  # Change to your domain in production
site.name = 'InHealth EHR'
site.save()
exit()
```

**5. Test the server:**

```bash
python manage.py runserver
```

Navigate to: http://localhost:8000/auth/

You should see the provider selection page.

---

## Minimal Configuration for Testing

If you just want to test the system without configuring external providers, you can use standard login:

1. All environment variables for external providers default to disabled
2. Standard email/password login still works
3. Navigate to: http://localhost:8000/login/

To enable a provider later, edit `.env` and set the appropriate credentials.

---

## Configuration Steps

### For Development/Testing:

1. **Copy environment template:**
   ```bash
   cp .env.django.example .env
   ```

2. **Leave most settings as default** - They're already configured for disabled state

3. **Set only required settings in `.env`:**
   ```bash
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DB_NAME=inhealth_db
   DB_USER=inhealth_user
   DB_PASSWORD=your-password
   ```

### For Production with SSO:

See `ENTERPRISE_AUTH_SETUP.md` for detailed configuration of:
- Azure Active Directory
- Okta
- AWS Cognito
- SAML 2.0
- CAC/PKI
- Microsoft Active Directory (LDAP)

---

## Troubleshooting

### Error: "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### Error: "No module named 'django_recaptcha'"
```bash
pip install django-recaptcha
```

### Error: "No module named 'axes'"
```bash
pip install django-axes
```

### Error: Site matching query does not exist
```bash
python manage.py shell
>>> from django.contrib.sites.models import Site
>>> Site.objects.create(id=1, domain='localhost:8000', name='InHealth EHR')
>>> exit()
```

### Error: CSRF verification failed
Make sure you're accessing the site via the same domain configured in the Site object.

---

## Package List

The following packages are installed for enterprise authentication:

**Core Authentication:**
- `django-allauth` - Social/enterprise authentication framework
- `mozilla-django-oidc` - OpenID Connect authentication
- `python3-saml` - SAML 2.0 authentication
- `django-axes` - Failed login protection

**Identity Providers:**
- `msal` - Microsoft Authentication Library (Azure AD)
- `boto3` - AWS SDK (for Cognito)

**Security:**
- `pyOpenSSL` - Certificate/PKI authentication
- `cryptography` - Cryptographic operations
- `PyJWT` - JSON Web Tokens

**Optional:**
- `django-auth-ldap` - Active Directory integration
- `python-ldap` - LDAP support

---

## Minimal Test Setup

To test the authentication system without external providers:

1. Install packages: `pip install -r requirements.txt`
2. Run migrations: `python manage.py migrate`
3. Create site: See step 4 in Solution section above
4. Create superuser: `python manage.py createsuperuser`
5. Run server: `python manage.py runserver`
6. Visit: http://localhost:8000/auth/

All SSO providers will show as disabled. Click "Standard Login" to use email/password.

---

## Next Steps

Once the basic system is working:

1. ✅ Install packages and run migrations
2. ⬜ Choose authentication providers to enable
3. ⬜ Register applications with providers (Azure AD, Okta, etc.)
4. ⬜ Configure `.env` with provider credentials
5. ⬜ Test each provider
6. ⬜ Configure MFA requirements
7. ⬜ Set up production SSL/TLS
8. ⬜ Deploy to production

Refer to `ENTERPRISE_AUTH_SETUP.md` for detailed provider setup instructions.
