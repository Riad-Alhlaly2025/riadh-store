"""
API Documentation for Store Application
=====================================

This document provides comprehensive documentation for the Store API endpoints.

Authentication
--------------
All API endpoints require authentication using Django session authentication.
Include the session cookie in your requests.

Base URL
--------
All endpoints are relative to: /api/

Endpoints
---------
"""

API_ENDPOINTS = {
    "products": {
        "list": {
            "method": "GET",
            "url": "/api/products/",
            "description": "List all products",
            "permissions": "Authenticated users",
            "response": {
                "200": "List of products with details",
                "401": "Authentication required"
            }
        },
        "detail": {
            "method": "GET",
            "url": "/api/products/{id}/",
            "description": "Retrieve a specific product",
            "permissions": "Authenticated users",
            "parameters": {
                "id": "Product ID (integer)"
            },
            "response": {
                "200": "Product details",
                "401": "Authentication required",
                "404": "Product not found"
            }
        }
    },
    "orders": {
        "list": {
            "method": "GET",
            "url": "/api/orders/",
            "description": "List all orders for the authenticated user",
            "permissions": "Authenticated users",
            "response": {
                "200": "List of user's orders",
                "401": "Authentication required"
            }
        },
        "detail": {
            "method": "GET",
            "url": "/api/orders/{id}/",
            "description": "Retrieve a specific order",
            "permissions": "Authenticated users",
            "parameters": {
                "id": "Order ID (integer)"
            },
            "response": {
                "200": "Order details",
                "401": "Authentication required",
                "403": "Not authorized to view this order",
                "404": "Order not found"
            }
        }
    },
    "payments": {
        "stripe": {
            "method": "POST",
            "url": "/api/payments/stripe/",
            "description": "Process Stripe payment",
            "permissions": "Authenticated users",
            "request_body": {
                "order_id": "ID of the order to pay for (integer)"
            },
            "response": {
                "201": "Payment intent created with client_secret",
                "400": "Bad request or payment error",
                "401": "Authentication required",
                "404": "Order not found"
            }
        },
        "paypal_create": {
            "method": "POST",
            "url": "/api/payments/paypal/create/",
            "description": "Create PayPal payment",
            "permissions": "Authenticated users",
            "request_body": {
                "order_id": "ID of the order to pay for (integer)"
            },
            "response": {
                "201": "PayPal payment created with approval URL",
                "400": "Bad request or payment error",
                "401": "Authentication required",
                "404": "Order not found"
            }
        },
        "paypal_execute": {
            "method": "POST",
            "url": "/api/payments/paypal/execute/",
            "description": "Execute PayPal payment",
            "permissions": "Authenticated users",
            "request_body": {
                "payment_id": "PayPal payment ID (string)",
                "payer_id": "PayPal payer ID (string)"
            },
            "response": {
                "200": "Payment executed successfully",
                "400": "Bad request or payment error",
                "401": "Authentication required"
            }
        }
    },
    "users": {
        "list": {
            "method": "GET",
            "url": "/api/users/",
            "description": "List users (managers see all, others see only themselves)",
            "permissions": "Authenticated users",
            "response": {
                "200": "List of users",
                "401": "Authentication required"
            }
        },
        "detail": {
            "method": "GET",
            "url": "/api/users/{id}/",
            "description": "Retrieve a specific user",
            "permissions": "Authenticated users (can only view own profile unless manager)",
            "parameters": {
                "id": "User ID (integer)"
            },
            "response": {
                "200": "User details",
                "401": "Authentication required",
                "403": "Not authorized to view this user",
                "404": "User not found"
            }
        }
    },
    "reviews": {
        "list": {
            "method": "GET",
            "url": "/api/reviews/",
            "description": "List all reviews",
            "permissions": "Authenticated users",
            "response": {
                "200": "List of reviews",
                "401": "Authentication required"
            }
        },
        "detail": {
            "method": "GET",
            "url": "/api/reviews/{id}/",
            "description": "Retrieve a specific review",
            "permissions": "Authenticated users",
            "parameters": {
                "id": "Review ID (integer)"
            },
            "response": {
                "200": "Review details",
                "401": "Authentication required",
                "404": "Review not found"
            }
        }
    },
    "coupons": {
        "list": {
            "method": "GET",
            "url": "/api/coupons/",
            "description": "List coupons (managers only)",
            "permissions": "Managers only",
            "response": {
                "200": "List of coupons",
                "401": "Authentication required",
                "403": "Manager permissions required"
            }
        },
        "detail": {
            "method": "GET",
            "url": "/api/coupons/{id}/",
            "description": "Retrieve a specific coupon (managers only)",
            "permissions": "Managers only",
            "parameters": {
                "id": "Coupon ID (integer)"
            },
            "response": {
                "200": "Coupon details",
                "401": "Authentication required",
                "403": "Manager permissions required",
                "404": "Coupon not found"
            }
        }
    },
    "loyalty_programs": {
        "list": {
            "method": "GET",
            "url": "/api/loyalty-programs/",
            "description": "List loyalty programs (managers see all, users see only their own)",
            "permissions": "Authenticated users",
            "response": {
                "200": "List of loyalty programs",
                "401": "Authentication required"
            }
        },
        "detail": {
            "method": "GET",
            "url": "/api/loyalty-programs/{id}/",
            "description": "Retrieve a specific loyalty program",
            "permissions": "Authenticated users (can only view own unless manager)",
            "parameters": {
                "id": "Loyalty program ID (integer)"
            },
            "response": {
                "200": "Loyalty program details",
                "401": "Authentication required",
                "403": "Not authorized to view this loyalty program",
                "404": "Loyalty program not found"
            }
        }
    },
    "notifications": {
        "list": {
            "method": "GET",
            "url": "/api/notifications/",
            "description": "List notifications for the authenticated user",
            "permissions": "Authenticated users",
            "response": {
                "200": "List of user's notifications",
                "401": "Authentication required"
            }
        },
        "detail": {
            "method": "GET",
            "url": "/api/notifications/{id}/",
            "description": "Retrieve a specific notification",
            "permissions": "Authenticated users (can only view own notifications)",
            "parameters": {
                "id": "Notification ID (integer)"
            },
            "response": {
                "200": "Notification details",
                "401": "Authentication required",
                "403": "Not authorized to view this notification",
                "404": "Notification not found"
            }
        }
    },
    "wishlists": {
        "list": {
            "method": "GET",
            "url": "/api/wishlists/",
            "description": "List wishlist items for the authenticated user",
            "permissions": "Authenticated users",
            "response": {
                "200": "List of user's wishlist items",
                "401": "Authentication required"
            }
        }
    },
    "pages": {
        "list": {
            "method": "GET",
            "url": "/api/pages/",
            "description": "List published pages",
            "permissions": "Authenticated users",
            "response": {
                "200": "List of published pages",
                "401": "Authentication required"
            }
        },
        "detail": {
            "method": "GET",
            "url": "/api/pages/{id}/",
            "description": "Retrieve a specific published page",
            "permissions": "Authenticated users",
            "parameters": {
                "id": "Page ID (integer)"
            },
            "response": {
                "200": "Page details",
                "401": "Authentication required",
                "404": "Page not found or not published"
            }
        }
    },
    "articles": {
        "list": {
            "method": "GET",
            "url": "/api/articles/",
            "description": "List published articles",
            "permissions": "Authenticated users",
            "response": {
                "200": "List of published articles",
                "401": "Authentication required"
            }
        },
        "detail": {
            "method": "GET",
            "url": "/api/articles/{id}/",
            "description": "Retrieve a specific published article",
            "permissions": "Authenticated users",
            "parameters": {
                "id": "Article ID (integer)"
            },
            "response": {
                "200": "Article details",
                "401": "Authentication required",
                "404": "Article not found or not published"
            }
        }
    },
    "faqs": {
        "list": {
            "method": "GET",
            "url": "/api/faqs/",
            "description": "List active FAQs",
            "permissions": "Authenticated users",
            "response": {
                "200": "List of active FAQs",
                "401": "Authentication required"
            }
        }
    },
    "commissions": {
        "list": {
            "method": "GET",
            "url": "/api/commissions/",
            "description": "List commissions (managers see all, users see only their own)",
            "permissions": "Authenticated users",
            "response": {
                "200": "List of commissions",
                "401": "Authentication required"
            }
        }
    },
    "analytics": {
        "events": {
            "method": "POST",
            "url": "/api/analytics/events/",
            "description": "Create an analytics event",
            "permissions": "Authenticated users",
            "request_body": {
                "event_type": "Type of event (string)",
                "product_id": "Associated product ID (optional, integer)",
                "order_id": "Associated order ID (optional, integer)",
                "metadata": "Additional event data (optional, string)",
                "url": "Page URL (optional, string)",
                "referrer": "Referrer URL (optional, string)"
            },
            "response": {
                "201": "Analytics event created successfully",
                "400": "Bad request",
                "401": "Authentication required"
            }
        },
        "dashboard": {
            "method": "GET",
            "url": "/api/analytics/dashboard/",
            "description": "Get dashboard analytics data",
            "permissions": "Authenticated users",
            "response": {
                "200": "Dashboard analytics data",
                "401": "Authentication required"
            }
        }
    }
}

