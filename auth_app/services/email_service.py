from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings


class EmailService:
    """
    Service for sending emails
    currently: Password Reset + Registration Confirmation
    """

    @staticmethod
    def send_password_reset_email(user):
        """Sends Password Reset Email"""
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"{settings.SITE_URL}/pages/auth/confirm_password.html?uid={uidb64}&token={token}"

        context = {
            'user': user,
            'reset_url': reset_url,
            'site_name': getattr(settings, 'SITE_NAME', 'Ihre Website'),
        }

        EmailService._send_templated_email(
            template_name='password_reset',
            subject='Passwort zurücksetzen',
            recipient=user.email,
            context=context
        )

    @staticmethod
    def send_registration_confirmation_email(user, token):
        """Sendet Registrierungs-Bestätigungs E-Mail"""
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        confirmation_url = f"{settings.SITE_URL}/pages/auth/activate.html?uid={uidb64}&token={token}"

        context = {
            'user': user,
            'confirmation_url': confirmation_url,
            'site_name': getattr(settings, 'SITE_NAME', 'Ihre Website'),
        }

        EmailService._send_templated_email(
            template_name='registration_confirmation',
            subject='Account bestätigen',
            recipient=user.email,
            context=context
        )

    @staticmethod
    def _send_templated_email(template_name, subject, recipient, context):
        """
        Private Methode für Template-basierte E-Mails
        DRY: Gemeinsame Logic für beide E-Mail-Typen
        """
        try:
            message = render_to_string(f'auth_app/emails/{template_name}.txt', context)

            try:
                html_message = render_to_string(f'auth_app/emails/{template_name}.html', context)
            except Exception:
                html_message = None

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                html_message=html_message,
                fail_silently=False,
            )

        except Exception as e:
            # for logging
            print(f"E-Mail-Versand fehlgeschlagen: {e}")
            raise