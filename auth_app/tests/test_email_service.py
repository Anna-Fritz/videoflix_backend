from django.test import TestCase
from django.core import mail
from django.contrib.auth import get_user_model
from services.email_service import EmailService

User = get_user_model()


class EmailServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_password_reset_email(self):
        EmailService.send_password_reset_email(self.user)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Passwort zurücksetzen', mail.outbox[0].subject)
        self.assertIn('reset', mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, [self.user.email])

    def test_registration_confirmation_email(self):
        EmailService.send_registration_confirmation_email(self.user)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('bestätigen', mail.outbox[0].subject)
        self.assertIn('confirmation', mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, [self.user.email])

    def test_email_contains_proper_links(self):
        EmailService.send_password_reset_email(self.user)

        email_body = mail.outbox[0].body
        self.assertIn('password-reset-confirm', email_body)
        self.assertIn('http://localhost:3000', email_body)


class PasswordResetAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_password_reset_existing_email(self):
        response = self.client.post('/api/password_reset/', {
            'email': 'test@example.com'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('reset', mail.outbox[0].subject.lower())

    def test_password_reset_nonexisting_email(self):
        response = self.client.post('/api/password_reset/', {
            'email': 'nonexistent@example.com'
        })

        # should return 200 anyway (Security)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_invalid_email_format(self):
        response = self.client.post('/api/password_reset/', {
            'email': 'invalid-email'
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)
