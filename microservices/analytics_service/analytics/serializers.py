from rest_framework import serializers
from .models import Report, Dashboard, DashboardWidget, DataExport, AnalyticsEvent, UserBehavior, SalesMetrics, TrafficMetrics

class ReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source='generated_by.username', read_only=True)
    
    class Meta:
        model = Report
        fields = ['id', 'name', 'report_type', 'description', 'generated_by', 'generated_by_name', 
                  'file_path', 'is_published', 'created_at', 'updated_at']

class DashboardSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Dashboard
        fields = ['id', 'name', 'description', 'created_by', 'created_by_name', 'is_public', 'created_at', 'updated_at']

class DashboardWidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardWidget
        fields = ['id', 'dashboard', 'title', 'widget_type', 'data_source', 'configuration',
                  'position_x', 'position_y', 'width', 'height', 'is_visible', 'created_at', 'updated_at']

class DataExportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source='generated_by.username', read_only=True)
    
    class Meta:
        model = DataExport
        fields = ['id', 'name', 'export_format', 'data_source', 'file_path', 'generated_by', 'generated_by_name',
                  'created_at', 'completed_at', 'status']

class AnalyticsEventSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AnalyticsEvent
        fields = ['id', 'event_type', 'user', 'user_name', 'session_id', 'url', 'referrer', 
                  'user_agent', 'ip_address', 'metadata', 'created_at']

class UserBehaviorSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserBehavior
        fields = ['id', 'user', 'user_name', 'session_id', 'page_views', 'clicks', 'time_spent',
                  'bounce_rate', 'conversion_rate', 'created_at', 'updated_at']

class SalesMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesMetrics
        fields = ['id', 'date', 'total_revenue', 'total_orders', 'average_order_value',
                  'conversion_rate', 'new_customers', 'returning_customers', 'created_at']

class TrafficMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficMetrics
        fields = ['id', 'date', 'total_visitors', 'unique_visitors', 'page_views',
                  'average_session_duration', 'bounce_rate', 'traffic_sources', 'created_at']