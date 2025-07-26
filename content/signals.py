import os
import glob
import django_rq

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import Video
from .tasks import convert_all_resolutions


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print('video saved')
    if created and instance.video_file:
        try:
            queue = django_rq.get_queue('default', autocommit=True)
            queue.enqueue(convert_all_resolutions, instance.video_file.path)
        except Exception as e:
            print(f"Error during video conversion: {e}")


@receiver(post_delete, sender=Video)
def auto_delete_on_delete(sender, instance, **kwargs):
    if instance.video_file and os.path.isfile(instance.video_file.path):
        os.remove(instance.video_file.path)

        base_path = os.path.splitext(instance.video_file.path)[0]
        for file in glob.glob(f"{base_path}_*.mp4"):
            os.remove(file)
