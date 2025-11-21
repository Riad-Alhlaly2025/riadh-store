# Store API Documentation

## Overview
The Store API provides programmatic access to all features of the e-commerce platform. It follows REST principles and uses JSON for request and response bodies.

## Authentication
All API endpoints require authentication. Use Django session authentication by including the session cookie with your requests.

## Base URL
All endpoints are relative to: `/api/`

## Endpoints

### Products
- `GET /api/products/` - List all products
- `GET /api/products/{id}/` - Retrieve a specific product

### Orders
- `GET /api/orders/` - List all orders for the authenticated user
- `GET /api/orders/{id}/` - Retrieve a specific order

### Payments
- `POST /api/payments/stripe/` - Process Stripe payment
- `POST /api/payments/paypal/create/` - Create PayPal payment
- `POST /api/payments/paypal/execute/` - Execute PayPal payment

### Users
- `GET /api/users/` - List users (managers see all, others see only themselves)
- `GET /api/users/{id}/` - Retrieve a specific user

### Reviews
- `GET /api/reviews/` - List all reviews
- `GET /api/reviews/{id}/` - Retrieve a specific review

### Coupons
- `GET /api/coupons/` - List coupons (managers only)
- `GET /api/coupons/{id}/` - Retrieve a specific coupon (managers only)

### Loyalty Programs
- `GET /api/loyalty-programs/` - List loyalty programs
- `GET /api/loyalty-programs/{id}/` - Retrieve a specific loyalty program

### Notifications
- `GET /api/notifications/` - List notifications for the authenticated user
- `GET /api/notifications/{id}/` - Retrieve a specific notification

### Wishlists
- `GET /api/wishlists/` - List wishlist items for the authenticated user

### Pages
- `GET /api/pages/` - List published pages
- `GET /api/pages/{id}/` - Retrieve a specific published page

### Articles
- `GET /api/articles/` - List published articles
- `GET /api/articles/{id}/` - Retrieve a specific published article

### FAQs
- `GET /api/faqs/` - List active FAQs

### Commissions
- `GET /api/commissions/` - List commissions

### Analytics
- `POST /api/analytics/events/` - Create an analytics event
- `GET /api/analytics/dashboard/` - Get dashboard analytics data

## Error Responses
All error responses follow standard HTTP status codes:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Rate Limiting
The API implements rate limiting to prevent abuse. Exceeding the limit will result in a 429 (Too Many Requests) response.

## Versioning
The API is currently at version 1.0. Breaking changes will be introduced with new version numbers.

## Support
For API support, contact the development team or refer to the main application documentation.