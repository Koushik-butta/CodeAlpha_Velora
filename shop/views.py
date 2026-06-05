from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, Http404
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST

from shop.models import (
    Product, Category, ProductImage,
    Wishlist, RecentlyViewed, Review, SearchHistory,
)
from shop.forms import ProductForm, ReviewForm
from notifications.models import Notification

User = get_user_model()

from django.conf import settings
from core.integrations import upload_image

def is_cloudinary_available():
    """Dynamically determine if Cloudinary credentials are configured, with a runtime file fallback."""
    if settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'):
        return True
    try:
        from pathlib import Path
        import environ
        env_file = Path(settings.BASE_DIR) / '.env'
        if env_file.exists():
            env = environ.Env()
            env.read_env(env_file, overwrite=True)
            cloud_name = env.str('CLOUDINARY_CLOUD_NAME', default='')
            if cloud_name:
                settings.CLOUDINARY_STORAGE['CLOUD_NAME'] = cloud_name
                settings.CLOUDINARY_STORAGE['API_KEY'] = str(env('CLOUDINARY_API_KEY', default=''))
                settings.CLOUDINARY_STORAGE['API_SECRET'] = env('CLOUDINARY_API_SECRET', default='')
                return True
    except Exception:
        pass
    return False


# ──────────────────────────────────────────────────────────────
# HOME / LANDING
# ──────────────────────────────────────────────────────────────

