from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.notifications_list_view, name='notifications_list'),
    path('notifications/<int:pk>/read/', views.mark_notification_read_view, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_read_view, name='mark_all_read'),
]
