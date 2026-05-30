from django.urls import path
from . import views

urlpatterns = [
    # ── Exchange Browse ────────────────────────────────────────
    path('exchange/', views.exchange_index_view, name='exchange_index'),

    # ── Create a request ──────────────────────────────────────
    path('exchange/request/<uuid:pk>/', views.exchange_request_view, name='exchange_request'),

    # ── Detail ────────────────────────────────────────────────
    path('exchange/<int:pk>/', views.exchange_detail_view, name='exchange_detail'),

    # ── Actions ───────────────────────────────────────────────
    path('exchange/<int:pk>/accept/', views.accept_exchange_view, name='accept_exchange'),
    path('exchange/<int:pk>/reject/', views.reject_exchange_view, name='reject_exchange'),
    path('exchange/<int:pk>/cancel/', views.cancel_exchange_view, name='cancel_exchange'),
]
