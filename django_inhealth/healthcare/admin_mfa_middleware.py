"""
Multi-Factor Authentication Middleware for Django Admin
Requires MFA verification for admin and staff users accessing Django admin
"""
import pyotp
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin


class AdminMFAMiddleware(MiddlewareMixin):
    """
    Middleware to enforce MFA for Django admin users
    """
    def process_request(self, request):
        # Skip MFA check for non-authenticated users
        if not request.user.is_authenticated:
            return None

        # Skip MFA check for non-staff/non-superusers
        if not (request.user.is_staff or request.user.is_superuser):
            return None

        # Skip MFA check if not accessing admin
        if not request.path.startswith('/admin/'):
            return None

        # Allow access to MFA setup and logout URLs
        allowed_paths = [
            '/admin/login/',
            '/admin/logout/',
            '/admin/jsi18n/',
            '/mfa/setup/',
            '/mfa/verify/',
        ]

        if any(request.path.startswith(path) for path in allowed_paths):
            return None

        # Check if user has MFA enabled
        try:
            profile = request.user.profile
            if not profile.mfa_enabled:
                # Redirect to MFA setup
                messages.warning(
                    request,
                    'Multi-Factor Authentication is required for admin access. '
                    'Please set up MFA to continue.'
                )
                return redirect('mfa_setup')
        except:
            # User doesn't have a profile
            pass

        # Check if MFA has been verified in this session
        if not request.session.get('mfa_verified', False):
            # Store the intended URL
            request.session['mfa_redirect_url'] = request.path
            messages.info(request, 'Please verify your identity with MFA code.')
            return redirect('mfa_verify')

        return None
