from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.apps import apps
from decimal import Decimal

# Store the original status before saving
@receiver(pre_save, sender='store.Order')
def store_original_status(sender, instance, **kwargs):
    Order = apps.get_model('store', 'Order')
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._original_status = old_instance.status
        except Order.DoesNotExist:
            instance._original_status = instance.status
    else:
        instance._original_status = instance.status


@receiver(post_save, sender='store.Order')
def send_order_notification(sender, instance, created, **kwargs):
    """
    Send notification when order status changes or when order is created
    """
    Notification = apps.get_model('store', 'Notification')
    if created:
        # Send notification for new order
        try:
            Notification.objects.create(
                user=instance.user,
                order=instance,
                notification_type='order_created',
                message=f'تم إنشاء طلبك بنجاح برقم #{instance.pk}'
            )
        except Exception:
            # Silently ignore notification creation errors to avoid disrupting order creation
            pass
    else:
        # Check if status has changed using the stored original status
        if hasattr(instance, '_original_status') and instance._original_status != instance.status:
            # Status has changed, send notification
            status_messages = {
                'processing': 'طلبك قيد المعالجة الآن',
                'shipped': 'تم شحن طلبك',
                'delivered': 'تم تسليم طلبك',
                'cancelled': 'تم إلغاء طلبك'
            }
            
            message = status_messages.get(instance.status, f'تغيرت حالة طلبك إلى: {instance.get_status_display()}')
            
            notification_types = {
                'processing': 'order_status_changed',
                'shipped': 'order_shipped',
                'delivered': 'order_delivered',
                'cancelled': 'order_status_changed'
            }
            
            notification_type = notification_types.get(instance.status, 'order_status_changed')
            
            try:
                Notification.objects.create(
                    user=instance.user,
                    order=instance,
                    notification_type=notification_type,
                    message=message
                )
            except Exception:
                # Silently ignore notification creation errors to avoid disrupting order updates
                pass


def get_commission_rate(user_role, product_category=None):
    """
    Get commission rate based on user role and product category
    """
    CommissionSettings = apps.get_model('store', 'CommissionSettings')
    
    # Try to get specific category rate first
    if product_category:
        try:
            settings = CommissionSettings.objects.get(
                user_role=user_role,
                product_category=product_category,
                is_active=True
            )
            return settings.commission_rate
        except CommissionSettings.DoesNotExist:
            pass
    
    # Try to get general rate for the user role
    try:
        settings = CommissionSettings.objects.get(
            user_role=user_role,
            product_category=None,
            is_active=True
        )
        return settings.commission_rate
    except CommissionSettings.DoesNotExist:
        pass
    
    # Return default rates if no settings found
    if user_role == 'seller':
        return Decimal('10.00')
    elif user_role == 'buyer':
        return Decimal('2.00')
    else:
        return Decimal('0.00')


