from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, F
from django.utils import timezone
from .models import Warehouse, Supplier, Category, Product, InventoryTransaction, StockAlert
from .serializers import WarehouseSerializer, SupplierSerializer, CategorySerializer, ProductSerializer, InventoryTransactionSerializer, StockAlertSerializer

# Warehouse Views
class WarehouseListView(generics.ListCreateAPIView):
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Warehouse.objects.all()

class WarehouseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Warehouse.objects.all()

# Supplier Views
class SupplierListView(generics.ListCreateAPIView):
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Supplier.objects.all()

class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Supplier.objects.all()

# Category Views
class CategoryListView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Category.objects.all()

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Category.objects.all()

# Product Views
class ProductListView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Product.objects.all()
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(sku__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by low stock
        low_stock = self.request.query_params.get('low_stock', None)
        if low_stock:
            queryset = queryset.filter(quantity_in_stock__lte=F('reorder_level'))
        
        return queryset

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Product.objects.all()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_stock_status(request):
    """
    Get stock status summary for all products
    """
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(quantity_in_stock__lte=F('reorder_level')).count()
    out_of_stock_products = Product.objects.filter(quantity_in_stock=0).count()
    
    data = {
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'in_stock_products': total_products - out_of_stock_products
    }
    
    return Response(data)

# Inventory Transaction Views
class InventoryTransactionListView(generics.ListCreateAPIView):
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = InventoryTransaction.objects.all()
        # Filter by product
        product = self.request.query_params.get('product', None)
        if product:
            queryset = queryset.filter(product_id=product)
        
        # Filter by transaction type
        transaction_type = self.request.query_params.get('transaction_type', None)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class InventoryTransactionDetailView(generics.RetrieveAPIView):
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return InventoryTransaction.objects.all()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stock_adjustment(request):
    """
    Adjust stock levels for a product
    """
    try:
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 0))
        notes = request.data.get('notes', '')
        
        if not product_id or quantity == 0:
            return Response(
                {'error': 'product_id and quantity (non-zero) are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product = get_object_or_404(Product, id=product_id)
        
        # Create transaction record
        transaction = InventoryTransaction.objects.create(
            product=product,
            transaction_type='adjustment',
            quantity=quantity,
            unit_cost=product.cost_price,
            notes=notes,
            created_by=request.user
        )
        
        # Update product stock
        product.quantity_in_stock += quantity
        product.save()
        
        # Check for stock alerts
        check_stock_alerts(product)
        
        serializer = InventoryTransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

# Stock Alert Views
class StockAlertListView(generics.ListAPIView):
    serializer_class = StockAlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = StockAlert.objects.all()
        # Filter by resolved status
        resolved = self.request.query_params.get('resolved', None)
        if resolved is not None:
            resolved = resolved.lower() == 'true'
            queryset = queryset.filter(is_resolved=resolved)
        
        # Filter by alert type
        alert_type = self.request.query_params.get('alert_type', None)
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        
        return queryset

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resolve_stock_alert(request, alert_id):
    """
    Mark a stock alert as resolved
    """
    try:
        alert = get_object_or_404(StockAlert, id=alert_id)
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save()
        
        serializer = StockAlertSerializer(alert)
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

def check_stock_alerts(product):
    """
    Check and create stock alerts for a product based on current stock levels
    """
    # Check for low stock
    if product.quantity_in_stock <= product.reorder_level:
        StockAlert.objects.create(
            product=product,
            alert_type='low_stock',
            threshold=product.reorder_level,
            current_stock=product.quantity_in_stock
        )
    
    # Check for out of stock
    if product.quantity_in_stock == 0:
        StockAlert.objects.create(
            product=product,
            alert_type='out_of_stock',
            threshold=0,
            current_stock=product.quantity_in_stock
        )