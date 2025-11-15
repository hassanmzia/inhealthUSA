# Session Security and Cookie Management Guide

## Overview

This guide covers the comprehensive session security and cookie management features implemented for the InHealth EHR application, designed to meet HIPAA compliance requirements and security best practices.

## Key Features Implemented

✅ **HTTPOnly Cookies** - Prevents JavaScript access to cookies (XSS protection)
✅ **Secure Cookies** - Cookies only transmitted over HTTPS
✅ **Short Session Expiration** - 30-minute session timeout (configurable)
✅ **Automatic Logout** - Auto-logout after inactivity period
✅ **Session Renewal** - Automatic session extension on user activity
✅ **SameSite Protection** - CSRF attack prevention
✅ **Concurrent Session Prevention** - Optional single-session enforcement
✅ **Activity Tracking** - Logs session events for auditing

---

## Session Security Settings

### Default Configuration

The application is configured with the following defaults:

| Setting | Value | Description |
|---------|-------|-------------|
| **Session Timeout** | 30 minutes | Maximum session duration |
| **Inactivity Timeout** | 30 minutes | Auto-logout after no activity |
| **Renewal Threshold** | 5 minutes | Renew session if activity within 5 min of expiry |
| **HTTPOnly** | True | Prevents XSS attacks |
| **Secure** | True (production) | HTTPS-only cookies |
| **SameSite** | Lax | CSRF protection |

### Configuration Files

Session security is configured in:
- **Main Settings**: `django_inhealth/inhealth/settings.py` (lines 261-310)
- **Middleware**: `django_inhealth/healthcare/middleware/session_security.py`
- **Reference Config**: `deployment_configs/session_security_settings.py`

---

## How It Works

### 1. Session Initialization

When a user logs in:
```python
# Session is created with:
- Unique session ID
- HTTPOnly flag (prevents JavaScript access)
- Secure flag (HTTPS only in production)
- SameSite=Lax (CSRF protection)
- Initial activity timestamp
```

### 2. Activity Tracking

Every request from authenticated user:
```python
# SessionSecurityMiddleware:
1. Checks last activity timestamp
2. Calculates time since last activity
3. If > 30 minutes → Auto-logout
4. If < 30 minutes → Update timestamp
5. If within 5 minutes of expiry → Renew session
```

### 3. Automatic Logout

If user is inactive for 30 minutes:
```python
1. Session is terminated
2. User is logged out
3. Message displayed: "Your session has expired"
4. Redirected to login page with 'next' parameter
```

### 4. Session Renewal

If user is active within 5 minutes of expiry:
```python
1. Session cookie is renewed
2. New session ID generated (security)
3. Activity timestamp updated
4. Session continues seamlessly
```

---

## Security Levels

Choose a security level based on your compliance requirements:

### High Security (HIPAA Compliance)
```python
# Environment variables or settings:
SESSION_COOKIE_AGE = 900  # 15 minutes
SESSION_INACTIVITY_TIMEOUT = 900
SESSION_RENEWAL_THRESHOLD = 180  # 3 minutes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
PREVENT_CONCURRENT_SESSIONS = True
```

**Use for**: Healthcare providers handling PHI, financial institutions

### Medium Security (Recommended)
```python
# Current default settings:
SESSION_COOKIE_AGE = 1800  # 30 minutes
SESSION_INACTIVITY_TIMEOUT = 1800
SESSION_RENEWAL_THRESHOLD = 300  # 5 minutes
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
PREVENT_CONCURRENT_SESSIONS = False
```

**Use for**: General healthcare applications, business applications

### Standard Security
```python
SESSION_COOKIE_AGE = 3600  # 60 minutes
SESSION_INACTIVITY_TIMEOUT = 3600
SESSION_RENEWAL_THRESHOLD = 600  # 10 minutes
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
PREVENT_CONCURRENT_SESSIONS = False
```

**Use for**: Internal applications, low-risk environments

---

## Environment Variable Configuration

You can customize session security without changing code:

