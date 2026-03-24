from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta

from blog.models import BlogPost
from customers.serializers import CustomerSerializer
from farmers.models import Farmer, FarmerSupply
from farmers.serializers import FarmerSerializer
from inventory.models import Stock, StockMovement
from inventory.serializers import StockMovementSerializer, StockSerializer
from orders.models import Order
from orders.serializers import OrderSerializer
from products.models import Product

from .models import BenefitSection, FooterContact, HeroMetric, Testimonial
from .serializers import (
    AnnouncementPreviewSerializer,
    BenefitSectionSerializer,
    FooterContactSerializer,
    HeroMetricSerializer,
    HomepageProductPreviewSerializer,
    TestimonialSerializer,
)


class HomepageProductPreviewView(ListAPIView):
    """Public homepage product cards with contract-specific shape."""

    serializer_class = HomepageProductPreviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Product.objects.all().order_by("-updated_at")
        featured = self.request.query_params.get("featured")
        if featured == "true":
            queryset = queryset.filter(is_available=True)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        limit = self.request.query_params.get("limit")
        if limit:
            try:
                parsed_limit = max(1, min(int(limit), 50))
                queryset = queryset[:parsed_limit]
            except ValueError:
                pass
        serializer = self.get_serializer(queryset, many=True)
        from rest_framework.response import Response

        return Response(serializer.data)


class AnnouncementPreviewView(ListAPIView):
    """Public announcement/blog preview cards."""

    serializer_class = AnnouncementPreviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = BlogPost.objects.all().order_by("-published_at", "-created_at")
        published = self.request.query_params.get("published")
        if published is None or published == "true":
            queryset = queryset.filter(is_published=True)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        limit = self.request.query_params.get("limit")
        if limit:
            try:
                parsed_limit = max(1, min(int(limit), 50))
                queryset = queryset[:parsed_limit]
            except ValueError:
                pass
        serializer = self.get_serializer(queryset, many=True)
        from rest_framework.response import Response

        return Response(serializer.data)


class TestimonialListView(ListAPIView):
    serializer_class = TestimonialSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Testimonial.objects.filter(is_published=True).order_by("-created_at")
        is_featured = self.request.query_params.get("is_featured")
        if is_featured == "true":
            queryset = queryset.filter(is_featured=True)
        return queryset


class HeroMetricView(RetrieveAPIView):
    serializer_class = HeroMetricSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        metric = HeroMetric.objects.order_by("-last_updated").first()
        if metric is None:
            metric = HeroMetric.objects.create()
        return metric


class BenefitSectionListView(ListAPIView):
    serializer_class = BenefitSectionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return BenefitSection.objects.filter(is_active=True).order_by("-updated_at")


class FooterContactView(RetrieveAPIView):
    serializer_class = FooterContactSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        contact = FooterContact.objects.filter(is_active=True).order_by("-updated_at").first()
        if contact is None:
            contact = FooterContact.objects.create()
        return contact