def home_view(request):
    """Landing page for unauthenticated users; redirect to dashboard if logged in."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    categories = Category.get_all_active()
    featured_products = Product.objects.filter(
        is_active=True, is_sold=False
    ).select_related('category').prefetch_related('images')[:8]

    stats_products = Product.objects.filter(is_active=True, is_sold=False).count()
    stats_sellers = User.objects.filter(is_active=True).count()
    stats_cities = Product.objects.filter(is_active=True, is_sold=False).values('city').exclude(city='').distinct().count()
    stats_cities = max(stats_cities, 1)

    return render(request, 'landing.html', {
        'categories': categories,
        'featured_products': featured_products,
        'stats_products': stats_products,
        'stats_sellers': stats_sellers,
        'stats_cities': stats_cities,
    })


# ──────────────────────────────────────────────────────────────
# PRODUCT LIST / BROWSE
# ──────────────────────────────────────────────────────────────

def product_list_view(request):
    """Browse all products with filtering and sorting."""
    products_qs = Product.objects.filter(is_active=True, is_sold=False).select_related(
        'category', 'seller'
    ).prefetch_related('images')

    categories = Category.get_all_active()

    # ── Filters ────────────────────────────────────────────────
    query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()
    condition = request.GET.get('condition', '').strip()
    listing_type = request.GET.get('type', request.GET.get('listing_type', '')).strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    city = request.GET.get('city', '').strip()
    sort = request.GET.get('sort', 'featured').strip()

    if query:
        products_qs = products_qs.filter(
            Q(title__icontains=query) |
            Q(brand__icontains=query) |
            Q(model_name__icontains=query) |
            Q(city__icontains=query) |
            Q(state__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    if selected_category:
        products_qs = products_qs.filter(category__slug=selected_category)

    if condition:
        products_qs = products_qs.filter(condition=condition)

    if listing_type:
        if listing_type == 'buy':
            products_qs = products_qs.filter(listing_type__in=['buy', 'sell'])
        else:
            products_qs = products_qs.filter(listing_type=listing_type)

    if city:
        products_qs = products_qs.filter(city__icontains=city)

    try:
        if min_price:
            products_qs = products_qs.filter(price__gte=float(min_price))
        if max_price:
            products_qs = products_qs.filter(price__lte=float(max_price))
    except ValueError:
        pass

    # ── Sorting ────────────────────────────────────────────────
    sort_map = {
        'featured': ('-is_featured', '-created_at'),
        'newest': ('-created_at',),
        '-created_at': ('-created_at',),
        'oldest': ('created_at',),
        'created_at': ('created_at',),
        'price_asc': ('price',),
        'price': ('price',),
        'price_desc': ('-price',),
        '-price': ('-price',),
        'most_viewed': ('-views_count',),
        '-views_count': ('-views_count',),
    }
    ordering = sort_map.get(sort, ('-is_featured', '-created_at'))
    products_qs = products_qs.order_by(*ordering)

    # ── Pagination ─────────────────────────────────────────────
    paginator = Paginator(products_qs, 12)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    has_any_products = Product.objects.filter(is_active=True, is_sold=False).exists()

    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist_product_ids = list(
            Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    return render(request, 'shop/listing.html', {
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'sort': sort,
        'query': query,
        'condition': condition,
        'listing_type': listing_type,
        'min_price': min_price,
        'max_price': max_price,
        'city': city,
        'has_any_products': has_any_products,
        'wishlist_product_ids': wishlist_product_ids,
    })


# ──────────────────────────────────────────────────────────────
# PRODUCT DETAIL
# ──────────────────────────────────────────────────────────────

def product_detail_view(request, slug):
    """Show full product detail page. Increment view count, track recently viewed."""
    product = get_object_or_404(Product, slug=slug)

    # Draft product validation: only allow the seller or the admin to view it
    if not product.is_active:
        if not (request.user.is_authenticated and (request.user == product.seller or request.user.email == 'b.kowshik2007@gmail.com')):
            raise Http404("Product not found or in draft mode.")

    # Increment views atomically
    Product.objects.filter(pk=product.pk).update(views_count=product.views_count + 1)
    product.refresh_from_db()

    # Track recently viewed for authenticated users
    if request.user.is_authenticated:
        RecentlyViewed.objects.update_or_create(
            user=request.user,
            product=product,
        )

    # Related products (same category, not the current product)
    related_products = Product.objects.filter(
        is_active=True,
        is_sold=False,
        category=product.category,
    ).exclude(pk=product.pk).prefetch_related('images')[:6]

    # Reviews
    reviews = product.reviews.select_related('reviewer').order_by('-created_at')
    review_form = ReviewForm()

    # Wishlist / cart status
    in_wishlist = False
    in_cart = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
        try:
            from cart.models import Cart
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                in_cart = cart.items.filter(product=product).exists()
        except Exception:
            pass

    return render(request, 'shop/detail.html', {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'review_form': review_form,
        'in_wishlist': in_wishlist,
        'in_cart': in_cart,
    })


# ──────────────────────────────────────────────────────────────
# SELL / CREATE PRODUCT
# ──────────────────────────────────────────────────────────────

@login_required
def sell_product_view(request):
    """Create a new product listing with Cloudinary image uploads."""
    categories = Category.get_all_active()
    form = ProductForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            if 'draft' in request.POST:
                product.is_active = False
            else:
                product.is_active = True
            product.save()

            # Handle up to 5 image uploads
            images = request.FILES.getlist('images')
            for idx, image_file in enumerate(images[:5]):
                image_url = ''
                public_id = ''
                if is_cloudinary_available():
                    try:
                        result = upload_image(
                            image_file,
                            folder='velora/products',
                        )
                        image_url = result['url']
                        public_id = result['public_id']
                    except Exception as e:
                        messages.warning(request, f'Failed to upload image "{image_file.name}" to Cloudinary: {str(e)}')
                        continue
                else:
                    messages.warning(request, 'Cloudinary storage setup is not available. Please verify settings.')
                    continue

                ProductImage.objects.create(
                    product=product,
                    image_url=image_url,
                    public_id=public_id,
                    is_primary=(idx == 0),
                    order=idx,
                )

            if 'draft' in request.POST:
                messages.success(request, f'"{product.title}" saved as draft successfully!')
                return redirect('dashboard_my_products')
            else:
                messages.success(request, f'"{product.title}" listed successfully!')
                next_url = request.GET.get('next', '')
                if next_url:
                    return redirect(next_url)
                return redirect('product_detail', slug=product.slug)
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'shop/sell.html', {
        'form': form,
        'categories': categories,
        'edit_mode': False,
        'product': None,
    })


# ──────────────────────────────────────────────────────────────
# EDIT PRODUCT
# ──────────────────────────────────────────────────────────────

@login_required
def edit_product_view(request, slug):
    """Edit an existing product listing owned by the current user."""
    if request.user.email == 'b.kowshik2007@gmail.com':
        product = get_object_or_404(Product, slug=slug)
    else:
        product = get_object_or_404(Product, slug=slug, seller=request.user)
    categories = Category.get_all_active()
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)

    if request.method == 'POST':
        if form.is_valid():
            product = form.save(commit=False)
            if 'draft' in request.POST:
                product.is_active = False
            else:
                product.is_active = True
            product.save()

            # Handle additional image uploads
            new_images = request.FILES.getlist('images')
            existing_count = product.images.count()
            for idx, image_file in enumerate(new_images[: max(0, 5 - existing_count)]):
                if is_cloudinary_available():
                    try:
                        result = upload_image(
                            image_file,
                            folder='velora/products',
                        )
                        image_url = result['url']
                        public_id = result['public_id']
                    except Exception as e:
                        messages.warning(request, f'Failed to upload image "{image_file.name}" to Cloudinary: {str(e)}')
                        continue
                else:
                    messages.warning(request, 'Cloudinary storage setup is not available. Please verify settings.')
                    continue

                is_primary = existing_count == 0 and idx == 0
                ProductImage.objects.create(
                    product=product,
                    image_url=image_url,
                    public_id=public_id,
                    is_primary=is_primary,
                    order=existing_count + idx,
                )

            if 'draft' in request.POST:
                messages.success(request, f'"{product.title}" saved as draft successfully!')
                return redirect('dashboard_my_products')
            else:
                messages.success(request, f'"{product.title}" updated successfully!')
                return redirect('product_detail', slug=product.slug)
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'shop/sell.html', {
        'form': form,
        'categories': categories,
        'edit_mode': True,
        'product': product,
    })


# ──────────────────────────────────────────────────────────────
# DELETE PRODUCT
# ──────────────────────────────────────────────────────────────

@login_required
def delete_product_view(request, slug):
    """Delete a product owned by the current user (POST only)."""
    if request.user.email == 'b.kowshik2007@gmail.com':
        product = get_object_or_404(Product, slug=slug)
    else:
        product = get_object_or_404(Product, slug=slug, seller=request.user)

    if request.method == 'POST':
        title = product.title
        product.delete()
        messages.success(request, f'"{title}" has been deleted.')
        return redirect('dashboard_my_products')

    return render(request, 'shop/confirm_delete.html', {'product': product})


# ──────────────────────────────────────────────────────────────
# TOGGLE WISHLIST (AJAX-friendly)
# ──────────────────────────────────────────────────────────────

@login_required
def toggle_wishlist_view(request, pk):
    """Add or remove a product from the user's wishlist. Returns JSON."""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    wishlist_entry, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product,
    )

    if not created:
        # Already wishlisted — remove it
        wishlist_entry.delete()
        product.wishlist_count = max(0, product.wishlist_count - 1)
        product.save(update_fields=['wishlist_count'])
        added = False
    else:
        product.wishlist_count += 1
        product.save(update_fields=['wishlist_count'])
        added = True

    count = product.wishlist_count
    return JsonResponse({'added': added, 'count': count})


