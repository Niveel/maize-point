from django.contrib import admin
from .models import Stock, StockMovement


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity_bags', 'quantity_tons', 'warehouse_location',
                    'source_type', 'date_received', 'is_low_stock']
    list_filter = ['source_type', 'warehouse_location', 'date_received']
    search_fields = ['product__name', 'warehouse_location']
    readonly_fields = ['created_at', 'updated_at', 'is_low_stock']
    ordering = ['-date_received']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('product', 'quantity_bags', 'quantity_tons')
        }),
        ('Source', {
            'fields': ('source_type', 'farmer')
        }),
        ('Quality', {
            'fields': ('quality_grade', 'moisture_content')
        }),
        ('Location & Pricing', {
            'fields': ('warehouse_location', 'cost_price')
        }),
        ('Dates', {
            'fields': ('date_received', 'expiry_alert_date')
        }),
        ('Additional', {
            'fields': ('notes', 'is_low_stock')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['stock', 'movement_type', 'quantity_bags', 'quantity_tons',
                    'performed_by', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['stock__product__name', 'reason']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Movement Information', {
            'fields': ('stock', 'movement_type', 'quantity_bags', 'quantity_tons')
        }),
        ('Details', {
            'fields': ('order', 'reason', 'performed_by')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
