from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('brands/', views.BrandListView.as_view(), name='brand_list'),
    path('', views.ProductListView.as_view(), name='product_list'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('search/', views.product_search, name='product_search'),
    path('featured/', views.featured_products, name='featured_products'),
    path('<int:product_id>/reviews/', views.add_product_review, name='add_product_review'),
]