# ============================================================================
# COMPREHENSIVE SECURITY SETTINGS FOR INHEALTH EHR
# Add these settings to django_inhealth/inhealth/settings.py
# ============================================================================

"""
Security Implementation:
1. SQL Injection Prevention - Django ORM, parameterized queries
2. XSS Prevention - Template auto-escaping, CSP headers
3. CSRF Prevention - CSRF middleware, tokens
4. Secure Headers - CSP, HSTS, X-Frame-Options, etc.
5. HTTPS Enforcement - Secure cookies, SSL redirects
"""

import os

# ============================================================================
# INSTALLED APPS - Add Security Apps
# ============================================================================

INSTALLED_APPS = [
    # ... existing apps ...
    'csp',  # Content Security Policy
    'rest_framework',  # For API
]

# ============================================================================
# MIDDLEWARE - Security Stack (Order Matters!)
# ============================================================================

MIDDLEWARE = [
    # 1. Security Middleware - MUST be first
    'django.middleware.security.SecurityMiddleware',

    # 2. Session Middleware
    'django.contrib.sessions.middleware.SessionMiddleware',

    # 3. Content Security Policy Middleware
    'csp.middleware.CSPMiddleware',

    # 4. Common Middleware
    'django.middleware.common.CommonMiddleware',

    # 5. CSRF Protection Middleware - CRITICAL
    'django.middleware.csrf.CsrfViewMiddleware',

    # 6. Authentication Middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # 7. Session Security Middleware (custom)
    'healthcare.middleware.session_security.SessionSecurityMiddleware',
    'healthcare.middleware.session_security.ConcurrentSessionMiddleware',
    'healthcare.middleware.session_security.SecurityHeadersMiddleware',

    # 8. Messages Middleware
    'django.contrib.messages.middleware.MessageMiddleware',

    # 9. Clickjacking Protection
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # 10. Additional security middleware
    'allauth.account.middleware.AccountMiddleware',
    'axes.middleware.AxesMiddleware',  # Must be last
]

# ============================================================================
# CSRF PROTECTION (Cross-Site Request Forgery)
# ============================================================================

# Enable CSRF Protection - CRITICAL
CSRF_COOKIE_NAME = 'inhealth_csrftoken'
CSRF_COOKIE_SECURE = not DEBUG  # HTTPS only in production
CSRF_COOKIE_HTTPONLY = True  # Prevents JavaScript access
CSRF_COOKIE_SAMESITE = 'Strict'  # Maximum CSRF protection
CSRF_COOKIE_AGE = 31449600  # 1 year
CSRF_USE_SESSIONS = True  # Store CSRF token in session

# Trusted origins for CSRF (update with your domains)
if not DEBUG:
    CSRF_TRUSTED_ORIGINS = [
        'https://yourdomain.com',
        'https://www.yourdomain.com',
    ]

# CSRF failure view (optional custom view)
# CSRF_FAILURE_VIEW = 'healthcare.views.csrf_failure'

# ============================================================================
# XSS PROTECTION (Cross-Site Scripting)
# ============================================================================

# Template Auto-Escaping is enabled by default in Django
# Never disable it!
# TEMPLATE_STRING_IF_INVALID = ''  # Don't show invalid variables

# Secure browser XSS filter
SECURE_BROWSER_XSS_FILTER = True

# Content-Type Options (prevents MIME sniffing)
SECURE_CONTENT_TYPE_NOSNIFF = True

# ============================================================================
# CONTENT SECURITY POLICY (CSP)
# ============================================================================

# CSP Directives - Restrictive by default
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",  # Allow inline scripts (use nonces in production)
    "'unsafe-eval'",    # Required for some JS libraries (remove if possible)
    "https://cdn.heapanalytics.com",  # Analytics
    "https://www.google.com",  # reCAPTCHA
    "https://www.gstatic.com",  # reCAPTCHA
)
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",  # Allow inline styles
    "https://fonts.googleapis.com",  # Google Fonts
)
CSP_IMG_SRC = (
    "'self'",
    "data:",  # Allow data: URIs for images
    "https:",  # Allow HTTPS images
)
CSP_FONT_SRC = (
    "'self'",
    "data:",
    "https://fonts.gstatic.com",  # Google Fonts
)
CSP_CONNECT_SRC = (
    "'self'",
    "https://cdn.heapanalytics.com",  # Analytics
)
CSP_FRAME_SRC = (
    "'self'",
    "https://www.google.com",  # reCAPTCHA
)
CSP_OBJECT_SRC = ("'none'",)  # Disable plugins
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)  # Prevent framing (same as X-Frame-Options: DENY)
CSP_UPGRADE_INSECURE_REQUESTS = True  # Upgrade HTTP to HTTPS

