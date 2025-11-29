from rest_framework import serializers
from .models import Warehouse, Supplier, Category, Product, InventoryTransaction, StockAlert

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'location', 'contact_person', 'phone', 'email', 'is_active', 'created_at', 'updated_at']

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_person', 'phone', 'email', 'address', 'website', 'is_active', 'created_at', 'updated_at']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    profit_margin = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'sku', 'name', 'description', 'category', 'category_name', 'supplier', 'supplier_name',
                  'warehouse', 'warehouse_name', 'cost_price', 'selling_price', 'quantity_in_stock',
                  'reorder_level', 'max_stock_level', 'is_active', 'is_featured', 'is_low_stock',
                  'profit_margin', 'created_at', 'updated_at']

class InventoryTransactionSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = InventoryTransaction
        fields = ['id', 'product', 'product_sku', 'product_name', 'transaction_type', 'transaction_type_display',
                  'quantity', 'unit_cost', 'reference_number', 'notes', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['created_at']

class StockAlertSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    
    class Meta:
        model = StockAlert
        fields = ['id', 'product', 'product_sku', 'product_name', 'alert_type', 'alert_type_display',
                  'threshold', 'current_stock', 'is_resolved', 'created_at', 'resolved_at']