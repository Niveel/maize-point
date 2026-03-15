from django.urls import path

from .views import (
    AnnouncementPreviewView,
    BenefitSectionListView,
    FooterContactView,
    HeroMetricView,
    HomepageProductPreviewView,
    TestimonialListView,
)

app_name = "homepage"

urlpatterns = [
    path("products-preview/", HomepageProductPreviewView.as_view(), name="products_preview"),
    path(
        "announcements-preview/",
        AnnouncementPreviewView.as_view(),
        name="announcements_preview",
    ),
    path("testimonials/", TestimonialListView.as_view(), name="testimonials"),
    path("hero-metrics/", HeroMetricView.as_view(), name="hero_metrics"),
    path("benefits/", BenefitSectionListView.as_view(), name="benefits"),
    path("footer-contact/", FooterContactView.as_view(), name="footer_contact"),
]
