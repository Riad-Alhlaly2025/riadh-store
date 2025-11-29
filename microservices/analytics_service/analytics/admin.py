from django.contrib import admin
from .models import Report, Dashboard, DashboardWidget, DataExport, AnalyticsEvent, UserBehavior, SalesMetrics, TrafficMetrics

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'generated_by', 'is_published', 'created_at']
    list_filter = ['report_type', 'is_published', 'created_at']
    search_fields = ['name', 'description']

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description']

@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['title', 'dashboard', 'widget_type', 'is_visible', 'created_at']
    list_filter = ['widget_type', 'is_visible', 'created_at']
    search_fields = ['title', 'dashboard__name']

@admin.register(DataExport)
class DataExportAdmin(admin.ModelAdmin):
    list_display = ['name', 'export_format', 'generated_by', 'status', 'created_at']
    list_filter = ['export_format', 'status', 'created_at']
    search_fields = ['name']

@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'user', 'session_id', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['user__username', 'session_id']

@admin.register(UserBehavior)
class UserBehaviorAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_id', 'page_views', 'clicks', 'time_spent', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'session_id']

@admin.register(SalesMetrics)
class SalesMetricsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_revenue', 'total_orders', 'average_order_value', 'conversion_rate']
    list_filter = ['date']
    date_hierarchy = 'date'

@admin.register(TrafficMetrics)
class TrafficMetricsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_visitors', 'unique_visitors', 'page_views', 'bounce_rate']
    list_filter = ['date']
    date_hierarchy = 'date'