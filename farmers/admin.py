from django.contrib import admin
from .models import Farmer, FarmerSupply


@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'mobile_number', 'community', 'district', 'region',
                    'is_approved', 'is_active', 'created_at']
    list_filter = ['is_approved', 'is_active', 'region', 'district', 'created_at']
    search_fields = ['full_name', 'mobile_number', 'ghana_card_number', 'community']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('profile_picture', 'full_name', 'mobile_number', 'ghana_card_number')
        }),
        ('Location', {
            'fields': ('gps_latitude', 'gps_longitude', 'region', 'district', 'community')
        }),
        ('Business Information', {
            'fields': ('maize_types_supplied', 'notes')
        }),
        ('Status', {
            'fields': ('is_approved', 'is_active', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(FarmerSupply)
class FarmerSupplyAdmin(admin.ModelAdmin):
    list_display = ['farmer', 'product', 'quantity_bags', 'quantity_tons',
                    'date_delivered', 'payment_status', 'balance_due', 'recorded_by']
    list_filter = ['payment_status', 'date_delivered', 'product']
    search_fields = ['farmer__full_name', 'product__name']
    readonly_fields = ['total_cost', 'balance_due', 'created_at', 'updated_at']
    ordering = ['-date_delivered']
    
    fieldsets = (
        ('Supply Information', {
            'fields': ('farmer', 'product', 'quantity_bags', 'quantity_tons', 'date_delivered')
        }),
        ('Financial', {
            'fields': ('cost_per_bag', 'total_cost', 'payment_status', 'amount_paid', 'balance_due')
        }),
        ('Additional', {
            'fields': ('stock', 'notes', 'recorded_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
