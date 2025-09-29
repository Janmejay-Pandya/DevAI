from django.urls import path
from .views import upload_sketch

urlpatterns = [
    path('upload-sketch/', upload_sketch, name='upload-sketch'),
]
