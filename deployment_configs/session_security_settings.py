# ============================================================================
# SESSION AND COOKIE SECURITY SETTINGS
# Add these settings to your django_inhealth/inhealth/settings.py file
# ============================================================================

"""
HIPAA Compliance & Security Best Practices:
- HTTPOnly cookies (prevent XSS attacks)
- Secure cookies (HTTPS only)
- Short session expiration (auto-logout after inactivity)
- Session renewal on activity
- SameSite cookie protection (CSRF prevention)
- Concurrent session prevention
"""

# ============================================================================
# SESSION CONFIGURATION
# ============================================================================

# Session Engine - Database-backed sessions (required for tracking)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Alternative: Cached database sessions for better performance
# Requires cache backend configuration (Redis recommended)
# SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# ============================================================================
# SESSION EXPIRATION SETTINGS
# ============================================================================

# Session cookie age - Maximum session duration (30 minutes)
# HIPAA recommendation: 15-30 minutes for healthcare applications
SESSION_COOKIE_AGE = 1800  # 30 minutes in seconds

# Options for different security levels:
# SESSION_COOKIE_AGE = 900   # 15 minutes (High security)
# SESSION_COOKIE_AGE = 1800  # 30 minutes (Recommended)
# SESSION_COOKIE_AGE = 3600  # 60 minutes (Medium security)

# Session inactivity timeout (auto-logout after no activity)
# This is used by our SessionSecurityMiddleware
SESSION_INACTIVITY_TIMEOUT = 1800  # 30 minutes

# Session renewal threshold
# Renew session if activity occurs with less than this time remaining
SESSION_RENEWAL_THRESHOLD = 300  # 5 minutes

# Save session on every request (required for activity tracking)
SESSION_SAVE_EVERY_REQUEST = True

# Close session when browser closes
# Set to True for maximum security, False for user convenience
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Set to True for high security

# ============================================================================
# SESSION COOKIE SECURITY
# ============================================================================

# Custom session cookie name (obscures Django framework usage)
SESSION_COOKIE_NAME = 'inhealth_sid'

# HTTPOnly - Prevents JavaScript access to session cookie (XSS protection)
SESSION_COOKIE_HTTPONLY = True  # CRITICAL: Always True

# Secure - Only send cookie over HTTPS
# Set to True in production, False in development
if not DEBUG:
    SESSION_COOKIE_SECURE = True
else:
    SESSION_COOKIE_SECURE = False

# SameSite - Prevents CSRF attacks
# Options: 'Strict', 'Lax', 'None'
# 'Strict' = Maximum security, may affect user experience
# 'Lax' = Good balance of security and usability (recommended)
SESSION_COOKIE_SAMESITE = 'Lax'

# Cookie domain - Limit to specific domain
# SESSION_COOKIE_DOMAIN = '.yourdomain.com'  # Include subdomains
# SESSION_COOKIE_DOMAIN = 'yourdomain.com'   # Exact domain only

# Cookie path - Limit to specific URL path
SESSION_COOKIE_PATH = '/'

# ============================================================================
# CSRF COOKIE SECURITY
# ============================================================================

# Custom CSRF cookie name
CSRF_COOKIE_NAME = 'inhealth_csrftoken'

# HTTPOnly for CSRF cookie
# Note: Set to False if you need JavaScript access for AJAX requests
CSRF_COOKIE_HTTPONLY = True

# Secure cookie (HTTPS only)
if not DEBUG:
    CSRF_COOKIE_SECURE = True
else:
    CSRF_COOKIE_SECURE = False

# SameSite setting for CSRF cookie
CSRF_COOKIE_SAMESITE = 'Strict'  # Strict for maximum CSRF protection

# CSRF cookie age (how long the CSRF token is valid)
CSRF_COOKIE_AGE = 31449600  # 1 year in seconds

# CSRF cookie path
CSRF_COOKIE_PATH = '/'

# Trusted origins for CSRF (for AJAX requests from your domain)
if not DEBUG:
    CSRF_TRUSTED_ORIGINS = [
        'https://yourdomain.com',
        'https://www.yourdomain.com',
    ]

# Use X-CSRFToken header for AJAX requests
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'

# ============================================================================
# CONCURRENT SESSION PREVENTION
# ============================================================================

# Prevent users from logging in from multiple devices simultaneously
# Recommended for high-security healthcare applications
PREVENT_CONCURRENT_SESSIONS = False  # Set to True to enable

# ============================================================================
# SESSION TIMEOUT EXCLUDED PATHS
# ============================================================================

