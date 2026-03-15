from decimal import Decimal

from rest_framework import serializers

from .models import Product, ProductCategory


class ProductCategoryMiniSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="slug", read_only=True)

    class Meta:
        model = ProductCategory
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    """Serializer aligned with frontend products contract."""

    category = ProductCategoryMiniSerializer(read_only=True)
    price_per_bag = serializers.SerializerMethodField()
    price_per_ton = serializers.SerializerMethodField()
    packaging_size = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    availability_status = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "slug",
            "name",
            "category",
            "maize_type",
            "description",
            "packaging_size",
            "price_per_bag",
            "price_per_ton",
            "currency",
            "availability_status",
            "min_order_quantity",
            "image_url",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "updated_at"]

    def get_packaging_size(self, obj):
        current = obj.current_price
        if current and current.packaging_size:
            return current.packaging_size
        if obj.packaging_sizes:
            return obj.packaging_sizes[0]
        return ""

    def get_price_per_bag(self, obj):
        current = obj.current_price
        return str(current.price_per_bag) if current else None

    def get_price_per_ton(self, obj):
        current = obj.current_price
        return str(current.price_per_ton) if current else None

    def get_currency(self, obj):
        return "GHS"

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    def get_availability_status(self, obj):
        if obj.availability_status == "OUT_OF_STOCK":
            return "OUT_OF_STOCK"
        stock = obj.current_stock or {}
        bags = stock.get("total_bags") or 0
        tons = stock.get("total_tons") or Decimal("0")
        if bags <= 50 or tons <= Decimal("2"):
            return "LOW_STOCK"
        return "AVAILABLE"


class ProductCategorySerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="slug", read_only=True)
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProductCategory
        fields = ["id", "name", "description", "product_count"]
