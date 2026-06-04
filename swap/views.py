from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone

from swap.models import ExchangeRequest, ExchangeTimeline
from swap.forms import ExchangeRequestForm
from shop.models import Product
from notifications.models import Notification


# ──────────────────────────────────────────────────────────────
# EXCHANGE INDEX — list products available for exchange
# ──────────────────────────────────────────────────────────────

def exchange_index_view(request):
    """Browse products that are available for exchange."""
    exchange_products = Product.objects.filter(
        is_active=True,
        is_sold=False,
        exchange_available=True,
    ).select_related('seller', 'category').prefetch_related('images').order_by('-created_at')

    # Also include listing_type='exchange' products
    exchange_type_products = Product.objects.filter(
        is_active=True,
        is_sold=False,
        listing_type='exchange',
    ).select_related('seller', 'category').prefetch_related('images').order_by('-created_at')

    # Combine and deduplicate via OR query
    from django.db.models import Q
    exchange_products = Product.objects.filter(
        is_active=True,
        is_sold=False,
    ).filter(
        Q(exchange_available=True) | Q(listing_type='exchange')
    ).select_related('seller', 'category').prefetch_related('images').order_by('-created_at').distinct()

    paginator = Paginator(exchange_products, 12)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'exchange/index.html', {
        'exchange_products': page_obj.object_list,
        'page_obj': page_obj,
    })


# ──────────────────────────────────────────────────────────────
# EXCHANGE REQUEST — create a new exchange proposal
# ──────────────────────────────────────────────────────────────

@login_required
def exchange_request_view(request, pk):
    """Send an exchange request for a target product."""
    target_product = get_object_or_404(
        Product,
        pk=pk,
        is_active=True,
        is_sold=False,
    )

    # Prevent requesting exchange on own product
    if target_product.seller == request.user:
        messages.error(request, 'You cannot request an exchange for your own product.')
        return redirect('product_detail', slug=target_product.slug)

    # Prevent requesting exchange on non-exchange products
    if not target_product.exchange_available and target_product.listing_type != 'exchange':
        messages.error(request, 'This product is not available for exchange.')
        return redirect('product_detail', slug=target_product.slug)

    form = ExchangeRequestForm(requester=request.user, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            offered_product = form.cleaned_data['offered_product']

            # Check if a pending request already exists for this pair
            existing = ExchangeRequest.objects.filter(
                requester=request.user,
                target_product=target_product,
                offered_product=offered_product,
                status='pending',
            ).exists()
            if existing:
                messages.warning(request, 'You already have a pending exchange request for this product.')
                return redirect('product_detail', slug=target_product.slug)

            exchange = form.save(commit=False)
            exchange.requester = request.user
            exchange.target_user = target_product.seller
            exchange.target_product = target_product
            exchange.save()

            # Create timeline entry
            ExchangeTimeline.objects.create(
                exchange=exchange,
                step='request_sent',
                note=f'Exchange request sent by {request.user.email}.',
                created_by=request.user,
            )

            # Notify the seller
            Notification.create_for_user(
                user=target_product.seller,
                notification_type='exchange',
                title='New Exchange Request',
                message=(
                    f'{request.user.email} wants to exchange '
                    f'"{offered_product.title}" for your "{target_product.title}".'
                ),
                link=f'/exchange/{exchange.pk}/',
                icon='🔄',
            )

            messages.success(request, 'Exchange request sent successfully!')
            return redirect('exchange_detail', pk=exchange.pk)
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'exchange/request_form.html', {
        'form': form,
        'target_product': target_product,
    })


# ──────────────────────────────────────────────────────────────
# EXCHANGE DETAIL
# ──────────────────────────────────────────────────────────────

@login_required
def exchange_detail_view(request, pk):
    """View the full detail of an exchange request."""
    exchange = get_object_or_404(ExchangeRequest, pk=pk)

    # Only requester or target user may view
    if request.user not in (exchange.requester, exchange.target_user):
        messages.error(request, 'You do not have permission to view this exchange.')
        return redirect('exchange_index')

    timeline = exchange.timeline.select_related('created_by').order_by('created_at')

    return render(request, 'exchange/detail.html', {
        'exchange': exchange,
        'timeline': timeline,
    })


