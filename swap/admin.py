from django.contrib import admin

from swap.models import ExchangeRequest, ExchangeTimeline


class ExchangeTimelineInline(admin.TabularInline):
    model = ExchangeTimeline
    extra = 0
    readonly_fields = ('created_at', 'created_by', 'step', 'note')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ExchangeRequest)
class ExchangeRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'requester', 'target_user', 'target_product',
        'offered_product', 'cash_adjustment', 'status', 'created_at',
    )
    list_filter = ('status',)
    search_fields = (
        'requester__email', 'target_user__email',
        'target_product__title', 'offered_product__title',
    )
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    raw_id_fields = ('requester', 'target_user', 'target_product', 'offered_product')
    inlines = [ExchangeTimelineInline]
    date_hierarchy = 'created_at'
    list_per_page = 25

    fieldsets = (
        ('Parties', {'fields': ('requester', 'target_user')}),
        ('Products', {'fields': ('target_product', 'offered_product')}),
        ('Exchange Terms', {'fields': ('cash_adjustment', 'message', 'status')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'completed_at')}),
    )


@admin.register(ExchangeTimeline)
class ExchangeTimelineAdmin(admin.ModelAdmin):
    list_display = ('exchange', 'step', 'created_by', 'created_at')
    list_filter = ('step',)
    search_fields = ('exchange__requester__email', 'note')
    readonly_fields = ('created_at',)
    raw_id_fields = ('exchange', 'created_by')
    ordering = ('-created_at',)
