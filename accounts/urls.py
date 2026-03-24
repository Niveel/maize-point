from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView,
    ProfileView, ChangePasswordView, NotificationPreferenceView, ProfilePictureView
)

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', ProfileView.as_view(), name='me'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile-picture/', ProfilePictureView.as_view(), name='profile_picture'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('notification-preferences/', NotificationPreferenceView.as_view(), name='notification_preferences'),
]
