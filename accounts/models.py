from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    """Custom User model extending AbstractUser"""
    
    USER_TYPE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('STAFF', 'Staff'),
        ('CUSTOMER', 'Customer'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='CUSTOMER')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    mobile_number = PhoneNumberField(unique=True, region='GH', help_text='Ghana phone number')
    whatsapp_number = PhoneNumberField(blank=True, null=True, region='GH')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_type']),
            models.Index(fields=['mobile_number']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.username} - {self.get_user_type_display()}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
