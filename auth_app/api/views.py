from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

from .serializers import RegistrationSerializer, CustomTokenObtainPairSerializer
from ..models import EmailConfirmationToken
import base64

User = get_user_model()


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()

            token = EmailConfirmationToken.objects.create(user=saved_account)

            send_activation_email(saved_account, token)

            data = {
                'user': {
                    'id': saved_account.pk,
                    'email': saved_account.email
                },
                'token': token.token
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            print(f"❌ Serializer Fehler: {serializer.errors}")
            return Response({
                'error': 'Email or Password is invalid'
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def activate_account(request, uidb64, token):
    """
    Activates user account with token send by mail
    URL: /api/activate/<uidb64>/<token>/
    """
    try:
        # decode user-ID from base64
        user_id = base64.b64decode(uidb64).decode('utf-8')
        user = get_object_or_404(User, id=user_id)

        # validate token
        confirmation_token = get_object_or_404(
            EmailConfirmationToken,
            user=user,
            token=token
        )

        # check if user is active
        if user.is_active:
            return Response({
                'message': 'Account is already activated.'
            }, status=status.HTTP_200_OK)

        # activate user
        user.is_active = True
        user.save()

        # delete token
        confirmation_token.delete()

        return Response({
            'message': 'Account successfully activated.'
        }, status=status.HTTP_200_OK)

    except (ValueError, User.DoesNotExist, EmailConfirmationToken.DoesNotExist):
        return Response({
            'error': 'Invalid activation link or token expired.'
        }, status=status.HTTP_400_BAD_REQUEST)


def send_activation_email(user, token):
    """Sendet Aktivierungsmail an den User"""
    subject = 'Aktiviere dein Konto'

    # create base64-coded user-ID
    uidb64 = token.get_encoded_user_id()

    # create activation url
    activation_url = f"{settings.SITE_URL}/api/activate/{uidb64}/{token.token}/"

    message = f"""
    Hallo {user.username},

    bitte aktiviere dein Konto, indem du auf folgenden Link klickst:
    {activation_url}

    Falls du dich nicht registriert hast, ignoriere diese E-Mail.

    Viele Grüße
    Dein Team
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


class CookieLoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh = response.data.get("refresh")
        access = response.data.get("access")

        response.set_cookie(
            key="access_token",
            value=access,
            httponly=True,
            secure=True,        # better safe in .env file
            samesite="Lax"
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=True,
            samesite="Lax"
        )

        response.data = {"message": "login successfull"}
        return response


class CookieRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response(
                {"detail": "Refresh token invalid!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = serializer.validated_data.get('access')

        response = Response({"message": "access Token refreshed"})

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax"
        )

        return response


class CookieEmailLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh = serializer.validated_data["refresh"]
        access = serializer.validated_data["access"]

        response = Response({"message": "login successfull"})

        response.set_cookie(
            key="access_token",
            value=str(access),
            httponly=True,
            secure=True,        # better safe in .env file
            samesite="Lax"
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="Lax"
        )

        return response
