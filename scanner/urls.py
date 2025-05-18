from django.urls import path
from . import views

app_name = 'scanner'

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload, name='upload'),
    path('document/<int:document_id>/', views.document_detail, name='document_detail'),
    path('api/upload/', views.api_upload, name='api_upload'),
    path('edit/<int:document_id>/', views.edit_document, name='edit'),
    path('preview/<int:document_id>/', views.preview_document, name='preview'),
    path('original/<int:document_id>/', views.original_document, name='original'),
    path('download/<int:document_id>/', views.download_document, name='download'),
    path('api/undo/<int:document_id>/', views.undo_edit, name='undo'),
    path('api/redo/<int:document_id>/', views.redo_edit, name='redo'),
]
