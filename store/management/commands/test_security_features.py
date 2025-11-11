from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import MFADevice, SecurityLog, SensitiveData

class Command(BaseCommand):
    help = 'Test security features by creating sample data'

    def handle(self, *args, **options):
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'testuser@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            user.set_password('testpassword123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created test user: testuser'))
        
        # Create sample MFA device
        mfa_device, created = MFADevice.objects.get_or_create(
            user=user,
            name='Test Device',
            defaults={
                'secret_key': 'TESTSECRETKEY123456',
                'device_type': 'totp',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created MFA device for test user'))
        
        # Create sample security logs
        SecurityLog.objects.get_or_create(
            user=user,
            event_type='login_success',
            ip_address='127.0.0.1',
            details='Successful login'
        )
        
        SecurityLog.objects.get_or_create(
            user=user,
            event_type='mfa_success',
            ip_address='127.0.0.1',
            details='MFA verification successful'
        )
        
        # Create sample sensitive data
        SensitiveData.objects.get_or_create(
            user=user,
            data_type='credit_card',
            defaults={
                'encrypted_data': 'ENCRYPTED_CREDIT_CARD_DATA',
                'encryption_method': 'AES-256'
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully created sample security data'))