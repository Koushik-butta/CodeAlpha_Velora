from shop.models import Category, Wishlist
from cart.models import Cart
from notifications.models import Notification

def velora_global_context(request):
    """Provides global context variables for Velora layout."""
    categories = Category.get_all_active()
    
    cart_item_count = 0
    wishlist_item_count = 0
    unread_notifications_count = 0
    
    if request.user.is_authenticated:
        # Cart item count
        try:
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                cart_item_count = cart.items.count()
        except Exception:
            pass
            
        # Wishlist item count
        try:
            wishlist_item_count = Wishlist.objects.filter(user=request.user).count()
        except Exception:
            pass
            
        # Unread notifications count
        try:
            unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
        except Exception:
            pass
            
    return {
        'global_categories': categories,
        'cart_item_count': cart_item_count,
        'wishlist_item_count': wishlist_item_count,
        'unread_notifications_count': unread_notifications_count,
    }
