"""
Product Service Module
Contains business logic for product management
"""

import logging
from typing import Dict, Any, List, Optional
from django.apps import apps
from django.db import transaction
from django.db.models import Count, Sum, Avg, Q, F
from decimal import Decimal
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ProductService:
    """Service class for product-related operations"""
    
    @staticmethod
    def get_product_statistics() -> Dict[str, Any]:
        """
        Get product statistics for dashboard with optimized queries
        
        Returns:
            Dictionary with product statistics
        """
        try:
            Product = apps.get_model('store', 'Product')
            OrderItem = apps.get_model('store', 'OrderItem')
            
            total_products = Product.objects.count()
            out_of_stock_products = Product.objects.filter(stock_quantity=0).count()
            low_stock_products = Product.objects.filter(
                stock_quantity__gt=0,
                stock_quantity__lte=F('low_stock_threshold')
            ).count()
            
            # Get category distribution
            category_distribution = {}
            for category, display_name in Product.CATEGORY_CHOICES:
                count = Product.objects.filter(category=category).count()
                category_distribution[category] = {
                    'count': count,
                    'display_name': display_name
                }
            
            # Get top selling products with optimized queries
            top_products = Product.objects.select_related(
                'seller'
            ).annotate(
                total_sold=Sum('orderitem__quantity')
            ).filter(total_sold__gt=0).order_by('-total_sold')[:10]
            
            return {
                'success': True,
                'data': {
                    'total_products': total_products,
                    'out_of_stock_products': out_of_stock_products,
                    'low_stock_products': low_stock_products,
                    'category_distribution': category_distribution,
                    'top_products': [
                        {
                            'id': product.id,
                            'name': product.name,
                            'total_sold': product.total_sold or 0
                        } for product in top_products
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting product statistics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def search_products(query: str = '', category: str = '', min_price: Optional[Decimal] = None, 
                       max_price: Optional[Decimal] = None, sort_by: str = 'name') -> List:
        """
        Search products with filters and optimized queries
        
        Args:
            query: Search query
            category: Product category
            min_price: Minimum price filter
            max_price: Maximum price filter
            sort_by: Sorting criteria
            
        Returns:
            List of products matching criteria
        """
        try:
            Product = apps.get_model('store', 'Product')
            OrderItem = apps.get_model('store', 'OrderItem')
            
            # Start with all products with optimized queries
            products = Product.objects.select_related('seller')
            
            # Apply search query
            if query:
                products = products.filter(
                    Q(name__icontains=query) | 
                    Q(description__icontains=query) |
                    Q(seo_keywords__icontains=query)
                )
            
            # Apply category filter
            if category:
                products = products.filter(category=category)
            
            # Apply price filters
            if min_price is not None:
                products = products.filter(price__gte=min_price)
            if max_price is not None:
                products = products.filter(price__lte=max_price)
            
            # Apply sorting
            if sort_by == 'price_asc':
                products = products.order_by('price')
            elif sort_by == 'price_desc':
                products = products.order_by('-price')
            elif sort_by == 'name':
                products = products.order_by('name')
            elif sort_by == 'popularity':
                products = products.annotate(
                    order_count=Count('orderitem')
                ).order_by('-order_count')
            
            return products
            
        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            return []
    
    @staticmethod
    @transaction.atomic
    def update_product_stock(product_id: int, quantity: int, operation: str = 'add') -> bool:
        """
        Update product stock quantity
        
        Args:
            product_id: ID of the product
            quantity: Quantity to add/remove
            operation: 'add' or 'subtract'
            
        Returns:
            Boolean indicating success
        """
        try:
            Product = apps.get_model('store', 'Product')
            product = Product.objects.get(id=product_id)
            
            if operation == 'add':
                product.stock_quantity += quantity
            elif operation == 'subtract':
                if product.stock_quantity >= quantity:
                    product.stock_quantity -= quantity
                else:
                    raise ValueError("Insufficient stock")
            else:
                raise ValueError("Invalid operation")
            
            product.save()
            logger.info(f"Updated stock for product {product_id}: {operation} {quantity}")
            return True
            
        except Product.DoesNotExist:
            logger.error(f"Product {product_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error updating product stock: {str(e)}")
            return False
    
    @staticmethod
    def get_low_stock_alerts(threshold: int = 5) -> List:
        """
        Get products with low stock with optimized queries
        
        Args:
            threshold: Stock threshold for alerts
            
        Returns:
            List of products with low stock
        """
        try:
            Product = apps.get_model('store', 'Product')
            return Product.objects.select_related(
                'seller'
            ).filter(
                stock_quantity__gt=0,
                stock_quantity__lte=threshold
            )
            
        except Exception as e:
            logger.error(f"Error getting low stock alerts: {str(e)}")
            return []
    
    @staticmethod
    def get_dashboard_statistics() -> Dict[str, Any]:
        """
        Get comprehensive dashboard statistics with optimized queries
        
        Returns:
            Dictionary with dashboard statistics
        """
        try:
            Product = apps.get_model('store', 'Product')
            Order = apps.get_model('store', 'Order')
            UserProfile = apps.get_model('store', 'UserProfile')
            Commission = apps.get_model('store', 'Commission')
            OrderItem = apps.get_model('store', 'OrderItem')
            
            # Get counts with optimized queries
            total_products = Product.objects.count()
            total_orders = Order.objects.count()
            pending_orders = Order.objects.filter(status='pending').count()
            total_sellers = UserProfile.objects.filter(role='seller').count()
            
            # Calculate total profits from commissions
            total_profits = Commission.objects.aggregate(total=Sum('amount'))['total'] or 0
            
            # Get pending/rejected products
            pending_products = Product.objects.filter(verification_status='pending').count()
            rejected_products = Product.objects.filter(verification_status='rejected').count()
            
            # Get recent orders with optimized queries
            recent_orders = Order.objects.select_related(
                'user'
            ).prefetch_related(
                'items', 'items__product'
            ).order_by('-created_at')[:10]
            
            # Get top selling products with optimized queries
            top_products = Product.objects.select_related(
                'seller'
            ).annotate(
                total_sold=Sum('orderitem__quantity')
            ).filter(total_sold__gt=0).order_by('-total_sold')[:5]
            
            return {
                'success': True,
                'data': {
                    'total_products': total_products,
                    'total_orders': total_orders,
                    'pending_orders': pending_orders,
                    'total_sellers': total_sellers,
                    'total_profits': total_profits,
                    'pending_products': pending_products,
                    'rejected_products': rejected_products,
                    'recent_orders': [
                        {
                            'id': order.id,
                            'user': order.user.username,
                            'total_amount': float(order.total_amount),
                            'status': order.status,
                            'created_at': order.created_at
                        } for order in recent_orders
                    ],
                    'top_products': [
                        {
                            'id': product.id,
                            'name': product.name,
                            'seller': product.seller.username if product.seller else 'Unknown',
                            'total_sold': product.total_sold or 0
                        } for product in top_products
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard statistics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Singleton instance
product_service = ProductService()