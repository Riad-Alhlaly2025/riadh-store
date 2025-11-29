from django.apps import apps
from typing import Any, Dict


def notifications_processor(request: Any) -> Dict[str, int]:
    """
    Context processor to add unread notifications count to all templates
    """
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            Notification = apps.get_model('store', 'Notification')
            unread_count = Notification.objects.filter(
                user=request.user, 
                is_read=False
            ).count()
            return {'unread_notifications_count': unread_count}
        except Exception:
            # Return default value if there's any database error
            return {'unread_notifications_count': 0}
    return {'unread_notifications_count': 0}


def cart_processor(request: Any) -> Dict[str, int]:
    """
    Context processor to add cart count to all templates
    """
    cart = request.session.get('cart', {})
    # Convert string values to integers before summing
    try:
        cart_count = sum(int(quantity) for quantity in cart.values())
    except (ValueError, TypeError):
        cart_count = 0
    return {'cart_count': cart_count}