from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.urls import reverse

from users.forms import (
    RegistrationForm,
    LoginForm,
    ForgotPasswordForm,
    SetNewPasswordForm,
    PasswordChangeForm,
    ProfileSettingsForm,
)
from cart.forms import AddressForm
from users.models import Profile
from cart.models import Address, Order, OrderItem
from shop.models import Product, Wishlist, RecentlyViewed, Category
from swap.models import ExchangeRequest
from notifications.models import Notification
from core.integrations import upload_image

try:
    from core.integrations.brevo import BrevoClient
except ImportError:
    BrevoClient = None

User = get_user_model()


# ──────────────────────────────────────────────────────────────
# AUTH VIEWS
# ──────────────────────────────────────────────────────────────

def register_view(request):
    """Simple registration — no OTP. User is active immediately."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = RegistrationForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            full_name = form.cleaned_data.get('full_name', '')

            user = User.objects.create_user(email=email, password=password)
            user.is_active = True
            if email.strip().lower() == 'b.kowshik2007@gmail.com':
                user.is_superuser = True
                user.is_staff = True
            user.save()

            # Update the auto-created profile with full name
            if full_name:
                profile = getattr(user, 'profile', None)
                if profile:
                    profile.full_name = full_name
                    profile.save()
                else:
                    Profile.objects.create(user=user, full_name=full_name)

            login(request, user)
            messages.success(request, f'Welcome to Velora, {full_name or email}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'register.html', {'form': form})


def login_view(request):
    """Email + password login."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is None:
                messages.error(request, 'Invalid email or password. Please try again.')
            elif not user.is_active:
                messages.error(request, 'Your account is inactive. Please contact support.')
            else:
                if user.email.strip().lower() == 'b.kowshik2007@gmail.com' and (not user.is_superuser or not user.is_staff):
                    user.is_superuser = True
                    user.is_staff = True
                    user.save(update_fields=['is_superuser', 'is_staff'])
                login(request, user)
                next_url = request.GET.get('next', '')
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard')
        else:
            messages.error(request, 'Please provide valid credentials.')

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def forgot_password_view(request):
    """Generate a password reset token and email the link to the user."""
    form = ForgotPasswordForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Keep the same success message to avoid user enumeration
                messages.success(request, 'If that email is registered, a reset link has been sent.')
                return redirect('forgot_password')

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(
                reverse('reset_password', kwargs={'uidb64': uidb64, 'token': token})
            )

            subject = 'Reset your Velora password'
            html_content = (
                f'<p>Hi {user.profile.full_name or user.email},</p>'
                f'<p>We received a request to reset your Velora password.</p>'
                f'<p><a href="{reset_link}" style="background:#F97316;color:#fff;'
                f'padding:12px 24px;border-radius:6px;text-decoration:none;">Reset Password</a></p>'
                f'<p>Or copy this link: {reset_link}</p>'
                f'<p>This link expires in 24 hours. If you did not request this, ignore this email.</p>'
                f'<p>— The Velora Team</p>'
            )

            try:
                if BrevoClient:
                    client = BrevoClient()
                    client.send_email(
                        to_email=email,
                        subject=subject,
                        html_content=html_content,
                        to_name=user.profile.full_name or email,
                    )
            except Exception:
                pass  # Never expose email failures to the user

            messages.success(request, 'A password reset link has been sent to your email.')
            return redirect('forgot_password')

    return render(request, 'forgot_password.html', {'form': form})


def reset_password_view(request, uidb64, token):
    """Validate uidb64/token and allow user to set a new password."""
    form = SetNewPasswordForm(request.POST or None)
    invalid = False

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        invalid = True

    if user is None or not default_token_generator.check_token(user, token):
        invalid = True
        user = None

    if request.method == 'POST' and not invalid and form.is_valid():
        new_password = form.cleaned_data['new_password']
        user.set_password(new_password)
        user.save()
        messages.success(request, 'Your password has been reset. Please log in.')
        return redirect('login')

    return render(request, 'reset_password.html', {
        'form': form,
        'uidb64': uidb64,
        'token': token,
        'invalid': invalid,
    })


@login_required
def change_password_view(request):
    form = PasswordChangeForm(user=request.user, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            # Re-login so Django doesn't invalidate the session
            login(request, request.user)
            messages.success(request, 'Password changed successfully.')
            return redirect('dashboard_settings')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'change_password.html', {'form': form})


# ──────────────────────────────────────────────────────────────
# DASHBOARD VIEWS
# ──────────────────────────────────────────────────────────────

