from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Category(models.Model):
    """Product category with icon and color branding."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=10, default='📦', help_text='Emoji icon')
    color = models.CharField(max_length=20, default='#8B5CF6', help_text='Hex color')
    image = models.CharField(max_length=500, blank=True, help_text='Cloudinary image URL')
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ('order', 'name')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @classmethod
    def get_all_active(cls):
        """Get active categories, auto-creating default ones if none exist."""
        if not cls.objects.filter(is_active=True).exists():
            defaults = [
                ('Mobiles', '📱', '#F97316', 0),
                ('Laptops', '💻', '#10B981', 1),
                ('Bikes', '🚲', '#F59E0B', 2),
                ('Fashion', '👕', '#FF6B00', 3),
                ('Electronics', '🔌', '#3B82F6', 4),
                ('Books', '📚', '#8B5CF6', 5),
                ('Sports', '🏏', '#10B981', 6),
                ('Furniture', '🪑', '#F59E0B', 7),
                ('Gaming', '🎮', '#EF4444', 8),
                ('Home Appliances', '🏠', '#128807', 9),
            ]
            for name, icon, color, order in defaults:
                cls.objects.get_or_create(
                    name=name,
                    defaults={
                        'icon': icon,
                        'color': color,
                        'order': order,
                        'is_active': True,
                    }
                )
        return cls.objects.filter(is_active=True).order_by('order')


class Product(models.Model):
    """Core product listing — Buy, Sell, or Exchange."""

    LISTING_TYPE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
        ('exchange', 'Exchange'),
    ]
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    RETURN_POLICY_CHOICES = [
        ('no_return', 'No Return'),
        ('3_days', '3 Days Return'),
        ('7_days', '7 Days Return'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='products',
    )
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES, default='sell')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    original_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='good')
    brand = models.CharField(max_length=100, blank=True)
    model_name = models.CharField(max_length=100, blank=True)
    # Location
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    # Exchange specifics
    exchange_available = models.BooleanField(default=False)
    exchange_value_estimate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    exchange_for = models.TextField(blank=True, help_text='What would you like in exchange?')
    # Policies
    return_policy = models.CharField(max_length=10, choices=RETURN_POLICY_CHOICES, default='no_return')
    # Status
    is_active = models.BooleanField(default=True)
    is_sold = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    # Analytics
    views_count = models.PositiveIntegerField(default=0)
    wishlist_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:250]
            self.slug = f"{base}-{str(self.id)[:8]}"
        super().save(*args, **kwargs)

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return round((1 - self.price / self.original_price) * 100)
        return 0

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews.exists():
            return None
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)


class ProductImage(models.Model):
    """Cloudinary-backed product image."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=800)
    public_id = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('order', 'id')

    def __str__(self):
        return f"Image for {self.product.title}"

    @property
    def url(self):
        return self.image_url


class Wishlist(models.Model):
    """User's saved/wishlisted products."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ('-added_at',)

    def __str__(self):
        return f"{self.user.email} → {self.product.title}"


class RecentlyViewed(models.Model):
    """Track recently viewed products per user."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recently_viewed')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='viewed_by')
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ('-viewed_at',)

    def __str__(self):
        return f"{self.user.email} viewed {self.product.title}"


class Review(models.Model):
    """Buyer review for a product listing."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given',
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 (worst) to 5 (best)',
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ('product', 'reviewer')
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.reviewer.email} → {self.product.title} ({self.rating}★)"


class SearchHistory(models.Model):
    """Persisted search queries for logged-in users."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='search_history',
    )
    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Search History'
        verbose_name_plural = 'Search Histories'
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.user.email}: '{self.query}'"