```bash
# .env file or environment variables

# Session timeout (seconds)
export SESSION_COOKIE_AGE=1800  # 30 minutes
export SESSION_INACTIVITY_TIMEOUT=1800
export SESSION_RENEWAL_THRESHOLD=300

# Concurrent sessions (true/false)
export PREVENT_CONCURRENT_SESSIONS=False

# Browser close behavior (true/false)
export SESSION_EXPIRE_AT_BROWSER_CLOSE=False
```

Then restart your application:
```bash
sudo systemctl restart inhealth
```

---

## Middleware Components

### 1. SessionSecurityMiddleware

**Purpose**: Enforces session timeouts and automatic renewal

**Features**:
- Tracks last activity timestamp
- Auto-logout after inactivity
- Automatic session renewal
- Logs security events

**Configuration**:
```python
# settings.py
SESSION_INACTIVITY_TIMEOUT = 1800  # 30 minutes
SESSION_RENEWAL_THRESHOLD = 300    # 5 minutes

SESSION_TIMEOUT_EXCLUDED_PATHS = [
    '/auth/',
    '/login/',
    '/static/',
    '/media/',
]
```

### 2. ConcurrentSessionMiddleware

**Purpose**: Prevents multiple simultaneous logins

**Features**:
- Detects concurrent sessions
- Terminates old sessions
- Logs concurrent login attempts

**Enable**:
```python
# settings.py
PREVENT_CONCURRENT_SESSIONS = True
```

### 3. SecurityHeadersMiddleware

**Purpose**: Adds additional security headers

**Headers Added**:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`

---

## Cookie Security

### Session Cookie Settings

```python
SESSION_COOKIE_NAME = 'inhealth_sid'        # Custom name (security)
SESSION_COOKIE_SECURE = True                 # HTTPS only
SESSION_COOKIE_HTTPONLY = True               # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'             # CSRF protection
SESSION_COOKIE_AGE = 1800                    # 30 minutes
```

### CSRF Cookie Settings

```python
CSRF_COOKIE_NAME = 'inhealth_csrftoken'     # Custom name
CSRF_COOKIE_SECURE = True                    # HTTPS only
CSRF_COOKIE_HTTPONLY = True                  # No JavaScript access
CSRF_COOKIE_SAMESITE = 'Strict'             # Maximum CSRF protection
CSRF_COOKIE_AGE = 31449600                   # 1 year
```

### Cookie Attributes Explained

| Attribute | Value | Purpose |
|-----------|-------|---------|
| **HTTPOnly** | True | Prevents XSS attacks - JavaScript cannot access cookie |
| **Secure** | True | Cookie only sent over HTTPS connections |
| **SameSite=Lax** | Session | Prevents CSRF, allows navigation from external sites |
| **SameSite=Strict** | CSRF | Maximum CSRF protection, blocks all cross-site requests |

---

## Testing Session Security

### Test 1: Session Timeout

1. Log in to the application
2. Wait 30 minutes without any activity
3. Try to navigate to a protected page
4. **Expected**: Automatically logged out with message

```bash
# Test with shorter timeout for quick testing
export SESSION_INACTIVITY_TIMEOUT=60  # 1 minute
sudo systemctl restart inhealth
```

### Test 2: Session Renewal

1. Log in to the application
2. Perform activity every 2-3 minutes
3. Continue for 45 minutes
4. **Expected**: Session remains active (auto-renewed)

### Test 3: Cookie Security

Open browser DevTools → Application → Cookies:

**Verify**:
- ✓ Cookie name is `inhealth_sid` (not `sessionid`)
- ✓ HttpOnly flag is set
- ✓ Secure flag is set (production only)
- ✓ SameSite is `Lax`

### Test 4: Concurrent Sessions (if enabled)

1. Log in on Computer A
2. Log in on Computer B with same account
3. **Expected**: Computer A session is terminated

### Test 5: Excluded Paths

1. Visit `/login/` page
2. Wait > 30 minutes
3. Submit login form
4. **Expected**: Login works (timeout doesn't apply to excluded paths)

---

## Monitoring and Logging

### View Session Security Logs

```bash
# Application logs
sudo tail -f /var/log/inhealth/error.log | grep -i session

