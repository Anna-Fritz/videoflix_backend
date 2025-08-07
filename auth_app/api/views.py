from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.http import Http404

from .serializers import RegistrationSerializer, CustomTokenObtainPairSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer
from ..authentication import CookieJWTAuthentication
from ..services.email_service import EmailService

User = get_user_model()


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()

            token = default_token_generator.make_token(saved_account)

            EmailService.send_registration_confirmation_email(saved_account, token)

            data = {
                'user': {
                    'id': saved_account.pk,
                    'email': saved_account.email
                },
                'token': token
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
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
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User, pk=uid)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Token invalid or expired.'}, status=status.HTTP_400_BAD_REQUEST)

        # check if user is active
        if user.is_active:
            return Response({
                'message': 'Account is already activated.'
            }, status=status.HTTP_200_OK)

        # activate user
        user.is_active = True
        user.save()

        return Response({
            'message': 'Account successfully activated.'
        }, status=status.HTTP_200_OK)

    # except (ValueError, User.DoesNotExist, EmailConfirmationToken.DoesNotExist):
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({
            'error': 'Invalid activation link or token expired.'
        }, status=status.HTTP_400_BAD_REQUEST)


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

        response = Response({"message": "Login successful"})
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


class LogoutView(APIView):
    permission_classes = [AllowAny]
    # authentication_classes = [CookieJWTAuthentication]
    authentication_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response(
                {"detail": "Refresh-Token is missing."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"detail": "Invalid Refresh-Token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        response = Response(
            {"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK
        )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


class PasswordResetView(APIView):
    """
    API Endpoint for sending password reset emails
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                user = User.objects.get(email=email, is_active=True)
                EmailService.send_password_reset_email(user)
            except User.DoesNotExist:
                # Return “successfully” anyway for security reasons
                # This prevents attackers from finding out which emails exist
                pass

            return Response(
                {"detail": "An email has been sent to reset your password."},
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class PasswordResetConfirmView(APIView):
    """
    POST /api/password_confirm/<uidb64>/<token>/

    Bestätigt die Passwortänderung mit dem in der E-Mail enthaltenen Token.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def get_user(self, uidb64):
        """
        Dekodiert die uidb64 und gibt den entsprechenden User zurück

        Der Prozess:
        1. uidb64 ist base64-kodiert → muss dekodiert werden
        2. Dekodiertes Ergebnis ist die User-ID als String
        3. Mit dieser ID den User aus der Datenbank holen
        """
        try:
            # Schritt 1: Base64-Dekodierung der uidb64
            uid = force_str(urlsafe_base64_decode(uidb64))

            # Schritt 2: User anhand der dekodierten ID finden
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise Http404("Link invalid or expired.")
        return user

    def validate_token(self, user, token):
        """Überprüft ob der Token für den User gültig ist"""
        if not default_token_generator.check_token(user, token):
            raise Http404("Token invalid or expired.")

    def post(self, request, uidb64, token):
        """
        Verarbeitet die Passwort-Reset-Bestätigung
        """
        try:
            # User anhand der uidb64 finden
            user = self.get_user(uidb64)

            # Token validieren
            self.validate_token(user, token)

            # Serializer validieren
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                # Passwort ändern
                serializer.save(user)

                return Response(
                    {
                        "detail": "Your Password has been successfully reset."
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Http404 as e:
            return Response(
                {
                    "detail": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                {
                    "detail": "An error has occurred. Please try again."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
