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

def edit_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    return render(request, 'scanner/edit.html', {
        'document': document,
        'undo_edit_url': reverse('scanner:undo', args=[document_id]),
        'redo_edit_url': reverse('scanner:redo', args=[document_id]),
        'preview_url': reverse('scanner:preview', args=[document_id]),
        'original_url': reverse('scanner:original', args=[document_id]),
        'download_url': reverse('scanner:download', args=[document_id])
    })

@csrf_exempt
def update_document(request, document_id):
    if request.method == 'POST':
        document = get_object_or_404(Document, pk=document_id)
        
        # Update editing parameters
        document.rotation = float(request.POST.get('rotation', document.rotation))
        document.brightness = float(request.POST.get('brightness', document.brightness))
        document.contrast = float(request.POST.get('contrast', document.contrast))
        document.grayscale = bool(request.POST.get('grayscale', document.grayscale))
        document.sepia = bool(request.POST.get('sepia', document.sepia))
        document.vintage = bool(request.POST.get('vintage', document.vintage))
        document.crop_x = int(request.POST.get('crop_x', document.crop_x))
        document.crop_y = int(request.POST.get('crop_y', document.crop_y))
        document.crop_width = int(request.POST.get('crop_width', document.crop_width))
        document.crop_height = int(request.POST.get('crop_height', document.crop_height))
        document.width = int(request.POST.get('width', document.width))
        document.height = int(request.POST.get('height', document.height))
        document.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

def preview_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    
    # Open the image
    image_path = document.file.path
    image = Image.open(image_path)
    
    # Apply transformations
    if document.crop_width > 0 and document.crop_height > 0:
        image = image.crop((document.crop_x, document.crop_y,
                          document.crop_x + document.crop_width,
                          document.crop_y + document.crop_height))
    
    if document.width > 0 and document.height > 0:
        image = image.resize((document.width, document.height))
    
    if document.rotation != 0:
        image = image.rotate(document.rotation, expand=True)
    
    if document.grayscale:
        image = image.convert('L')
    
    if document.sepia:
        # Apply sepia filter
        sepia = ImageEnhance.Color(image)
        image = sepia.enhance(0.8)
        
    if document.vintage:
        # Apply vintage filter
        vintage = ImageEnhance.Color(image)
        image = vintage.enhance(0.7)
        
    # Save the transformed image temporarily
    temp_path = os.path.join(settings.MEDIA_ROOT, f'temp_{document_id}.jpg')
    image.save(temp_path, 'JPEG')
    
    # Return the URL of the transformed image
    return JsonResponse({
        'success': True,
        'preview_url': request.build_absolute_uri(f'/media/temp_{document_id}.jpg')
    })

@csrf_exempt
def original_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    return JsonResponse({
        'success': True,
        'original_url': request.build_absolute_uri(document.file.url)
    })

@csrf_exempt
def download_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    file_path = document.file.path
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    return JsonResponse({'success': False, 'error': 'File not found'}, status=404)

@csrf_exempt
def undo_edit(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    
    # Reset all editing parameters to defaults
    document.rotation = 0
    document.brightness = 1.0
    document.contrast = 1.0
    document.grayscale = False
    document.sepia = False
    document.vintage = False
    document.crop_x = 0
    document.crop_y = 0
    document.crop_width = 0
    document.crop_height = 0
    document.width = 0
    document.height = 0
    document.save()
    
    return JsonResponse({'success': True})

@csrf_exempt
def redo_edit(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    
    # Get the last saved state from the request
    if request.method == 'POST':
        try:
            data = request.POST
            document.rotation = float(data.get('rotation', document.rotation))
            document.brightness = float(data.get('brightness', document.brightness))
            document.contrast = float(data.get('contrast', document.contrast))
            document.grayscale = bool(data.get('grayscale', document.grayscale))
            document.sepia = bool(data.get('sepia', document.sepia))
            document.vintage = bool(data.get('vintage', document.vintage))
            document.crop_x = int(data.get('crop_x', document.crop_x))
            document.crop_y = int(data.get('crop_y', document.crop_y))
            document.crop_width = int(data.get('crop_width', document.crop_width))
            document.crop_height = int(data.get('crop_height', document.crop_height))
            document.width = int(data.get('width', document.width))
            document.height = int(data.get('height', document.height))
            document.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
        sepia_filter = ImageEnhance.Color(image)
        image = sepia_filter.enhance(0.5)
        
        # Apply sepia tone
        sepia_matrix = (
            0.393, 0.769, 0.189, 0,
            0.349, 0.686, 0.168, 0,
            0.272, 0.534, 0.131, 0
        )
        image = image.convert('RGB', sepia_matrix)
    
    if document.vintage:
        # Apply vintage effect
        image = image.filter(ImageFilter.GaussianBlur(radius=1))
        
        # Add vignette effect
        width, height = image.size
        vignette = Image.new('L', (width, height), 255)
        draw = ImageDraw.Draw(vignette)
        draw.ellipse((0, 0, width, height), fill=0)
        vignette = vignette.filter(ImageFilter.GaussianBlur(radius=width/2))
        image = Image.composite(image, image, vignette)
    
    if document.brightness != 1.0 or document.contrast != 1.0:
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(document.brightness)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(document.contrast)
    
    # Convert to JPEG
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    buffer.seek(0)
    
    return HttpResponse(buffer.getvalue(), content_type='image/jpeg')

def original_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    return HttpResponse(document.file.read(), content_type='image/jpeg')

def download_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    response = HttpResponse(document.file.read(), content_type='image/jpeg')
    response['Content-Disposition'] = f'attachment; filename="{document.title}.jpg"'
    return response

@csrf_exempt
def undo_edit(request, document_id):
    if request.method == 'POST':
        document = get_object_or_404(Document, pk=document_id)
        # Reset all editing parameters
        document.rotation = 0
        document.brightness = 1.0
        document.contrast = 1.0
        document.grayscale = False
        document.sepia = False
        document.vintage = False
        document.crop_x = 0
        document.crop_y = 0
        document.crop_width = 0
        document.crop_height = 0
        document.width = 0
        document.height = 0
        document.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@csrf_exempt
def redo_edit(request, document_id):
    if request.method == 'POST':
        document = get_object_or_404(Document, pk=document_id)
        # Apply all editing parameters
        document.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