# Filter for timeout events
sudo grep "Session expired" /var/log/inhealth/error.log

# Filter for renewal events
sudo grep "Session renewed" /var/log/inhealth/error.log

# Filter for concurrent sessions
sudo grep "Concurrent session" /var/log/inhealth/error.log
```

### Important Log Events

| Event | Message | Severity |
|-------|---------|----------|
| Session Timeout | "Session expired for user X after Y seconds" | WARNING |
| Auto-logout | "Auto-logout user X due to session timeout" | INFO |
| Session Renewal | "Session renewed for user X" | DEBUG |
| Concurrent Session | "Concurrent session detected for user X" | WARNING |

---

## Troubleshooting

### Issue: Users Being Logged Out Too Quickly

**Cause**: Session timeout too short

**Solution**:
```bash
# Increase timeout to 60 minutes
export SESSION_COOKIE_AGE=3600
export SESSION_INACTIVITY_TIMEOUT=3600
sudo systemctl restart inhealth
```

### Issue: Session Not Expiring

**Cause**: Middleware not configured

**Solution**:
```python
# Verify in settings.py MIDDLEWARE:
'healthcare.middleware.session_security.SessionSecurityMiddleware',
```

### Issue: Session Timeout on Login Page

**Cause**: Login path not excluded

**Solution**:
```python
# Add to SESSION_TIMEOUT_EXCLUDED_PATHS:
SESSION_TIMEOUT_EXCLUDED_PATHS = [
    '/login/',
    '/auth/',
    # ... other paths
]
```

### Issue: Concurrent Session Detection Not Working

**Cause**: Feature not enabled

**Solution**:
```python
# Enable in settings.py:
PREVENT_CONCURRENT_SESSIONS = True
```

### Issue: Cookie Not Secure in Development

**Cause**: Expected behavior (HTTPS not used in development)

**Solution**: This is normal. Cookies are only secure in production (DEBUG=False)

---

## HIPAA Compliance

### Required Settings for HIPAA

```python
# Mandatory for HIPAA compliance:
SESSION_COOKIE_SECURE = True           # HTTPS only
SESSION_COOKIE_HTTPONLY = True         # XSS protection
SESSION_COOKIE_AGE = 1800              # ≤ 30 minutes
SESSION_INACTIVITY_TIMEOUT = 1800      # Auto-logout
SESSION_SAVE_EVERY_REQUEST = True      # Track activity
SECURE_SSL_REDIRECT = True             # Force HTTPS
SECURE_HSTS_SECONDS = 31536000         # HSTS enabled
```

### HIPAA Requirements Met

✅ **Automatic Logoff**: Users auto-logged out after 30 minutes inactivity
✅ **Session Timeout**: Maximum session duration enforced
✅ **Audit Logging**: Session events logged for compliance
✅ **Encryption in Transit**: HTTPS-only cookies
✅ **Access Control**: HTTPOnly prevents XSS attacks

### Compliance Documentation

For HIPAA audits, document:
1. Session timeout policy (30 minutes)
2. Auto-logout implementation
3. Session activity logging
4. Cookie security settings
5. Regular security testing

---

## Best Practices

### 1. Production Deployment

✅ **Always use HTTPS** - Secure cookies require HTTPS
✅ **Test before deploying** - Verify session timeout works
✅ **Monitor logs** - Watch for security events
✅ **Regular audits** - Review session settings quarterly

### 2. User Communication

✅ **Notify users** of session timeout policy
✅ **Display countdown** timer (optional enhancement)
✅ **Clear error messages** on timeout
✅ **"Remember me" option** for trusted devices (optional)

### 3. Development

✅ **Use longer timeouts** in development for convenience
✅ **Test with short timeouts** before deployment
✅ **Document changes** to session settings

### 4. Security

✅ **Never disable HTTPOnly** - Critical for XSS protection
✅ **Never disable Secure** in production - HTTPS required
✅ **Review logs regularly** - Detect unusual activity
✅ **Update dependencies** - Security patches

---

## Advanced Configuration

### Custom Timeout Messages

Edit `healthcare/middleware/session_security.py`:

```python
def _handle_expired_session(self, request):
    messages.warning(
        request,
        'Your session expired after 30 minutes of inactivity. '
        'This is required for security. Please log in again.'
    )
