from django.urls import path
from . import views

urlpatterns = [
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/json/', views.cart_json_view, name='cart_json'),
    path('cart/add/<uuid:pk>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('cart/update/', views.update_cart_view, name='update_cart'),

    # Buy Now
    path('buy-now/<uuid:pk>/', views.buy_now_view, name='buy_now'),

    # Checkout
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/place/', views.place_order_view, name='place_order'),

    # Orders
    path('orders/', views.order_list_view, name='order_list'),
    path('orders/<uuid:pk>/', views.order_detail_view, name='order_detail'),
    path('orders/<uuid:pk>/confirmation/', views.order_confirmation_view, name='order_confirmation'),
    path('orders/<uuid:pk>/cancel/', views.cancel_order_view, name='cancel_order'),
    path('orders/sales/cancel/<int:pk>/', views.seller_cancel_order_view, name='seller_cancel_order'),
    path('orders/<uuid:pk>/reorder/', views.reorder_view, name='reorder'),

    # Return Requests
    path('orders/<uuid:order_pk>/item/<int:item_pk>/return/', views.return_request_view, name='return_request'),

    # Address Management (owned by cart app, accessed via users dashboard URLs too)
    # These are exposed here for direct access; users/urls.py re-exposes under /dashboard/
    path('_cart/addresses/', views.addresses_view, name='_cart_addresses'),
    path('_cart/addresses/add/', views.add_address_view, name='_cart_add_address'),
    path('_cart/addresses/<int:pk>/edit/', views.edit_address_view, name='_cart_edit_address'),
    path('_cart/addresses/<int:pk>/delete/', views.delete_address_view, name='_cart_delete_address'),
    path('_cart/addresses/<int:pk>/default/', views.set_default_address_view, name='_cart_set_default'),
]
