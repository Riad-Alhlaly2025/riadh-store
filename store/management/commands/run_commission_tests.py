from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.apps import apps
from decimal import Decimal
from store.signals import get_commission_rate

class Command(BaseCommand):
    help = 'Run commission calculation tests'

    def handle(self, *args, **options):
        self.stdout.write('Running commission calculation tests...')
        
        # Test get_commission_rate function
        self.stdout.write('\n1. Testing get_commission_rate function...')
        
        # Test seller commission rate
        seller_rate = get_commission_rate('seller')
        if seller_rate == Decimal('10.00'):
            self.stdout.write('   ✓ Seller commission rate test passed')
        else:
            self.stdout.write(f'   ✗ Seller commission rate test failed: expected 10.00, got {seller_rate}')
        
        # Test buyer commission rate
        buyer_rate = get_commission_rate('buyer')
        if buyer_rate == Decimal('2.00'):
            self.stdout.write('   ✓ Buyer commission rate test passed')
        else:
            self.stdout.write(f'   ✗ Buyer commission rate test failed: expected 2.00, got {buyer_rate}')
        
        # Test manager commission rate
        manager_rate = get_commission_rate('manager')
        if manager_rate == Decimal('0.00'):
            self.stdout.write('   ✓ Manager commission rate test passed')
        else:
            self.stdout.write(f'   ✗ Manager commission rate test failed: expected 0.00, got {manager_rate}')
        
        self.stdout.write(
            '\nCommission calculation tests completed!'
        )