"""
Enterprise Authentication Adapters for django-allauth
Handles custom logic for account creation and social authentication
"""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class EnterpriseAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter for enterprise authentication
    Handles account creation, email verification, and security policies
    """

    def is_open_for_signup(self, request):
        """
        Allow signups - can be restricted based on enterprise policies
        """
        # Check if self-registration is allowed
        allow_self_registration = getattr(
            settings, 'ALLOW_SELF_REGISTRATION', True
        )
        return allow_self_registration

    def save_user(self, request, user, form, commit=True):
        """
        Save user with additional enterprise policies
        """
        user = super().save_user(request, user, form, commit=False)

        # Set default user properties for enterprise users
        user.is_active = True  # Can be changed to False if email verification required

        # Check for email domain restrictions
        allowed_domains = getattr(settings, 'ALLOWED_EMAIL_DOMAINS', None)
        if allowed_domains:
            email_domain = user.email.split('@')[1].lower()
            if email_domain not in allowed_domains:
                raise ValidationError(
                    f'Registration is only allowed for email domains: {", ".join(allowed_domains)}'
                )

        if commit:
            user.save()

        logger.info(f'New user registered via enterprise auth: {user.email}')
        return user

    def get_login_redirect_url(self, request):
        """
        Redirect after successful login
        Can be customized based on user role
        """
        user = request.user

        # Check if MFA is required
        if getattr(settings, 'MFA_ENABLED', False):
            if not hasattr(user, 'mfa_enabled') or not user.mfa_enabled:
                # Check if MFA is required for this user
                if user.is_staff and getattr(settings, 'MFA_REQUIRED_FOR_STAFF', False):
                    return '/mfa/setup/'
                if user.is_superuser and getattr(settings, 'MFA_REQUIRED_FOR_SUPERUSER', False):
                    return '/mfa/setup/'

        # Default redirect
        return super().get_login_redirect_url(request)


class EnterpriseSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom social account adapter for enterprise SSO
    Handles user creation from OIDC, SAML, OAuth providers
    """

    def is_open_for_signup(self, request, sociallogin):
        """
        Allow social signups based on enterprise policy
        """
        # Allow signup from trusted enterprise providers
        return True

    def pre_social_login(self, request, sociallogin):
        """
        Perform actions before social login
        Link existing accounts if email matches
        """
        if sociallogin.is_existing:
            return

        # Try to link to existing user by email
        try:
            email = sociallogin.account.extra_data.get('email')
            if email:
                user = User.objects.get(email=email)
                sociallogin.connect(request, user)
                logger.info(f'Linked social account to existing user: {email}')
        except User.DoesNotExist:
            pass
        except User.MultipleObjectsReturned:
            # Multiple users with same email - manual intervention required
            logger.warning(f'Multiple users found with email: {email}')

    def populate_user(self, request, sociallogin, data):
        """
        Populate user model with data from social provider
        """
        user = super().populate_user(request, sociallogin, data)

        # Extract additional data from provider
        extra_data = sociallogin.account.extra_data

        # Azure AD / Microsoft specific attributes
        if sociallogin.account.provider == 'microsoft':
            user.first_name = extra_data.get('givenName', '')
            user.last_name = extra_data.get('surname', '')
            # Can extract department, job title, etc.

        # Okta specific attributes
        elif 'okta' in sociallogin.account.provider:
            user.first_name = extra_data.get('given_name', '')
            user.last_name = extra_data.get('family_name', '')

        # AWS Cognito specific attributes
        elif 'cognito' in sociallogin.account.provider:
            user.first_name = extra_data.get('given_name', '')
            user.last_name = extra_data.get('family_name', '')

        logger.info(f'Populated user from {sociallogin.account.provider}: {user.email}')
        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Save user with enterprise policies
        """
        user = super().save_user(request, sociallogin, form)

        # Automatically activate users from trusted enterprise providers
        trusted_providers = getattr(
            settings,
            'TRUSTED_SSO_PROVIDERS',
            ['microsoft', 'azuread', 'okta', 'cognito', 'saml']
        )

        if sociallogin.account.provider in trusted_providers:
            user.is_active = True
            user.email_verified = True
            user.save()

            logger.info(
                f'Auto-activated user from trusted provider '
                f'{sociallogin.account.provider}: {user.email}'
            )

        return user
