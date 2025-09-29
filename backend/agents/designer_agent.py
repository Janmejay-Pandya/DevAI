import os
from google import genai
from google.generativeai import types
from dotenv import load_dotenv, find_dotenv
from .prompts import UI_DESIGNER_PROMPT
import re

load_dotenv(find_dotenv(), override=True)


def generate_ui_from_image(image):
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    image_file = client.files.upload(file=image)
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=[UI_DESIGNER_PROMPT, image_file]
    )
    html_match = re.search(r"(<html[\s\S]*?</html>)", response.text, re.IGNORECASE)
    if html_match:
        response_text = html_match.group(1)
    else:
        response_text = ""
    return response_text
