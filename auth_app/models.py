from django.db import models
from django.conf import settings
import uuid
import base64

# Create your models here.


class EmailConfirmationToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_encoded_user_id(self):
        """returns base64-coded user-ID"""
        user_id_bytes = str(self.user.id).encode('utf-8')
        return base64.b64encode(user_id_bytes).decode('utf-8')

    def __str__(self):
        return f"Token für {self.user.username}"