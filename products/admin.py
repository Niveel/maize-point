from django.contrib import admin
from .models import Product, ProductCategory


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ["slug", "name"]
    search_fields = ["slug", "name"]
    ordering = ["name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "availability_status",
        "is_available",
        "created_at",
        "updated_at",
    ]
    list_filter = ["category", "availability_status", "is_available", "created_at"]
    search_fields = ["name", "maize_type", "description", "slug"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["name"]

    fieldsets = (
        (
            "Product Information",
            {
                "fields": (
                    "name",
                    "slug",
                    "category",
                    "maize_type",
                    "description",
                    "packaging_sizes",
                    "min_order_quantity",
                    "image",
                    "availability_status",
                )
            },
        ),
        ("Compatibility", {"fields": ("is_available",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
