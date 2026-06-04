from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
import random


class UserManager(BaseUserManager):
    """Custom manager for User model with email-only authentication."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Email-based user; inactive until email verification (Phase 1+)."""

    username = None
    email = models.EmailField('email address', unique=True)
    is_active = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self) -> str:
        return self.email


class Profile(models.Model):
    """Extended profile and marketplace identity."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    address_line = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True, default='India')
    avatar_url = models.URLField(max_length=500, blank=True)
    avatar_public_id = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True, help_text='Short bio visible on seller profile')
    website = models.URLField(max_length=300, blank=True)
    # Marketplace reputation
    trade_score = models.IntegerField(default=0, help_text='Velora Trade Score — earned through successful deals')
    is_verified_seller = models.BooleanField(default=False, help_text='Manually verified by Velora team')
    total_sales = models.PositiveIntegerField(default=0)
    total_exchanges = models.PositiveIntegerField(default=0)
    # Notification preferences
    notify_email = models.BooleanField(default=True)
    notify_swap_updates = models.BooleanField(default=True)
    notify_marketing = models.BooleanField(default=False)
    THEME_CHOICES = [
        ('classic-light', 'Classic Light'),
        ('sunset-saffron', 'Sunset Saffron (Charcoal & Amber)'),
        ('royal-ashoka', 'Royal Ashoka Blue (Dark Deep Blue)'),
        ('vibrant-emerald', 'Nordic Sage (Dark Sage Green)'),
        ('cosmic-lavender', 'Cosmic Lavender (Dark Indigo-Violet)'),
    ]
    theme = models.CharField(max_length=30, choices=THEME_CHOICES, default='sunset-saffron')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'

    def __str__(self) -> str:
        return self.full_name or str(self.user)


class OTP(models.Model):
    """One-Time Password model for logins, registration, and resets."""

    PURPOSE_CHOICES = [
        ('login', 'Login'),
        ('register', 'Registration'),
        ('reset', 'Password Reset'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='otps',
    )
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'otp'
        verbose_name_plural = 'otps'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return f"{self.user.email} - {self.purpose} - {self.code}"

    def is_expired(self) -> bool:
        expiry_minutes = getattr(settings, 'OTP_EXPIRY_MINUTES', 10)
        return timezone.now() > self.created_at + timezone.timedelta(minutes=expiry_minutes)

    def is_max_attempts_reached(self) -> bool:
        max_attempts = getattr(settings, 'OTP_MAX_ATTEMPTS', 5)
        return self.attempts >= max_attempts

    @classmethod
    def generate(cls, user, purpose) -> 'OTP':
        """Deactivate old active OTPs for user and purpose, then create a new one."""
        cls.objects.filter(user=user, purpose=purpose, is_verified=False).delete()
        code = f"{random.randint(100000, 999999)}"
        return cls.objects.create(user=user, code=code, purpose=purpose)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Signal receiver to automatically create user profile when user registers."""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Signal receiver to ensure profile changes are saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
