from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FarmerViewSet

router = DefaultRouter()
router.register(r'', FarmerViewSet, basename='farmer')

app_name = 'farmers'

urlpatterns = [
    path('', include(router.urls)),
]
