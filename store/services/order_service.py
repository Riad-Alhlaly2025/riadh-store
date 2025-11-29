"""
Order service module
Contains business logic for order management
"""

from django.apps import apps
from django.db import transaction
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class OrderService:
    """Service class for order-related operations"""
    
    @staticmethod
    @transaction.atomic
    def create_order(user, cart_items, shipping_address, payment_method='cash_on_delivery'):
        """
        Create an order from cart items
        
        Args:
            user: Django User object
            cart_items: List of cart items
            shipping_address: Dictionary with address details
            payment_method: String representing payment method
            
        Returns:
            Order object
        """
        Order = apps.get_model('store', 'Order')
        OrderItem = apps.get_model('store', 'OrderItem')
        Product = apps.get_model('store', 'Product')
        
        try:
            # Calculate total amount
            total_amount = sum(item['total_price'] for item in cart_items)
            
            # Create order
            order = Order.objects.create(
                user=user,
                total_amount=total_amount,
                shipping_address=f"{shipping_address.get('address', '')}, "
                               f"{shipping_address.get('city', '')}, "
                               f"{shipping_address.get('state', '')}",
                phone_number=shipping_address.get('phone', ''),
                status='pending',
                payment_method=payment_method
            )
            
            # Create order items and update stock
            for item in cart_items:
                product = item['product']
                
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=product.price
                )
                
                # Update product stock
                product.stock_quantity -= item['quantity']
                product.save()
            
            logger.info(f"Order {order.id} created successfully for user {user.username}")
            return order
            
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            raise
    
    @staticmethod
    def update_order_status(order_id, new_status, user=None):
        """
        Update order status
        
        Args:
            order_id: ID of the order to update
            new_status: New status for the order
            user: User performing the update (optional)
            
        Returns:
            Updated Order object
        """
        Order = apps.get_model('store', 'Order')
        
        try:
            order = Order.objects.get(id=order_id)
            
            # Validate status transition
            if not OrderService._is_valid_status_transition(order.status, new_status):
                raise ValueError(f"Invalid status transition from {order.status} to {new_status}")
            
            # Update status
            old_status = order.status
            order.status = new_status
            order.save()
            
            logger.info(f"Order {order.id} status updated from {old_status} to {new_status}")
            return order
            
        except Order.DoesNotExist:
            logger.error(f"Order {order_id} not found")
            raise
        except Exception as e:
            logger.error(f"Error updating order status: {str(e)}")
            raise
    
    @staticmethod
    def _is_valid_status_transition(current_status, new_status):
        """
        Validate if a status transition is allowed
        
        Args:
            current_status: Current order status
            new_status: Proposed new status
            
        Returns:
            Boolean indicating if transition is valid
        """
        # Define valid status transitions
        valid_transitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'returned'],
            'delivered': ['returned'],
            'cancelled': [],
            'returned': []
        }
        
        return new_status in valid_transitions.get(current_status, [])
    
    @staticmethod
    def get_user_orders(user):
        """
        Get all orders for a user
        
        Args:
            user: Django User object
            
        Returns:
            QuerySet of orders
        """
        Order = apps.get_model('store', 'Order')
        return Order.objects.filter(user=user).order_by('-created_at')
    
    @staticmethod
    def get_order_statistics():
        """
        Get order statistics for dashboard
        
        Returns:
            Dictionary with order statistics
        """
        Order = apps.get_model('store', 'Order')
        
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        processing_orders = Order.objects.filter(status='processing').count()
        shipped_orders = Order.objects.filter(status='shipped').count()
        delivered_orders = Order.objects.filter(status='delivered').count()
        cancelled_orders = Order.objects.filter(status='cancelled').count()
        returned_orders = Order.objects.filter(status='returned').count()
        
        # Calculate revenue
        total_revenue = Order.objects.filter(status='delivered').aggregate(
            total=models.Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        return {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'processing_orders': processing_orders,
            'shipped_orders': shipped_orders,
            'delivered_orders': delivered_orders,
            'cancelled_orders': cancelled_orders,
            'returned_orders': returned_orders,
            'total_revenue': total_revenue
        }

# Singleton instance
order_service = OrderService()