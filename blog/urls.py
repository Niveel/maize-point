from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlogPostViewSet

router = DefaultRouter()
router.register(r'', BlogPostViewSet, basename='blogpost')

app_name = 'blog'

urlpatterns = [
    path('', include(router.urls)),
]
