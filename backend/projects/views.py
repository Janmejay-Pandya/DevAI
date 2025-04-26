from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Project

@api_view(['GET'])
def get_deployed_url(request, chat_id):
    try:
        project = Project.objects.get(chat__id=chat_id)
        return Response({
            "deployed_url": project.deployed_url
        })
    except Project.DoesNotExist:
        return Response({"error": "Project not found"}, status=404)

