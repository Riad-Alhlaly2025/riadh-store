from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from .models import Report, Dashboard, DashboardWidget, DataExport, AnalyticsEvent, UserBehavior, SalesMetrics, TrafficMetrics
from .serializers import ReportSerializer, DashboardSerializer, DashboardWidgetSerializer, DataExportSerializer, AnalyticsEventSerializer, UserBehaviorSerializer, SalesMetricsSerializer, TrafficMetricsSerializer

# Report Views
class ReportListView(generics.ListCreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Report.objects.all()

class ReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Report.objects.all()

# Dashboard Views
class DashboardListView(generics.ListCreateAPIView):
    serializer_class = DashboardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Dashboard.objects.filter(Q(created_by=self.request.user) | Q(is_public=True))

class DashboardDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DashboardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Dashboard.objects.filter(Q(created_by=self.request.user) | Q(is_public=True))

# Dashboard Widget Views
class DashboardWidgetListView(generics.ListCreateAPIView):
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        dashboard_id = self.request.query_params.get('dashboard_id', None)
        if dashboard_id:
            return DashboardWidget.objects.filter(dashboard_id=dashboard_id)
        return DashboardWidget.objects.all()

class DashboardWidgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DashboardWidget.objects.all()

# Data Export Views
class DataExportListView(generics.ListCreateAPIView):
    serializer_class = DataExportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DataExport.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)

class DataExportDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DataExportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DataExport.objects.all()

# Analytics Event Views
class AnalyticsEventListView(generics.ListCreateAPIView):
    serializer_class = AnalyticsEventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AnalyticsEvent.objects.all()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analytics_summary(request):
    """
    Get a summary of analytics data
    """
    try:
        # Get date range from query params
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timezone.timedelta(days=days)
        
        # Get recent events
        recent_events = AnalyticsEvent.objects.filter(created_at__gte=start_date)
        
        # Calculate metrics
        total_events = recent_events.count()
        unique_users = recent_events.values('user').distinct().count()
        page_views = recent_events.filter(event_type='page_view').count()
        purchases = recent_events.filter(event_type='purchase').count()
        
        # Get sales metrics
        sales_metrics = SalesMetrics.objects.filter(date__gte=start_date)
        total_revenue = sales_metrics.aggregate(total=Sum('total_revenue'))['total'] or 0
        total_orders = sales_metrics.aggregate(total=Sum('total_orders'))['total'] or 0
        
        data = {
            'period_days': days,
            'total_events': total_events,
            'unique_users': unique_users,
            'page_views': page_views,
            'purchases': purchases,
            'total_revenue': float(total_revenue),
            'total_orders': total_orders,
            'average_order_value': float(total_revenue / total_orders) if total_orders > 0 else 0
        }
        
        return Response(data)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

# User Behavior Views
class UserBehaviorListView(generics.ListAPIView):
    serializer_class = UserBehaviorSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserBehavior.objects.all()

# Metrics Views
class SalesMetricsListView(generics.ListAPIView):
    serializer_class = SalesMetricsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        days = int(self.request.query_params.get('days', 30))
        start_date = timezone.now() - timezone.timedelta(days=days)
        return SalesMetrics.objects.filter(date__gte=start_date)

class TrafficMetricsListView(generics.ListAPIView):
    serializer_class = TrafficMetricsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        days = int(self.request.query_params.get('days', 30))
        start_date = timezone.now() - timezone.timedelta(days=days)
        return TrafficMetrics.objects.filter(date__gte=start_date)