# Paths that should not trigger session timeout
# (e.g., login page, static files, health checks)
SESSION_TIMEOUT_EXCLUDED_PATHS = [
    '/auth/',
    '/login/',
    '/logout/',
    '/static/',
    '/media/',
    '/health/',
    '/password-reset/',
    '/verify-email/',
]

# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

# Add these middleware classes to your MIDDLEWARE setting
# Order matters - add after authentication middleware

"""
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # Add session security middleware HERE
    'healthcare.middleware.session_security.SessionSecurityMiddleware',
    'healthcare.middleware.session_security.ConcurrentSessionMiddleware',
    'healthcare.middleware.session_security.SecurityHeadersMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
"""

# ============================================================================
# AUTHENTICATION SETTINGS
# ============================================================================

# Redirect URL after login
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# ============================================================================
# PASSWORD VALIDATION (Enhanced)
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # HIPAA recommendation: minimum 12 characters
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Password hashers - Use strong hashing algorithms
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Recommended
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# Note: Install argon2 for best security
# pip install argon2-cffi

# ============================================================================
# ADDITIONAL SECURITY SETTINGS
# ============================================================================

if not DEBUG:
    # Force HTTPS
    SECURE_SSL_REDIRECT = True

    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Browser security
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True

    # Proxy configuration
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Clickjacking protection
X_FRAME_OPTIONS = 'DENY'  # Prevents site from being embedded in iframe

# ============================================================================
# LOGGING FOR SESSION SECURITY
# ============================================================================

# Add session security logging to your LOGGING configuration

"""
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/security.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'healthcare.middleware.session_security': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
"""

# ============================================================================
# CACHE CONFIGURATION (Optional but recommended)
# ============================================================================

# For better session performance with cached_db backend
# Requires Redis: pip install django-redis

"""
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'inhealth',
        'TIMEOUT': 300,
    }
}
"""

# ============================================================================
# DEPLOYMENT CHECKLIST
# ============================================================================

"""
Before deploying to production, verify:

1. Session Security:
   ✓ SESSION_COOKIE_SECURE = True
   ✓ SESSION_COOKIE_HTTPONLY = True
   ✓ SESSION_COOKIE_SAMESITE = 'Lax' or 'Strict'
   ✓ SESSION_COOKIE_AGE = 1800 (30 minutes or less)
   ✓ SESSION_SAVE_EVERY_REQUEST = True

2. CSRF Protection:
   ✓ CSRF_COOKIE_SECURE = True
   ✓ CSRF_COOKIE_HTTPONLY = True
   ✓ CSRF_COOKIE_SAMESITE = 'Strict'
   ✓ CSRF_TRUSTED_ORIGINS configured

3. Middleware:
   ✓ SessionSecurityMiddleware added
   ✓ ConcurrentSessionMiddleware added (optional)
   ✓ SecurityHeadersMiddleware added

4. HTTPS:
   ✓ SECURE_SSL_REDIRECT = True
   ✓ SECURE_HSTS_SECONDS = 31536000
   ✓ SSL certificate installed

5. Testing:
   ✓ Test session timeout (wait 30 min)
   ✓ Test session renewal (activity before timeout)
   ✓ Test concurrent sessions (if enabled)
   ✓ Test cookie security (inspect with browser DevTools)
   ✓ Run: python manage.py check --deploy

6. Compliance:
   ✓ Document session timeout policy
   ✓ Log session events (login, logout, timeout)
   ✓ Regular security audits
"""

# ============================================================================
# SECURITY LEVELS
# ============================================================================

"""
Choose a security level based on your requirements:

HIGH SECURITY (Recommended for HIPAA compliance):
- SESSION_COOKIE_AGE = 900 (15 minutes)
- SESSION_INACTIVITY_TIMEOUT = 900
- SESSION_EXPIRE_AT_BROWSER_CLOSE = True
- PREVENT_CONCURRENT_SESSIONS = True
- PASSWORD min_length = 14

MEDIUM SECURITY (Balanced):
- SESSION_COOKIE_AGE = 1800 (30 minutes)
- SESSION_INACTIVITY_TIMEOUT = 1800
- SESSION_EXPIRE_AT_BROWSER_CLOSE = False
- PREVENT_CONCURRENT_SESSIONS = False
- PASSWORD min_length = 12

STANDARD SECURITY:
- SESSION_COOKIE_AGE = 3600 (60 minutes)
- SESSION_INACTIVITY_TIMEOUT = 3600
- SESSION_EXPIRE_AT_BROWSER_CLOSE = False
- PREVENT_CONCURRENT_SESSIONS = False
- PASSWORD min_length = 10
"""
