from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import google.generativeai as genai
import re

# Set up the API key for Gemini
genai.configure(api_key="AIzaSyA8bOtlnf8mj-90HX9H-ec6HmMElPpvZVA")

# Create a model instance once (can reuse)
model = genai.GenerativeModel("gemini-2.0-flash")


@csrf_exempt
def suggest_colors(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            title = data.get("title", "").lower()

            # Create a very explicit prompt
            prompt = f"""
            Generate exactly 3 hex color codes for a website themed '{title}'.
            Output format must be exactly: #XXXXXX, #YYYYYY, #ZZZZZZ
            Do not include any other text, explanations, or formatting.
            """

            # Use Gemini model to generate
            response = model.generate_content(prompt)

            # Clean and parse response
            colors_text = response.text.strip()

            # Extract valid hex codes using regex
            hex_pattern = r"#[0-9A-Fa-f]{6}"
            colors = re.findall(hex_pattern, colors_text)

            # Ensure we have exactly 3 colors
            if len(colors) < 3:
                default_colors = ["#4287f5", "#42f5a7", "#f54242"]
                colors.extend(default_colors[len(colors) : 3])

            return JsonResponse({"suggestedColors": colors[:3]})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def generate_website_code(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            selected_colors = data.get("colors", [])
            theme = data.get("theme", "My Website")

            # Extremely explicit prompt with strict formatting requirements
            prompt = f"""
            Generate ONLY HTML and CSS code for a professional, modern website about '{theme}'.

            Create content that is specifically relevant to '{theme}' with appropriate sections, headings, and placeholder text.
            Use these exact colors in your design: {', '.join(selected_colors)}
            - Use the first color as the primary brand color
            - Use the second color for accents and highlights
            - Use the third color for secondary elements

            Requirements:
            - Create a responsive layout that works on mobile and desktop
            - Include a navigation menu with 4-5 relevant sections for '{theme}'
            - Add a hero section with a compelling headline related to '{theme}'
            - Include features/services section with 3-4 key points related to '{theme}'
            - Add an about section with placeholder text specific to the '{theme}' industry
            - Include a contact form
            - Use modern, clean typography with good readability
            - Ensure all content directly relates to '{theme}' with NO generic lorem ipsum
            - All CSS must be in a <style> tag in the head section

            Your response must begin with <!DOCTYPE html> and end with </html> with no other text.
            """

            # Generate with strict parameters
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,  # Lower temperature for more deterministic output
                    "max_output_tokens": 8192,
                },
            )

            # Get the raw generated code
            html_code = response.text.strip()

            # Additional cleaning to ensure only HTML is returned
            # Extract only content between <!DOCTYPE html> and </html>
            html_pattern = r"<!DOCTYPE html>.*?</html>"
            html_match = re.search(html_pattern, html_code, re.DOTALL | re.IGNORECASE)

            if html_match:
                html_code = html_match.group(0)
            else:
                # Fallback if pattern isn't found - check if it at least starts with <
                if html_code.startswith("<"):
                    # Keep it as is, it's probably HTML
                    pass
                else:
                    # Return an error if no HTML is detected
                    return JsonResponse(
                        {"error": "Generated content does not appear to be HTML"},
                        status=500,
                    )

            return JsonResponse({"htmlCode": html_code})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
