from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer
import os
from django.conf import settings

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Extract metadata (basic for now, can be expanded)
        document = serializer.instance
        metadata = {
            'file_size': os.path.getsize(document.file.path),
            'file_extension': os.path.splitext(document.file.name)[1].lower(),
            'upload_date': document.uploaded_at.isoformat()
        }
        document.metadata = metadata
        document.save()
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
