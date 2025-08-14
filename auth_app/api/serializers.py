from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import uuid
import re

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    confirmed_password = serializers.CharField(write_only=True)
    privacy_policy = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password', 'privacy_policy']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'email': {
                'required': True
            },
        }

    def validate_confirmed_password(self, value):
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError('Passwords do not match')
        return value

    def validate_email(self, value):
        # ASCII-only validation
        if not re.match(r'^[\x00-\x7F]+$', value):
            raise serializers.ValidationError('Unicode characters in email are not allowed')

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email or Password is invalid')
        return value

    def validate_privacy_policy(self, value):
        if value != "on":
            raise serializers.ValidationError('Privacy policy must be accepted')
        return value

    def save(self):
        pw = self.validated_data['password']
        email = self.validated_data['email']
        username = email.split('@')[0]

        # if username already exists → fallback to UUID
        if User.objects.filter(username=username).exists():
            username = f"{username}_{uuid.uuid4().hex[:8]}"

        account = User(email=email, username=username, is_active=False)
        account.set_password(pw)
        account.save()
        return account


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "username" in self.fields:
            self.fields.pop("username")

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Email case-insensitive
        if isinstance(email, str):
            email = email.lower()
            attrs['email'] = email

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")

        attrs['username'] = user.username
        data = super().validate(attrs)

        return data


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Email validation
        """
        return value.lower().strip()


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Das neue Passwort (mindestens 8 Zeichen)"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        help_text="Bestätigung des neuen Passworts"
    )

    def validate_new_password(self, value):
        """Validiert das neue Passwort mit Django's Standard-Validatoren"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """Überprüft ob beide Passwörter übereinstimmen"""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Die Passwörter stimmen nicht überein.'
            })
        return attrs

    def save(self, user):
        """Setzt das neue Passwort für den Benutzer"""
        password = self.validated_data['new_password']
        user.set_password(password)
        user.save()
        return user
