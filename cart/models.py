from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid


class Address(models.Model):
    """User delivery address book."""

    ADDRESS_TYPE_CHOICES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    house_no = models.CharField(max_length=100, blank=True)
    street = models.CharField(max_length=255)
    area = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    landmark = models.CharField(max_length=200, blank=True)
    address_type = models.CharField(max_length=8, choices=ADDRESS_TYPE_CHOICES, default='home')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        ordering = ('-is_default', '-created_at')

    def __str__(self):
        return f"{self.full_name} — {self.city}, {self.state} {self.pincode}"

    @property
    def full_address(self):
        parts = [self.house_no, self.street, self.area, self.city, self.state, self.pincode]
        return ', '.join(p for p in parts if p)

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class Cart(models.Model):
    """Shopping cart — one per user."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='cart', null=True, blank=True
    )
    session_key = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cart'

    def __str__(self):
        return f"Cart — {self.user or self.session_key}"

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.select_related('product').all())

    @property
    def delivery_charge(self):
        return 0 if self.subtotal >= 499 else 49

    @property
    def total(self):
        return self.subtotal + self.delivery_charge

    @property
    def item_count(self):
        return self.items.count()


class CartItem(models.Model):
    """Individual item in a cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.product.title} × {self.quantity}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity


class Order(models.Model):
    """Buyer order — complete purchase record."""

    STATUS_CHOICES = [
        ('pending', 'Order Placed'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Packed'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('return_requested', 'Return Requested'),
        ('returned', 'Returned'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('upi', 'UPI'),
        ('card', 'Debit / Credit Card'),
        ('netbanking', 'Net Banking'),
    ]

    # Status ordering for progress tracker
    STATUS_ORDER = [
        'pending', 'confirmed', 'processing',
        'shipped', 'out_for_delivery', 'delivered',
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders'
    )
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    # Snapshot of address at order time
    address_snapshot = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=12, choices=PAYMENT_CHOICES, default='cod')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    tracking_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ('-created_at',)

    def __str__(self):
        return f"Order #{self.short_id} — {self.buyer.email}"

    @property
    def short_id(self):
        return str(self.id).upper()[:8]

    @property
    def estimated_delivery(self):
        """Returns estimated delivery date — 5-7 days from order date."""
        if self.status == 'delivered' and self.delivered_at:
            return self.delivered_at
        if self.status == 'shipped':
            return self.updated_at + timedelta(days=2)
        if self.status == 'out_for_delivery':
            return timezone.now() + timedelta(days=1)
        return self.created_at + timedelta(days=6)

    @property
    def is_cancellable(self):
        return self.status in ('pending', 'confirmed')

    @property
    def is_returnable(self):
        return self.status == 'delivered'

    @property
    def status_step(self):
        """0-based index in STATUS_ORDER for progress tracker."""
        try:
            return self.STATUS_ORDER.index(self.status)
        except ValueError:
            return -1  # cancelled / returned

    @property
    def status_progress_pct(self):
        step = self.status_step
        if step < 0:
            return 0
        return int((step / (len(self.STATUS_ORDER) - 1)) * 100)


class OrderItem(models.Model):
    """Item within an order — price snapshot at purchase time."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('shop.Product', on_delete=models.SET_NULL, null=True)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='order_items_sold'
    )
    # Snapshots
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    image_url = models.URLField(max_length=800, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Order Item'

    def __str__(self):
        return f"{self.title} × {self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity


class ReturnRequest(models.Model):
    """Return / Exchange / Replacement request for a delivered order."""

    TYPE_CHOICES = [
        ('return', 'Return & Refund'),
        ('exchange', 'Exchange Product'),
        ('replacement', 'Replacement'),
    ]

    REASON_CHOICES = [
        ('damaged', 'Damaged / Defective Product'),
        ('wrong', 'Wrong Product Delivered'),
        ('not_as_described', 'Product Not as Described'),
        ('size_issue', 'Size / Fit Issue'),
        ('changed_mind', 'Changed My Mind'),
        ('other', 'Other Reason'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='return_requests')
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='return_requests')
    request_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default='return')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Return Request'
        verbose_name_plural = 'Return Requests'
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.get_request_type_display()} — Order #{self.order.short_id}"
