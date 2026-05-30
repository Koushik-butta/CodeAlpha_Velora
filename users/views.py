from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
import logging

from core.integrations.brevo import BrevoClient
from .forms import (
    RegistrationForm,
    LoginForm,
    OTPVerificationForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    PasswordChangeForm,
)
from .models import OTP

logger = logging.getLogger(__name__)
User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False  # Keep inactive until OTP verified
            user.save()

            # Update Profile full name
            profile = user.profile
            profile.full_name = form.cleaned_data['full_name']
            profile.save()

            # Generate and Send OTP
            otp = OTP.generate(user, 'register')
            try:
                client = BrevoClient()
                client.send_otp_email(user.email, otp.code)
                messages.success(request, 'Registration successful! Verification code sent to your email.')
            except Exception as e:
                logger.error(f"Error sending registration OTP: {e}")
                messages.warning(request, 'Registration successful, but email delivery failed. Code logged to console.')

            request.session['otp_email'] = user.email
            request.session['otp_purpose'] = 'register'
            return redirect('verify_otp')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    error_message = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None:
                # Store email and purpose in session
                request.session['otp_email'] = user.email
                
                if not user.is_active:
                    # Send registration OTP to activate account
                    otp = OTP.generate(user, 'register')
                    request.session['otp_purpose'] = 'register'
                    try:
                        BrevoClient().send_otp_email(user.email, otp.code)
                        messages.info(request, 'Account is inactive. Verification code sent to your email.')
                    except Exception as e:
                        logger.error(f"Error sending registration OTP: {e}")
                        messages.warning(request, 'Account is inactive. Verification code logged to console.')
                    return redirect('verify_otp')
                else:
                    # User is active, send login OTP
                    otp = OTP.generate(user, 'login')
                    request.session['otp_purpose'] = 'login'
                    request.session['pre_otp_user_id'] = user.id
                    try:
                        BrevoClient().send_otp_email(user.email, otp.code)
                        messages.info(request, 'Verification code sent to your email.')
                    except Exception as e:
                        logger.error(f"Error sending login OTP: {e}")
                        messages.warning(request, 'Verification code logged to console.')
                    return redirect('verify_otp')
            else:
                error_message = "Invalid email or password."
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form, 'error_message': error_message})


def verify_otp_view(request):
    email = request.session.get('otp_email')
    purpose = request.session.get('otp_purpose')

    if not email or not purpose:
        messages.error(request, 'Session expired or invalid authentication state.')
        return redirect('login')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('login')

    # Handle resend request
    if request.GET.get('resend') == '1':
        otp = OTP.generate(user, purpose)
        try:
            BrevoClient().send_otp_email(user.email, otp.code)
            messages.success(request, 'A new verification code has been sent to your email.')
        except Exception as e:
            logger.error(f"Error resending OTP: {e}")
            messages.warning(request, 'A new verification code has been logged to console.')
        return redirect('verify_otp')

    error_message = None
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['otp_code']
            otp = OTP.objects.filter(user=user, purpose=purpose, is_verified=False).first()

            if otp:
                if otp.is_expired():
                    error_message = 'This code has expired. Please request a new one.'
                elif otp.is_max_attempts_reached():
                    error_message = 'Too many failed attempts. Please request a new code.'
                else:
                    otp.attempts += 1
                    otp.save()

                    if otp.code == code:
                        otp.is_verified = True
                        otp.save()

                        if purpose == 'register':
                            user.is_active = True
                            user.save()

                        # Perform login
                        login(request, user)

                        # Clean up session
                        request.session.pop('otp_email', None)
                        request.session.pop('otp_purpose', None)
                        request.session.pop('pre_otp_user_id', None)

                        messages.success(request, f'Welcome back, {user.profile.full_name or user.email}!')
                        return redirect('/')
                    else:
                        error_message = 'Invalid verification code.'
            else:
                error_message = 'No active verification code found. Please request a new one.'
    else:
        form = OTPVerificationForm()

    return render(request, 'verify_otp.html', {
        'form': form,
        'email': email,
        'purpose': purpose,
        'error_message': error_message
    })


def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)

            otp = OTP.generate(user, 'reset')
            try:
                BrevoClient().send_otp_email(user.email, otp.code)
                messages.info(request, 'Verification code for password reset has been sent to your email.')
            except Exception as e:
                logger.error(f"Error sending reset OTP: {e}")
                messages.warning(request, 'Verification code for password reset logged to console.')

            request.session['otp_email'] = email
            request.session['otp_purpose'] = 'reset'
            return redirect('reset_password')
    else:
        form = ForgotPasswordForm()

    return render(request, 'forgot_password.html', {'form': form})


def reset_password_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    email = request.session.get('otp_email')
    purpose = request.session.get('otp_purpose')

    if not email or purpose != 'reset':
        messages.error(request, 'Invalid password reset session.')
        return redirect('forgot_password')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('forgot_password')

    error_message = None
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['otp_code']
            password = form.cleaned_data['new_password']
            otp = OTP.objects.filter(user=user, purpose='reset', is_verified=False).first()

            if otp:
                if otp.is_expired():
                    error_message = 'This code has expired. Please request a new one.'
                elif otp.is_max_attempts_reached():
                    error_message = 'Too many failed attempts. Please request a new code.'
                else:
                    otp.attempts += 1
                    otp.save()

                    if otp.code == code:
                        otp.is_verified = True
                        otp.save()

                        # Update password and activate user if they were inactive
                        user.set_password(password)
                        user.is_active = True
                        user.save()

                        # Clean up session
                        request.session.pop('otp_email', None)
                        request.session.pop('otp_purpose', None)

                        messages.success(request, 'Password reset successful! You can now log in.')
                        return redirect('login')
                    else:
                        error_message = 'Invalid verification code.'
            else:
                error_message = 'No active verification code found. Please request a new one.'
    else:
        form = ResetPasswordForm()

    return render(request, 'reset_password.html', {
        'form': form,
        'email': email,
        'error_message': error_message
    })


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Logged out successfully.')
        return redirect('/')
    return redirect('/')


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Keeps the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('/')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})
