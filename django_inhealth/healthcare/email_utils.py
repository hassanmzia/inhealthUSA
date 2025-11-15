"""
Email verification utilities
Handles sending verification emails and token generation
"""
import secrets
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone


def generate_verification_token():
    """Generate a secure random token for email verification"""
    return secrets.token_urlsafe(32)


def send_verification_email(user, user_profile, request):
    """
    Send email verification link to user

    Args:
        user: Django User object
        user_profile: UserProfile object
        request: HTTP request object for building absolute URL

    Returns:
        Boolean indicating if email was sent successfully
    """
    # Generate verification token
    token = generate_verification_token()
    user_profile.email_verification_token = token
    user_profile.email_verification_sent_at = timezone.now()
    user_profile.save()

    # Build verification URL
    verification_url = request.build_absolute_uri(
        f'/verify-email/{token}/'
    )

    # Prepare email context
    context = {
        'user': user,
        'verification_url': verification_url,
        'site_name': 'InHealth EHR',
    }

    # Render email templates
    html_message = render_to_string('healthcare/email/verification_email.html', context)
    plain_message = strip_tags(html_message)

    # Email subject
    subject = 'Verify Your Email - InHealth EHR'

    # Send email
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@inhealth.com',
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False


def send_welcome_email(user):
    """
    Send welcome email after successful verification

    Args:
        user: Django User object

    Returns:
        Boolean indicating if email was sent successfully
    """
    context = {
        'user': user,
        'site_name': 'InHealth EHR',
    }

    html_message = render_to_string('healthcare/email/welcome_email.html', context)
    plain_message = strip_tags(html_message)

    subject = 'Welcome to InHealth EHR!'

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@inhealth.com',
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False
