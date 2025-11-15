from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from .models import UserProfile


class UserRegistrationForm(UserCreationForm):
    """Extended user registration form with email and reCAPTCHA"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'captcha')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class ProfilePictureForm(forms.ModelForm):
    """Form for uploading/updating profile picture"""

    class Meta:
        model = UserProfile
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            })
        }

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            # Validate file size (max 5MB)
            if picture.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image file too large (max 5MB)')

            # Validate file type
            valid_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if hasattr(picture, 'content_type') and picture.content_type not in valid_types:
                raise forms.ValidationError('Invalid image type. Allowed types: JPEG, PNG, GIF, WebP')

        return picture
