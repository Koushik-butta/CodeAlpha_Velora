from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
import json

from shop.models import Product
from notifications.models import Notification
from .models import Cart, CartItem, Order, OrderItem, Address, ReturnRequest
from .forms import AddressForm, ReturnRequestForm


# ─────────────────────────────────────────────────
# CART VIEWS
# ─────────────────────────────────────────────────

@login_required
def cart_view(request):
    """Show the shopping cart."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product', 'product__category').all()

    subtotal = sum(item.subtotal for item in cart_items)
    delivery_charge = 0 if subtotal >= 499 else (49 if subtotal > 0 else 0)
    total = subtotal + delivery_charge

    return render(request, 'cart/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'total': total,
        'free_delivery_remaining': max(0, 499 - subtotal),
    })


@login_required
def cart_json_view(request):
    """Retrieve full cart contents as JSON."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product').all()
    items_data = []
    for item in cart_items:
        image_url = ''
        primary = item.product.primary_image
        if primary:
            image_url = primary.image_url
        items_data.append({
            'id': item.pk,
            'product_id': str(item.product.pk),
            'product_title': item.product.title,
            'product_price': float(item.product.price),
            'product_image': image_url,
            'product_slug': item.product.slug,
            'quantity': item.quantity,
            'subtotal': float(item.subtotal),
        })
    subtotal = sum(item.subtotal for item in cart_items)
    delivery_charge = 0 if subtotal >= 499 else (49 if subtotal > 0 else 0)
    return JsonResponse({
        'success': True,
        'items': items_data,
        'subtotal': float(subtotal),
        'delivery_charge': float(delivery_charge),
        'total': float(subtotal + delivery_charge),
        'cart_count': cart.item_count,
    })


@login_required
@require_POST
def add_to_cart_view(request, pk):
    """Add a product to cart. Returns JSON for AJAX or redirects."""
    product = get_object_or_404(Product, pk=pk, is_active=True, is_sold=False)

    if product.seller == request.user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'You cannot buy your own product.'})
        messages.error(request, 'You cannot add your own product to cart.')
        return redirect('product_detail', slug=product.slug)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        item.quantity = min(item.quantity + 1, 10)
        item.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'"{product.title}" added to cart!',
            'cart_count': cart.item_count,
        })

    messages.success(request, f'"{product.title}" added to cart!')
    next_url = request.POST.get('next', '')
    return redirect(next_url or 'cart')


@login_required
@require_POST
def remove_from_cart_view(request, pk):
    """Remove a cart item."""
    item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    title = item.product.title
    cart = item.cart
    item.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        subtotal = sum(i.subtotal for i in cart.items.all())
        delivery_charge = 0 if subtotal >= 499 else (49 if subtotal > 0 else 0)
        return JsonResponse({
            'success': True,
            'message': f'"{title}" removed from cart.',
            'cart_count': cart.item_count,
            'cart_subtotal': float(subtotal),
            'delivery_charge': float(delivery_charge),
            'cart_total': float(subtotal + delivery_charge),
        })

    messages.success(request, f'"{title}" removed from cart.')
    return redirect('cart')


@login_required
@require_POST
def update_cart_view(request):
    """Update cart item quantities. Accepts JSON body."""
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({'success': False, 'message': 'Invalid data.'}, status=400)

    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)

    if quantity < 1:
        item.delete()
        return JsonResponse({'success': True, 'removed': True})

    item.quantity = min(quantity, 10)
    item.save()

    cart = item.cart
    subtotal = sum(i.subtotal for i in cart.items.select_related('product').all())
    delivery_charge = 0 if subtotal >= 499 else (49 if subtotal > 0 else 0)

    return JsonResponse({
        'success': True,
        'item_subtotal': float(item.subtotal),
        'cart_subtotal': float(subtotal),
        'delivery_charge': float(delivery_charge),
        'cart_total': float(subtotal + delivery_charge),
        'cart_count': cart.item_count,
    })


# ─────────────────────────────────────────────────
# BUY NOW FLOW
# ─────────────────────────────────────────────────

@login_required
def buy_now_view(request, pk):
    """Initiate Buy Now — skip cart, go straight to checkout."""
    product = get_object_or_404(Product, pk=pk, is_active=True, is_sold=False)

    if product.seller == request.user:
        messages.error(request, 'You cannot buy your own product.')
        return redirect('product_detail', slug=product.slug)

    # Store buy_now context in session
    request.session['buy_now'] = {
        'product_id': str(product.pk),
        'quantity': 1,
    }
    return redirect('checkout')


# ─────────────────────────────────────────────────
# CHECKOUT
# ─────────────────────────────────────────────────