# Error Responses
ERROR_RESPONSES = {
    "400": {
        "description": "Bad Request",
        "content": {
            "error": "Error message describing the issue"
        }
    },
    "401": {
        "description": "Unauthorized",
        "content": {
            "detail": "Authentication credentials were not provided."
        }
    },
    "403": {
        "description": "Forbidden",
        "content": {
            "detail": "You do not have permission to perform this action."
        }
    },
    "404": {
        "description": "Not Found",
        "content": {
            "detail": "Not found."
        }
    },
    "500": {
        "description": "Internal Server Error",
        "content": {
            "error": "Internal server error occurred"
        }
    }
}

# Example Usage
EXAMPLES = {
    "get_products": {
        "request": "GET /api/products/",
        "headers": {
            "Authorization": "Bearer <your-token>"
        },
        "response": {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "name": "iPhone 12",
                    "price": "999.99",
                    "description": "Latest iPhone model",
                    "image": "/media/products/iphone12.jpg",
                    "category": "phones",
                    "currency": "USD",
                    "seller": 1,
                    "stock_quantity": 50,
                    "low_stock_threshold": 5,
                    "seo_title": "iPhone 12 - Latest Model",
                    "seo_description": "Buy the latest iPhone 12",
                    "seo_keywords": "iPhone, Apple, smartphone",
                    "name_en": "iPhone 12",
                    "description_en": "Latest iPhone model",
                    "seo_title_en": "iPhone 12 - Latest Model",
                    "seo_description_en": "Buy the latest iPhone 12",
                    "seo_keywords_en": "iPhone, Apple, smartphone",
                    "created_at": "2023-01-01T12:00:00Z",
                    "updated_at": "2023-01-01T12:00:00Z"
                }
            ]
        }
    }
}