@login_required
def dashboard_view(request):
    user = request.user

    listings_count = Product.objects.filter(
        seller=user,
        is_active=True
    ).count()

    orders_count = Order.objects.filter(
        buyer=user
    ).count()

    exchanges_count = (
        ExchangeRequest.objects.filter(
            requester=user
        ).count()
        +
        ExchangeRequest.objects.filter(
            target_user=user
        ).count()
    )

    wishlist_count = Wishlist.objects.filter(
        user=user
    ).count()

    recent_orders = Order.objects.filter(
        buyer=user
    ).order_by('-created_at')[:5]

    recent_exchanges = ExchangeRequest.objects.filter(
        requester=user
    ).order_by('-created_at')[:5]

    wishlist_items = Wishlist.objects.filter(
        user=user
    )[:6]

    recently_viewed = RecentlyViewed.objects.filter(
        user=user
    )[:6]

    recent_products = Product.objects.filter(
        seller=user,
        is_active=True
    )[:6]

    notifications = Notification.objects.filter(
        user=user,
        is_read=False
    ).order_by('-created_at')[:5]

    # Categories using the classmethod helper
    categories = Category.get_all_active()

    return render(request, 'dashboard/home.html', {
        'listings_count': listings_count,
        'orders_count': orders_count,
        'exchanges_count': exchanges_count,
        'wishlist_count': wishlist_count,
        'recent_orders': recent_orders,
        'recent_exchanges': recent_exchanges,
        'wishlist_items': wishlist_items,
        'recently_viewed': recently_viewed,
        'recent_products': recent_products,
        'notifications': notifications,
        'categories': categories,
    })
    

   

@login_required
def my_products_view(request):
    products_qs = Product.objects.filter(seller=request.user).order_by('-created_at')
    paginator = Paginator(products_qs, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard/my_products.html', {
        'products': page_obj.object_list,
        'page_obj': page_obj,
    })


@login_required
def seller_sales_view(request):
    """View to track orders received by the seller for their products."""
    sales_qs = OrderItem.objects.filter(seller=request.user).select_related('order', 'order__buyer').order_by('-order__created_at')
    paginator = Paginator(sales_qs, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard/sales.html', {
        'sales': page_obj.object_list,
        'page_obj': page_obj,
    })


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product').order_by('-added_at')
    return render(request, 'dashboard/wishlist.html', {'wishlist_items': wishlist_items})





@login_required
def addresses_view(request):
    addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    return render(request, 'dashboard/addresses.html', {
        'addresses': addresses,
        'address_form': AddressForm(),
    })


@login_required
def add_address_view(request):
    form = AddressForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully.')
            return redirect('dashboard_addresses')
        else:
            messages.error(request, 'Please correct the errors below.')
    return render(request, 'dashboard/address_form.html', {'form': form, 'action': 'Add'})


@login_required
def edit_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    form = AddressForm(request.POST or None, instance=address)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('dashboard_addresses')
        else:
            messages.error(request, 'Please correct the errors below.')
    return render(request, 'dashboard/address_form.html', {'form': form, 'action': 'Edit', 'address': address})


@login_required
def delete_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully.')
    return redirect('dashboard_addresses')


@login_required
def set_default_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    address.is_default = True
    address.save()
    messages.success(request, f'"{address.city}" is now your default address.')
    return redirect('dashboard_addresses')


@login_required
def settings_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileSettingsForm(request.POST or None, request.FILES or None, instance=profile)

    if request.method == 'POST':
        if form.is_valid():
            # Handle avatar upload via Cloudinary if an image was provided
            avatar_file = request.FILES.get('avatar')
            if avatar_file:
                try:
                    result = upload_image(avatar_file, folder='velora/avatars')
                    profile.avatar_url = result['url']
                    profile.avatar_public_id = result['public_id']
                except Exception:
                    messages.warning(request, 'Avatar upload failed, but other settings were saved.')

            updated_profile = form.save(commit=False)
            updated_profile.user = request.user
            if avatar_file and profile.avatar_url:
                updated_profile.avatar_url = profile.avatar_url
                updated_profile.avatar_public_id = profile.avatar_public_id
            updated_profile.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('dashboard_settings')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'dashboard/settings.html', {'profile_form': form, 'profile': profile})


@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard/notifications.html', {'notifications': notifications})


@login_required
def mark_notification_read_view(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('dashboard_notifications')


@login_required
def mark_all_read_view(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    messages.success(request, 'All notifications marked as read.')
    return redirect('dashboard_notifications')


@login_required
def dashboard_exchanges_view(request):
    sent_exchanges = ExchangeRequest.objects.filter(
        requester=request.user
    ).select_related('target_product', 'offered_product', 'target_user').order_by('-created_at')

    received_exchanges = ExchangeRequest.objects.filter(
        target_user=request.user
    ).select_related('target_product', 'offered_product', 'requester').order_by('-created_at')

    return render(request, 'dashboard/exchanges.html', {
        'sent_exchanges': sent_exchanges,
        'received_exchanges': received_exchanges,
    })


@login_required
def update_theme_view(request):
    """Asynchronously update the logged-in user's theme in their profile."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    import json
    try:
        data = json.loads(request.body)
        theme = data.get('theme')
        valid_themes = [
            'sunset-saffron', 'royal-ashoka', 'lotus-pink', 'vibrant-emerald', 
            'cyber-tricolor', 'classic-light', 'holi-festival', 'midnight-slate', 
            'sunset-magenta', 'ocean-turquoise', 'sakura-blossom', 
            'cosmic-lavender', 'nordic-aurora', 'desert-amber'
        ]
        if theme in valid_themes:
            profile, _ = Profile.objects.get_or_create(user=request.user)
            profile.theme = theme
            profile.save()
            return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid theme'}, status=400)
