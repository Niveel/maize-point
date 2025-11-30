from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StockViewSet, StockMovementViewSet

router = DefaultRouter()
router.register(r'stock', StockViewSet, basename='stock')
router.register(r'movements', StockMovementViewSet, basename='movement')

app_name = 'inventory'

urlpatterns = [
    path('', include(router.urls)),
]
