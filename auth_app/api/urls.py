from django.urls import path

from .views import RegistrationView, CookieLoginView, CookieRefreshView


urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', CookieLoginView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', CookieRefreshView.as_view(), name='token_refresh'),
]
