from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from notifications.models import Notification


@login_required
def notifications_list_view(request):
    """Redirect to the dashboard notifications page."""
    return redirect('dashboard_notifications')


@login_required
def mark_notification_read_view(request, pk):
    """Mark a single notification as read."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'pk': pk})
    return redirect('dashboard_notifications')


@login_required
def mark_all_read_view(request):
    """Mark all unread notifications as read for the current user."""
    updated = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'updated': updated})
    return redirect('dashboard_notifications')
