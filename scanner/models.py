from django.db import models
from django.utils import timezone

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict)
    
    # Image editing fields
    rotation = models.FloatField(default=0)  # degrees
    brightness = models.FloatField(default=1.0)  # 0.0 to 2.0
    contrast = models.FloatField(default=1.0)  # 0.0 to 2.0
    grayscale = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    def get_edit_url(self):
        return reverse('scanner:edit', args=[self.pk])
    
    def get_preview_url(self):
        return reverse('scanner:preview', args=[self.pk])
