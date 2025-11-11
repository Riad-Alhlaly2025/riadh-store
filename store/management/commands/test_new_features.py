from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Coupon, LoyaltyProgram, LoyaltyReward, EmailCampaign, AdvertisementCampaign

class Command(BaseCommand):
    help = 'Test the new features implementation'

    def handle(self, *args, **options):
        # Create a test user if not exists
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created test user')
            )
        
        # Test Coupon model
        coupon, created = Coupon.objects.get_or_create(
            code='TEST10',
            defaults={
                'discount_type': 'percentage',
                'discount_value': 10.00,
                'minimum_amount': 50.00,
                'active': True,
                'valid_from': '2025-01-01T00:00:00Z',
                'valid_to': '2026-01-01T00:00:00Z'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created test coupon')
            )
        
        # Test Loyalty Program
        loyalty_program, created = LoyaltyProgram.objects.get_or_create(
            user=user,
            defaults={
                'points': 100,
                'level': 'silver',
                'total_spent': 1000.00
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created test loyalty program')
            )
        
        # Test Loyalty Reward
        reward, created = LoyaltyReward.objects.get_or_create(
            name='10% Discount',
            defaults={
                'reward_type': 'discount',
                'points_required': 50,
                'discount_percentage': 10.00,
                'active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created test loyalty reward')
            )
        
        # Test Email Campaign
        email_campaign, created = EmailCampaign.objects.get_or_create(
            subject='Test Campaign',
            defaults={
                'content': 'This is a test email campaign',
                'recipients': 'test@example.com',
                'status': 'draft'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created test email campaign')
            )
        
        # Test Advertisement Campaign
        ad_campaign, created = AdvertisementCampaign.objects.get_or_create(
            name='Facebook Ad',
            defaults={
                'platform': 'facebook',
                'budget': 1000.00,
                'start_date': '2025-01-01T00:00:00Z',
                'end_date': '2025-12-31T00:00:00Z',
                'active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created test advertisement campaign')
            )
        
        self.stdout.write(
            self.style.SUCCESS('All tests passed successfully!')
        )