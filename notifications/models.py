from django.db import models
from django.conf import settings


class Notification(models.Model):
    """In-app notification for users."""

    TYPE_CHOICES = [
        ('order', 'Order Update'),
        ('exchange', 'Exchange Update'),
        ('offer', 'New Offer'),
        ('wishlist', 'Wishlist Update'),
        ('system', 'System'),
        ('review', 'Review'),
        ('promotion', 'Promotion'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    notification_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default='system')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, help_text='URL to link this notification to')
    icon = models.CharField(max_length=10, default='🔔', help_text='Emoji icon for the notification')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.user.email} — {self.title}"

    @classmethod
    def create_for_user(cls, user, notification_type, title, message, link='', icon='🔔'):
        """Helper to quickly create a notification."""
        return cls.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
            icon=icon,
        )
