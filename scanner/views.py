from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.conf import settings
import os
from .models import Document

def home(request):
    documents = Document.objects.order_by('-uploaded_at')[:10]
    return render(request, 'scanner/home.html', {'documents': documents})

def upload(request):
    return render(request, 'scanner/upload.html')

def document_detail(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    return render(request, 'scanner/document_detail.html', {'document': document})

@csrf_exempt
def api_upload(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        file = request.FILES.get('file')
        
        if not file:
            return JsonResponse({'success': False, 'error': 'No file uploaded'}, status=400)
            
        document = Document.objects.create(title=title, file=file)
        
        # Extract metadata
        metadata = {
            'file_size': file.size,
            'file_extension': os.path.splitext(file.name)[1].lower(),
            'upload_date': document.uploaded_at.isoformat()
        }
        document.metadata = metadata
        document.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
