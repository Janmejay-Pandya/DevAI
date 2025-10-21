from django.urls import path
from .views import get_deployed_url, update_development_stage_pages

urlpatterns = [
    path("<int:chat_id>/deployed-url/", get_deployed_url, name="get-deployed-url"),
    path(
        "update-development-pages/<int:chat_id>/",
        update_development_stage_pages,
        name="update-development-pages",
    ),
]
