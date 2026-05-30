from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User, Profile, OTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom email-based User model."""
    ordering = ('email',)
    list_display = ('email', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('email',)
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )

    # No username field
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin for user profiles / seller identities."""
    list_display = (
        'user', 'full_name', 'phone', 'city', 'state',
        'is_verified_seller', 'trade_score', 'total_sales', 'total_exchanges',
    )
    list_filter = ('is_verified_seller', 'country', 'state')
    search_fields = ('user__email', 'full_name', 'phone', 'city')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)

    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Personal Info', {'fields': ('full_name', 'phone', 'bio', 'website', 'avatar_url', 'avatar_public_id')}),
        ('Location', {'fields': ('city', 'state', 'postal_code', 'country', 'address_line')}),
        ('Marketplace Reputation', {'fields': ('trade_score', 'is_verified_seller', 'total_sales', 'total_exchanges')}),
        ('Notification Prefs', {'fields': ('notify_email', 'notify_swap_updates', 'notify_marketing')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    """Admin for OTP records (kept for diagnostics, not used in active auth)."""
    list_display = ('user', 'purpose', 'code', 'is_verified', 'attempts', 'created_at')
    list_filter = ('purpose', 'is_verified')
    search_fields = ('user__email', 'code')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user',)
    ordering = ('-created_at',)
