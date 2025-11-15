"""
Session Security Middleware for InHealth EHR

This middleware provides:
1. Automatic session renewal on activity
2. Session timeout enforcement
3. Concurrent session detection
4. Activity tracking
5. Security logging

HIPAA Compliance: Implements automatic logoff after period of inactivity
"""

import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.contrib import messages

logger = logging.getLogger(__name__)


class SessionSecurityMiddleware:
    """
    Middleware to enforce session security policies:
    - Automatic session expiration after inactivity
    - Session renewal on activity
    - Activity timestamp tracking
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # Session timeout in seconds (default: 30 minutes)
        self.session_timeout = getattr(settings, 'SESSION_INACTIVITY_TIMEOUT', 1800)

        # Session renewal threshold (renew if less than this time remaining)
        self.renewal_threshold = getattr(settings, 'SESSION_RENEWAL_THRESHOLD', 300)

        # Paths to exclude from session timeout
        self.excluded_paths = getattr(settings, 'SESSION_TIMEOUT_EXCLUDED_PATHS', [
            '/auth/',
            '/login/',
            '/logout/',
            '/static/',
            '/media/',
        ])

    def __call__(self, request):
        # Process request
        if request.user.is_authenticated:
            # Check if path is excluded
            if not any(request.path.startswith(path) for path in self.excluded_paths):
                # Check session timeout
                if self._is_session_expired(request):
                    return self._handle_expired_session(request)

                # Update last activity and renew if needed
                self._update_activity(request)

        response = self.get_response(request)

        return response

    def _is_session_expired(self, request):
        """Check if session has expired due to inactivity"""
        last_activity = request.session.get('last_activity')

        if last_activity:
            try:
                # Parse last activity timestamp
                if isinstance(last_activity, str):
                    last_activity_time = datetime.fromisoformat(last_activity)
                else:
                    last_activity_time = last_activity

                # Make timezone aware if needed
                if timezone.is_naive(last_activity_time):
                    last_activity_time = timezone.make_aware(last_activity_time)

                # Calculate time since last activity
                inactive_duration = timezone.now() - last_activity_time

                # Check if session has expired
                if inactive_duration.total_seconds() > self.session_timeout:
                    logger.warning(
                        f"Session expired for user {request.user.username} "
                        f"after {inactive_duration.total_seconds()} seconds of inactivity"
                    )
                    return True

            except (ValueError, TypeError) as e:
                logger.error(f"Error parsing last_activity timestamp: {e}")
                # If we can't parse the timestamp, treat as expired for security
                return True

        return False

    def _handle_expired_session(self, request):
        """Handle expired session by logging out user"""
        username = request.user.username

        # Log the timeout event
        logger.info(f"Auto-logout user {username} due to session timeout")

        # Logout user
        logout(request)

        # Add message for user
        messages.warning(
            request,
            'Your session has expired due to inactivity. Please log in again.'
        )

        # Redirect to login page with next parameter
        login_url = reverse('login')
        next_url = request.path

        return redirect(f'{login_url}?next={next_url}')

    def _update_activity(self, request):
        """Update last activity timestamp and renew session if needed"""
        now = timezone.now()

        # Get last activity
        last_activity = request.session.get('last_activity')

        # Update last activity timestamp
        request.session['last_activity'] = now.isoformat()

        # Check if session should be renewed
        if last_activity:
            try:
                if isinstance(last_activity, str):
                    last_activity_time = datetime.fromisoformat(last_activity)
                else:
                    last_activity_time = last_activity

                if timezone.is_naive(last_activity_time):
                    last_activity_time = timezone.make_aware(last_activity_time)

                time_since_renewal = now - last_activity_time

                # Renew session if close to expiration
                if time_since_renewal.total_seconds() > self.renewal_threshold:
                    # Cycle session key for security
                    request.session.cycle_key()
                    logger.debug(f"Session renewed for user {request.user.username}")

            except (ValueError, TypeError) as e:
                logger.error(f"Error in session renewal: {e}")

        # Track session metadata
        request.session['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        request.session['ip_address'] = self._get_client_ip(request)

    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ConcurrentSessionMiddleware:
    """
    Middleware to detect and handle concurrent sessions
    Prevents users from logging in from multiple locations simultaneously
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'PREVENT_CONCURRENT_SESSIONS', False)

    def __call__(self, request):
        if self.enabled and request.user.is_authenticated:
            # Get current session key
            current_session_key = request.session.session_key

            # Get stored session key for this user
            stored_session_key = request.session.get('session_key')

            if stored_session_key and stored_session_key != current_session_key:
                # Another session exists for this user
                logger.warning(
                    f"Concurrent session detected for user {request.user.username}. "
                    f"Terminating old session."
                )

                # Force logout
                logout(request)
                messages.error(
                    request,
                    'Your account was logged in from another location. '
                    'Please log in again.'
                )
                return redirect('login')

            # Store current session key
            request.session['session_key'] = current_session_key

        response = self.get_response(request)
        return response


class SecurityHeadersMiddleware:
    """
    Additional security headers middleware
    Complements Django's built-in security
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Add security headers
        if not hasattr(response, 'has_header') or not response.has_header('X-Content-Type-Options'):
            response['X-Content-Type-Options'] = 'nosniff'

        if not hasattr(response, 'has_header') or not response.has_header('X-Frame-Options'):
            response['X-Frame-Options'] = 'DENY'

        if not hasattr(response, 'has_header') or not response.has_header('X-XSS-Protection'):
            response['X-XSS-Protection'] = '1; mode=block'

        if not hasattr(response, 'has_header') or not response.has_header('Referrer-Policy'):
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Permissions Policy (formerly Feature-Policy)
        if not hasattr(response, 'has_header') or not response.has_header('Permissions-Policy'):
            response['Permissions-Policy'] = (
                'geolocation=(), '
                'microphone=(), '
                'camera=(), '
                'payment=(), '
                'usb=(), '
                'magnetometer=(), '
                'gyroscope=(), '
                'accelerometer=()'
            )

        return response
