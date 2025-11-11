# Payment Integration Guide

This document explains how to set up and test the electronic payment integration using Stripe in the myshop application.

## Prerequisites

1. Stripe account (sign up at https://stripe.com)
2. Django application running
3. Python packages installed (stripe package)

## Setup Instructions

### 1. Configure Stripe API Keys

1. Go to your Stripe Dashboard
2. Navigate to Developers > API keys
3. Copy your Publishable key and Secret key
4. Update the settings in `shopsite/settings.py`:

```python
STRIPE_PUBLISHABLE_KEY = 'pk_test_your_publishable_key_here'
STRIPE_SECRET_KEY = 'sk_test_your_secret_key_here'
STRIPE_WEBHOOK_SECRET = 'whsec_your_webhook_secret_here'
```

### 2. Set up Webhook (Optional but Recommended)

1. In your Stripe Dashboard, go to Developers > Webhooks
2. Add a new endpoint with the URL: `https://yourdomain.com/payment/webhook/stripe/`
3. Select the events you want to receive:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
4. Copy the webhook signing secret and update `STRIPE_WEBHOOK_SECRET` in settings

## Testing Payment Integration

### Test Cards

Use these test card numbers for testing:

- **Successful payment**: `4242 4242 4242 4242`
- **Failed payment**: `4000 0000 0000 0002`
- **Requires authentication**: `4000 0025 0000 3155`

All test cards use:
- Expiration: Any future date
- CVC: Any 3 digits
- ZIP: Any 5 digits

### Testing Process

1. Add products to cart
2. Proceed to checkout
3. Fill shipping information
4. On the payment page, select Stripe payment method
5. Enter test card details
6. Complete payment

## Code Structure

### Models

- `Payment`: Stores payment information including transaction ID, amount, status, and method

### Views

- `payment_view`: Displays payment options
- `create_stripe_payment_intent`: Creates a Stripe PaymentIntent
- `stripe_webhook`: Handles Stripe webhook events

### Templates

- `payment.html`: Payment page with Stripe Elements form

## Security Considerations

1. Never expose secret keys in client-side code
2. Always verify webhook signatures
3. Use HTTPS in production
4. Validate all payment data

## Troubleshooting

### Common Issues

1. **Webhook verification fails**: Check that the webhook secret is correct
2. **Payment intent creation fails**: Verify API keys and network connectivity
3. **Payment status not updating**: Check webhook configuration

### Logs

Check Django logs for payment-related errors:
- Successful payments: "Payment successful for order #X"
- Failed payments: "Payment failed for order #X"
- Webhook errors: "Invalid payload" or "Invalid signature"