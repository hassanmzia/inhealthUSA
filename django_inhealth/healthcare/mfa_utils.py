"""
Multi-Factor Authentication utilities
Provides TOTP-based 2FA functionality using pyotp
"""
import pyotp
import qrcode
import io
import base64
import secrets
import string


def generate_totp_secret():
    """Generate a random TOTP secret key"""
    return pyotp.random_base32()


def get_totp_uri(user, secret):
    """
    Generate TOTP URI for QR code generation
    Args:
        user: Django User object
        secret: TOTP secret key
    Returns:
        TOTP URI string
    """
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email or user.username,
        issuer_name='InHealth EHR'
    )


def generate_qr_code(totp_uri):
    """
    Generate QR code image from TOTP URI
    Args:
        totp_uri: TOTP URI string
    Returns:
        Base64 encoded QR code image
    """
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"


def verify_totp_token(secret, token):
    """
    Verify TOTP token
    Args:
        secret: TOTP secret key
        token: 6-digit TOTP code
    Returns:
        Boolean indicating if token is valid
    """
    if not secret or not token:
        return False

    totp = pyotp.TOTP(secret)
    # Allow 1 period before and after for clock skew
    return totp.verify(token, valid_window=1)


def generate_backup_codes(count=10):
    """
    Generate backup codes for MFA recovery
    Args:
        count: Number of backup codes to generate
    Returns:
        List of backup codes
    """
    codes = []
    for _ in range(count):
        # Generate 8-character alphanumeric code
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        # Format as XXXX-XXXX
        formatted_code = f"{code[:4]}-{code[4:]}"
        codes.append(formatted_code)
    return codes


def verify_backup_code(user_profile, code):
    """
    Verify and consume a backup code
    Args:
        user_profile: UserProfile object
        code: Backup code to verify
    Returns:
        Boolean indicating if code is valid
    """
    if not code or not user_profile.mfa_backup_codes:
        return False

    # Normalize code (remove spaces, hyphens, convert to uppercase)
    normalized_code = code.replace('-', '').replace(' ', '').upper()

    # Check if code exists in backup codes
    for i, backup_code in enumerate(user_profile.mfa_backup_codes):
        normalized_backup = backup_code.replace('-', '').replace(' ', '').upper()
        if normalized_backup == normalized_code:
            # Remove used backup code
            user_profile.mfa_backup_codes.pop(i)
            user_profile.save()
            return True

    return False
