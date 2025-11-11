"""
User models for the user service.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Extended user model."""
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('seller', 'Seller'),
        ('buyer', 'Buyer'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """User profile model."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    business_name = models.CharField(max_length=100, blank=True, null=True)
    business_license = models.FileField(upload_to='licenses/', blank=True, null=True)
    id_document = models.FileField(upload_to='ids/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"