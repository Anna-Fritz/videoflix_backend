from django.urls import path
from rest_framework_simplejwt.views import (
    # TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegistrationView, CookieLoginView


urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', CookieLoginView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