@login_required
def checkout_view(request):
    """Unified checkout for both Cart and Buy Now."""
    user = request.user
    buy_now = request.session.get('buy_now')

    if buy_now:
        # Buy Now mode
        product = get_object_or_404(Product, pk=buy_now['product_id'], is_active=True, is_sold=False)
        quantity = int(buy_now.get('quantity', 1))
        subtotal = product.price * quantity
        checkout_items = [{
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
            'is_dict': True,
        }]
        mode = 'buy_now'
    else:
        # Cart mode
        cart = Cart.objects.filter(user=user).first()
        if not cart or not cart.items.exists():
            messages.warning(request, 'Your cart is empty.')
            return redirect('cart')
        cart_items = cart.items.select_related('product').all()
        checkout_items = list(cart_items)
        subtotal = sum(item.subtotal for item in cart_items)
        mode = 'cart'

    delivery_charge = 0 if subtotal >= 499 else 49
    total = subtotal + delivery_charge
    estimated_delivery = timezone.now() + timedelta(days=6)

    addresses = Address.objects.filter(user=user).order_by('-is_default', '-created_at')
    address_form = AddressForm()
    selected_address = addresses.filter(is_default=True).first() or addresses.first()

    return render(request, 'cart/checkout.html', {
        'checkout_items': checkout_items,
        'addresses': addresses,
        'address_form': address_form,
        'selected_address': selected_address,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'total': total,
        'estimated_delivery': estimated_delivery,
        'mode': mode,
    })


@login_required
@require_POST
def place_order_view(request):
    """Place the order — creates Order + OrderItems, clears cart/session."""
    user = request.user

    # Get address
    address_id = request.POST.get('address_id')
    address = None

    if not address_id:
        # Check if they filled out the new address form
        if request.POST.get('full_name') and request.POST.get('street'):
            addr_form = AddressForm(request.POST)
            if addr_form.is_valid():
                address = addr_form.save(commit=False)
                address.user = user
                address.save()
                address_id = address.pk
            else:
                # If form is invalid, re-render checkout page showing errors
                buy_now = request.session.get('buy_now')
                if buy_now:
                    product = get_object_or_404(Product, pk=buy_now['product_id'], is_active=True, is_sold=False)
                    quantity = int(buy_now.get('quantity', 1))
                    subtotal = product.price * quantity
                    checkout_items = [{
                        'product': product,
                        'quantity': quantity,
                        'subtotal': subtotal,
                        'is_dict': True,
                    }]
                    mode = 'buy_now'
                else:
                    cart = Cart.objects.filter(user=user).first()
                    cart_items = cart.items.select_related('product').all() if cart else []
                    checkout_items = list(cart_items)
                    subtotal = sum(item.subtotal for item in cart_items)
                    mode = 'cart'

                delivery_charge = 0 if subtotal >= 499 else 49
                total = subtotal + delivery_charge
                estimated_delivery = timezone.now() + timedelta(days=6)
                addresses = Address.objects.filter(user=user).order_by('-is_default', '-created_at')

                messages.error(request, 'Please correct the errors in the new address form.')
                return render(request, 'cart/checkout.html', {
                    'checkout_items': checkout_items,
                    'addresses': addresses,
                    'address_form': addr_form,
                    'selected_address': None,
                    'subtotal': subtotal,
                    'delivery_charge': delivery_charge,
                    'total': total,
                    'estimated_delivery': estimated_delivery,
                    'mode': mode,
                })
        else:
            messages.error(request, 'Please select or add a delivery address.')
            return redirect('checkout')
    else:
        address = get_object_or_404(Address, pk=address_id, user=user)

    payment_method = request.POST.get('payment_method', 'cod')
    buy_now = request.session.get('buy_now')

    # Build order items list
    order_items_data = []

    if buy_now:
        product = get_object_or_404(
            Product, pk=buy_now['product_id'], is_active=True, is_sold=False
        )
        quantity = int(buy_now.get('quantity', 1))
        order_items_data.append({
            'product': product,
            'quantity': quantity,
            'price': product.price,
        })
    else:
        cart = Cart.objects.filter(user=user).first()
        if not cart or not cart.items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('cart')
        for item in cart.items.select_related('product').all():
            if item.product.is_active and not item.product.is_sold:
                order_items_data.append({
                    'product': item.product,
                    'quantity': item.quantity,
                    'price': item.product.price,
                })

    if not order_items_data:
        messages.error(request, 'No valid items to order.')
        return redirect('cart')

    subtotal = sum(i['price'] * i['quantity'] for i in order_items_data)
    delivery_charge = 0 if subtotal >= 499 else 49
    total = subtotal + delivery_charge

    # Snapshot address
    address_snapshot = (
        f"{address.full_name}, {address.phone}\n"
        f"{address.house_no}, {address.street}, {address.area}\n"
        f"{address.city}, {address.state} — {address.pincode}\n"
        f"Landmark: {address.landmark or 'N/A'}"
    )

    # Create Order
    order = Order.objects.create(
        buyer=user,
        address=address,
        address_snapshot=address_snapshot,
        status='pending',
        payment_method=payment_method,
        subtotal=subtotal,
        delivery_charge=delivery_charge,
        total=total,
    )

    # Create OrderItems
    for item_data in order_items_data:
        product = item_data['product']
        primary_image = product.images.filter(is_primary=True).first() or product.images.first()
        OrderItem.objects.create(
            order=order,
            product=product,
            seller=product.seller,
            title=product.title,
            price=item_data['price'],
            image_url=primary_image.image_url if primary_image else '',
            quantity=item_data['quantity'],
        )
        product.is_sold = True
        product.save()

    # Clear cart or buy_now session
    if buy_now:
        request.session.pop('buy_now', None)
    else:
        CartItem.objects.filter(cart__user=user).delete()

    # Send buyer notification
    Notification.objects.create(
        user=user,
        notification_type='order',
        title='Order Placed Successfully! 🎉',
        message=f'Your order #{order.short_id} has been placed. '
                f'Estimated delivery: {order.estimated_delivery.strftime("%d %b %Y")}.',
        link=f'/orders/{order.pk}/',
        icon='📦',
    )

    messages.success(request, f'Order #{order.short_id} placed successfully!')
    return redirect('order_confirmation', pk=order.pk)