# ──────────────────────────────────────────────────────────────
# MARK SOLD / RESERVED
# ──────────────────────────────────────────────────────────────

@login_required
def mark_sold_view(request, slug):
    """Mark a product as sold."""
    if request.user.email == 'b.kowshik2007@gmail.com':
        product = get_object_or_404(Product, slug=slug)
    else:
        product = get_object_or_404(Product, slug=slug, seller=request.user)
    product.is_sold = True
    product.save(update_fields=['is_sold'])
    messages.success(request, f'"{product.title}" marked as sold.')
    return redirect('dashboard_my_products')


@login_required
def mark_reserved_view(request, slug):
    """Mark a product as reserved (inactive but not sold)."""
    if request.user.email == 'b.kowshik2007@gmail.com':
        product = get_object_or_404(Product, slug=slug)
    else:
        product = get_object_or_404(Product, slug=slug, seller=request.user)
    product.is_active = not product.is_active
    product.save(update_fields=['is_active'])
    status = 'active' if product.is_active else 'reserved/inactive'
    messages.success(request, f'"{product.title}" is now {status}.')
    return redirect('dashboard_my_products')


# ──────────────────────────────────────────────────────────────
# SELLER PROFILE
# ──────────────────────────────────────────────────────────────

def seller_profile_view(request, user_id):
    """Public seller profile showing their active listings and reviews."""
    seller = get_object_or_404(User, pk=user_id, is_active=True)
    seller_profile = getattr(seller, 'profile', None)

    products = Product.objects.filter(
        seller=seller,
        is_active=True,
        is_sold=False,
    ).prefetch_related('images').order_by('-created_at')

    # Aggregate reviews for products sold by this seller
    reviews = Review.objects.filter(
        product__seller=seller
    ).select_related('reviewer', 'product').order_by('-created_at')[:20]

    return render(request, 'shop/seller_profile.html', {
        'seller': seller,
        'seller_profile': seller_profile,
        'products': products,
        'reviews': reviews,
    })


