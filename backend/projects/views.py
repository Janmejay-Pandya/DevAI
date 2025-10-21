from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Project
from rest_framework import status
from .models import DevelopmentStage


@api_view(["GET"])
def get_deployed_url(request, chat_id):
    try:
        project = Project.objects.get(chat__id=chat_id)
        return Response({"deployed_url": project.deployed_url})
    except Project.DoesNotExist:
        return Response({"error": "Project not found"}, status=404)


@api_view(["PUT", "PATCH"])
def update_development_stage_pages(request, chat_id):
    try:
        project = Project.objects.get(chat__id=chat_id)
    except Project.DoesNotExist:
        return Response(
            {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
        )

    dev_stage = project.development_stage
    if dev_stage is None:
        dev_stage = DevelopmentStage.objects.create(project=project)

    data = request.data
    if data:
        dev_stage.pages = data

    try:
        dev_stage.save()
    except Exception as exc:
        return Response(
            {"error": "Failed to save development stage", "details": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {"message": "Pages data updated successfully."},
        status=status.HTTP_200_OK,
    )
