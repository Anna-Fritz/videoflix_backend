from rest_framework import serializers
from ..models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Includes all key fields and returns the full URL of the thumbnail if available"""
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'category', 'thumbnail_url', 'created_at']

    def get_thumbnail_url(self, obj):
        if obj.thumbnail_url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail_url.url)
            return f"http://127.0.0.1:8000{obj.thumbnail_url.url}"
        return None