@receiver(post_save, sender='store.Order')
def calculate_commission_on_delivery(sender, instance, created, **kwargs):
    """
    Automatically calculate and create commission when order status changes to 'delivered'
    """
    # Only process when updating an existing order (not creating)
    if not created:
        # Check if status has changed using the stored original status
        if hasattr(instance, '_original_status') and instance._original_status != instance.status:
            # Check if the new status is 'delivered' (completed)
            if instance.status == 'delivered':
                # Import models
                Commission = apps.get_model('store', 'Commission')
                OrderItem = apps.get_model('store', 'OrderItem')
                UserProfile = apps.get_model('store', 'UserProfile')
                Product = apps.get_model('store', 'Product')
                Notification = apps.get_model('store', 'Notification')
                
                try:
                    # Check if commissions already exist for this order
                    if Commission.objects.filter(order=instance).exists():
                        return  # Commissions already calculated for this order
                    
                    # Get order items
                    order_items = OrderItem.objects.filter(order=instance)
                    
                    # Dictionary to track commissions by user
                    commissions_by_user = {}
                    
                    # Calculate commissions for each order item
                    for item in order_items:
                        product = item.product
                        seller = product.seller
                        
                        # If product has a specific seller, calculate commission for that seller
                        if seller:
                            # Get seller's user profile
                            try:
                                seller_profile = UserProfile.objects.get(user=seller)
                                seller_role = seller_profile.role
                            except UserProfile.DoesNotExist:
                                seller_role = 'seller'  # Default to seller role
                            
                            # Get commission rate for seller
                            commission_rate = get_commission_rate(seller_role, product.category)
                            
                            # Calculate commission amount for this item
                            item_total = item.price * item.quantity
                            commission_amount = (commission_rate / Decimal('100.00')) * item_total
                            
                            # Add to seller's commission
                            if seller.id not in commissions_by_user:
                                commissions_by_user[seller.id] = {
                                    'user': seller,
                                    'total_amount': Decimal('0.00'),
                                    'items': []
                                }
                            
                            commissions_by_user[seller.id]['total_amount'] += commission_amount
                            commissions_by_user[seller.id]['items'].append({
                                'product': product,
                                'amount': commission_amount,
                                'rate': commission_rate
                            })
                        else:
                            # If no specific seller, calculate commission for the order owner
                            # Only if the order owner is a seller
                            try:
                                owner_profile = UserProfile.objects.get(user=instance.user)
                                owner_role = owner_profile.role
                            except UserProfile.DoesNotExist:
                                owner_role = 'buyer'  # Default to buyer role
                            
                            # Only calculate commission if owner is a seller
                            if owner_role == 'seller':
                                commission_rate = get_commission_rate(owner_role, product.category)
                                
                                # Calculate commission amount for this item
                                item_total = item.price * item.quantity
                                commission_amount = (commission_rate / Decimal('100.00')) * item_total
                                
                                # Add to owner's commission
                                if instance.user.id not in commissions_by_user:
                                    commissions_by_user[instance.user.id] = {
                                        'user': instance.user,
                                        'total_amount': Decimal('0.00'),
                                        'items': []
                                    }
                                
                                commissions_by_user[instance.user.id]['total_amount'] += commission_amount
                                commissions_by_user[instance.user.id]['items'].append({
                                    'product': product,
                                    'amount': commission_amount,
                                    'rate': commission_rate
                                })
                    
                    # Create commissions for each user
                    for user_id, commission_data in commissions_by_user.items():
                        user = commission_data['user']
                        total_amount = commission_data['total_amount']
                        items = commission_data['items']
                        
                        # Only create commission if amount is greater than 0
                        if total_amount > Decimal('0.00'):
                            # Calculate average rate for display
                            total_rate = sum([item['rate'] for item in items])
                            avg_rate = total_rate / len(items) if items else Decimal('0.00')
                            
                            # Create commission record
                            commission = Commission.objects.create(
                                user=user,
                                order=instance,
                                amount=total_amount,
                                rate=avg_rate
                            )
                            
                            # Send notification about commission
                            try:
                                # Create a summary of products for the notification
                                product_names = [item['product'].name for item in items[:3]]  # Limit to first 3 products
                                if len(items) > 3:
                                    product_names.append(f'و {len(items) - 3} منتجات أخرى')
                                
                                products_list = ', '.join(product_names)
                                
                                message = f'تم حساب عمولة بقيمة {total_amount} ر.س بنسبة {avg_rate}% لمنتجاتك: {products_list} في طلب #{instance.pk}'
                                
                                Notification.objects.create(
                                    user=user,
                                    order=instance,
                                    notification_type='commission_calculated',
                                    message=message
                                )
                            except Exception:
                                # Silently ignore notification creation errors
                                pass
                    
                    # Calculate buyer commission (if applicable)
                    try:
                        buyer_profile = UserProfile.objects.get(user=instance.user)
                        buyer_role = buyer_profile.role
                    except UserProfile.DoesNotExist:
                        buyer_role = 'buyer'
                    
                    # Only calculate buyer commission if buyer settings exist and are active
                    buyer_commission_rate = get_commission_rate(buyer_role)
                    
                    if buyer_commission_rate > Decimal('0.00'):
                        # Calculate buyer commission based on total order amount
                        buyer_commission_amount = (buyer_commission_rate / Decimal('100.00')) * instance.total_amount
                        
                        # Only create commission if amount is greater than 0
                        if buyer_commission_amount > Decimal('0.00'):
                            # Create buyer commission
                            buyer_commission = Commission.objects.create(
                                user=instance.user,
                                order=instance,
                                amount=buyer_commission_amount,
                                rate=buyer_commission_rate
                            )
                            
                            # Send notification to buyer
                            try:
                                message = f'تم حساب عمولة مشتري بقيمة {buyer_commission_amount} ر.س بنسبة {buyer_commission_rate}% لطلبك #{instance.pk}'
                                
                                Notification.objects.create(
                                    user=instance.user,
                                    order=instance,
                                    notification_type='commission_calculated',
                                    message=message
                                )
                            except Exception:
                                # Silently ignore notification creation errors
                                pass
                            
                except Exception as e:
                    # Log error but don't disrupt order processing
                    print(f"Error calculating commission for order {instance.pk}: {str(e)}")
                    pass