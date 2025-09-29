from django.urls import path
from .views import suggest_colors, generate_website_code

urlpatterns = [
    path('suggest_colors/', suggest_colors, name='suggest_colors'),
    path('generate_website_code/', generate_website_code, name='generate_website_code'),
]
