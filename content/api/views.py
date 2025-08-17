from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..models import Video
from .serializers import VideoSerializer


class VideoListView(generics.ListAPIView):
    """List all completed videos"""
    queryset = Video.objects.filter(processing_status='completed')
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

