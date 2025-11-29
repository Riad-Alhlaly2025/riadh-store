from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Warehouse URLs
    path('warehouses/', views.WarehouseListView.as_view(), name='warehouse_list'),
    path('warehouses/<int:pk>/', views.WarehouseDetailView.as_view(), name='warehouse_detail'),
    
    # Supplier URLs
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    
    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Product URLs
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<uuid:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/stock-status/', views.product_stock_status, name='product_stock_status'),
    
    # Inventory Transaction URLs
    path('transactions/', views.InventoryTransactionListView.as_view(), name='transaction_list'),
    path('transactions/<uuid:pk>/', views.InventoryTransactionDetailView.as_view(), name='transaction_detail'),
    path('transactions/adjustment/', views.stock_adjustment, name='stock_adjustment'),
    
    # Stock Alert URLs
    path('alerts/', views.StockAlertListView.as_view(), name='alert_list'),
    path('alerts/<uuid:alert_id>/resolve/', views.resolve_stock_alert, name='resolve_stock_alert'),
]