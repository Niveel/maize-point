from django.db.models import Case, Count, IntegerField, OuterRef, Q, Subquery, Value, When
from rest_framework import permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from pricing.models import Price

from .models import Product, ProductCategory
from .serializers import ProductCategorySerializer, ProductSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """Custom permission: Allow read-only for anyone, write for admins only."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.user_type == "ADMIN"


class ProductPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for products with URL-query contract support."""

    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = ProductPagination

    def list(self, request, *args, **kwargs):
        validation_error = self._validate_query_params(request)
        if validation_error is not None:
            return validation_error

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = Product.objects.select_related("category").all()

        current_prices = Price.objects.filter(
            product=OuterRef("pk"), is_current=True
        ).order_by("-effective_date")
        queryset = queryset.annotate(
            current_price_per_bag=Subquery(current_prices.values("price_per_bag")[:1]),
            current_price_per_ton=Subquery(current_prices.values("price_per_ton")[:1]),
            featured_rank=Case(
                When(availability_status="AVAILABLE", then=Value(3)),
                When(availability_status="LOW_STOCK", then=Value(2)),
                default=Value(1),
                output_field=IntegerField(),
            ),
        )

        q = self.request.query_params.get("q")
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q)
                | Q(maize_type__icontains=q)
                | Q(description__icontains=q)
                | Q(category__name__icontains=q)
            )

        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(
                Q(category__slug__iexact=category) | Q(category__name__iexact=category)
            )

        availability = self.request.query_params.get("availability")
        if availability:
            queryset = queryset.filter(availability_status=availability.upper())

        sort = self.request.query_params.get("sort", "featured")
        order_map = {
            "featured": ["-featured_rank", "-updated_at", "id"],
            "price_asc": ["current_price_per_ton", "name", "id"],
            "price_desc": ["-current_price_per_ton", "name", "id"],
            "name_asc": ["name", "id"],
            "name_desc": ["-name", "id"],
        }
        return queryset.order_by(*order_map.get(sort, order_map["featured"]))

    def _validate_query_params(self, request):
        page_size_raw = request.query_params.get("page_size")
        if page_size_raw is not None:
            try:
                page_size_val = int(page_size_raw)
            except ValueError:
                return Response(
                    {"errors": {"page_size": ["Must be an integer"]}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if page_size_val < 1 or page_size_val > 100:
                return Response(
                    {"errors": {"page_size": ["Must be between 1 and 100"]}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        availability = request.query_params.get("availability")
        if availability:
            allowed = {"AVAILABLE", "LOW_STOCK", "OUT_OF_STOCK"}
            if availability.upper() not in allowed:
                return Response(
                    {"detail": "Invalid availability value."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        sort = request.query_params.get("sort")
        allowed_sorts = {"featured", "price_asc", "price_desc", "name_asc", "name_desc"}
        if sort and sort not in allowed_sorts:
            return Response(
                {
                    "errors": {
                        "sort": [
                            "Must be one of featured, price_asc, price_desc, name_asc, name_desc"
                        ]
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None


class ProductCategoryListViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return ProductCategory.objects.order_by("name").annotate(
            product_count=Count("products")
        )
