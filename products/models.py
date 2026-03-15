from django.db import models
from django.utils.text import slugify


class ProductCategory(models.Model):
    slug = models.SlugField(max_length=100, primary_key=True)
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "product_categories"
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product model for maize types"""

    AVAILABILITY_CHOICES = (
        ("AVAILABLE", "Available"),
        ("LOW_STOCK", "Low Stock"),
        ("OUT_OF_STOCK", "Out Of Stock"),
    )

    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Product name (e.g., Yellow Maize, White Maize)",
    )
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    maize_type = models.CharField(max_length=150, blank=True)
    description = models.TextField(help_text="Detailed product description")
    packaging_sizes = models.JSONField(
        default=list,
        help_text='List of available packaging sizes (e.g., ["50kg bag", "100kg bag", "1 ton"])',
    )
    min_order_quantity = models.CharField(max_length=50, default="1 bag")
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    availability_status = models.CharField(
        max_length=20, choices=AVAILABILITY_CHOICES, default="AVAILABLE"
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        ordering = ["name", "id"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["maize_type"]),
            models.Index(fields=["availability_status"]),
            models.Index(fields=["category"]),
            models.Index(fields=["is_available"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if not self.maize_type:
            self.maize_type = self.name
        self.is_available = self.availability_status != "OUT_OF_STOCK"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def current_stock(self):
        """Get current total stock for this product"""
        return self.stock_items.aggregate(
            total_bags=models.Sum("quantity_bags"), total_tons=models.Sum("quantity_tons")
        )

    @property
    def current_price(self):
        """Get current price for this product"""
        return self.prices.filter(is_current=True).order_by("-effective_date").first()
