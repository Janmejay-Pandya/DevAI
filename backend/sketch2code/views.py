import os
import uuid
import base64
from rest_framework.decorators import api_view
from rest_framework.response import Response
from PIL import Image
from io import BytesIO
from agents.designer_agent import generate_ui_from_image
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes


@api_view(["POST"])
@permission_classes([AllowAny])
def upload_sketch(request):
    image_data = request.data.get("image")

    if not image_data:
        return Response({"error": "No image provided"}, status=400)

    try:
        # Strip the base64 header
        format, imgstr = image_data.split(";base64,")
        ext = format.split("/")[-1]
        img_data = base64.b64decode(imgstr)

        # Save to file (optional)
        filename = f"sketch_{uuid.uuid4()}.{ext}"
        filepath = os.path.join("media/sketches", filename)
        filepath = os.path.abspath(filepath)
        image = Image.open(BytesIO(img_data))
        image.save(f"media/sketches/{filename}")

        print("Processing Sketch!")
        llm_response = generate_ui_from_image(filepath)

        return Response(
            {
                "message": "Image received and processed",
                "filename": filename,
                "llm_output": llm_response,
            }
        )

    except Exception as e:
        return Response({"error": str(e)}, status=500)
