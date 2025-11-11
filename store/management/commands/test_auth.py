from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.decorators import check_user_role

class Command(BaseCommand):
    help = 'Test user authentication and role checking'

    def handle(self, *args, **options):
        # Get the manager user
        try:
            user = User.objects.get(username='manager')
            self.stdout.write(f"User found: {user.username}")
            self.stdout.write(f"User role: {user.userprofile.role}")
            
            # Test role checking
            is_manager = user.userprofile.role == 'manager'
            self.stdout.write(f"Is manager: {is_manager}")
            
            # Test the decorator logic
            if hasattr(user, 'userprofile') and user.userprofile.role == 'manager':
                self.stdout.write("Decorator check would PASS")
            else:
                self.stdout.write("Decorator check would FAIL")
                
        except User.DoesNotExist:
            self.stdout.write("Manager user not found")
        except Exception as e:
            self.stdout.write(f"Error: {str(e)}")