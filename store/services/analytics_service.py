"""
Analytics Service Module
Provides AI-powered business intelligence and advanced analytics
"""

import logging
from typing import Dict, Any, List
from django.conf import settings
from django.db.models import Count, Sum, Avg, Q
from datetime import datetime, timedelta
from store.models import AnalyticsIntegration, Product, Order, OrderItem, User

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service class for handling advanced analytics with AI-powered business intelligence"""
    
    def __init__(self):
        # AI/ML service configuration
        self.ml_service_url = getattr(settings, 'ML_SERVICE_URL', None)
        self.ml_service_api_key = getattr(settings, 'ML_SERVICE_API_KEY', None)
    
    def get_basic_analytics(self) -> Dict[str, Any]:
        """
        Get basic analytics data
        
        Returns:
            Dictionary with basic analytics data
        """
        try:
            # Get basic statistics
            total_events = AnalyticsIntegration.objects.count()
            total_products = Product.objects.count()
            total_orders = Order.objects.count()
            total_users = User.objects.count()
            
            # Get recent events (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_events = AnalyticsIntegration.objects.filter(
                timestamp__gte=thirty_days_ago
            ).count()
            
            # Get conversion data
            total_visitors = AnalyticsIntegration.objects.filter(event_type='page_view').count()
            total_purchases = Order.objects.filter(status='delivered').count()
            conversion_rate = (total_purchases / total_visitors * 100) if total_visitors > 0 else 0
            
            # Get top products by views
            top_products = Product.objects.annotate(
                view_count=Count('analyticsintegration')
            ).filter(view_count__gt=0).order_by('-view_count')[:10]
            
            # Get user engagement data
            active_users = User.objects.filter(
                analyticsintegration__timestamp__gte=thirty_days_ago
            ).distinct().count()
            
            return {
                'success': True,
                'data': {
                    'total_events': total_events,
                    'total_products': total_products,
                    'total_orders': total_orders,
                    'total_users': total_users,
                    'recent_events': recent_events,
                    'conversion_rate': round(conversion_rate, 2),
                    'total_visitors': total_visitors,
                    'total_purchases': total_purchases,
                    'top_products': [
                        {
                            'id': product.id,
                            'name': product.name,
                            'view_count': product.view_count
                        } for product in top_products
                    ],
                    'active_users': active_users
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting basic analytics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_sales_analytics(self) -> Dict[str, Any]:
        """
        Get sales analytics data
        
        Returns:
            Dictionary with sales analytics data
        """
        try:
            # Get sales data by category
            category_sales = {}
            for category, _ in Product.CATEGORY_CHOICES:
                category_orders = OrderItem.objects.filter(
                    product__category=category,
                    order__status='delivered'
                )
                
                quantity = category_orders.aggregate(total=Sum('quantity'))['total'] or 0
                amount = category_orders.aggregate(total=Sum('price'))['total'] or 0
                
                category_sales[category] = {
                    'quantity': quantity,
                    'amount': float(amount),
                    'display_name': dict(Product.CATEGORY_CHOICES)[category]
                }
            
            # Get top selling products
            top_products = OrderItem.objects.values(
                'product_id', 'product__name'
            ).annotate(
                quantity=Sum('quantity'),
                amount=Sum('price')
            ).order_by('-quantity')[:10]
            
            # Get order status distribution
            order_status_data = Order.objects.values('status').annotate(
                count=Count('id')
            ).order_by('status')
            
            # Get sales trends (monthly)
            monthly_sales = []
            for i in range(12):
                month_start = datetime.now().replace(day=1) - timedelta(days=30*i)
                month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                
                month_orders = Order.objects.filter(
                    created_at__gte=month_start,
                    created_at__lte=month_end,
                    status='delivered'
                )
                
                monthly_total = month_orders.aggregate(
                    total=Sum('total_amount')
                )['total'] or 0
                
                monthly_sales.append({
                    'month': month_start.strftime('%Y-%m'),
                    'total': float(monthly_total)
                })
            
            # Reverse to show oldest first
            monthly_sales.reverse()
            
            return {
                'success': True,
                'data': {
                    'category_sales': category_sales,
                    'top_products': list(top_products),
                    'order_status_distribution': list(order_status_data),
                    'monthly_sales': monthly_sales
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting sales analytics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_analytics(self) -> Dict[str, Any]:
        """
        Get user analytics data
        
        Returns:
            Dictionary with user analytics data
        """
        try:
            # User statistics
            sellers_count = User.objects.filter(userprofile__role='seller').count()
            buyers_count = User.objects.filter(userprofile__role='buyer').count()
            managers_count = User.objects.filter(userprofile__role='manager').count()
            
            # Get user engagement by role
            user_engagement = {}
            for role, _ in User.objects.filter(userprofile__isnull=False).values_list(
                'userprofile__role'
            ).distinct():
                role_users = User.objects.filter(userprofile__role=role)
                engaged_users = role_users.filter(
                    analyticsintegration__timestamp__gte=datetime.now() - timedelta(days=30)
                ).distinct().count()
                
                user_engagement[role] = {
                    'total': role_users.count(),
                    'engaged': engaged_users,
                    'engagement_rate': round(
                        (engaged_users / role_users.count() * 100) if role_users.count() > 0 else 0,
                        2
                    ),
                    'display_name': dict(UserProfile.USER_ROLES)[role] if hasattr(UserProfile, 'USER_ROLES') else role
                }
            
            # Get user acquisition trends
            user_acquisition = []
            for i in range(12):
                month_start = datetime.now().replace(day=1) - timedelta(days=30*i)
                month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                
                new_users = User.objects.filter(
                    date_joined__gte=month_start,
                    date_joined__lte=month_end
                ).count()
                
                user_acquisition.append({
                    'month': month_start.strftime('%Y-%m'),
                    'new_users': new_users
                })
            
            # Reverse to show oldest first
            user_acquisition.reverse()
            
            return {
                'success': True,
                'data': {
                    'user_counts': {
                        'sellers': sellers_count,
                        'buyers': buyers_count,
                        'managers': managers_count
                    },
                    'user_engagement': user_engagement,
                    'user_acquisition': user_acquisition
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user analytics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_ai_insights(self) -> Dict[str, Any]:
        """
        Get AI-powered business insights
        
        Returns:
            Dictionary with AI-powered insights
        """
        try:
            # This would typically connect to an external ML service
            # For demonstration, we'll generate some basic insights
            
            insights = []
            
            # Sales trend insight
            sales_data = self.get_sales_analytics()
            if sales_data['success']:
                monthly_sales = sales_data['data']['monthly_sales']
                if len(monthly_sales) >= 2:
                    current_month = monthly_sales[-1]['total']
                    previous_month = monthly_sales[-2]['total']
                    
                    if current_month > previous_month:
                        growth_rate = ((current_month - previous_month) / previous_month * 100) if previous_month > 0 else 0
                        insights.append({
                            'type': 'sales_growth',
                            'title': 'نمو المبيعات',
                            'description': f'المبيعات نمت بنسبة {round(growth_rate, 2)}% مقارنة بالشهر الماضي',
                            'priority': 'high'
                        })
                    elif current_month < previous_month:
                        decline_rate = ((previous_month - current_month) / previous_month * 100) if previous_month > 0 else 0
                        insights.append({
                            'type': 'sales_decline',
                            'title': 'انخفاض المبيعات',
                            'description': f'المبيعات انخفضت بنسبة {round(decline_rate, 2)}% مقارنة بالشهر الماضي',
                            'priority': 'high'
                        })
            
            # Conversion rate insight
            basic_data = self.get_basic_analytics()
            if basic_data['success']:
                conversion_rate = basic_data['data']['conversion_rate']
                if conversion_rate < 2:
                    insights.append({
                        'type': 'low_conversion',
                        'title': 'معدل تحويل منخفض',
                        'description': f'معدل التحويل الحالي {conversion_rate}% أقل من المتوسط الصناعي',
                        'priority': 'medium',
                        'recommendations': [
                            'تحسين تجربة المستخدم في عملية الدفع',
                            'تقديم عروض خاصة لزيادة التحويلات',
                            'تحليل سلوك الزوار لتحديد نقاط التحسين'
                        ]
                    })
            
            # Product performance insight
            if sales_data['success']:
                top_products = sales_data['data']['top_products']
                if len(top_products) >= 5:
                    # Identify slow-moving products (assuming we have inventory data)
                    slow_products = Product.objects.filter(
                        stock_quantity__gt=50
                    ).annotate(
                        order_count=Count('orderitem')
                    ).filter(order_count=0)[:5]
                    
                    if slow_products:
                        insights.append({
                            'type': 'slow_moving_inventory',
                            'title': 'منتجات بطيئة الحركة',
                            'description': f'{slow_products.count()} من المنتجات لديها مخزون عالي ولكن مبيعات منخفضة',
                            'priority': 'medium',
                            'recommendations': [
                                ' النظر في تخفيض أسعار هذه المنتجات',
                                'تحسين تسويق هذه المنتجات',
                                'تقييم الحاجة للاحتفاظ بهذا المخزون'
                            ]
                        })
            
            return {
                'success': True,
                'data': {
                    'insights': insights
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting AI insights: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_real_time_dashboard_data(self) -> Dict[str, Any]:
        """
        Get real-time dashboard data
        
        Returns:
            Dictionary with real-time dashboard data
        """
        try:
            # Get real-time data for the last hour
            one_hour_ago = datetime.now() - timedelta(hours=1)
            
            # Active users in the last hour
            active_users = User.objects.filter(
                analyticsintegration__timestamp__gte=one_hour_ago
            ).distinct().count()
            
            # Recent orders
            recent_orders = Order.objects.filter(
                created_at__gte=one_hour_ago
            ).count()
            
            # Recent page views
            recent_page_views = AnalyticsIntegration.objects.filter(
                timestamp__gte=one_hour_ago,
                event_type='page_view'
            ).count()
            
            # Conversion events
            recent_conversions = AnalyticsIntegration.objects.filter(
                timestamp__gte=one_hour_ago,
                event_type='purchase'
            ).count()
            
            # Sales in the last hour
            recent_sales = Order.objects.filter(
                created_at__gte=one_hour_ago,
                status='delivered'
            ).aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            
            return {
                'success': True,
                'data': {
                    'active_users': active_users,
                    'recent_orders': recent_orders,
                    'recent_page_views': recent_page_views,
                    'recent_conversions': recent_conversions,
                    'recent_sales': float(recent_sales),
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time dashboard data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_advanced_real_time_data(self) -> Dict[str, Any]:
        """
        Get advanced real-time dashboard data with more detailed metrics
        
        Returns:
            Dictionary with advanced real-time dashboard data
        """
        try:
            # Get real-time data for the last 15 minutes (more granular)
            fifteen_minutes_ago = datetime.now() - timedelta(minutes=15)
            one_hour_ago = datetime.now() - timedelta(hours=1)
            
            # Active users in the last 15 minutes and last hour
            active_users_15min = User.objects.filter(
                analyticsintegration__timestamp__gte=fifteen_minutes_ago
            ).distinct().count()
            
            active_users_1hr = User.objects.filter(
                analyticsintegration__timestamp__gte=one_hour_ago
            ).distinct().count()
            
            # Recent orders (last 15 minutes and last hour)
            recent_orders_15min = Order.objects.filter(
                created_at__gte=fifteen_minutes_ago
            ).count()
            
            recent_orders_1hr = Order.objects.filter(
                created_at__gte=one_hour_ago
            ).count()
            
            # Page views trend (last 15 minutes vs last hour)
            page_views_15min = AnalyticsIntegration.objects.filter(
                timestamp__gte=fifteen_minutes_ago,
                event_type='page_view'
            ).count()
            
            page_views_1hr = AnalyticsIntegration.objects.filter(
                timestamp__gte=one_hour_ago,
                event_type='page_view'
            ).count()
            
            # Conversion rate calculation
            conversions_15min = AnalyticsIntegration.objects.filter(
                timestamp__gte=fifteen_minutes_ago,
                event_type='purchase'
            ).count()
            
            conversions_1hr = AnalyticsIntegration.objects.filter(
                timestamp__gte=one_hour_ago,
                event_type='purchase'
            ).count()
            
            # Sales data
            recent_sales_15min = Order.objects.filter(
                created_at__gte=fifteen_minutes_ago,
                status='delivered'
            ).aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            
            recent_sales_1hr = Order.objects.filter(
                created_at__gte=one_hour_ago,
                status='delivered'
            ).aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            
            # Top performing products in real-time
            top_products = OrderItem.objects.filter(
                order__created_at__gte=one_hour_ago
            ).values(
                'product_id', 'product__name'
            ).annotate(
                quantity=Sum('quantity'),
                revenue=Sum('price')
            ).order_by('-revenue')[:5]
            
            # Geographic distribution (simulated)
            geographic_data = [
                {'region': 'الرياض', 'orders': recent_orders_1hr * 0.35},
                {'region': 'جدة', 'orders': recent_orders_1hr * 0.25},
                {'region': 'الدمام', 'orders': recent_orders_1hr * 0.15},
                {'region': 'مكة', 'orders': recent_orders_1hr * 0.12},
                {'region': 'المدينة', 'orders': recent_orders_1hr * 0.08},
                {'region': 'أخرى', 'orders': recent_orders_1hr * 0.05},
            ]
            
            # Device type distribution (simulated)
            device_data = [
                {'device': 'Desktop', 'sessions': page_views_1hr * 0.45},
                {'device': 'Mobile', 'sessions': page_views_1hr * 0.50},
                {'device': 'Tablet', 'sessions': page_views_1hr * 0.05},
            ]
            
            return {
                'success': True,
                'data': {
                    'user_activity': {
                        'active_users_15min': active_users_15min,
                        'active_users_1hr': active_users_1hr,
                        'growth_rate': round(((active_users_15min - active_users_1hr/4) / (active_users_1hr/4) * 100) if active_users_1hr > 0 else 0, 2)
                    },
                    'order_metrics': {
                        'orders_15min': recent_orders_15min,
                        'orders_1hr': recent_orders_1hr,
                        'trend': 'up' if recent_orders_15min > recent_orders_1hr/4 else 'down'
                    },
                    'page_views': {
                        'views_15min': page_views_15min,
                        'views_1hr': page_views_1hr,
                        'trend': 'up' if page_views_15min > page_views_1hr/4 else 'down'
                    },
                    'conversions': {
                        'conversions_15min': conversions_15min,
                        'conversions_1hr': conversions_1hr,
                        'conversion_rate_15min': round((conversions_15min / page_views_15min * 100) if page_views_15min > 0 else 0, 2),
                        'conversion_rate_1hr': round((conversions_1hr / page_views_1hr * 100) if page_views_1hr > 0 else 0, 2)
                    },
                    'sales_data': {
                        'sales_15min': float(recent_sales_15min),
                        'sales_1hr': float(recent_sales_1hr),
                        'trend': 'up' if recent_sales_15min > recent_sales_1hr/4 else 'down'
                    },
                    'top_products': list(top_products),
                    'geographic_distribution': geographic_data,
                    'device_distribution': device_data,
                    'last_updated': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting advanced real-time dashboard data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_predictive_analytics(self) -> Dict[str, Any]:
        """
        Get predictive analytics data for future trends
        
        Returns:
            Dictionary with predictive analytics data
        """
        try:
            # Get historical data for the last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            # Daily sales data for trend analysis
            daily_sales = Order.objects.filter(
                created_at__gte=thirty_days_ago,
                status='delivered'
            ).extra(
                select={'day': 'date(created_at)'}
            ).values('day').annotate(
                total=Sum('total_amount')
            ).order_by('day')
            
            # Calculate average daily growth rate
            sales_data = [float(entry['total']) for entry in daily_sales]
            if len(sales_data) > 1:
                growth_rates = [(sales_data[i] - sales_data[i-1]) / sales_data[i-1] * 100 
                               for i in range(1, len(sales_data)) if sales_data[i-1] > 0]
                avg_growth_rate = sum(growth_rates) / len(growth_rates) if growth_rates else 0
            else:
                avg_growth_rate = 0
            
            # Predict next 7 days
            last_sales = sales_data[-1] if sales_data else 0
            predictions = []
            for i in range(1, 8):
                predicted_sales = last_sales * (1 + avg_growth_rate/100) ** i
                predictions.append({
                    'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
                    'predicted_sales': round(predicted_sales, 2)
                })
            
            # Seasonal trends (simplified)
            seasonal_trends = {
                'best_day_of_week': 'الأحد',  # Simplified
                'best_month': 'رمضان',  # Simplified
                'seasonal_factor': 1.15  # 15% increase during peak season
            }
            
            # Inventory predictions
            low_stock_products = Product.objects.filter(stock_quantity__lt=10).count()
            
            return {
                'success': True,
                'data': {
                    'sales_predictions': predictions,
                    'seasonal_trends': seasonal_trends,
                    'inventory_alerts': {
                        'low_stock_products': low_stock_products,
                        'recommended_actions': [
                            f'مراجعة {low_stock_products} منتج تحتاج إعادة التخزين' if low_stock_products > 0 else 'مستويات المخزون جيدة'
                        ]
                    },
                    'customer_behavior_predictions': {
                        'churn_risk': 'منخفض',  # Simplified
                        'retention_strategies': ['برنامج ولاء', 'عروض خاصة', 'خدمة عملاء محسنة']
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting predictive analytics data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Singleton instance for easy access
analytics_service = AnalyticsService()