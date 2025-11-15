"""
CAC (Common Access Card) / PKI Authentication Middleware
Automatically authenticates users with valid client certificates
"""

from django.conf import settings
from django.contrib.auth import login
from django.utils.deprecation import MiddlewareMixin
from healthcare.auth_backends import CACAuthBackend
import logging

logger = logging.getLogger(__name__)


class CACAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to automatically authenticate users via CAC/PKI certificates
    Should be placed after AuthenticationMiddleware in MIDDLEWARE setting
    """

    def process_request(self, request):
        """
        Check for CAC certificate and authenticate if present
        """
        # Skip if CAC is not enabled
        if not getattr(settings, 'CAC_ENABLED', False):
            return None

        # Skip if user is already authenticated
        if request.user.is_authenticated:
            return None

        # Skip if no certificate present
        client_cert = request.META.get(settings.CAC_CLIENT_CERT_HEADER)
        client_dn = request.META.get(settings.CAC_CLIENT_DN_HEADER)

        if not client_cert and not client_dn:
            # No certificate - check if cert is required for this path
            if self._is_cert_required(request):
                logger.warning(f'CAC required but not present for: {request.path}')
                # Could redirect to cert required page
                # return HttpResponseForbidden('CAC certificate required')
            return None

        # Attempt CAC authentication
        backend = CACAuthBackend()
        user = backend.authenticate(request)

        if user:
            # Store provider in session
            request.session['auth_provider'] = 'cac'

            # Log user in
            login(request, user, backend='healthcare.auth_backends.CACAuthBackend')

            logger.info(f'User authenticated via CAC: {user.email}')
        else:
            logger.warning('CAC certificate present but authentication failed')

        return None

    def _is_cert_required(self, request):
        """
        Check if CAC certificate is required for this request path
        """
        # Check global setting
        if getattr(settings, 'CAC_REQUIRE_CERT_FOR_LOGIN', False):
            return True

        # Could add path-specific requirements here
        # E.g., require CAC for admin paths
        # if request.path.startswith('/admin/'):
        #     return True

        return False
