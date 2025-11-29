#!/usr/bin/env python
"""
Test script to verify cart functionality fixes
"""
import os
import sys
import django
from django.test import TestCase
from django.test.client import Client

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopsite.settings')
django.setup()

from store.utils import Cart
from django.contrib.sessions.backends.db import SessionStore

def test_cart_count_calculation():
    """Test that cart count calculation works correctly"""
    print("Testing cart count calculation...")
    
    # Create a mock session
    session = SessionStore()
    session.create()
    
    # Create a cart
    cart = Cart(session)
    
    # Add some items
    cart.add(1, 3)  # Add product 1, quantity 3
    cart.add(2, 2)  # Add product 2, quantity 2
    
    # Test get_total_quantity
    total_quantity = cart.get_total_quantity()
    print(f"Total quantity: {total_quantity}")
    assert total_quantity == 5, f"Expected 5, got {total_quantity}"
    
    # Test get_items
    items = cart.get_items()
    print(f"Number of unique items: {len(items)}")
    assert len(items) == 2, f"Expected 2 unique items, got {len(items)}"
    
    print("Cart count calculation test passed!")

def test_context_processor():
    """Test the cart context processor"""
    print("Testing context processor...")
    
    # This would require a full Django test client setup
    # For now, we'll just verify the logic
    from store.context_processors import cart_processor
    
    # Create a mock request with session
    class MockRequest:
        def __init__(self):
            self.session = {'cart': {'1': '3', '2': '2'}}
    
    request = MockRequest()
    context = cart_processor(request)
    
    print(f"Context processor result: {context}")
    assert 'cart_count' in context, "cart_count not in context"
    assert context['cart_count'] == 5, f"Expected cart_count=5, got {context['cart_count']}"
    
    print("Context processor test passed!")

if __name__ == "__main__":
    print("Running cart functionality tests...")
    test_cart_count_calculation()
    test_context_processor()
    print("All tests passed!")