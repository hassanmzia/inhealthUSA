"""
Custom Password Validators for Enhanced Security
Implements password complexity requirements for InHealth EHR
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class ComplexityValidator:
    """
    Validates that the password contains:
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    def validate(self, password, user=None):
        errors = []

        if not re.search(r'[A-Z]', password):
            errors.append(_('Password must contain at least one uppercase letter (A-Z).'))

        if not re.search(r'[a-z]', password):
            errors.append(_('Password must contain at least one lowercase letter (a-z).'))

        if not re.search(r'[0-9]', password):
            errors.append(_('Password must contain at least one digit (0-9).'))

        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]', password):
            errors.append(_('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>_-+=[]\\\/~`).'))

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _(
            'Your password must contain at least one uppercase letter, '
            'one lowercase letter, one digit, and one special character.'
        )


class MinimumLengthValidator:
    """
    Validates that the password is at least the specified minimum length.
    """
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("This password is too short. It must contain at least %(min_length)d characters."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least %(min_length)d characters."
            % {'min_length': self.min_length}
        )


class MaximumLengthValidator:
    """
    Validates that the password is not longer than the specified maximum length.
    """
    def __init__(self, max_length=128):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
            raise ValidationError(
                _("This password is too long. It must contain no more than %(max_length)d characters."),
                code='password_too_long',
                params={'max_length': self.max_length},
            )

    def get_help_text(self):
        return _(
            "Your password must contain no more than %(max_length)d characters."
            % {'max_length': self.max_length}
        )


class NoConsecutiveCharactersValidator:
    """
    Validates that the password doesn't contain too many consecutive identical characters.
    """
    def __init__(self, max_consecutive=3):
        self.max_consecutive = max_consecutive

    def validate(self, password, user=None):
        for i in range(len(password) - self.max_consecutive + 1):
            if len(set(password[i:i + self.max_consecutive])) == 1:
                raise ValidationError(
                    _("Password cannot contain %(max_consecutive)d or more consecutive identical characters."),
                    code='password_consecutive_chars',
                    params={'max_consecutive': self.max_consecutive},
                )

    def get_help_text(self):
        return _(
            "Your password cannot contain %(max_consecutive)d or more consecutive identical characters."
            % {'max_consecutive': self.max_consecutive}
        )


class NoCommonPatternsValidator:
    """
    Validates that the password doesn't contain common patterns.
    """
    def validate(self, password, user=None):
        common_patterns = [
            'password', 'pass1234', '12345678', 'qwerty', 'abc123',
            'letmein', 'welcome', 'monkey', '1q2w3e4r', 'admin',
            'iloveyou', 'princess', 'dragon', 'master', 'trustno1'
        ]

        password_lower = password.lower()
        for pattern in common_patterns:
            if pattern in password_lower:
                raise ValidationError(
                    _("Password contains a common pattern and is not secure."),
                    code='password_common_pattern',
                )

    def get_help_text(self):
        return _("Your password cannot contain common patterns or sequences.")
