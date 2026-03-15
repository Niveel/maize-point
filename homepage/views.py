from rest_framework import permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView

from blog.models import BlogPost
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
