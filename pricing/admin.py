from django.contrib import admin
from .models import Price


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ['product', 'packaging_size', 'price_per_bag', 'price_per_ton', 
                    'is_current', 'effective_date', 'updated_by']
    list_filter = ['is_current', 'product', 'effective_date']
    search_fields = ['product__name', 'packaging_size']
    readonly_fields = ['effective_date']
    ordering = ['-effective_date']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('product', 'packaging_size')
        }),
        ('Pricing', {
            'fields': ('price_per_bag', 'price_per_ton', 'is_current')
        }),
        ('Additional Information', {
            'fields': ('market_notes', 'updated_by', 'effective_date')
        }),
    )
