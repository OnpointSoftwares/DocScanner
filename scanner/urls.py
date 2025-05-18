from django.urls import path
from . import views

app_name = 'scanner'

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload, name='upload'),
    path('document/<int:document_id>/', views.document_detail, name='document_detail'),
    path('api/upload/', views.api_upload, name='api_upload'),
]
