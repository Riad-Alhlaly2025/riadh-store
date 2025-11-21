"""
Coupon utility functions for the e-commerce platform
"""
from decimal import Decimal
from django.apps import apps
from django.utils import timezone


def apply_coupon_to_order(order, coupon_code, user=None):
    """
    Apply a coupon to an order and return the discount amount
    
    Args:
        order: Order object
        coupon_code: String representing the coupon code
        user: Optional user object for validation
    
    Returns:
        Decimal: Discount amount or 0 if coupon is invalid
    """
    try:
        Coupon = apps.get_model('store', 'Coupon')
        
        # Get coupon
        coupon = Coupon.objects.get(
            code=coupon_code,
            active=True,
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now()
        )
        
        # Check usage limit
        if coupon.usage_limit and coupon.times_used >= coupon.usage_limit:
            return Decimal('0.00')
        
        # Check minimum amount requirement
        if order.total_amount < coupon.minimum_amount:
            return Decimal('0.00')
        
        # Calculate discount
        discount_amount = Decimal('0.00')
        if coupon.discount_type == 'percentage':
            discount_amount = (order.total_amount * coupon.discount_value / 100).quantize(Decimal('0.01'))
        else:  # fixed amount
            discount_amount = min(coupon.discount_value, order.total_amount)
        
        # Update coupon usage count
        coupon.times_used += 1
        coupon.save()
        
        return discount_amount
        
    except Coupon.DoesNotExist:
        return Decimal('0.00')
    except Exception:
        return Decimal('0.00')


def calculate_loyalty_discount(order, user):
    """
    Calculate loyalty discount for an order
    
    Args:
        order: Order object
        user: User object
    
    Returns:
        Decimal: Discount amount from loyalty rewards
    """
    try:
        LoyaltyProgram = apps.get_model('store', 'LoyaltyProgram')
        
        # Get user's loyalty program
        loyalty_program = LoyaltyProgram.objects.get(user=user)
        
        # Calculate discount based on loyalty level
        # This is a simplified implementation - in a real system, you might have more complex rules
        discount_percentage = 0
        if loyalty_program.level == 'silver':
            discount_percentage = 5
        elif loyalty_program.level == 'gold':
            discount_percentage = 10
        elif loyalty_program.level == 'platinum':
            discount_percentage = 15
            
        if discount_percentage > 0:
            discount_amount = (order.total_amount * discount_percentage / 100).quantize(Decimal('0.01'))
            return discount_amount
            
        return Decimal('0.00')
        
    except LoyaltyProgram.DoesNotExist:
        return Decimal('0.00')
    except Exception:
        return Decimal('0.00')


def get_user_rewards(user):
    """
    Get user's available rewards
    
    Args:
        user: User object
    
    Returns:
        List: Available rewards
    """
    try:
        LoyaltyProgram = apps.get_model('store', 'LoyaltyProgram')
        LoyaltyReward = apps.get_model('store', 'LoyaltyReward')
        
        # Get user's loyalty program
        loyalty_program = LoyaltyProgram.objects.get(user=user)
        
        # Get rewards user can afford
        available_rewards = LoyaltyReward.objects.filter(
            active=True,
            points_required__lte=loyalty_program.points
        )
        
        return list(available_rewards)
        
    except (LoyaltyProgram.DoesNotExist, Exception):
        return []


def calculate_earned_points(order, user):
    """
    Calculate loyalty points earned from an order
    
    Args:
        order: Order object
        user: User object
    
    Returns:
        int: Points earned
    """
    try:
        # Simple calculation: 1 point per 10 SAR spent
        points = int(order.total_amount // 10)
        return points
    except Exception:
        return 0


def update_user_loyalty_points(user, points):
    """
    Update user's loyalty points
    
    Args:
        user: User object
        points: Points to add (can be negative)
    """
    try:
        LoyaltyProgram = apps.get_model('store', 'LoyaltyProgram')
        
        # Get or create loyalty program for user
        loyalty_program, created = LoyaltyProgram.objects.get_or_create(
            user=user,
            defaults={
                'points': 0,
                'level': 'bronze',
                'total_spent': 0
            }
        )
        
        # Update points
        loyalty_program.points += points
        if loyalty_program.points < 0:
            loyalty_program.points = 0
            
        # Update total spent
        # This would typically be done when the order is completed
        
        # Update level based on points
        if loyalty_program.points >= 1000:
            loyalty_program.level = 'platinum'
        elif loyalty_program.points >= 500:
            loyalty_program.level = 'gold'
        elif loyalty_program.points >= 100:
            loyalty_program.level = 'silver'
        else:
            loyalty_program.level = 'bronze'
            
        loyalty_program.save()
        
    except Exception:
        pass  # Silently fail to avoid breaking the checkout process