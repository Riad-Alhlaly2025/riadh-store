from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Reports
    path('reports/', views.ReportListView.as_view(), name='report_list'),
    path('reports/<uuid:pk>/', views.ReportDetailView.as_view(), name='report_detail'),
    
    # Dashboards
    path('dashboards/', views.DashboardListView.as_view(), name='dashboard_list'),
    path('dashboards/<uuid:pk>/', views.DashboardDetailView.as_view(), name='dashboard_detail'),
    
    # Dashboard Widgets
    path('widgets/', views.DashboardWidgetListView.as_view(), name='widget_list'),
    path('widgets/<uuid:pk>/', views.DashboardWidgetDetailView.as_view(), name='widget_detail'),
    
    # Data Exports
    path('exports/', views.DataExportListView.as_view(), name='export_list'),
    path('exports/<uuid:pk>/', views.DataExportDetailView.as_view(), name='export_detail'),
    
    # Analytics Events
    path('events/', views.AnalyticsEventListView.as_view(), name='event_list'),
    path('summary/', views.get_analytics_summary, name='analytics_summary'),
    
    # User Behavior
    path('behavior/', views.UserBehaviorListView.as_view(), name='behavior_list'),
    
    # Metrics
    path('metrics/sales/', views.SalesMetricsListView.as_view(), name='sales_metrics_list'),
    path('metrics/traffic/', views.TrafficMetricsListView.as_view(), name='traffic_metrics_list'),
]