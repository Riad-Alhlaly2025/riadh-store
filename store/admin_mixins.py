from django.contrib import admin
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncMonth, TruncDay
from django.urls import path
from django.shortcuts import render
from django.contrib.admin.views.main import ChangeList
from django.http import JsonResponse, HttpResponse
import json
import csv
from io import StringIO


class ChartMixin:
    """
    Mixin to add chart functionality to Django admin
    """
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('chart-data/', self.admin_site.admin_view(self.chart_data_view), name=f'{self.model._meta.app_label}_{self.model._meta.model_name}_chart_data'),
        ]
        return custom_urls + urls
    
    def chart_data_view(self, request):
        """
        Return chart data as JSON
        """
        # Get queryset
        queryset = self.get_queryset(request)
        
        # Get chart data based on model
        chart_data = self.get_chart_data(queryset)
        
        return JsonResponse(chart_data)
    
    def get_chart_data(self, queryset):
        """
        Override this method to provide chart data
        """
        return {}


class AdvancedFilterMixin:
    """
    Mixin to add advanced filtering capabilities
    """
    
    def get_search_results(self, request, queryset, search_term):
        """
        Override to add advanced search capabilities
        """
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        
        # Add custom filtering based on request parameters
        filters = request.GET
        for key, value in filters.items():
            if key.startswith('filter_') and value:
                field_name = key.replace('filter_', '')
                try:
                    queryset = queryset.filter(**{f'{field_name}__icontains': value})
                except:
                    pass
        
        return queryset, use_distinct


class ExportMixin:
    """
    Mixin to add export functionality
    """
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'export_as_csv' not in actions:
            actions['export_as_csv'] = (self.export_as_csv, 'export_as_csv', 'Export as CSV')
        if 'export_as_excel' not in actions:
            actions['export_as_excel'] = (self.export_as_excel, 'export_as_excel', 'Export as Excel')
        return actions
    
    def export_as_csv(self, request, queryset):
        """
        Export selected objects as CSV
        """
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.model._meta.verbose_name_plural}.csv"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Write header
        field_names = [field.name for field in self.model._meta.fields]
        writer.writerow(field_names)
        
        # Write data
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        
        return response
    
    def export_as_excel(self, request, queryset):
        """
        Export selected objects as Excel (CSV format for simplicity)
        """
        # For simplicity, we'll export as CSV which Excel can open
        return self.export_as_csv(request, queryset)


class DashboardWidgetMixin:
    """
    Mixin to add dashboard widget functionality
    """
    
    def get_dashboard_widgets(self, request):
        """
        Override this method to provide dashboard widgets
        """
        return []
    
    def get_dashboard_data(self, request):
        """
        Override this method to provide dashboard data
        """
        return {}


class VisualizationAdmin(ChartMixin, AdvancedFilterMixin, ExportMixin, DashboardWidgetMixin, admin.ModelAdmin):
    """
    Enhanced admin class with all visualization features
    """
    
    change_list_template = 'admin/enhanced_change_list.html'
    
    def get_chart_data(self, queryset):
        """
        Default implementation for chart data
        """
        # Monthly data
        monthly_data = queryset.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Daily data for last 30 days
        daily_data = queryset.annotate(
            day=TruncDay('created_at')
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')[:30]
        
        return {
            'monthly_data': list(monthly_data),
            'daily_data': list(daily_data),
        }
    
    def get_dashboard_widgets(self, request):
        """
        Default implementation for dashboard widgets
        """
        model_name = self.model._meta.verbose_name_plural
        return [
            {
                'title': f'Total {model_name}',
                'value': self.get_queryset(request).count(),
                'icon': '📊',
                'color': '#0074D9'
            }
        ]