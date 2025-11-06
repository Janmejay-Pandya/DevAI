import os
import base64
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from PIL import Image
from io import BytesIO


@api_view(["POST"])
@permission_classes([AllowAny])
def upload_sketch(request):
    """
    Accepts a base64-encoded image along with chat_id and file_name.
    Saves it under media/sketches/<chat_id>/<file_name> and returns the relative path.
    """
    image_data = request.data.get("image")
    chat_id = request.data.get("chat_id")
    file_name = request.data.get("file_name")

    if not image_data or not chat_id or not file_name:
        return Response(
            {"error": "Missing required fields: image, chat_id, or file_name"},
            status=400,
        )

    try:
        # Extract base64 part and file extension
        format, imgstr = image_data.split(";base64,")
        ext = format.split("/")[-1]
        img_data = base64.b64decode(imgstr)

        # Ensure directory exists
        save_dir = os.path.join("media", "sketches", str(chat_id))
        os.makedirs(save_dir, exist_ok=True)

        # Normalize filename to avoid injection or bad chars
        safe_name = os.path.splitext(file_name)[0]
        safe_path = os.path.join(save_dir, f"{safe_name}.{ext}")

        # Save the image
        image = Image.open(BytesIO(img_data))
        image.save(safe_path)

        # Return relative path for future processing
        relative_path = f"sketches/{chat_id}/{safe_name}.{ext}"

        return Response(
            {
                "message": "Image received and saved successfully.",
                "filepath": relative_path,
            }
        )

    except Exception as e:
        return Response({"error": str(e)}, status=500)
