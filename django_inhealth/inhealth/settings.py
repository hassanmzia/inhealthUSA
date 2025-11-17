"""
Django settings for InHealth EHR project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-change-this-in-production-2024-inhealth-ehr'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Silence system checks for development
SILENCED_SYSTEM_CHECKS = [
    'django_recaptcha.recaptcha_test_key_error',  # Allow test keys in development
]

# Application definition
INSTALLED_APPS = [
    'healthcare',  # Our main healthcare app - must come before django.contrib.admin to override templates
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required for django-allauth
    'django_recaptcha',  # django-recaptcha for spam protection

    # Enterprise Authentication
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.microsoft',
    'allauth.socialaccount.providers.oauth2',
    'mozilla_django_oidc',  # OIDC for Azure AD, Okta, AWS Cognito
    'axes',  # Login attempt tracking and blocking
]

# Sites framework (required for django-allauth)
SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Multi-Factor Authentication middleware - Enforces MFA for admin users
    'healthcare.admin_mfa_middleware.AdminMFAMiddleware',
    # Session security middleware - Auto-logout on inactivity
    'healthcare.middleware.session_security.SessionSecurityMiddleware',
    'healthcare.middleware.session_security.ConcurrentSessionMiddleware',
    'healthcare.middleware.session_security.SecurityHeadersMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Required for django-allauth
    'axes.middleware.AxesMiddleware',  # Login attempt tracking (must be last)
]

ROOT_URLCONF = 'inhealth.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'inhealth.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'inhealth_db'),
        'USER': os.environ.get('DB_USER', 'inhealth_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'inhealth_password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'healthcare.password_validators.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'healthcare.password_validators.MaximumLengthValidator',
        'OPTIONS': {
            'max_length': 128,
        }
    },
    {
        'NAME': 'healthcare.password_validators.ComplexityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'healthcare.password_validators.NoConsecutiveCharactersValidator',
        'OPTIONS': {
            'max_consecutive': 3,
        }
    },
    {
        'NAME': 'healthcare.password_validators.NoCommonPatternsValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Date and time formats
DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'

# ============================================================================
# AUTHENTICATION SETTINGS - Multi-Provider Enterprise Authentication
# ============================================================================

# Authentication Backends - Order matters! First successful auth wins.
AUTHENTICATION_BACKENDS = [
    # Standard Django authentication
    'django.contrib.auth.backends.ModelBackend',

    # Django-allauth for social/enterprise auth
    'allauth.account.auth_backends.AuthenticationBackend',

    # Mozilla Django OIDC for Azure AD, Okta, AWS Cognito
    'mozilla_django_oidc.auth.OIDCAuthenticationBackend',

    # Axes authentication backend for failed login tracking
    'axes.backends.AxesBackend',
]

# Basic authentication settings
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'login'

# ============================================================================
# DJANGO-ALLAUTH CONFIGURATION
# ============================================================================
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'optional'

# Adapter for custom logic
ACCOUNT_ADAPTER = 'healthcare.auth_adapters.EnterpriseAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'healthcare.auth_adapters.EnterpriseSocialAccountAdapter'

# ============================================================================
# OIDC CONFIGURATION - Azure AD, Okta, AWS Cognito
# ============================================================================

# Azure AD Configuration
OIDC_RP_CLIENT_ID = os.environ.get('AZURE_AD_CLIENT_ID', '')
OIDC_RP_CLIENT_SECRET = os.environ.get('AZURE_AD_CLIENT_SECRET', '')
OIDC_OP_AUTHORIZATION_ENDPOINT = os.environ.get(
    'AZURE_AD_AUTHORIZATION_ENDPOINT',
    'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize'
)
OIDC_OP_TOKEN_ENDPOINT = os.environ.get(
    'AZURE_AD_TOKEN_ENDPOINT',
    'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
)
OIDC_OP_USER_ENDPOINT = os.environ.get(
    'AZURE_AD_USER_ENDPOINT',
    'https://graph.microsoft.com/v1.0/me'
)
OIDC_OP_JWKS_ENDPOINT = os.environ.get(
    'AZURE_AD_JWKS_ENDPOINT',
    'https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys'
)

# Okta Configuration (when OKTA_ENABLED=True)
OKTA_ENABLED = os.environ.get('OKTA_ENABLED', 'False') == 'True'
OKTA_ORG_URL = os.environ.get('OKTA_ORG_URL', '')
OKTA_CLIENT_ID = os.environ.get('OKTA_CLIENT_ID', '')
OKTA_CLIENT_SECRET = os.environ.get('OKTA_CLIENT_SECRET', '')
OKTA_ISSUER = os.environ.get('OKTA_ISSUER', f'{OKTA_ORG_URL}/oauth2/default')

# AWS Cognito Configuration (when AWS_COGNITO_ENABLED=True)
AWS_COGNITO_ENABLED = os.environ.get('AWS_COGNITO_ENABLED', 'False') == 'True'
AWS_COGNITO_REGION = os.environ.get('AWS_COGNITO_REGION', 'us-east-1')
AWS_COGNITO_USER_POOL_ID = os.environ.get('AWS_COGNITO_USER_POOL_ID', '')
AWS_COGNITO_APP_CLIENT_ID = os.environ.get('AWS_COGNITO_APP_CLIENT_ID', '')
AWS_COGNITO_APP_CLIENT_SECRET = os.environ.get('AWS_COGNITO_APP_CLIENT_SECRET', '')
AWS_COGNITO_DOMAIN = os.environ.get('AWS_COGNITO_DOMAIN', '')

# OIDC Settings
OIDC_RP_SIGN_ALGO = os.environ.get('OIDC_RP_SIGN_ALGO', 'RS256')
OIDC_RP_SCOPES = os.environ.get('OIDC_RP_SCOPES', 'openid email profile')
OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS = int(os.environ.get('OIDC_RENEW_TOKEN_EXPIRY', '3600'))
OIDC_CREATE_USER = True
OIDC_USE_NONCE = True
OIDC_STORE_ID_TOKEN = True

# Custom callback for user creation from OIDC
OIDC_USERNAME_ALGO = 'healthcare.auth_backends.generate_username_from_email'

# ============================================================================
# SAML CONFIGURATION
# ============================================================================
SAML_ENABLED = os.environ.get('SAML_ENABLED', 'False') == 'True'
SAML_SP_ENTITY_ID = os.environ.get('SAML_SP_ENTITY_ID', 'https://your-app.com/saml/metadata/')
SAML_SP_ACS_URL = os.environ.get('SAML_SP_ACS_URL', 'https://your-app.com/saml/acs/')
SAML_SP_SLS_URL = os.environ.get('SAML_SP_SLS_URL', 'https://your-app.com/saml/sls/')
SAML_IDP_METADATA_URL = os.environ.get('SAML_IDP_METADATA_URL', '')
SAML_IDP_ENTITY_ID = os.environ.get('SAML_IDP_ENTITY_ID', '')
SAML_IDP_SSO_URL = os.environ.get('SAML_IDP_SSO_URL', '')
SAML_IDP_X509_CERT = os.environ.get('SAML_IDP_X509_CERT', '')

# SAML Attribute mapping
SAML_ATTRIBUTE_MAPPING = {
    'email': ['email', 'emailAddress', 'mail'],
    'first_name': ['givenName', 'firstName'],
    'last_name': ['surname', 'lastName', 'sn'],
    'username': ['username', 'uid', 'userPrincipalName'],
}

# ============================================================================
# CAC (Common Access Card) / PKI AUTHENTICATION
# ============================================================================
CAC_ENABLED = os.environ.get('CAC_ENABLED', 'False') == 'True'
CAC_VERIFY_CLIENT_CERT = CAC_ENABLED
CAC_CLIENT_CERT_HEADER = os.environ.get('CAC_CLIENT_CERT_HEADER', 'HTTP_X_SSL_CLIENT_CERT')
CAC_CLIENT_DN_HEADER = os.environ.get('CAC_CLIENT_DN_HEADER', 'HTTP_X_SSL_CLIENT_S_DN')
CAC_ISSUER_DN_HEADER = os.environ.get('CAC_ISSUER_DN_HEADER', 'HTTP_X_SSL_CLIENT_I_DN')

# CAC Certificate validation
CAC_CERT_AUTHORITY_CERT_PATH = os.environ.get(
    'CAC_CERT_AUTHORITY_CERT_PATH',
    '/etc/ssl/certs/dod_ca_bundle.pem'
)
CAC_REQUIRE_CERT_FOR_LOGIN = os.environ.get('CAC_REQUIRE_CERT_FOR_LOGIN', 'False') == 'True'

# ============================================================================
# SESSION SECURITY AND TOKEN STORAGE
# ============================================================================

# Session Engine - Database-backed sessions for tracking and security
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Session Expiration - HIPAA Compliance (30 minutes recommended)
# Override with environment variable: SESSION_COOKIE_AGE=1800
SESSION_COOKIE_AGE = int(os.environ.get('SESSION_COOKIE_AGE', '1800'))  # 30 minutes (was 8 hours)

# Session Inactivity Timeout - Auto-logout after no activity
# This works with SessionSecurityMiddleware
SESSION_INACTIVITY_TIMEOUT = int(os.environ.get('SESSION_INACTIVITY_TIMEOUT', '1800'))  # 30 minutes

# Session Renewal Threshold - Renew session if activity within this time
SESSION_RENEWAL_THRESHOLD = int(os.environ.get('SESSION_RENEWAL_THRESHOLD', '300'))  # 5 minutes

# Session cookie name - Custom name for security through obscurity
SESSION_COOKIE_NAME = 'inhealth_sid'

# Enhanced session security settings
SESSION_COOKIE_SECURE = not DEBUG  # Use secure cookies in production (HTTPS only)
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access (XSS protection)
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection (Lax = good balance, Strict = maximum security)
SESSION_SAVE_EVERY_REQUEST = True  # Required for activity tracking and auto-renewal
SESSION_EXPIRE_AT_BROWSER_CLOSE = os.environ.get('SESSION_EXPIRE_AT_BROWSER_CLOSE', 'False') == 'True'

# Session timeout excluded paths (won't trigger auto-logout)
SESSION_TIMEOUT_EXCLUDED_PATHS = [
    '/auth/',
    '/login/',
    '/logout/',
    '/static/',
    '/media/',
    '/password-reset/',
    '/verify-email/',
    '/resend-verification/',
]

# Prevent concurrent sessions - Optional (set to True for high security)
PREVENT_CONCURRENT_SESSIONS = os.environ.get('PREVENT_CONCURRENT_SESSIONS', 'False') == 'True'

# CSRF Protection - Enhanced
CSRF_COOKIE_NAME = 'inhealth_csrftoken'
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True  # Set to False if you need JavaScript access for AJAX
CSRF_COOKIE_SAMESITE = 'Strict'  # Strict for maximum CSRF protection
CSRF_COOKIE_AGE = 31449600  # 1 year
CSRF_USE_SESSIONS = True

# ============================================================================
# HTTPS/SSL SECURITY SETTINGS
# ============================================================================
# These settings ensure Django works properly with SSL certificates served by Nginx

# Redirect all HTTP requests to HTTPS (only in production)
# Nginx handles the actual SSL/TLS, this tells Django to enforce HTTPS URLs
SECURE_SSL_REDIRECT = not DEBUG

# Trust the X-Forwarded-Proto header from Nginx reverse proxy
# This tells Django when a request came in via HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HTTP Strict Transport Security (HSTS)
# Tells browsers to always use HTTPS for this site
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000  # 1 year (31536000 seconds)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Apply to all subdomains
    SECURE_HSTS_PRELOAD = True  # Eligible for browser HSTS preload list
else:
    SECURE_HSTS_SECONDS = 0  # Disabled in development

# Content Security and Browser Protection
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME type sniffing
SECURE_BROWSER_XSS_FILTER = True  # Enable browser XSS filter
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking (already set by middleware)

# Referrer Policy - Control what information is sent in the Referer header
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# SSL/TLS Certificate Paths (for reference - Nginx uses these, not Django directly)
# Certificate location: /etc/ssl/inhealth/certificate.crt
# Private key location: /etc/ssl/inhealth/private.key
# Nginx config: /etc/nginx/conf.d/inhealth_ssl.conf

# ============================================================================
# MULTI-FACTOR AUTHENTICATION (MFA) ENFORCEMENT
# ============================================================================
MFA_ENABLED = os.environ.get('MFA_ENABLED', 'True') == 'True'
MFA_REQUIRED_FOR_STAFF = os.environ.get('MFA_REQUIRED_FOR_STAFF', 'True') == 'True'
MFA_REQUIRED_FOR_SUPERUSER = os.environ.get('MFA_REQUIRED_FOR_SUPERUSER', 'True') == 'True'
MFA_GRACE_PERIOD_DAYS = int(os.environ.get('MFA_GRACE_PERIOD_DAYS', '7'))

# TOTP Settings (Time-based One-Time Password)
OTP_TOTP_ISSUER = os.environ.get('OTP_TOTP_ISSUER', 'InHealth EHR')
OTP_TOTP_DIGITS = 6
OTP_TOTP_PERIOD = 30

# ============================================================================
# DJANGO-AXES CONFIGURATION (Failed Login Protection)
# ============================================================================
AXES_ENABLED = True
AXES_FAILURE_LIMIT = int(os.environ.get('AXES_FAILURE_LIMIT', '5'))
AXES_COOLOFF_TIME = int(os.environ.get('AXES_COOLOFF_TIME', '1'))  # Hours
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = 'healthcare/auth/account_locked.html'
AXES_LOCKOUT_URL = '/account-locked/'
AXES_USERNAME_FORM_FIELD = 'email'
AXES_ONLY_USER_FAILURES = False

# ============================================================================
# MICROSOFT ACTIVE DIRECTORY (LDAP) - Optional
# ============================================================================
AD_ENABLED = os.environ.get('AD_ENABLED', 'False') == 'True'
if AD_ENABLED:
    # Add LDAP authentication backend
    AUTHENTICATION_BACKENDS.insert(1, 'django_auth_ldap.backend.LDAPBackend')

    # LDAP Server settings
    import ldap
    from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

    AUTH_LDAP_SERVER_URI = os.environ.get('AUTH_LDAP_SERVER_URI', 'ldap://ad.example.com')
    AUTH_LDAP_BIND_DN = os.environ.get('AUTH_LDAP_BIND_DN', '')
    AUTH_LDAP_BIND_PASSWORD = os.environ.get('AUTH_LDAP_BIND_PASSWORD', '')
    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        os.environ.get('AUTH_LDAP_USER_SEARCH_BASE', 'ou=users,dc=example,dc=com'),
        ldap.SCOPE_SUBTREE,
        "(sAMAccountName=%(user)s)"
    )

    # User attribute mapping
    AUTH_LDAP_USER_ATTR_MAP = {
        "first_name": "givenName",
        "last_name": "sn",
        "email": "mail"
    }

    # Cache settings
    AUTH_LDAP_CACHE_TIMEOUT = 3600

# Email Settings
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
# DEFAULT_FROM_EMAIL must match EMAIL_HOST_USER for Gmail SMTP authentication
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# Twilio SMS Settings
# Set these in your environment variables or .env file for security
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')  # Format: +1234567890

# Google reCAPTCHA Settings
# Get your keys from: https://www.google.com/recaptcha/admin
# Set these in your environment variables or .env file for security
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY', '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI')  # Test key
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY', '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe')  # Test key
# Note: The keys above are Google's test keys and will always pass validation.
# For production, replace with your own keys from https://www.google.com/recaptcha/admin
