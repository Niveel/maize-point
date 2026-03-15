from django.contrib import admin

from .models import BenefitItem, BenefitSection, FooterContact, HeroMetric, Testimonial


class BenefitItemInline(admin.TabularInline):
    model = BenefitItem
    extra = 1


@admin.register(BenefitSection)
class BenefitSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active", "updated_at"]
    list_filter = ["is_active", "updated_at"]
    search_fields = ["title", "description"]
    inlines = [BenefitItemInline]


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ["customer_name", "role_or_business", "is_featured", "is_published", "created_at"]
    list_filter = ["is_featured", "is_published", "created_at"]
    search_fields = ["customer_name", "role_or_business", "quote"]


@admin.register(HeroMetric)
class HeroMetricAdmin(admin.ModelAdmin):
    list_display = ["partner_farmers_count", "avg_delivery_window", "repeat_customer_rate", "last_updated"]


@admin.register(FooterContact)
class FooterContactAdmin(admin.ModelAdmin):
    list_display = ["email", "phone", "whatsapp", "updated_at", "is_active"]
    list_filter = ["is_active", "updated_at"]
