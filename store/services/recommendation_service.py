import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.apps import apps
from django.db.models import Count
from collections import defaultdict

class RecommendationService:
    """AI-powered product recommendation service"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
    
    def get_content_based_recommendations(self, product_id, num_recommendations=5):
        """Get content-based recommendations for a product"""
        Product = apps.get_model('store', 'Product')
        
        # Get all products
        products = Product.objects.all()
        if not products.exists():
            return []
        
        # Create feature matrix based on product descriptions
        product_descriptions = [f"{p.name} {p.description}" for p in products]
        
        try:
            # Vectorize product descriptions
            tfidf_matrix = self.vectorizer.fit_transform(product_descriptions)
            
            # Calculate similarity matrix
            cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
            
            # Get the product index
            product_indices = {product.id: i for i, product in enumerate(products)}
            if product_id not in product_indices:
                return []
            
            idx = product_indices[product_id]
            
            # Get similarity scores for this product
            sim_scores = list(enumerate(cosine_sim[idx]))
            
            # Sort products based on similarity scores
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            
            # Get top similar products (excluding the product itself)
            sim_scores = sim_scores[1:num_recommendations+1]
            
            # Get product indices
            product_indices_list = [i[0] for i in sim_scores]
            
            # Return recommended products
            recommended_products = [products[i] for i in product_indices_list]
            return recommended_products
            
        except Exception as e:
            # Fallback to simple category-based recommendations
            return self._get_category_based_recommendations(product_id, num_recommendations)
    
    def _get_category_based_recommendations(self, product_id, num_recommendations=5):
        """Fallback method for category-based recommendations"""
        Product = apps.get_model('store', 'Product')
        
        try:
            # Get the product
            product = Product.objects.get(id=product_id)
            
            # Get products from the same category
            similar_products = Product.objects.filter(
                category=product.category
            ).exclude(id=product_id)[:num_recommendations]
            
            return list(similar_products)
        except Product.DoesNotExist:
            return []
    
    def get_user_based_recommendations(self, user, num_recommendations=5):
        """Get recommendations based on user behavior"""
        Product = apps.get_model('store', 'Product')
        Order = apps.get_model('store', 'Order')
        OrderItem = apps.get_model('store', 'OrderItem')
        
        if not user.is_authenticated:
            # For anonymous users, return popular products
            return self._get_popular_products(num_recommendations)
        
        try:
            # Get user's purchased products
            user_orders = Order.objects.filter(user=user)
            user_products = OrderItem.objects.filter(order__in=user_orders).values_list('product', flat=True)
            
            if not user_products.exists():
                # If user hasn't purchased anything, return popular products
                return self._get_popular_products(num_recommendations)
            
            # Get products purchased by other users who bought similar items
            similar_users_orders = OrderItem.objects.filter(
                product__in=user_products
            ).exclude(order__user=user).values_list('order__user', flat=True)
            
            # Get products purchased by similar users
            recommended_products = OrderItem.objects.filter(
                order__user__in=similar_users_orders
            ).exclude(product__in=user_products).values('product').annotate(
                purchase_count=Count('product')
            ).order_by('-purchase_count')[:num_recommendations]
            
            # Get product objects
            product_ids = [item['product'] for item in recommended_products]
            products = Product.objects.filter(id__in=product_ids)
            
            return list(products)
            
        except Exception as e:
            # Fallback to popular products
            return self._get_popular_products(num_recommendations)
    
    def _get_popular_products(self, num_recommendations=5):
        """Get popular products based on purchase count"""
        Product = apps.get_model('store', 'Product')
        OrderItem = apps.get_model('store', 'OrderItem')
        
        # Get products with highest purchase counts
        popular_products = OrderItem.objects.values('product').annotate(
            purchase_count=Count('product')
        ).order_by('-purchase_count')[:num_recommendations]
        
        # Get product objects
        product_ids = [item['product'] for item in popular_products]
        products = Product.objects.filter(id__in=product_ids)
        
        return list(products)
    
    def get_personalized_recommendations(self, user=None, product_id=None, num_recommendations=5):
        """Get personalized recommendations using hybrid approach"""
        if product_id:
            # Content-based recommendations
            return self.get_content_based_recommendations(product_id, num_recommendations)
        elif user:
            # User-based recommendations
            return self.get_user_based_recommendations(user, num_recommendations)
        else:
            # Popular products
            return self._get_popular_products(num_recommendations)

# Singleton instance
recommendation_service = RecommendationService()