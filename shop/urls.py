from django.urls import path
from . import views

urlpatterns = [
    # ── Landing / Home ────────────────────────────────────────
    path('', views.home_view, name='home'),
    path('deals/', views.deals_view, name='deals'),

    # ── Product browse ────────────────────────────────────────
    path('products/', views.product_list_view, name='product_list'),
    path('products/sell/', views.sell_product_view, name='sell_product'),

    # ── Wishlist ──────────────────────────────────────────────
    path('products/wishlist/toggle/<uuid:pk>/', views.toggle_wishlist_view, name='toggle_wishlist'),

    # ── Product detail (slug must come after specific patterns) ─
    path('products/search-suggestions/', views.search_suggestions_view, name='search_suggestions'),
    path('products/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('products/<slug:slug>/edit/', views.edit_product_view, name='edit_product'),
    path('products/<slug:slug>/delete/', views.delete_product_view, name='delete_product'),
    path('products/<slug:slug>/mark-sold/', views.mark_sold_view, name='mark_sold'),
    path('products/<slug:slug>/mark-reserved/', views.mark_reserved_view, name='mark_reserved'),
    path('products/<slug:slug>/review/', views.add_review_view, name='add_review'),

    # ── Seller profile ────────────────────────────────────────
    path('seller/<int:user_id>/', views.seller_profile_view, name='seller_profile'),

    # ── Search ────────────────────────────────────────────────
    path('search/', views.search_view, name='search'),
]