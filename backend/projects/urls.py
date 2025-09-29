from django.urls import path
from .views import get_deployed_url

urlpatterns = [
    path("<int:chat_id>/deployed-url/", get_deployed_url, name="get-deployed-url"),
]
