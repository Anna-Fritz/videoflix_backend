import os
from django.http import HttpResponse
from django.conf import settings
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def video_manifest(request, movie_id, resolution):
    """Authenticated API endpoint that returns the HLS manifest file for a completed video at a specified resolution."""
    try:
        video = Video.objects.get(id=movie_id, processing_status='completed')
    except Video.DoesNotExist:
        return Response({"detail": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

    # Determines the appropriate HLS path according to the requested resolution.
    resolution_map = {
        '480p': video.hls_480p_path,
        '720p': video.hls_720p_path,
        '1080p': video.hls_1080p_path,
    }

    hls_path = resolution_map.get(resolution)
    if not hls_path:
        return Response({"detail": "Resolution not available"}, status=status.HTTP_404_NOT_FOUND)

    manifest_file = os.path.join(settings.MEDIA_ROOT, hls_path, 'index.m3u8')

    if not os.path.exists(manifest_file):
        return Response({"detail": "Manifest file not found"}, status=status.HTTP_404_NOT_FOUND)

    with open(manifest_file, 'r') as f:
        content = f.read()

    response = HttpResponse(content, content_type='application/vnd.apple.mpegurl')
    response['Content-Disposition'] = 'inline'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def video_segment(request, movie_id, resolution, segment):
    """Serves a specific video segment (.ts) file for a completed video at the requested resolution."""
    try:
        video = Video.objects.get(id=movie_id, processing_status='completed')
    except Video.DoesNotExist:
        return Response({"detail": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

    resolution_map = {
        '480p': video.hls_480p_path,
        '720p': video.hls_720p_path,
        '1080p': video.hls_1080p_path,
    }

    hls_path = resolution_map.get(resolution)
    if not hls_path:
        return Response({"detail": "Resolution not available"}, status=status.HTTP_404_NOT_FOUND)

    segment_file = os.path.join(settings.MEDIA_ROOT, hls_path, segment)

    if not os.path.exists(segment_file):
        return Response({"detail": "Segment file not found"}, status=status.HTTP_404_NOT_FOUND)

    with open(segment_file, 'rb') as f:
        content = f.read()

    response = HttpResponse(content, content_type='video/MP2T')
    response['Content-Disposition'] = 'inline'
    return response
