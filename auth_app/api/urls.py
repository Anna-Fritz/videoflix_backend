from django.urls import path

from .views import RegistrationView, CookieRefreshView, CookieEmailLoginView, activate_account, \
    LogoutView


urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', CookieEmailLoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CookieRefreshView.as_view(), name='token_refresh'),
    path('activate/<str:uidb64>/<uuid:token>/', activate_account, name='activate_account'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