```

### Per-Role Timeouts

Add to middleware:

```python
def __init__(self, get_response):
    # Different timeouts for different roles
    self.role_timeouts = {
        'admin': 1800,      # 30 minutes
        'doctor': 3600,     # 60 minutes
        'patient': 1800,    # 30 minutes
    }
```

### Activity Extension API

Add endpoint for JavaScript to ping:

```python
# views.py
@require_http_methods(["POST"])
def extend_session(request):
    """Extend session on user activity"""
    if request.user.is_authenticated:
        request.session['last_activity'] = timezone.now().isoformat()
        return JsonResponse({'status': 'extended'})
    return JsonResponse({'status': 'error'}, status=401)
```

### Session Timeout Warning

Add JavaScript countdown timer (optional):

```javascript
// Warn user 5 minutes before timeout
let warningTime = 25 * 60 * 1000; // 25 minutes
setTimeout(() => {
    alert('Your session will expire in 5 minutes due to inactivity.');
}, warningTime);
```

---

## Security Checklist

Before going live, verify:

- [ ] SESSION_COOKIE_SECURE = True (production)
- [ ] SESSION_COOKIE_HTTPONLY = True
- [ ] SESSION_COOKIE_AGE ≤ 1800 (30 min)
- [ ] SESSION_INACTIVITY_TIMEOUT = 1800
- [ ] CSRF_COOKIE_SECURE = True (production)
- [ ] CSRF_COOKIE_HTTPONLY = True
- [ ] CSRF_COOKIE_SAMESITE = 'Strict'
- [ ] Middleware configured correctly
- [ ] HTTPS enabled (production)
- [ ] Session timeout tested
- [ ] Session renewal tested
- [ ] Logging configured
- [ ] Excluded paths configured
- [ ] Documentation updated

---

## Support and Resources

### Documentation
- Django Sessions: https://docs.djangoproject.com/en/stable/topics/http/sessions/
- Django Security: https://docs.djangoproject.com/en/stable/topics/security/
- OWASP Session Management: https://owasp.org/www-project-web-security-testing-guide/

### Testing Tools
- Browser DevTools (inspect cookies)
- OWASP ZAP (security testing)
- Burp Suite (penetration testing)

### Compliance
- HIPAA Security Rule: https://www.hhs.gov/hipaa/for-professionals/security/
- NIST Guidelines: https://csrc.nist.gov/publications

---

## Quick Reference

### Environment Variables

```bash
# Session timeout (30 minutes)
SESSION_COOKIE_AGE=1800
SESSION_INACTIVITY_TIMEOUT=1800

# Session renewal (5 minutes)
SESSION_RENEWAL_THRESHOLD=300

# Concurrent sessions (disabled)
PREVENT_CONCURRENT_SESSIONS=False

# Browser close (disabled)
SESSION_EXPIRE_AT_BROWSER_CLOSE=False
```

### Common Commands

```bash
# Restart application
sudo systemctl restart inhealth

# View session logs
sudo tail -f /var/log/inhealth/error.log

# Check active sessions (Django shell)
python manage.py shell
>>> from django.contrib.sessions.models import Session
>>> Session.objects.count()

# Clear expired sessions
python manage.py clearsessions
```

### Security Test Commands

```bash
# Test session timeout (1 minute for testing)
export SESSION_INACTIVITY_TIMEOUT=60
sudo systemctl restart inhealth

# Check cookie security
curl -I https://yourdomain.com/login/

# Django security check
python manage.py check --deploy
```

---

**Need Help?** Check the detailed configuration in:
- `django_inhealth/inhealth/settings.py`
- `deployment_configs/session_security_settings.py`
- `django_inhealth/healthcare/middleware/session_security.py`