# ─────────────────────────────────────────────────
# ORDER CONFIRMATION
# ─────────────────────────────────────────────────

@login_required
def order_confirmation_view(request, pk):
    """Order confirmation page — shown right after placing an order."""
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    order_items = order.items.select_related('product').all()

    return render(request, 'cart/order_confirmation.html', {
        'order': order,
        'order_items': order_items,
        'estimated_delivery': order.estimated_delivery,
    })


# ─────────────────────────────────────────────────
# ORDER LIST (MY ORDERS)
# ─────────────────────────────────────────────────

@login_required
def order_list_view(request):
    """My Orders — Amazon-style order history."""
    status_filter = request.GET.get('status', '')
    orders = Order.objects.filter(buyer=request.user).prefetch_related('items__product')

    if status_filter:
        orders = orders.filter(status=status_filter)

    paginator = Paginator(orders, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/orders.html', {
        'orders': page_obj,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES,
    })


# ─────────────────────────────────────────────────
# ORDER DETAIL + TRACKING
# ─────────────────────────────────────────────────

@login_required
def order_detail_view(request, pk):
    """Full order detail with visual status tracker."""
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    order_items = order.items.select_related('product', 'seller').all()
    return_requests = order.return_requests.all()

    # Build progress steps for tracker
    progress_steps = [
        {'key': 'pending', 'label': 'Order Placed', 'icon': '📦'},
        {'key': 'confirmed', 'label': 'Confirmed', 'icon': '✅'},
        {'key': 'processing', 'label': 'Packed', 'icon': '📫'},
        {'key': 'shipped', 'label': 'Shipped', 'icon': '🚚'},
        {'key': 'out_for_delivery', 'label': 'Out for Delivery', 'icon': '🛵'},
        {'key': 'delivered', 'label': 'Delivered', 'icon': '🏠'},
    ]

    current_step = order.status_step  # -1 if cancelled

    for i, step in enumerate(progress_steps):
        if current_step < 0:  # cancelled
            step['state'] = 'cancelled'
        elif i < current_step:
            step['state'] = 'completed'
        elif i == current_step:
            step['state'] = 'active'
        else:
            step['state'] = 'pending'

    return render(request, 'cart/order_detail.html', {
        'order': order,
        'order_items': order_items,
        'return_requests': return_requests,
        'progress_steps': progress_steps,
        'is_cancelled': order.status == 'cancelled',
        'estimated_delivery': order.estimated_delivery,
    })


# ─────────────────────────────────────────────────
# CANCEL ORDER
# ─────────────────────────────────────────────────

@login_required
@require_POST
def cancel_order_view(request, pk):
    """Cancel an order if it's cancellable."""
    order = get_object_or_404(Order, pk=pk, buyer=request.user)

    if not order.is_cancellable:
        messages.error(request, 'This order cannot be cancelled anymore.')
        return redirect('order_detail', pk=pk)

    order.status = 'cancelled'
    order.save()

    # Revert products associated with order items to not sold
    for item in order.items.select_related('product').all():
        if item.product:
            item.product.is_sold = False
            item.product.save()

    Notification.objects.create(
        user=request.user,
        notification_type='order',
        title='Order Cancelled',
        message=f'Your order #{order.short_id} has been cancelled.',
        link=f'/orders/{order.pk}/',
        icon='❌',
    )

    messages.success(request, f'Order #{order.short_id} has been cancelled.')
    return redirect('order_detail', pk=pk)