# ──────────────────────────────────────────────────────────────
# ACCEPT EXCHANGE
# ──────────────────────────────────────────────────────────────

@login_required
def accept_exchange_view(request, pk):
    """Target user accepts the exchange request."""
    exchange = get_object_or_404(ExchangeRequest, pk=pk, target_user=request.user)

    if exchange.status != 'pending':
        messages.error(request, f'Cannot accept an exchange with status "{exchange.get_status_display()}".')
        return redirect('exchange_detail', pk=pk)

    exchange.status = 'accepted'
    exchange.save(update_fields=['status', 'updated_at'])

    ExchangeTimeline.objects.create(
        exchange=exchange,
        step='accepted',
        note=f'Exchange accepted by {request.user.email}.',
        created_by=request.user,
    )

    # Notify the requester
    Notification.create_for_user(
        user=exchange.requester,
        notification_type='exchange',
        title='Exchange Accepted! 🎉',
        message=(
            f'{request.user.email} has accepted your exchange request for '
            f'"{exchange.target_product.title}".'
        ),
        link=f'/exchange/{exchange.pk}/',
        icon='✅',
    )

    messages.success(request, 'Exchange accepted! The requester has been notified.')
    return redirect('exchange_detail', pk=pk)


# ──────────────────────────────────────────────────────────────
# REJECT EXCHANGE
# ──────────────────────────────────────────────────────────────

@login_required
def reject_exchange_view(request, pk):
    """Target user rejects the exchange request."""
    exchange = get_object_or_404(ExchangeRequest, pk=pk, target_user=request.user)

    if exchange.status != 'pending':
        messages.error(request, f'Cannot reject an exchange with status "{exchange.get_status_display()}".')
        return redirect('exchange_detail', pk=pk)

    exchange.status = 'rejected'
    exchange.save(update_fields=['status', 'updated_at'])

    ExchangeTimeline.objects.create(
        exchange=exchange,
        step='rejected',
        note=f'Exchange rejected by {request.user.email}.',
        created_by=request.user,
    )

    # Notify the requester
    Notification.create_for_user(
        user=exchange.requester,
        notification_type='exchange',
        title='Exchange Request Declined',
        message=(
            f'{request.user.email} has declined your exchange request for '
            f'"{exchange.target_product.title}".'
        ),
        link=f'/exchange/{exchange.pk}/',
        icon='❌',
    )

    messages.info(request, 'Exchange request rejected.')
    return redirect('dashboard_exchanges')


# ──────────────────────────────────────────────────────────────
# CANCEL EXCHANGE
# ──────────────────────────────────────────────────────────────

@login_required
def cancel_exchange_view(request, pk):
    """Requester or target user cancels their pending/accepted exchange request."""
    from django.db.models import Q
    exchange = get_object_or_404(ExchangeRequest, Q(requester=request.user) | Q(target_user=request.user), pk=pk)

    if exchange.status not in ('pending', 'accepted'):
        messages.error(request, f'Cannot cancel an exchange with status "{exchange.get_status_display()}".')
        return redirect('exchange_detail', pk=pk)

    exchange.status = 'cancelled'
    exchange.save(update_fields=['status', 'updated_at'])

    ExchangeTimeline.objects.create(
        exchange=exchange,
        step='cancelled',
        note=f'Exchange cancelled by {request.user.email}.',
        created_by=request.user,
    )

    # Notify the other user
    other_user = exchange.target_user if request.user == exchange.requester else exchange.requester
    Notification.create_for_user(
        user=other_user,
        notification_type='exchange',
        title='Exchange Request Cancelled',
        message=(
            f'{request.user.email} has cancelled the exchange request for '
            f'"{exchange.target_product.title}".'
        ),
        link=f'/exchange/{exchange.pk}/',
        icon='🚫',
    )

    messages.info(request, 'Exchange request cancelled.')
    return redirect('dashboard_exchanges')


# ──────────────────────────────────────────────────────────────
# DASHBOARD EXCHANGES REDIRECT
# ──────────────────────────────────────────────────────────────

@login_required
def dashboard_exchanges_view(request):
    """Redirect to the users app dashboard exchanges view."""
    return redirect('dashboard_exchanges')
