# Django HTTPS/SSL Settings
# Add these settings to your django_inhealth/inhealth/settings.py file

# ============================================================================
# HTTPS/SSL CONFIGURATION
# ============================================================================

# Determine if we're in production based on DEBUG setting
# You can also use environment variable: PRODUCTION = os.getenv('PRODUCTION', 'False') == 'True'

if not DEBUG:
    # Force HTTPS for all requests
    SECURE_SSL_REDIRECT = True

    # Use secure cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HTTP Strict Transport Security (HSTS)
    # Tells browsers to only connect via HTTPS
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Prevent browsers from guessing content type
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # Enable browser's XSS filtering
    SECURE_BROWSER_XSS_FILTER = True

    # Prevent clickjacking attacks
    X_FRAME_OPTIONS = 'DENY'  # or 'SAMEORIGIN' if you need iframes

    # Trust X-Forwarded-Proto header from Nginx/proxy
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

else:
    # Development settings - Allow HTTP
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# ============================================================================
# ALLOWED HOSTS - Update with your actual domains
# ============================================================================

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '172.168.1.125',  # Your current local IP
    'yourdomain.com',  # CHANGE THIS to your actual domain
    'www.yourdomain.com',  # CHANGE THIS to your actual domain
]

# ============================================================================
# CORS SETTINGS (if using django-cors-headers)
# ============================================================================

# If you're building a separate frontend (React, Vue, etc.)
# pip install django-cors-headers

# INSTALLED_APPS = [
#     ...
#     'corsheaders',
# ]

# MIDDLEWARE = [
#     'corsheaders.middleware.CorsMiddleware',  # Add this near the top
#     ...
# ]

# Production CORS settings
# if not DEBUG:
#     CORS_ALLOWED_ORIGINS = [
#         "https://yourdomain.com",
#         "https://www.yourdomain.com",
#     ]
# else:
#     # Development - Allow all origins
#     CORS_ALLOW_ALL_ORIGINS = True

# ============================================================================
# STATIC AND MEDIA FILES FOR PRODUCTION
# ============================================================================

import os

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Additional directories for static files
STATICFILES_DIRS = [
    # Add any additional static directories here
]

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ============================================================================
# LOGGING CONFIGURATION
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
            'format': '{levelname} {message}',
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
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'healthcare': {  # Your app name
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# ============================================================================
# DATABASE CONNECTION POOLING (Optional but recommended)
# ============================================================================

# If using PostgreSQL, consider using connection pooling
# pip install psycopg2-binary

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'your_db_name',
#         'USER': 'your_db_user',
#         'PASSWORD': 'your_db_password',
#         'HOST': 'localhost',
#         'PORT': '5432',
#         'CONN_MAX_AGE': 600,  # Connection pooling
#         'OPTIONS': {
#             'connect_timeout': 10,
#         }
#     }
# }

# ============================================================================
# CACHING (Recommended for production)
# ============================================================================

# Using Redis for caching (pip install django-redis)
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         },
#         'KEY_PREFIX': 'inhealth',
#         'TIMEOUT': 300,
#     }
# }

# Or using file-based caching (simpler, no extra dependencies)
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
#         'LOCATION': os.path.join(BASE_DIR, 'cache'),
#     }
# }

# ============================================================================
# SESSION CONFIGURATION
# ============================================================================

# Session cookie age (2 weeks)
SESSION_COOKIE_AGE = 1209600

# Session cookie name
SESSION_COOKIE_NAME = 'inhealth_sessionid'

# Close session on browser close
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Use database-backed sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Or use cached sessions for better performance
# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
# SESSION_CACHE_ALIAS = 'default'

# ============================================================================
# EMAIL CONFIGURATION (for password reset, notifications, etc.)
# ============================================================================

# For Gmail (not recommended for production)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password'
# DEFAULT_FROM_EMAIL = 'InHealth EHR <your-email@gmail.com>'

# For production, use a service like SendGrid, Mailgun, or AWS SES
# Example with SendGrid:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.sendgrid.net'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'apikey'
# EMAIL_HOST_PASSWORD = os.getenv('SENDGRID_API_KEY')
# DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'

# ============================================================================
# ADMIN CONFIGURATION
# ============================================================================

# Admins will receive error emails
ADMINS = [
    ('Admin Name', 'admin@yourdomain.com'),
]

MANAGERS = ADMINS

# ============================================================================
# FILE UPLOAD CONFIGURATION
# ============================================================================

# Maximum upload size (100 MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100 MB

# Allowed file upload extensions (for security)
ALLOWED_UPLOAD_EXTENSIONS = [
    '.jpg', '.jpeg', '.png', '.gif', '.pdf',
    '.doc', '.docx', '.xls', '.xlsx'
]

# ============================================================================
# SECURITY CHECKLIST
# ============================================================================

# Run this command to check security settings:
# python manage.py check --deploy

# Additional security settings to consider:
# - SECURE_REFERRER_POLICY = 'same-origin'
# - CSRF_COOKIE_HTTPONLY = True
# - CSRF_COOKIE_SAMESITE = 'Strict'
# - SESSION_COOKIE_SAMESITE = 'Strict'
# - SESSION_COOKIE_HTTPONLY = True
