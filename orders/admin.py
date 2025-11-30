from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'customer', 'product', 'quantity_bags', 'total_price',
                    'order_status', 'payment_option', 'created_at']
    list_filter = ['order_status', 'payment_option', 'delivery_method', 'created_at']
    search_fields = ['order_id', 'customer__customer_id', 'customer__user__email',
                    'customer__user__first_name', 'customer__user__last_name']
    readonly_fields = ['order_id', 'total_price', 'approved_at', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'customer', 'product', 'order_status')
        }),
        ('Quantity & Pricing', {
            'fields': ('quantity_bags', 'quantity_tons', 'unit_price', 'total_price')
        }),
        ('Delivery', {
            'fields': ('delivery_method', 'delivery_address', 'delivery_date')
        }),
        ('Payment', {
            'fields': ('payment_option',)
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('customer', 'product')
        return self.readonly_fields
