"""
Custom Authentication Backends for Enterprise SSO
Includes OIDC, SAML, and CAC/PKI authentication
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.conf import settings
from django.core.exceptions import PermissionDenied
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
import logging
import hashlib
import re

User = get_user_model()
logger = logging.getLogger(__name__)


def generate_username_from_email(email):
    """
    Generate a unique username from email address
    Used by OIDC authentication
    """
    if not email:
        return None

    # Use email prefix as base username
    username = email.split('@')[0]

    # Clean username (remove special chars)
    username = re.sub(r'[^a-zA-Z0-9_]', '_', username)

    # Ensure uniqueness
    if User.objects.filter(username=username).exists():
        # Append hash of email
        hash_suffix = hashlib.md5(email.encode()).hexdigest()[:8]
        username = f'{username}_{hash_suffix}'

    return username


class CustomOIDCBackend(OIDCAuthenticationBackend):
    """
    Custom OIDC backend supporting multiple providers
    (Azure AD, Okta, AWS Cognito)
    """

    def filter_users_by_claims(self, claims):
        """
        Return users matching the email claim
        """
        email = claims.get('email')
        if not email:
            return User.objects.none()

        return User.objects.filter(email__iexact=email)

    def create_user(self, claims):
        """
        Create user from OIDC claims
        """
        email = claims.get('email')
        if not email:
            logger.error('OIDC claims missing email')
            return None

        # Generate username
        username = generate_username_from_email(email)

        # Extract user information from claims
        first_name = claims.get('given_name', claims.get('givenName', ''))
        last_name = claims.get('family_name', claims.get('surname', ''))

        # Create user
        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
        )

        logger.info(f'Created new user from OIDC: {email}')
        return user

    def update_user(self, user, claims):
        """
        Update existing user with latest claims
        """
        user.first_name = claims.get('given_name', claims.get('givenName', user.first_name))
        user.last_name = claims.get('family_name', claims.get('surname', user.last_name))

        # Update email if changed
        new_email = claims.get('email')
        if new_email and new_email != user.email:
            user.email = new_email

        user.save()
        logger.info(f'Updated user from OIDC claims: {user.email}')
        return user

    def verify_claims(self, claims):
        """
        Verify OIDC claims before authentication
        """
        # Verify email exists
        if not claims.get('email'):
            logger.warning('OIDC claims missing email')
            return False

        # Verify email is verified (if claim exists)
        email_verified = claims.get('email_verified', True)
        if not email_verified:
            logger.warning(f'OIDC email not verified: {claims.get("email")}')
            return False

        # Add custom verification logic here
        # E.g., check if email domain is allowed

        return True


class SAMLAuthBackend(BaseBackend):
    """
    SAML 2.0 Authentication Backend
    Handles authentication via SAML IdP
    """

    def authenticate(self, request, saml_attributes=None, **kwargs):
        """
        Authenticate user via SAML attributes
        """
        if not saml_attributes:
            return None

        # Extract email from SAML attributes
        email = self._extract_attribute(
            saml_attributes,
            settings.SAML_ATTRIBUTE_MAPPING.get('email', ['email'])
        )

        if not email:
            logger.error('SAML attributes missing email')
            return None

        # Extract user attributes
        first_name = self._extract_attribute(
            saml_attributes,
            settings.SAML_ATTRIBUTE_MAPPING.get('first_name', ['givenName'])
        )
        last_name = self._extract_attribute(
            saml_attributes,
            settings.SAML_ATTRIBUTE_MAPPING.get('last_name', ['surname'])
        )

        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': generate_username_from_email(email),
                'first_name': first_name or '',
                'last_name': last_name or '',
                'is_active': True,
            }
        )

        if not created:
            # Update existing user
            user.first_name = first_name or user.first_name
            user.last_name = last_name or user.last_name
            user.save()
            logger.info(f'Updated user from SAML: {email}')
        else:
            logger.info(f'Created new user from SAML: {email}')

        return user

    def _extract_attribute(self, saml_attributes, attribute_names):
        """
        Extract attribute from SAML response
        Try multiple attribute name variations
        """
        if isinstance(attribute_names, str):
            attribute_names = [attribute_names]

        for attr_name in attribute_names:
            value = saml_attributes.get(attr_name)
            if value:
                # SAML attributes are often lists
                if isinstance(value, list):
                    return value[0] if value else None
                return value

        return None

    def get_user(self, user_id):
        """
        Retrieve user by ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class CACAuthBackend(BaseBackend):
    """
    CAC (Common Access Card) / PKI Certificate Authentication Backend
    Authenticates users based on client SSL certificates
    """

    def authenticate(self, request, **kwargs):
        """
        Authenticate using CAC/PKI certificate
        """
        if not getattr(settings, 'CAC_ENABLED', False):
            return None

        # Extract certificate from request headers
        client_cert = request.META.get(settings.CAC_CLIENT_CERT_HEADER)
        client_dn = request.META.get(settings.CAC_CLIENT_DN_HEADER)

        if not client_cert and not client_dn:
            logger.debug('No CAC certificate found in request')
            return None

        # Extract email from certificate DN
        email = self._extract_email_from_dn(client_dn)

        if not email:
            logger.warning(f'Could not extract email from CAC DN: {client_dn}')
            return None

        # Validate certificate (implement your validation logic)
        if not self._validate_certificate(client_cert, client_dn):
            logger.warning(f'CAC certificate validation failed for: {email}')
            return None

        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': generate_username_from_email(email),
                'is_active': True,
            }
        )

        if created:
            logger.info(f'Created new user from CAC: {email}')
        else:
            logger.info(f'Authenticated user via CAC: {email}')

        return user

    def _extract_email_from_dn(self, dn):
        """
        Extract email from certificate Distinguished Name
        Example DN: CN=DOE.JOHN.1234567890,OU=PKI,OU=DoD,O=U.S. Government,C=US
        """
        if not dn:
            return None

        # Try to find email in DN
        email_match = re.search(r'emailAddress=([^,]+)', dn, re.IGNORECASE)
        if email_match:
            return email_match.group(1).strip()

        # Extract from CN and construct email
        cn_match = re.search(r'CN=([^,]+)', dn, re.IGNORECASE)
        if cn_match:
            cn = cn_match.group(1).strip()
            # Convert "DOE.JOHN.1234567890" to email format
            # This is highly specific to your CAC format
            parts = cn.split('.')
            if len(parts) >= 2:
                # Construct email (customize this based on your org)
                return f'{parts[1].lower()}.{parts[0].lower()}@mil'

        return None

    def _validate_certificate(self, cert_pem, dn):
        """
        Validate CAC certificate
        Implement certificate validation logic here
        """
        # Basic validation - certificate exists
        if not cert_pem and not dn:
            return False

        # TODO: Implement full certificate validation:
        # 1. Verify certificate chain against DoD CA bundle
        # 2. Check certificate expiration
        # 3. Verify certificate revocation status (CRL/OCSP)
        # 4. Validate certificate attributes

        # For now, accept any certificate if CAC is enabled
        # SECURITY WARNING: Implement proper validation in production!
        return True

    def get_user(self, user_id):
        """
        Retrieve user by ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class MultiProviderAuthBackend(BaseBackend):
    """
    Meta backend that routes authentication to appropriate provider
    Based on request context
    """

    def authenticate(self, request, **kwargs):
        """
        Route to appropriate authentication backend
        """
        # Determine provider from request
        provider = request.session.get('auth_provider')

        if provider == 'saml':
            backend = SAMLAuthBackend()
            return backend.authenticate(request, **kwargs)

        elif provider == 'cac':
            backend = CACAuthBackend()
            return backend.authenticate(request, **kwargs)

        # Default to None (let other backends handle)
        return None

    def get_user(self, user_id):
        """
        Retrieve user by ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
