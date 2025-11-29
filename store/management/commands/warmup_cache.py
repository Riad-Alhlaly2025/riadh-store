"""
Management command to warm up the application cache
"""

from django.core.management.base import BaseCommand
from store.services.cache_service import cache_service
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Warm up the application cache with frequently accessed data'

    def handle(self, *args, **options):
        """
        Handle the command execution
        """
        self.stdout.write(
            self.style.SUCCESS('Starting cache warming process...')
        )
        
        try:
            # Warm up cache
            results = cache_service.warm_up_cache()
            
            # Report results
            for key, success in results.items():
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully warmed up {key}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to warm up {key}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS('Cache warming process completed successfully!')
            )
            
        except Exception as e:
            logger.error(f"Error during cache warming: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'Cache warming failed: {str(e)}')
            )