# CSP Reporting (optional - for monitoring CSP violations)
# CSP_REPORT_URI = '/csp-report/'
# CSP_REPORT_ONLY = False  # Set to True to test CSP without enforcing

# ============================================================================
# CLICKJACKING PROTECTION
# ============================================================================

# Prevent site from being embedded in iframe
X_FRAME_OPTIONS = 'DENY'  # or 'SAMEORIGIN' if you need iframes

# ============================================================================
# HTTPS / SSL / TLS SETTINGS
# ============================================================================

if not DEBUG:
    # Force HTTPS for all requests
    SECURE_SSL_REDIRECT = True

    # HSTS (HTTP Strict Transport Security)
    # Tells browsers to only connect via HTTPS
    SECURE_HSTS_SECONDS = 31536000  # 1 year (recommended: 63072000 for 2 years)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True  # Enable HSTS preloading

    # Redirect HTTP to HTTPS
    SECURE_REDIRECT_EXEMPT = []  # Paths exempt from HTTPS redirect

    # Proxy SSL Header (if behind load balancer/proxy)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Secure Referrer Policy
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

else:
    # Development settings
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0

# ============================================================================
# SESSION SECURITY
# ============================================================================

# Session Cookie Security
SESSION_COOKIE_NAME = 'inhealth_sid'
SESSION_COOKIE_SECURE = not DEBUG  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # Prevents JavaScript access (XSS protection)
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_COOKIE_AGE = 1800  # 30 minutes
SESSION_SAVE_EVERY_REQUEST = True  # Update session on every request

# Session timeout settings
SESSION_INACTIVITY_TIMEOUT = 1800  # 30 minutes of inactivity
SESSION_RENEWAL_THRESHOLD = 300  # Renew if within 5 minutes of expiry

# ============================================================================
# CSRF COOKIE SECURITY
# ============================================================================

CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# ============================================================================
# SQL INJECTION PREVENTION
# ============================================================================

"""
Django ORM prevents SQL injection by default through:
1. Parameterized queries (always use ORM, never raw SQL)
2. Query parameterization
3. Automatic escaping

NEVER USE:
    - User.objects.raw("SELECT * FROM users WHERE username = '%s'" % username)  # VULNERABLE!
    - cursor.execute("SELECT * FROM users WHERE id = %s" % user_id)  # VULNERABLE!

ALWAYS USE:
    - User.objects.filter(username=username)  # SAFE
    - cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])  # SAFE
    - User.objects.raw("SELECT * FROM users WHERE username = %s", [username])  # SAFE
"""

# Database connection settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'inhealth_db'),
        'USER': os.environ.get('DB_USER', 'inhealth_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'inhealth_password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c search_path=public',  # Prevent schema injection
        },
    }
}

# ============================================================================
# ALLOWED HOSTS - Production Security
# ============================================================================

if not DEBUG:
    # CRITICAL: Restrict allowed hosts in production
    ALLOWED_HOSTS = [
        'yourdomain.com',
        'www.yourdomain.com',
        # Add your actual domains
    ]
else:
    # Development only
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '172.168.1.125']

# ============================================================================
# ADMIN SECURITY
# ============================================================================

# Require HTTPS for admin in production
if not DEBUG:
    ADMIN_URL = 'secure-admin-panel/'  # Obscure admin URL
else:
    ADMIN_URL = 'admin/'

# Admin SSL redirect
ADMIN_FORCE_SSL = not DEBUG

# ============================================================================
# FILE UPLOAD SECURITY
# ============================================================================

# Maximum file upload size
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB

