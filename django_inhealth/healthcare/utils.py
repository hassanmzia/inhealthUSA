"""
Utility functions for the healthcare app
"""
import os
from django.conf import settings
from django.core.mail import EmailMessage


def send_email_notification(to_email, subject, message_body, from_email=None, cc_email=None):
    """
    Send email notification using Django's email backend with CC support

    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        message_body (str): Email body content
        from_email (str, optional): Sender email address
        cc_email (str or list, optional): CC email address(es)

    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate email address
    if not to_email:
        return (False, 'Invalid recipient email address')

    # Get from_email from settings if not provided
    if not from_email:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@inhealthehr.com')

    # Prepare CC list
    cc_list = []
    if cc_email:
        if isinstance(cc_email, str):
            cc_list = [cc_email.strip()] if cc_email.strip() else []
        elif isinstance(cc_email, list):
            cc_list = [email.strip() for email in cc_email if email.strip()]

    try:
        # Create email message with CC support
        email = EmailMessage(
            subject=subject,
            body=message_body,
            from_email=from_email,
            to=[to_email],
            cc=cc_list if cc_list else None,
        )

        # Send the email
        email.send(fail_silently=False)

        # Build success message
        recipients = [to_email]
        if cc_list:
            recipients.extend(cc_list)
        recipients_str = ', '.join(recipients)

        return (True, f'Email sent successfully to {recipients_str}')

    except Exception as e:
        error_msg = str(e)
        # Provide helpful error messages
        if 'Connection refused' in error_msg:
            return (False, 'Email server connection failed. Please check EMAIL_HOST and EMAIL_PORT settings.')
        elif 'authentication' in error_msg.lower():
            return (False, 'Email authentication failed. Please check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD.')
        else:
            return (False, f'Failed to send email: {error_msg}')


def send_sms(to_phone, message_body):
    """
    Send SMS using Twilio

    Args:
        to_phone (str): Recipient phone number in E.164 format (e.g., +1234567890)
        message_body (str): Message content

    Returns:
        tuple: (success: bool, message: str)
    """
    # Check if Twilio credentials are configured
    twilio_account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', os.environ.get('TWILIO_ACCOUNT_SID'))
    twilio_auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', os.environ.get('TWILIO_AUTH_TOKEN'))
    twilio_phone_number = getattr(settings, 'TWILIO_PHONE_NUMBER', os.environ.get('TWILIO_PHONE_NUMBER'))

    # If Twilio is not configured, return a helpful message
    if not all([twilio_account_sid, twilio_auth_token, twilio_phone_number]):
        return (False, 'SMS service not configured. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in settings or environment variables.')

    # Validate phone number format
    if not to_phone:
        return (False, 'Invalid recipient phone number')

    # Ensure phone number is in E.164 format
    if not to_phone.startswith('+'):
        # Assume US number if no country code
        to_phone = f'+1{to_phone.replace("-", "").replace("(", "").replace(")", "").replace(" ", "")}'

    try:
        from twilio.rest import Client

        # Create Twilio client
        client = Client(twilio_account_sid, twilio_auth_token)

        # Send message
        message = client.messages.create(
            body=message_body,
            from_=twilio_phone_number,
            to=to_phone
        )

        return (True, f'SMS sent successfully (SID: {message.sid})')

    except ImportError:
        return (False, 'Twilio library not installed. Run: pip install twilio')
    except Exception as e:
        return (False, f'Failed to send SMS: {str(e)}')


def format_phone_number(phone):
    """
    Format phone number to E.164 format

    Args:
        phone (str): Phone number in any format

    Returns:
        str: Phone number in E.164 format
    """
    if not phone:
        return None

    # Remove all non-numeric characters
    digits = ''.join(filter(str.isdigit, phone))

    # If already has country code (11+ digits), add +
    if len(digits) >= 11:
        return f'+{digits}'
    # If 10 digits, assume US number
    elif len(digits) == 10:
        return f'+1{digits}'
    # Otherwise return as is with +
    else:
        return f'+{digits}'
