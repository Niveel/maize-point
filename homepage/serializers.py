from decimal import Decimal

from django.utils.text import slugify
from rest_framework import serializers

from blog.models import BlogPost
from products.models import Product

from .models import BenefitItem, BenefitSection, FooterContact, HeroMetric, Testimonial


class HomepageProductPreviewSerializer(serializers.ModelSerializer):
    slug = serializers.SerializerMethodField()
    maize_type = serializers.SerializerMethodField()
    packaging_size = serializers.SerializerMethodField()
    price_per_bag = serializers.SerializerMethodField()
    price_per_ton = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    availability_status = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "maize_type",
            "packaging_size",
            "price_per_bag",
            "price_per_ton",
            "currency",
            "availability_status",
            "image",
            "updated_at",
        ]

    def get_slug(self, obj):
        return slugify(obj.name)

    def get_maize_type(self, obj):
        return obj.name

    def get_packaging_size(self, obj):
        if obj.packaging_sizes:
            return obj.packaging_sizes[0]
        return ""

    def get_price_per_bag(self, obj):
        price = obj.current_price
        if not price:
            return None
        return str(price.price_per_bag)

    def get_price_per_ton(self, obj):
        price = obj.current_price
        if not price:
            return None
        return str(price.price_per_ton)

    def get_currency(self, obj):
        return "GHS"

    def get_availability_status(self, obj):
        if not obj.is_available:
            return "OUT_OF_STOCK"

        stock = obj.current_stock or {}
        bags = stock.get("total_bags") or 0
        tons = stock.get("total_tons") or Decimal("0")
        if bags <= 50 or tons <= Decimal("2"):
            return "LOW_STOCK"
        return "AVAILABLE"

    def get_image(self, obj):
        image_field = getattr(obj, "image", None)
        if image_field:
            request = self.context.get("request")
            if request is not None:
                return request.build_absolute_uri(image_field.url)
            return image_field.url
        return None


class AnnouncementPreviewSerializer(serializers.ModelSerializer):
    excerpt = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "slug",
            "title",
            "excerpt",
            "cover_image",
            "published_at",
            "is_published",
        ]

    def get_excerpt(self, obj):
        content = obj.content or ""
        max_len = 180
        if len(content) <= max_len:
            return content
        return f"{content[:max_len].rstrip()}..."

    def get_cover_image(self, obj):
        if obj.featured_image:
            request = self.context.get("request")
            if request is not None:
                return request.build_absolute_uri(obj.featured_image.url)
            return obj.featured_image.url
        return None


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = [
            "id",
            "customer_name",
            "role_or_business",
            "quote",
            "is_featured",
            "created_at",
        ]


class HeroMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroMetric
        fields = [
            "partner_farmers_count",
            "avg_delivery_window",
            "repeat_customer_rate",
            "last_updated",
        ]


class BenefitItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BenefitItem
        fields = ["title", "description", "display_order"]


class BenefitSectionSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = BenefitSection
        fields = ["title", "description", "items"]

    def get_items(self, obj):
        items = obj.items.filter(is_active=True).order_by("display_order", "id")
        return BenefitItemSerializer(items, many=True).data


class FooterContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = FooterContact
        fields = [
            "phone",
            "whatsapp",
            "email",
            "office_location_text",
            "office_map_url",
        ]
