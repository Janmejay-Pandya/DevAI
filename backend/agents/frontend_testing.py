import os
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

llm = ChatGoogleGenerativeAI(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


fallback_pages = [
    {
        "name": "index",
        "description": "Landing page that introduces the application",
        "content": "Hero section, navigation, call-to-action buttons, feature overview",
    },
    {
        "name": "login",
        "description": "User authentication page for existing users",
        "content": "Login form with email and password fields, validation, links to register",
    },
    {
        "name": "register",
        "description": "User registration page for new users",
        "content": "Registration form with required fields, validation, terms acceptance",
    },
]


def identify_website_pages(
    description: str, mvp: str = "", design_guidelines: str = ""
) -> List[Dict[str, str]]:
    """Identify all pages needed for the website with detailed descriptions."""
    page_identification_prompt = f"""
    Based on the following project description, identify ALL pages that this website should contain.
    
    Project Description: {description.strip()}
    MVP Features: {mvp.strip()}
    Design Guidelines: {design_guidelines.strip()}
    
    Think about what pages a typical user would need to navigate through for this application.
    For each page, provide:
    1. The page name (without .html extension)
    2. A clear description of what this page is for
    3. Key elements/content that should be included on this page
    
    Return ONLY a JSON array of objects with this structure:
    [
        {{
            "name": "index",
            "description": "Landing/home page that introduces the application",
            "content": "Hero section with app description, navigation menu, call-to-action buttons to login/register, feature highlights, footer"
        }},
        {{
            "name": "login", 
            "description": "User authentication page for existing users",
            "content": "Login form with email/username and password fields, remember me checkbox, forgot password link, link to register page, form validation"
        }}
    ]
    
    Be comprehensive but realistic. Include all essential pages for the MVP functionality.
    """

    response = llm.predict(page_identification_prompt)

    try:
        # Extract JSON array from response
        import json

        # Find JSON array in response
        start = response.find("[")
        end = response.rfind("]") + 1
        if start != -1 and end != 0:
            pages_json = response[start:end]
            pages_data = json.loads(pages_json)
            # Validate structure
            if isinstance(pages_data, list) and all(
                isinstance(page, dict)
                and "name" in page
                and "description" in page
                and "content" in page
                for page in pages_data
            ):
                return pages_data
            else:
                # Fallback if structure is wrong
                return fallback_pages
        else:
            # Fallback to basic pages if JSON parsing fails
            return fallback_pages
    except Exception:
        # Fallback to basic pages
        return fallback_pages


description = "A note taking app"
mvp = (
    "* **Note Creation:**  Ability to create new notes with text input."
    "* **Note Saving:**  Persistent storage of notes (local storage initially is sufficient)."
    "* **Note Viewing:** Ability to view existing notes."
    "* **Note Editing:** Ability to modify existing notes."
    "* **Note Deletion:** Ability to delete notes."
)

design_guidelines = (
    "**Design Guidelines:**"
    "* **Color Palette:**  A muted, calming palette of  #F2F2F2 (light grey) as the background, #333333 (dark grey) for text and interface elements, and a subtle accent color of #A7D1AB (a soft, muted green) for highlighting and interactive elements. This palette promotes focus and readability without being visually distracting."
    "* **Typography:**  Roboto for all text.  Roboto is clean, legible, and widely available, ensuring consistency across platforms.  Use a slightly larger size for headings (e.g., 18sp) and a comfortable size for body text (e.g., 14sp)."
    "* **Branding Style:** Minimalist and clean. Avoid unnecessary ornamentation or decorative elements.  Focus on clear hierarchy and intuitive navigation. The overall aesthetic should be professional yet approachable.  A simple, geometric logo (perhaps a stylized notepad icon) would complement this style."
)


def structure_frontend_requests(
    description: str, mvp: str = "", design_guidelines: str = ""
) -> List[str]:
    """Structure frontend requests into step-by-step page generation prompts."""
    # First identify all pages needed
    pages = identify_website_pages(description, mvp, design_guidelines)

    prompts = []

    for i, page_info in enumerate(pages):
        page_name = page_info["name"]
        page_description = page_info["description"]
        page_content = page_info["content"]

        # Create context about other pages for proper linking
        other_pages = [p["name"] for p in pages if p["name"] != page_name]
        other_pages_context = (
            f"Other pages in this website: {', '.join(other_pages)}.html"
        )

        # Create context about previously generated pages
        if i > 0:
            previous_pages = [p["name"] for p in pages[:i]]
            previous_context = f"Previously generated pages: {', '.join(previous_pages)}.html - ensure consistent styling and navigation."
        else:
            previous_context = "This is the first page being generated."

        prompt = f"""
        Create a complete {page_name}.html file for the following project:
        
        Project Description: {description.strip()}
        MVP Features: {mvp.strip()}
        Design Guidelines: {design_guidelines.strip()}
        
        PAGE SPECIFIC DETAILS:
        Page Purpose: {page_description}
        Required Content/Elements: {page_content}
        
        {other_pages_context}
        {previous_context}
        
        Requirements for {page_name}.html:
        - Include proper HTML structure with semantic tags
        - Add internal <style> tags with modern, sleek CSS
        - Include internal <script> tags for interactivity
        - Use proper id and class attributes for styling and JavaScript targeting
        - Ensure responsive design with mobile-first approach
        - Include navigation links to other pages where appropriate
        - Make the design consistent with the overall project theme
        - Add proper form validation if the page contains forms
        - Use accessibility best practices (ARIA labels, semantic HTML)
        - IMPORTANT: Include all the required content/elements specified above for this specific page
        
        Generate a complete, self-contained HTML file that works independently but fits within the overall website structure.
        """

        prompts.append(prompt)

    return prompts


# identified_pages = identify_website_pages(description=description, mvp=mvp)

print(
    structure_frontend_requests(
        description=description, mvp=mvp, design_guidelines=design_guidelines
    )
)
