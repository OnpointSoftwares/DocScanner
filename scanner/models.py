from django.db import models
from django.utils import timezone

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return self.title
