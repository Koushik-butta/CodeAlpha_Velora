from django.urls import path
from . import views
from cart import views as cart_views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password_view, name='reset_password'),
    path('change-password/', views.change_password_view, name='change_password'),

    # ── Dashboard ─────────────────────────────────────────────
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/my-products/', views.my_products_view, name='dashboard_my_products'),
    path('dashboard/sales/', views.seller_sales_view, name='dashboard_sales'),
    path('dashboard/wishlist/', views.wishlist_view, name='dashboard_wishlist'),
    path('dashboard/orders/', cart_views.order_list_view, name='dashboard_orders'),
    path('dashboard/exchanges/', views.dashboard_exchanges_view, name='dashboard_exchanges'),
    path('dashboard/settings/', views.settings_view, name='dashboard_settings'),
    path('dashboard/notifications/', views.notifications_view, name='dashboard_notifications'),

    # ── Addresses ─────────────────────────────────────────────
    path('dashboard/addresses/', views.addresses_view, name='dashboard_addresses'),
    path('dashboard/addresses/add/', views.add_address_view, name='add_address'),
    path('dashboard/addresses/<int:pk>/edit/', views.edit_address_view, name='edit_address'),
    path('dashboard/addresses/<int:pk>/delete/', views.delete_address_view, name='delete_address'),
    path('dashboard/addresses/<int:pk>/default/', views.set_default_address_view, name='set_default_address'),

    # ── Notifications ──────────────────────────────────────────
    path('notifications/<int:pk>/read/', views.mark_notification_read_view, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_read_view, name='mark_all_read'),
    
    # ── Real-time Theme Sync ────────────────────────────────────
    path('dashboard/theme/update/', views.update_theme_view, name='update_theme'),
]
