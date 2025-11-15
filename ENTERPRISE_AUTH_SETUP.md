# Enterprise Authentication Setup Guide
## InHealth EHR - Multi-Provider SSO Configuration

This guide covers the setup and configuration of enterprise authentication for InHealth EHR, including Azure AD, Okta, AWS Cognito, SAML, CAC/PKI, and Microsoft Active Directory.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Authentication Providers](#authentication-providers)
   - [Azure Active Directory](#1-azure-active-directory)
   - [Okta](#2-okta)
   - [AWS Cognito](#3-aws-cognito)
   - [SAML 2.0](#4-saml-20)
   - [CAC/PKI](#5-cac-pki-common-access-card)
   - [Microsoft Active Directory (LDAP)](#6-microsoft-active-directory-ldap)
5. [Security Features](#security-features)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The InHealth EHR platform now supports multiple enterprise authentication methods:

- **Azure Active Directory** - Microsoft cloud identity service
- **Okta** - Cloud-based identity management
- **AWS Cognito** - Amazon's user authentication service
- **SAML 2.0** - Enterprise SSO standard
- **CAC/PKI** - Smart card/certificate authentication
- **Microsoft Active Directory** - On-premise LDAP integration
- **Standard Login** - Email/password authentication

All authentication methods include:
- Secure token storage
- Session management
- MFA enforcement
- Failed login protection
- Automatic account linking

---

## Prerequisites

- Python 3.8+
- Django 4.2+
- PostgreSQL 12+
- SSL/TLS certificates (for production)
- Access to chosen identity provider (Azure AD, Okta, etc.)

---

## Installation

### 1. Install Required Packages

```bash
pip install -r requirements.txt
```

Key packages installed:
- `django-allauth` - Social authentication
- `mozilla-django-oidc` - OIDC authentication
- `python3-saml` - SAML authentication
- `django-axes` - Failed login protection
- `msal` - Microsoft Authentication Library
- `pyOpenSSL` - Certificate handling

### 2. Configure Environment Variables

Copy the environment template:

```bash
cp .env.django.example .env
```

Edit `.env` with your configuration (see provider-specific sections below).

### 3. Run Database Migrations

```bash
python manage.py migrate
```

This creates tables for:
- Sites framework
- Django-allauth
- Django-axes (failed login tracking)
- OIDC sessions

### 4. Create a Site Object

```bash
python manage.py shell
```

```python
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
site.domain = 'your-domain.com'
site.name = 'InHealth EHR'
site.save()
```

---

## Authentication Providers

### 1. Azure Active Directory

**Setup Steps:**

1. **Register Application in Azure Portal**
   - Go to [Azure Portal](https://portal.azure.com)
   - Navigate to: Azure Active Directory > App registrations
   - Click "New registration"
   - Name: "InHealth EHR"
   - Supported account types: Choose based on your needs
   - Redirect URI: `https://your-domain.com/oidc/callback/`

2. **Get Client Credentials**
   - After registration, note the "Application (client) ID"
   - Note the "Directory (tenant) ID"
   - Go to "Certificates & secrets" > "New client secret"
   - Copy the secret value immediately (it won't be shown again)

3. **Configure API Permissions**
   - Go to "API permissions"
   - Add permissions: Microsoft Graph > Delegated
   - Add: `openid`, `email`, `profile`, `User.Read`
   - Grant admin consent

4. **Update `.env` File**

```bash
AZURE_AD_TENANT_ID=your-tenant-id
AZURE_AD_CLIENT_ID=your-client-id
AZURE_AD_CLIENT_SECRET=your-client-secret
AZURE_AD_AUTHORIZATION_ENDPOINT=https://login.microsoftonline.com/your-tenant-id/oauth2/v2.0/authorize
AZURE_AD_TOKEN_ENDPOINT=https://login.microsoftonline.com/your-tenant-id/oauth2/v2.0/token
AZURE_AD_USER_ENDPOINT=https://graph.microsoft.com/v1.0/me
AZURE_AD_JWKS_ENDPOINT=https://login.microsoftonline.com/your-tenant-id/discovery/v2.0/keys
```

5. **Test Login**
   - Navigate to `https://your-domain.com/auth/`
   - Click "Azure Active Directory"
   - You should be redirected to Microsoft login

---

### 2. Okta

**Setup Steps:**

1. **Create Application in Okta**
   - Log in to [Okta Developer Console](https://developer.okta.com/)
   - Applications > Create App Integration
   - Sign-in method: OIDC
   - Application type: Web Application
   - App name: "InHealth EHR"
   - Grant type: Authorization Code
   - Sign-in redirect URIs: `https://your-domain.com/oidc/callback/`
   - Sign-out redirect URIs: `https://your-domain.com/logout/`

2. **Get Client Credentials**
   - Copy Client ID
   - Copy Client Secret
   - Note your Okta domain (e.g., `dev-12345.okta.com`)

3. **Assign Users/Groups**
   - Go to Assignments tab
   - Assign people or groups who should have access

4. **Update `.env` File**

```bash
OKTA_ENABLED=True
OKTA_ORG_URL=https://your-org.okta.com
OKTA_CLIENT_ID=your-client-id
OKTA_CLIENT_SECRET=your-client-secret
OKTA_ISSUER=https://your-org.okta.com/oauth2/default
```

5. **Test Login**
   - Navigate to `https://your-domain.com/auth/`
   - Click "Okta SSO"

---

### 3. AWS Cognito

**Setup Steps:**

1. **Create User Pool**
   - Go to [AWS Cognito Console](https://console.aws.amazon.com/cognito/)
   - Create User Pool
   - Configure sign-in options (email, username)
   - Configure MFA requirements
   - Complete the wizard

2. **Create App Client**
   - In your User Pool, go to "App integration"
   - Create app client
   - App type: Confidential client
   - App client name: "InHealth EHR"
   - Generate client secret: Yes
   - Allowed callback URLs: `https://your-domain.com/oidc/callback/`
   - Allowed sign-out URLs: `https://your-domain.com/logout/`

3. **Configure Domain**
   - Go to "App integration" > "Domain"
   - Create a Cognito domain or use custom domain
   - Note the domain (e.g., `your-app.auth.us-east-1.amazoncognito.com`)

4. **Update `.env` File**

```bash
AWS_COGNITO_ENABLED=True
AWS_COGNITO_REGION=us-east-1
AWS_COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
AWS_COGNITO_APP_CLIENT_ID=your-client-id
AWS_COGNITO_APP_CLIENT_SECRET=your-client-secret
AWS_COGNITO_DOMAIN=your-domain.auth.us-east-1.amazoncognito.com
```

5. **Test Login**
   - Navigate to `https://your-domain.com/auth/`
   - Click "AWS Cognito"

---

### 4. SAML 2.0

**Setup Steps:**

1. **Get SP Metadata**
   - Start Django server
   - Navigate to: `https://your-domain.com/saml/metadata/`
   - Save the XML metadata file

2. **Configure Identity Provider (IdP)**
   - Upload SP metadata to your IdP (e.g., AD FS, OneLogin, etc.)
   - Configure attribute mappings:
     - Email: `email`, `emailAddress`, or `mail`
     - First Name: `givenName` or `firstName`
     - Last Name: `surname`, `lastName`, or `sn`

3. **Get IdP Metadata**
   - Download IdP metadata from your provider
   - Extract:
     - Entity ID
     - SSO URL
     - X.509 Certificate

4. **Update `.env` File**

```bash
SAML_ENABLED=True
SAML_SP_ENTITY_ID=https://your-app.com/saml/metadata/
SAML_SP_ACS_URL=https://your-app.com/saml/acs/
SAML_SP_SLS_URL=https://your-app.com/saml/sls/
SAML_IDP_ENTITY_ID=https://your-idp.com
SAML_IDP_SSO_URL=https://your-idp.com/sso
SAML_IDP_X509_CERT=-----BEGIN CERTIFICATE-----...-----END CERTIFICATE-----
```

5. **Test Login**
   - Navigate to `https://your-domain.com/auth/`
   - Click "SAML SSO"

---

### 5. CAC / PKI (Common Access Card)

**Setup Steps:**

1. **Configure Web Server for Client Certificates**

**For Apache:**

```apache
<VirtualHost *:443>
    ServerName your-domain.com
    SSLEngine on
    SSLCertificateFile /path/to/server.crt
    SSLCertificateKeyFile /path/to/server.key
    
    # Enable client certificate authentication
    SSLVerifyClient optional
    SSLVerifyDepth 3
    SSLCACertificateFile /etc/ssl/certs/dod_ca_bundle.pem
    
    # Pass certificate info to Django
    RequestHeader set X-SSL-Client-Cert "%{SSL_CLIENT_CERT}s"
    RequestHeader set X-SSL-Client-S-DN "%{SSL_CLIENT_S_DN}s"
    RequestHeader set X-SSL-Client-I-DN "%{SSL_CLIENT_I_DN}s"
    
    ProxyPass / http://localhost:8000/
    ProxyPassReverse / http://localhost:8000/
</VirtualHost>
```

**For Nginx:**

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/server.crt;
    ssl_certificate_key /path/to/server.key;
    
    # Enable client certificate authentication
    ssl_client_certificate /etc/ssl/certs/dod_ca_bundle.pem;
    ssl_verify_client optional;
    ssl_verify_depth 3;
    
    # Pass certificate info to Django
    proxy_set_header X-SSL-Client-Cert $ssl_client_cert;
    proxy_set_header X-SSL-Client-S-DN $ssl_client_s_dn;
    proxy_set_header X-SSL-Client-I-DN $ssl_client_i_dn;
    
    location / {
        proxy_pass http://localhost:8000;
    }
}
```

2. **Install DoD CA Certificates**

```bash
# Download DoD CA bundle
wget https://dl.dod.cyber.mil/wp-content/uploads/pki-pke/zip/unclass-certificates_pkcs7_DoD.zip
unzip unclass-certificates_pkcs7_DoD.zip
# Convert and install certificates
cat *.pem > /etc/ssl/certs/dod_ca_bundle.pem
```

3. **Update `.env` File**

```bash
CAC_ENABLED=True
CAC_REQUIRE_CERT_FOR_LOGIN=False
CAC_CLIENT_CERT_HEADER=HTTP_X_SSL_CLIENT_CERT
CAC_CLIENT_DN_HEADER=HTTP_X_SSL_CLIENT_S_DN
CAC_ISSUER_DN_HEADER=HTTP_X_SSL_CLIENT_I_DN
CAC_CERT_AUTHORITY_CERT_PATH=/etc/ssl/certs/dod_ca_bundle.pem
```

4. **Enable CAC Middleware**

Add to `settings.py` MIDDLEWARE (if not already present):

```python
MIDDLEWARE = [
    # ... other middleware ...
    'healthcare.cac_middleware.CACAuthenticationMiddleware',
]
```

5. **Test Login**
   - Insert CAC/smart card
   - Navigate to `https://your-domain.com/auth/cac/`
   - Browser should prompt for certificate selection

---

### 6. Microsoft Active Directory (LDAP)

**Setup Steps:**

1. **Install LDAP Packages**

```bash
sudo apt-get install libldap2-dev libsasl2-dev
pip install django-auth-ldap python-ldap
```

2. **Update `.env` File**

```bash
AD_ENABLED=True
AUTH_LDAP_SERVER_URI=ldap://ad.example.com
AUTH_LDAP_BIND_DN=CN=ServiceAccount,OU=Service Accounts,DC=example,DC=com
AUTH_LDAP_BIND_PASSWORD=your-service-account-password
AUTH_LDAP_USER_SEARCH_BASE=ou=users,dc=example,dc=com
```

3. **Test LDAP Connection**

```bash
ldapsearch -x -H ldap://ad.example.com \
  -D "CN=ServiceAccount,OU=Service Accounts,DC=example,DC=com" \
  -w your-password \
  -b "ou=users,dc=example,dc=com" \
  "(sAMAccountName=testuser)"
```

4. **Test Login**
   - Use AD username/password at standard login page
   - LDAP backend will authenticate automatically

---

## Security Features

### 1. Multi-Factor Authentication (MFA)

MFA is enforced through the existing TOTP system:

- Users can enable MFA from their profile
- MFA can be required for staff/superusers via `.env`:

```bash
MFA_REQUIRED_FOR_STAFF=True
MFA_REQUIRED_FOR_SUPERUSER=True
```

### 2. Failed Login Protection

Django-axes tracks failed login attempts:

```bash
AXES_FAILURE_LIMIT=5  # Lock after 5 failures
AXES_COOLOFF_TIME=1   # Lock for 1 hour
```

### 3. Session Security

Secure session configuration:

```bash
SESSION_COOKIE_AGE=28800  # 8 hours
SESSION_COOKIE_SECURE=True  # HTTPS only
SESSION_COOKIE_HTTPONLY=True  # No JavaScript access
SESSION_COOKIE_SAMESITE=Lax  # CSRF protection
```

### 4. Token Storage

All OAuth/OIDC tokens are stored securely:
- ID tokens stored in database sessions
- Refresh tokens encrypted
- Access tokens in memory only

---

## Deployment

### Production Checklist

1. **Environment Variables**
   - [ ] Set `DEBUG=False`
   - [ ] Generate strong `SECRET_KEY`
   - [ ] Configure `ALLOWED_HOSTS`
   - [ ] Use real credentials (not test keys)

2. **SSL/TLS**
   - [ ] Install SSL certificates
   - [ ] Force HTTPS
   - [ ] Configure HSTS headers

3. **Database**
   - [ ] Use PostgreSQL (not SQLite)
   - [ ] Enable connection pooling
   - [ ] Set up automated backups

4. **Web Server**
   - [ ] Use Gunicorn/uWSGI
   - [ ] Configure Nginx/Apache reverse proxy
   - [ ] Set up static file serving
   - [ ] Configure media file serving

5. **Security**
   - [ ] Run security checklist: `python manage.py check --deploy`
   - [ ] Enable firewall
   - [ ] Configure fail2ban
   - [ ] Set up monitoring

6. **Testing**
   - [ ] Test each authentication provider
   - [ ] Verify MFA enforcement
   - [ ] Test failed login lockout
   - [ ] Verify session expiration

---

## Troubleshooting

### Common Issues

#### 1. "OIDC authentication failed"

**Symptoms:** Redirect to IdP works, but callback fails

**Solutions:**
- Verify redirect URI matches exactly in IdP configuration
- Check client ID and secret are correct
- Ensure scopes include `openid email profile`
- Check server logs for detailed error

#### 2. "SAML attributes missing email"

**Symptoms:** SAML login fails with "SAML attributes missing email"

**Solutions:**
- Verify IdP is sending email attribute
- Check attribute mapping in IdP configuration
- Review SAML response in browser dev tools
- Update `SAML_ATTRIBUTE_MAPPING` in settings.py if needed

#### 3. "CAC certificate not found"

**Symptoms:** CAC login doesn't detect certificate

**Solutions:**
- Verify web server is passing certificate headers
- Check certificate is valid and not expired
- Ensure DoD CA bundle is installed correctly
- Test with: `curl -k --cert /path/to/cac.p12 https://your-domain.com/`

#### 4. "Account locked" after failed logins

**Symptoms:** User can't login even with correct credentials

**Solutions:**
- Wait for cooloff period to expire
- Or reset via admin:
  ```bash
  python manage.py axes_reset_username username@example.com
  ```

#### 5. LDAP connection timeout

**Symptoms:** AD/LDAP authentication hangs or times out

**Solutions:**
- Verify network connectivity to AD server
- Check firewall allows LDAP (port 389) or LDAPS (port 636)
- Test with `ldapsearch` command
- Verify service account credentials

### Debug Mode

Enable detailed logging in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'mozilla_django_oidc': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'healthcare.auth_backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

---

## Support and Documentation

- **Django-allauth docs:** https://django-allauth.readthedocs.io/
- **Mozilla Django OIDC:** https://mozilla-django-oidc.readthedocs.io/
- **Python SAML:** https://github.com/onelogin/python3-saml
- **Django-axes:** https://django-axes.readthedocs.io/

---

## License

InHealth EHR - Enterprise Authentication
Copyright (c) 2024

---

**Last Updated:** November 2024
**Version:** 1.0
