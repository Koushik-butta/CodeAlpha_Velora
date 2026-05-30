from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('', include('shop.urls')),
    path('', include('cart.urls')),
    path('', include('swap.urls')),
    path('', include('notifications.urls')),
]