from django.db import models


class HeroMetric(models.Model):
    """Singleton-style model for homepage hero metrics."""

    partner_farmers_count = models.PositiveIntegerField(default=0)
    avg_delivery_window = models.CharField(max_length=100, default="24-48 hours")
    repeat_customer_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hero_metrics"

    def __str__(self):
        return f"Hero Metrics ({self.last_updated:%Y-%m-%d})"


class BenefitSection(models.Model):
    """Top-level container for benefits/how-it-works content."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "benefit_sections"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title


class BenefitItem(models.Model):
    """Ordered benefit item under a section."""

    section = models.ForeignKey(
        BenefitSection, on_delete=models.CASCADE, related_name="items"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    display_order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "benefit_items"
        ordering = ["display_order", "id"]
        indexes = [models.Index(fields=["section", "display_order"])]

    def __str__(self):
        return f"{self.section.title} - {self.title}"


class Testimonial(models.Model):
    """Homepage testimonial cards."""

    customer_name = models.CharField(max_length=200)
    role_or_business = models.CharField(max_length=255, blank=True)
    quote = models.TextField()
    is_featured = models.BooleanField(default=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "testimonials"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_featured", "is_published"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.customer_name} testimonial"


class FooterContact(models.Model):
    """Singleton-style contact information rendered in footer."""

    phone = models.CharField(max_length=50, blank=True)
    whatsapp = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    office_location_text = models.TextField(blank=True)
    office_map_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "footer_contacts"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.email or "Footer Contact"