class DashboardOverviewView(APIView):
    """
    Single endpoint dashboard payload.

    - ADMIN/STAFF: business metrics, alerts, recent orders/movements/farmers
    - CUSTOMER: profile metrics + recent own orders + hero metrics
    """

    permission_classes = [permissions.IsAuthenticated]
    recent_limit = 5

    def get(self, request):
        user = request.user
        payload = {
            "role": user.user_type,
            "generated_at": timezone.now(),
        }

        if user.user_type in ["ADMIN", "STAFF"]:
            payload.update(self._build_admin_staff_payload(request))
        else:
            payload.update(self._build_customer_payload(request))

        return Response(payload)

    def _build_admin_staff_payload(self, request):
        today = timezone.now().date()
        expiry_cutoff = today + timedelta(days=30)

        supplies_summary = FarmerSupply.objects.aggregate(
            total_supplies=Sum("quantity_bags"),
            total_cost=Sum("total_cost"),
            total_paid=Sum("amount_paid"),
        )

        order_summary = Order.objects.aggregate(
            total_orders=Count("id"),
            pending_orders=Count("id", filter=Q(order_status="PENDING")),
            processing_orders=Count("id", filter=Q(order_status="PROCESSING")),
            dispatched_orders=Count("id", filter=Q(order_status="DISPATCHED")),
            delivered_orders=Count("id", filter=Q(order_status="DELIVERED")),
            cancelled_orders=Count("id", filter=Q(order_status="CANCELLED")),
            total_revenue=Sum("total_price", filter=Q(order_status="DELIVERED")),
        )

        inventory_summary = Stock.objects.aggregate(
            total_bags=Sum("quantity_bags"),
            total_tons=Sum("quantity_tons"),
            low_stock_count=Count("id", filter=Q(quantity_bags__lt=100)),
            expiring_soon_count=Count(
                "id",
                filter=Q(expiry_alert_date__gte=today, expiry_alert_date__lte=expiry_cutoff),
            ),
        )

        low_stock = (
            Stock.objects.select_related("product", "farmer")
            .filter(quantity_bags__lt=100)
            .order_by("quantity_bags", "date_received")[: self.recent_limit]
        )
        expiring_soon = (
            Stock.objects.select_related("product", "farmer")
            .filter(expiry_alert_date__gte=today, expiry_alert_date__lte=expiry_cutoff)
            .order_by("expiry_alert_date", "date_received")[: self.recent_limit]
        )

        recent_orders = Order.objects.select_related(
            "customer__user", "product", "approved_by"
        ).order_by("-created_at")[: self.recent_limit]
        recent_movements = StockMovement.objects.select_related(
            "stock__product", "performed_by"
        ).order_by("-created_at")[: self.recent_limit]
        recent_farmers = Farmer.objects.select_related("created_by").order_by("-created_at")[
            : self.recent_limit
        ]

        return {
            "metrics": {
                "farmers": {
                    "total_farmers": Farmer.objects.count(),
                    "approved_farmers": Farmer.objects.filter(is_approved=True).count(),
                    "active_farmers": Farmer.objects.filter(is_active=True).count(),
                    "supplies_summary": supplies_summary,
                },
                "orders": order_summary,
                "inventory": inventory_summary,
            },
            "alerts": {
                "low_stock": StockSerializer(low_stock, many=True).data,
                "expiring_soon": StockSerializer(expiring_soon, many=True).data,
            },
            "recent_activity": {
                "orders": OrderSerializer(recent_orders, many=True, context={"request": request}).data,
                "stock_movements": StockMovementSerializer(
                    recent_movements, many=True
                ).data,
                "farmers": FarmerSerializer(recent_farmers, many=True).data,
            },
        }

    def _build_customer_payload(self, request):
        customer_profile = getattr(request.user, "customer_profile", None)
        hero_metrics = HeroMetric.objects.order_by("-last_updated").first()
        if hero_metrics is None:
            hero_metrics = HeroMetric.objects.create()

        if customer_profile is None:
            return {
                "metrics": {
                    "orders": {
                        "total_orders": 0,
                        "pending_orders": 0,
                        "processing_orders": 0,
                        "dispatched_orders": 0,
                        "delivered_orders": 0,
                        "cancelled_orders": 0,
                        "total_spent": "0.00",
                    },
                    "hero": HeroMetricSerializer(hero_metrics).data,
                },
                "profile": None,
                "recent_activity": {"orders": []},
                "alerts": {},
            }

        customer_orders = Order.objects.filter(customer=customer_profile)
        order_metrics = customer_orders.aggregate(
            total_orders=Count("id"),
            pending_orders=Count("id", filter=Q(order_status="PENDING")),
            processing_orders=Count("id", filter=Q(order_status="PROCESSING")),
            dispatched_orders=Count("id", filter=Q(order_status="DISPATCHED")),
            delivered_orders=Count("id", filter=Q(order_status="DELIVERED")),
            cancelled_orders=Count("id", filter=Q(order_status="CANCELLED")),
            total_spent=Sum("total_price", filter=Q(order_status="DELIVERED")),
        )

        recent_orders = (
            Order.objects.select_related("customer__user", "product", "approved_by")
            .filter(customer=customer_profile)
            .order_by("-created_at")[: self.recent_limit]
        )

        return {
            "metrics": {
                "orders": order_metrics,
                "hero": HeroMetricSerializer(hero_metrics).data,
            },
            "profile": CustomerSerializer(customer_profile).data,
            "recent_activity": {
                "orders": OrderSerializer(recent_orders, many=True, context={"request": request}).data
            },
            "alerts": {},
        }
