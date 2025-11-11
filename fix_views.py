# Script to fix the views.py file by removing corrupted data and adding missing buyer dashboard view

with open('store/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the position of the debug_manager_access function
pos = content.rfind('def debug_manager_access')

# Truncate the file at that position
fixed_content = content[:pos]

# Add the buyer dashboard view
buyer_dashboard_view = '''

@login_required
def buyer_dashboard(request: HttpRequest) -> HttpResponse:
    """Buyer dashboard view"""
    # Import models
    Order = apps.get_model('store', 'Order')
    Commission = apps.get_model('store', 'Commission')
    Product = apps.get_model('store', 'Product')
    
    # Get buyer-specific statistics
    user_orders = Order.objects.filter(user=request.user)
    total_orders = user_orders.count()
    pending_orders = user_orders.filter(status="pending").count()
    
    # Get buyer's commissions
    buyer_commissions = Commission.objects.filter(user=request.user).order_by("-created_at").select_related("user", "order")
    total_commissions = buyer_commissions.count()
    total_commission_amount = sum([commission.amount for commission in buyer_commissions])
    
    # Get currency from first product or default to SAR
    currency = "SAR"
    if Product.objects.exists():
        first_product = Product.objects.first()
        if hasattr(first_product, "currency"):
            currency = first_product.currency
    
    context = {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_commissions": total_commissions,
        "total_commission_amount": total_commission_amount,
        "recent_commissions": buyer_commissions[:5],  # Last 5 commissions
        "currency": currency,
    }
    
    return render(request, "store/buyer_dashboard.html", context)
'''

# Write the fixed content back to the file
with open('store/views.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content + buyer_dashboard_view)

print("Fixed views.py file successfully!")