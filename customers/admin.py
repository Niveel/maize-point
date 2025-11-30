from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'user', 'location', 'is_active', 'total_orders', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['customer_id', 'user__username', 'user__email', 'user__first_name', 'user__last_name', 'location']
    readonly_fields = ['customer_id', 'created_at', 'updated_at', 'total_orders', 'total_spent']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_id', 'user', 'location', 'is_active')
        }),
        ('Statistics', {
            'fields': ('total_orders', 'total_spent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
