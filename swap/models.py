from django.db import models
from django.conf import settings


class ExchangeRequest(models.Model):
    """Peer-to-peer exchange proposal."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exchange_requests_sent',
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exchange_requests_received',
    )
    # Product the requester wants
    target_product = models.ForeignKey(
        'shop.Product',
        on_delete=models.CASCADE,
        related_name='exchange_targets',
    )
    # Product the requester is offering
    offered_product = models.ForeignKey(
        'shop.Product',
        on_delete=models.CASCADE,
        related_name='exchange_offers',
    )
    # Optional cash top-up adjustment
    cash_adjustment = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text='Positive = requester pays extra. Negative = requester receives extra.'
    )
    message = models.TextField(blank=True, help_text='Message to the other party')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Exchange Request'
        verbose_name_plural = 'Exchange Requests'
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.requester.email} → {self.target_product.title} [{self.status}]"


class ExchangeTimeline(models.Model):
    """Timeline of events for an exchange request."""

    STEP_CHOICES = [
        ('request_sent', 'Exchange Request Sent'),
        ('request_viewed', 'Request Viewed'),
        ('counter_offer', 'Counter Offer Made'),
        ('accepted', 'Exchange Accepted'),
        ('meetup_arranged', 'Meetup Arranged'),
        ('item_handed_over', 'Items Handed Over'),
        ('completed', 'Exchange Completed'),
        ('rejected', 'Exchange Rejected'),
        ('cancelled', 'Exchange Cancelled'),
    ]

    exchange = models.ForeignKey(ExchangeRequest, on_delete=models.CASCADE, related_name='timeline')
    step = models.CharField(max_length=20, choices=STEP_CHOICES)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f"{self.exchange} — {self.step}"
