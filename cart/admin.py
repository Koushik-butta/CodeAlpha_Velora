from django.contrib import admin
from .models import Address, Cart, CartItem, Order, OrderItem, ReturnRequest


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'seller', 'title', 'price', 'quantity', 'subtotal')
    fields = ('title', 'price', 'quantity', 'subtotal', 'seller', 'product')

    def subtotal(self, obj):
        return f'₹{obj.subtotal}'
    subtotal.short_description = 'Subtotal'


class ReturnRequestInline(admin.TabularInline):
    model = ReturnRequest
    extra = 0
    readonly_fields = ('order_item', 'request_type', 'reason', 'description', 'status', 'created_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'short_id', 'buyer', 'status', 'payment_method',
        'total', 'created_at', 'estimated_delivery_display',
    )
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('buyer__email', 'id', 'tracking_id')
    readonly_fields = ('id', 'short_id', 'created_at', 'updated_at', 'address_snapshot')
    inlines = [OrderItemInline, ReturnRequestInline]
    ordering = ('-created_at',)

    fieldsets = (
        ('Order Info', {
            'fields': ('id', 'short_id', 'buyer', 'status', 'payment_method'),
        }),
        ('Financials', {
            'fields': ('subtotal', 'delivery_charge', 'total'),
        }),
        ('Delivery', {
            'fields': ('address', 'address_snapshot', 'tracking_id'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'delivered_at'),
        }),
    )

    def estimated_delivery_display(self, obj):
        return obj.estimated_delivery.strftime('%d %b %Y')
    estimated_delivery_display.short_description = 'Est. Delivery'


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'city', 'state', 'pincode', 'is_default', 'address_type')
    list_filter = ('address_type', 'state', 'is_default')
    search_fields = ('user__email', 'full_name', 'city', 'pincode')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_count', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('order', 'order_item', 'request_type', 'reason', 'status', 'created_at')
    list_filter = ('request_type', 'reason', 'status')
    list_editable = ('status',)