@login_required
@require_POST
def seller_cancel_order_view(request, pk):
    """Cancel a sale/order item as a seller."""
    item = get_object_or_404(OrderItem, pk=pk, seller=request.user)
    order = item.order

    if order.status in ['cancelled', 'delivered']:
        messages.error(request, f'This order is already {order.status}.')
        return redirect('dashboard_sales')

    if item.product:
        item.product.is_sold = False
        item.product.save(update_fields=['is_sold'])

    order.status = 'cancelled'
    order.save()

    # Notify the buyer
    Notification.objects.create(
        user=order.buyer,
        notification_type='order',
        title='Order Cancelled by Seller',
        message=f'The seller has cancelled your order #{order.short_id} for "{item.title}".',
        link=f'/orders/{order.pk}/',
        icon='❌',
    )

    # Notify the seller
    Notification.objects.create(
        user=request.user,
        notification_type='order',
        title='Sale Cancelled',
        message=f'You have successfully cancelled the sale for "{item.title}" in order #{order.short_id}.',
        link=f'/orders/{order.pk}/',
        icon='❌',
    )

    messages.success(request, f'You have cancelled the sale for "{item.title}". The item is now back in the store.')
    return redirect('dashboard_sales')


# ─────────────────────────────────────────────────
# REORDER
# ─────────────────────────────────────────────────

@login_required
@require_POST
def reorder_view(request, pk):
    """Add all items from a past order back to cart."""
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    added, skipped = 0, 0

    for item in order.items.select_related('product').all():
        if item.product and item.product.is_active:
            # Force availability for reorder testing
            if item.product.is_sold:
                item.product.is_sold = False
                item.product.save(update_fields=['is_sold'])

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=item.product,
                defaults={'quantity': item.quantity},
            )
            if not created:
                cart_item.quantity = min(cart_item.quantity + item.quantity, 10)
                cart_item.save()
            added += 1
        else:
            skipped += 1

    if added:
        messages.success(request, f'{added} item(s) added to cart.')
    if skipped:
        messages.warning(request, f'{skipped} item(s) skipped (unavailable).')

    return redirect('cart')


# ─────────────────────────────────────────────────
# RETURN REQUEST
# ─────────────────────────────────────────────────

@login_required
def return_request_view(request, order_pk, item_pk):
    """Submit a return/exchange/replacement request."""
    order = get_object_or_404(Order, pk=order_pk, buyer=request.user)
    order_item = get_object_or_404(OrderItem, pk=item_pk, order=order)

    if not order.is_returnable:
        messages.error(request, 'Returns are only available for delivered orders.')
        return redirect('order_detail', pk=order_pk)

    # Check if already requested
    if ReturnRequest.objects.filter(order_item=order_item).exists():
        messages.info(request, 'A return request already exists for this item.')
        return redirect('order_detail', pk=order_pk)

    if request.method == 'POST':
        form = ReturnRequestForm(request.POST)
        if form.is_valid():
            ret = form.save(commit=False)
            ret.order = order
            ret.order_item = order_item
            ret.save()

            order.status = 'return_requested'
            order.save()

            Notification.objects.create(
                user=request.user,
                notification_type='order',
                title='Return Request Submitted',
                message=f'Your return request for "{order_item.title}" is under review.',
                link=f'/orders/{order.pk}/',
                icon='🔄',
            )

            messages.success(request, 'Return request submitted successfully.')
            return redirect('order_detail', pk=order_pk)
    else:
        form = ReturnRequestForm()

    return render(request, 'cart/return_request.html', {
        'form': form,
        'order': order,
        'order_item': order_item,
    })


# ─────────────────────────────────────────────────
# ADDRESS MANAGEMENT (Dashboard)
# ─────────────────────────────────────────────────

@login_required
def addresses_view(request):
    """List all saved addresses."""
    addresses = Address.objects.filter(user=request.user)
    form = AddressForm()
    return render(request, 'dashboard/addresses.html', {
        'addresses': addresses,
        'form': form,
    })


@login_required
def add_address_view(request):
    """Add a new address."""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully.')
            return redirect('dashboard_addresses')
    else:
        form = AddressForm()
    return render(request, 'dashboard/addresses.html', {
        'addresses': Address.objects.filter(user=request.user),
        'form': form,
        'show_form': True,
    })


@login_required
def edit_address_view(request, pk):
    """Edit an existing address."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('dashboard_addresses')
    else:
        form = AddressForm(instance=address)
    return render(request, 'dashboard/addresses.html', {
        'addresses': Address.objects.filter(user=request.user),
        'form': form,
        'edit_address': address,
        'show_form': True,
    })


@login_required
@require_POST
def delete_address_view(request, pk):
    """Delete an address."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted.')
    return redirect('dashboard_addresses')


@login_required
@require_POST
def set_default_address_view(request, pk):
    """Set an address as default."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, 'Default address updated.')
    return redirect('dashboard_addresses')