# ──────────────────────────────────────────────────────────────
# SEARCH
# ──────────────────────────────────────────────────────────────

def search_suggestions_view(request):
    """API endpoint for live search suggestions/autocomplete."""
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()

    if not query:
        return JsonResponse({'suggestions': []})

    products_qs = Product.objects.filter(is_active=True, is_sold=False).select_related('category')

    if category_slug:
        products_qs = products_qs.filter(category__slug=category_slug)

    products_qs = products_qs.filter(
        Q(title__icontains=query) |
        Q(brand__icontains=query) |
        Q(model_name__icontains=query) |
        Q(city__icontains=query) |
        Q(state__icontains=query) |
        Q(category__name__icontains=query)
    )[:6]

    suggestions = []
    for p in products_qs:
        primary_image = p.images.filter(is_primary=True).first() or p.images.first()
        suggestions.append({
            'title': p.title,
            'price': float(p.price),
            'slug': p.slug,
            'image_url': primary_image.image_url if primary_image else '',
            'category': p.category.name if p.category else 'Other',
        })

    return JsonResponse({'suggestions': suggestions})


def search_view(request):
    """Full-text product search with optional filters."""
    query = request.GET.get('q', '').strip()

    products_qs = Product.objects.filter(is_active=True, is_sold=False).select_related(
        'category', 'seller'
    ).prefetch_related('images')

    if query:
        products_qs = products_qs.filter(
            Q(title__icontains=query) |
            Q(brand__icontains=query) |
            Q(model_name__icontains=query) |
            Q(city__icontains=query) |
            Q(state__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

        # Save to SearchHistory for authenticated users
        if request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, query=query)

    # Optional additional filters
    condition = request.GET.get('condition', '').strip()
    listing_type = request.GET.get('listing_type', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    city = request.GET.get('city', '').strip()
    category_slug = request.GET.get('category', '').strip()

    if condition:
        products_qs = products_qs.filter(condition=condition)
    if listing_type:
        if listing_type == 'buy':
            products_qs = products_qs.filter(listing_type__in=['buy', 'sell'])
        else:
            products_qs = products_qs.filter(listing_type=listing_type)
    if city:
        products_qs = products_qs.filter(city__icontains=city)
    if category_slug:
        products_qs = products_qs.filter(category__slug=category_slug)
    try:
        if min_price:
            products_qs = products_qs.filter(price__gte=float(min_price))
        if max_price:
            products_qs = products_qs.filter(price__lte=float(max_price))
    except ValueError:
        pass

    products_qs = products_qs.order_by('-created_at')

    paginator = Paginator(products_qs, 12)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist_product_ids = list(
            Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    return render(request, 'search/results.html', {
        'products': page_obj.object_list,
        'query': query,
        'page_obj': page_obj,
        'condition': condition,
        'listing_type': listing_type,
        'min_price': min_price,
        'max_price': max_price,
        'city': city,
        'category_slug': category_slug,
        'wishlist_product_ids': wishlist_product_ids,
    })


# ──────────────────────────────────────────────────────────────
# REVIEW
# ──────────────────────────────────────────────────────────────

@login_required
def add_review_view(request, slug):
    """Submit a review for a product. One review per user per product."""
    product = get_object_or_404(Product, slug=slug, is_active=True)

    # Prevent reviewing own product
    if product.seller == request.user:
        messages.error(request, 'You cannot review your own listing.')
        return redirect('product_detail', slug=slug)

    # One review per product per user
    if Review.objects.filter(product=product, reviewer=request.user).exists():
        messages.warning(request, 'You have already reviewed this product.')
        return redirect('product_detail', slug=slug)

    form = ReviewForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.reviewer = request.user
            review.save()
            messages.success(request, 'Your review has been submitted. Thank you!')

            # Notify the seller
            Notification.create_for_user(
                user=product.seller,
                notification_type='review',
                title='New Review Received',
                message=f'{request.user.email} left a {review.rating}★ review on "{product.title}".',
                link=f'/products/{product.slug}/',
                icon='⭐',
            )
            return redirect('product_detail', slug=slug)
        else:
            messages.error(request, 'Please provide a valid rating.')
            return redirect('product_detail', slug=slug)

    return redirect('product_detail', slug=slug)


from django.db.models import F

def deals_view(request):
    """Deals page showing discounted, trending, viewed, recommended products and new arrivals."""
    # 1. Recently discounted products (original_price > price)
    discounted_products = Product.objects.filter(
        is_active=True,
        is_sold=False,
        original_price__isnull=False,
        original_price__gt=F('price')
    ).select_related('seller', 'category').prefetch_related('images').order_by('-updated_at')[:8]

    # 2. Trending products (ordered by wishlist count / views)
    trending_products = Product.objects.filter(
        is_active=True,
        is_sold=False
    ).select_related('seller', 'category').prefetch_related('images').order_by('-wishlist_count', '-views_count')[:8]

    # 3. Most viewed products
    most_viewed_products = Product.objects.filter(
        is_active=True,
        is_sold=False
    ).select_related('seller', 'category').prefetch_related('images').order_by('-views_count')[:8]

    # 4. Recommended products (Featured products or random)
    recommended_products = Product.objects.filter(
        is_active=True,
        is_sold=False,
        is_featured=True
    ).select_related('seller', 'category').prefetch_related('images').order_by('-created_at')[:8]

    if not recommended_products.exists():
        recommended_products = Product.objects.filter(
            is_active=True,
            is_sold=False
        ).select_related('seller', 'category').prefetch_related('images').order_by('?')[:8]

    # 5. New arrivals
    new_arrivals = Product.objects.filter(
        is_active=True,
        is_sold=False
    ).select_related('seller', 'category').prefetch_related('images').order_by('-created_at')[:8]

    return render(request, 'shop/deals.html', {
        'discounted_products': discounted_products,
        'trending_products': trending_products,
        'most_viewed_products': most_viewed_products,
        'recommended_products': recommended_products,
        'new_arrivals': new_arrivals,
    })