# Allowed file extensions (whitelist approach)
ALLOWED_UPLOAD_EXTENSIONS = [
    '.jpg', '.jpeg', '.png', '.gif', '.pdf',
    '.doc', '.docx', '.xls', '.xlsx', '.csv'
]

# File upload permissions
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Virus scanning (if available)
# VIRUS_SCAN_ENABLED = True
# VIRUS_SCAN_COMMAND = 'clamdscan'

# ============================================================================
# PASSWORD SECURITY
# ============================================================================

# Strong password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # HIPAA recommendation
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Password hashers - Use strong algorithms
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Recommended
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# ============================================================================
# LOGGING - Security Events
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/security.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security_file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security.csrf': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'healthcare': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ============================================================================
# ADDITIONAL SECURITY HEADERS
# ============================================================================

# Permissions Policy (formerly Feature-Policy)
PERMISSIONS_POLICY = {
    'accelerometer': [],
    'ambient-light-sensor': [],
    'autoplay': [],
    'camera': [],
    'encrypted-media': [],
    'fullscreen': ['self'],
    'geolocation': [],
    'gyroscope': [],
    'magnetometer': [],
    'microphone': [],
    'midi': [],
    'payment': [],
    'picture-in-picture': [],
    'usb': [],
    'vr': [],
    'xr-spatial-tracking': [],
}

# ============================================================================
# API SECURITY
# ============================================================================

# REST Framework Security Settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'device': '10000/day',
    }
}

# ============================================================================
# CORS SETTINGS (If using separate frontend)
# ============================================================================

# Only enable if you have a separate frontend
# CORS_ALLOWED_ORIGINS = [
#     "https://yourdomain.com",
#     "https://app.yourdomain.com",
# ]
# CORS_ALLOW_CREDENTIALS = True

# ============================================================================
# SECRET KEY SECURITY
# ============================================================================

# CRITICAL: Use environment variable in production
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-change-this-in-production')

# Warn if using default secret key in production
if not DEBUG and 'insecure' in SECRET_KEY:
    import warnings
    warnings.warn(
        "Using insecure SECRET_KEY in production! "
        "Set DJANGO_SECRET_KEY environment variable.",
        RuntimeWarning
    )

# ============================================================================
# DEBUG MODE SECURITY
# ============================================================================

# NEVER set DEBUG = True in production
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

# Show detailed error pages only in development
if not DEBUG:
    ADMINS = [
        ('Admin', 'admin@yourdomain.com'),
    ]
    MANAGERS = ADMINS

# ============================================================================
# SECURITY CHECKLIST
# ============================================================================

"""
Before deploying to production, verify:

1. HTTPS/SSL:
   ✓ SECURE_SSL_REDIRECT = True
   ✓ SECURE_HSTS_SECONDS = 31536000
   ✓ SESSION_COOKIE_SECURE = True
   ✓ CSRF_COOKIE_SECURE = True
   ✓ SSL certificate installed

2. CSRF Protection:
   ✓ CsrfViewMiddleware enabled
   ✓ CSRF tokens in all forms
   ✓ CSRF_COOKIE_HTTPONLY = True
   ✓ CSRF_COOKIE_SAMESITE = 'Strict'

3. XSS Protection:
   ✓ Template auto-escaping enabled
   ✓ CSP headers configured
   ✓ SECURE_BROWSER_XSS_FILTER = True
   ✓ User input sanitized

4. SQL Injection:
   ✓ Using Django ORM (no raw SQL)
   ✓ Parameterized queries only
   ✓ No string interpolation in queries

5. Headers:
   ✓ X-Frame-Options set
   ✓ Content-Security-Policy configured
   ✓ X-Content-Type-Options: nosniff
   ✓ Referrer-Policy set

6. Authentication:
   ✓ Strong password requirements
   ✓ Argon2 password hashing
   ✓ MFA enabled for admin users
   ✓ Session timeout configured

7. General:
   ✓ DEBUG = False
   ✓ ALLOWED_HOSTS restricted
   ✓ SECRET_KEY in environment variable
   ✓ Security logging enabled
   ✓ File upload restrictions
   ✓ Run: python manage.py check --deploy

Run security check:
    python manage.py check --deploy
"""
