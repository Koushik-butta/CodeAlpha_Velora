from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from users.models import Profile
from cart.models import Address

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your full name', 'class': 'formInput'}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email address', 'class': 'formInput'}),
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Create a password', 'class': 'formInput'}),
    )
    password_confirm = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password', 'class': 'formInput'}),
    )

    class Meta:
        model = User
        fields = ('email', 'password')

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email address already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Passwords do not match.')
            raise ValidationError('Passwords do not match.')
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email address', 'class': 'formInput'}),
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password', 'class': 'formInput'}),
    )


class OTPVerificationForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': '••••••',
            'class': 'formInput text-center',
            'style': 'letter-spacing: 0.5em; font-size: 1.5rem; text-align: center;',
            'autocomplete': 'off',
            'maxlength': '6'
        }),
    )

    def clean_otp_code(self):
        code = self.cleaned_data.get('otp_code', '').strip()
        if not code.isdigit():
            raise ValidationError('OTP code must contain digits only.')
        return code


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your registered email', 'class': 'formInput'}),
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not User.objects.filter(email=email).exists():
            raise ValidationError('No account found with this email address.')
        return email


class SetNewPasswordForm(forms.Form):
    """Used in the token-based reset flow (uidb64/token URL args)."""
    new_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password', 'class': 'formInput'}),
    )
    new_password_confirm = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password', 'class': 'formInput'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('new_password')
        password_confirm = cleaned_data.get('new_password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('new_password_confirm', 'Passwords do not match.')
            raise ValidationError('Passwords do not match.')
        return cleaned_data


class ResetPasswordForm(forms.Form):
    """Legacy OTP-based form kept for backwards compatibility."""
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': '••••••',
            'class': 'formInput text-center',
            'style': 'letter-spacing: 0.5em; font-size: 1.5rem; text-align: center;',
            'autocomplete': 'off',
            'maxlength': '6'
        }),
    )
    new_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password', 'class': 'formInput'}),
    )
    new_password_confirm = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password', 'class': 'formInput'}),
    )

    def clean_otp_code(self):
        code = self.cleaned_data.get('otp_code', '').strip()
        if not code.isdigit():
            raise ValidationError('OTP code must contain digits only.')
        return code

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('new_password')
        password_confirm = cleaned_data.get('new_password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('new_password_confirm', 'Passwords do not match.')
            raise ValidationError('Passwords do not match.')
        return cleaned_data


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter current password', 'class': 'formInput'}),
    )
    new_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password', 'class': 'formInput'}),
    )
    new_password_confirm = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password', 'class': 'formInput'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError('Your current password is incorrect.')
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('new_password')
        password_confirm = cleaned_data.get('new_password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('new_password_confirm', 'Passwords do not match.')
            raise ValidationError('Passwords do not match.')
        return cleaned_data


class ProfileSettingsForm(forms.ModelForm):
    """Form for updating the user's Profile model fields."""

    full_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Your full name', 'class': 'formInput'}),
    )
    phone = forms.CharField(
        max_length=32,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Phone number', 'class': 'formInput'}),
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'City', 'class': 'formInput'}),
    )
    state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'State', 'class': 'formInput'}),
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Tell buyers a bit about yourself…',
            'class': 'formInput',
            'rows': 4,
        }),
    )
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'placeholder': 'https://your-website.com', 'class': 'formInput'}),
    )

    class Meta:
        model = Profile
        fields = ('full_name', 'phone', 'city', 'state', 'bio', 'website', 'theme')
        widgets = {
            'theme': forms.Select(attrs={'class': 'formInput'}),
        }


class AddressForm(forms.ModelForm):
    """Form for creating/editing a delivery Address."""

    class Meta:
        model = Address
        fields = (
            'full_name', 'phone', 'house_no', 'street', 'area',
            'city', 'state', 'pincode', 'landmark', 'address_type', 'is_default',
        )
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'formInput', 'placeholder': 'Full name'}),
            'phone': forms.TextInput(attrs={'class': 'formInput', 'placeholder': 'Phone number'}),
            'house_no': forms.TextInput(attrs={'class': 'formInput', 'placeholder': 'House / Flat / Block No.'}),
            'street': forms.TextInput(attrs={'class': 'formInput', 'placeholder': 'Street / Road'}),
            'area': forms.TextInput(attrs={'class': 'formInput', 'placeholder': 'Area / Colony'}),
            'city': forms.TextInput(attrs={'class': 'formInput', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'formInput', 'placeholder': 'State'}),
            'pincode': forms.TextInput(attrs={'class': 'formInput', 'placeholder': 'Pincode'}),
            'landmark': forms.TextInput(attrs={'class': 'formInput', 'placeholder': 'Nearby landmark (optional)'}),
            'address_type': forms.Select(attrs={'class': 'formInput'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'formCheckbox'}),
        }
