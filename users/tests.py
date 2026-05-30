from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from .models import OTP, Profile

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user_automatically_creates_profile(self):
        """Verify that the Django signal creates a Profile when a User is created."""
        user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123'
        )
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, Profile)
        self.assertEqual(user.profile.user, user)


class OTPModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='otpuser@example.com',
            password='otppassword123'
        )

    def test_otp_generation(self):
        """Verify that generate creates a valid OTP and clears previous ones."""
        otp1 = OTP.generate(self.user, 'login')
        self.assertEqual(len(otp1.code), 6)
        self.assertTrue(otp1.code.isdigit())
        self.assertEqual(otp1.purpose, 'login')
        self.assertFalse(otp1.is_verified)

        # Generate a second OTP for same purpose
        otp2 = OTP.generate(self.user, 'login')
        # otp1 should have been deleted/cleared
        self.assertFalse(OTP.objects.filter(id=otp1.id).exists())
        self.assertTrue(OTP.objects.filter(id=otp2.id).exists())

    def test_otp_expiry(self):
        """Verify that OTP expiration logic works based on settings."""
        otp = OTP.generate(self.user, 'login')
        self.assertFalse(otp.is_expired())

        # Simulate expiration by modifying created_at field back in time
        expiry_minutes = getattr(settings, 'OTP_EXPIRY_MINUTES', 10)
        otp.created_at = timezone.now() - timezone.timedelta(minutes=expiry_minutes + 1)
        otp.save()
        self.assertTrue(otp.is_expired())

    def test_max_attempts_limit(self):
        """Verify attempt counter and brute-force block logic."""
        otp = OTP.generate(self.user, 'login')
        self.assertFalse(otp.is_max_attempts_reached())

        max_attempts = getattr(settings, 'OTP_MAX_ATTEMPTS', 5)
        otp.attempts = max_attempts
        otp.save()
        self.assertTrue(otp.is_max_attempts_reached())
