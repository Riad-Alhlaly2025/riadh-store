"""
Cache Service Module
Contains caching strategies and utilities for the application
"""

import logging
from typing import Any, Optional, Dict
from django.core.cache import cache
from django.apps import apps
from django.db.models import Sum, Count
from decimal import Decimal

logger = logging.getLogger(__name__)

class CacheService:
    """Service class for caching operations"""
    
    # Cache timeout constants (in seconds)
    SHORT_TIMEOUT = 60 * 5      # 5 minutes
    MEDIUM_TIMEOUT = 60 * 30    # 30 minutes
    LONG_TIMEOUT = 60 * 60 * 2  # 2 hours
    VERY_LONG_TIMEOUT = 60 * 60 * 24  # 24 hours
    
    @staticmethod
    def get_cache_key(prefix: str, identifier: str = '', user_id: Optional[int] = None) -> str:
        """
        Generate a cache key with consistent naming convention
        
        Args:
            prefix: Key prefix (e.g., 'product_list', 'user_dashboard')
            identifier: Additional identifier (e.g., category, page number)
            user_id: User ID for user-specific data
            
        Returns:
            Formatted cache key string
        """
        key_parts = [prefix]
        
        if identifier:
            key_parts.append(str(identifier))
            
        if user_id:
            key_parts.append(f"user_{user_id}")
            
        return "_".join(key_parts)
    
    @staticmethod
    def get_or_set(key: str, callable_func, timeout: int = MEDIUM_TIMEOUT) -> Any:
        """
        Get data from cache or set it using the provided function
        
        Args:
            key: Cache key
            callable_func: Function to call if cache miss
            timeout: Cache timeout in seconds
            
        Returns:
            Cached or newly computed data
        """
        try:
            data = cache.get(key)
            if data is None:
                data = callable_func()
                cache.set(key, data, timeout)
                logger.info(f"Cache miss for key: {key}, data computed and cached")
            else:
                logger.info(f"Cache hit for key: {key}")
            return data
        except Exception as e:
            logger.error(f"Error in cache get_or_set for key {key}: {str(e)}")
            # Return fresh data if cache fails
            return callable_func()
    
    @staticmethod
    def invalidate_pattern(pattern: str) -> None:
        """
        Invalidate all cache keys matching a pattern
        Note: This is a simplified implementation. In production, you might want
        to use Redis-specific commands for better performance.
        
        Args:
            pattern: Pattern to match cache keys (e.g., 'product_*')
        """
        # In a real implementation with Redis, you would use:
        # cache.delete_many(cache.keys(pattern))
        # But Django's cache backend doesn't support keys() method
        logger.info(f"Cache invalidation requested for pattern: {pattern}")
    
    @staticmethod
    def get_product_list_cache_key(page: int = 1, category: str = '', sort_by: str = 'name') -> str:
        """
        Generate cache key for product list with filters
        
        Args:
            page: Page number
            category: Product category filter
            sort_by: Sorting criteria
            
        Returns:
            Cache key for product list
        """
        identifier = f"page_{page}"
        if category:
            identifier += f"_cat_{category}"
        if sort_by:
            identifier += f"_sort_{sort_by}"
            
        return CacheService.get_cache_key('product_list', identifier)
    
    @staticmethod
    def get_dashboard_statistics_cache_key(user_id: int) -> str:
        """
        Generate cache key for dashboard statistics
        
        Args:
            user_id: User ID
            
        Returns:
            Cache key for dashboard statistics
        """
        return CacheService.get_cache_key('dashboard_stats', user_id=user_id)
    
    @staticmethod
    def get_user_orders_cache_key(user_id: int) -> str:
        """
        Generate cache key for user orders
        
        Args:
            user_id: User ID
            
        Returns:
            Cache key for user orders
        """
        return CacheService.get_cache_key('user_orders', user_id=user_id)
    
    @staticmethod
    def warm_up_cache() -> Dict[str, bool]:
        """
        Pre-populate cache with frequently accessed data
        
        Returns:
            Dictionary with warming status for each cache type
        """
        try:
            # Import models
            Product = apps.get_model('store', 'Product')
            Order = apps.get_model('store', 'Order')
            UserProfile = apps.get_model('store', 'UserProfile')
            Commission = apps.get_model('store', 'Commission')
            
            # Warm up product count
            product_count_key = CacheService.get_cache_key('global_stats', 'product_count')
            cache.set(product_count_key, Product.objects.count(), CacheService.LONG_TIMEOUT)
            
            # Warm up order count
            order_count_key = CacheService.get_cache_key('global_stats', 'order_count')
            cache.set(order_count_key, Order.objects.count(), CacheService.LONG_TIMEOUT)
            
            # Warm up seller count
            seller_count_key = CacheService.get_cache_key('global_stats', 'seller_count')
            cache.set(seller_count_key, UserProfile.objects.filter(role='seller').count(), CacheService.LONG_TIMEOUT)
            
            # Warm up total profits
            total_profits_key = CacheService.get_cache_key('global_stats', 'total_profits')
            total_profits = Commission.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            cache.set(total_profits_key, float(total_profits), CacheService.LONG_TIMEOUT)
            
            logger.info("Cache warming completed successfully")
            return {
                'product_count': True,
                'order_count': True,
                'seller_count': True,
                'total_profits': True
            }
            
        except Exception as e:
            logger.error(f"Error during cache warming: {str(e)}")
            return {
                'product_count': False,
                'order_count': False,
                'seller_count': False,
                'total_profits': False
            }

# Singleton instance
cache_service = CacheService()