from django.contrib import admin

from shop.models import Category, Product, ProductImage, Wishlist, RecentlyViewed, Review, SearchHistory


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ('image_url', 'public_id', 'is_primary', 'order')
    readonly_fields = ()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'color', 'order', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'seller', 'category', 'listing_type', 'condition',
        'price', 'city', 'state', 'is_active', 'is_sold', 'is_featured',
        'views_count', 'wishlist_count', 'created_at',
    )
    list_filter = ('listing_type', 'condition', 'is_active', 'is_sold', 'is_featured', 'category', 'return_policy')
    search_fields = ('title', 'brand', 'model_name', 'city', 'state', 'seller__email')
    readonly_fields = ('id', 'slug', 'views_count', 'wishlist_count', 'created_at', 'updated_at')
    raw_id_fields = ('seller', 'category')
    inlines = [ProductImageInline]
    date_hierarchy = 'created_at'
    list_per_page = 25

    fieldsets = (
        ('Core', {'fields': ('id', 'seller', 'category', 'listing_type', 'title', 'slug')}),
        ('Details', {'fields': ('brand', 'model_name', 'condition', 'description')}),
        ('Pricing', {'fields': ('price', 'original_price', 'return_policy')}),
        ('Location', {'fields': ('city', 'state')}),
        ('Exchange', {'fields': ('exchange_available', 'exchange_value_estimate', 'exchange_for')}),
        ('Status', {'fields': ('is_active', 'is_sold', 'is_featured')}),
        ('Analytics', {'fields': ('views_count', 'wishlist_count', 'created_at', 'updated_at')}),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'product', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('reviewer__email', 'product__title', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('product', 'reviewer')
    ordering = ('-created_at',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    search_fields = ('user__email', 'product__title')
    raw_id_fields = ('user', 'product')
    ordering = ('-added_at',)


@admin.register(RecentlyViewed)
class RecentlyViewedAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'viewed_at')
    search_fields = ('user__email', 'product__title')
    raw_id_fields = ('user', 'product')
    ordering = ('-viewed_at',)


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'query', 'created_at')
    search_fields = ('user__email', 'query')
    raw_id_fields = ('user',)
    ordering = ('-created_at',)
