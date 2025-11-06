"""Frontend agent for generating multi-step website pages with proper structure and references."""

import os
import re
import time
import json
import asyncio
import requests
import itertools
from typing import List, Dict
from langchain_core.tools import tool
from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv, find_dotenv
from agents.designer_agent import generate_ui_from_image
from utils.text_utils import extract_filename
from utils.terminal_utils import TerminalLogger
from .prompts import FRONTEND_SYSTEM_PROMPT, REACT_SYSTEM_PROMPT


load_dotenv(find_dotenv(), override=True)

# List of keys
API_KEYS = [
    os.getenv("GOOGLE_API_KEY"),
    os.getenv("GOOGLE_API_KEY_2"),
    os.getenv("GOOGLE_API_KEY_3"),
]

key_cycle = itertools.cycle(API_KEYS)


def get_llm():
    """Return a ChatGoogleGenerativeAI instance with a rotated API key."""
    key = next(key_cycle)
    return ChatGoogleGenerativeAI(
        google_api_key=key,
        model="gemini-2.0-flash",
        temperature=0,
        max_output_tokens=8192,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )


def get_tools(project_id: str):
    """Get tools for file operations within the project directory."""
    base_path = os.path.abspath(
        os.path.join(".", f"code-environment/project-{project_id}")
    )

    # Ensure the base project directory exists
    os.makedirs(base_path, exist_ok=True)

    @tool
    def list_project_structure() -> str:
        """To understand the project structure. It returns a formatted tree-like structure of the project."""
        result = os.popen(f"tree -f -I 'node_modules' {base_path}").read()
        with open("project_structure.txt", "w", encoding="utf-8") as file:
            file.write(result)
        return result

    @tool
    def read_file(file_path: str) -> str:
        """Reads the contents of a file if it exists."""
        safe_path = os.path.join(base_path, file_path.lstrip("./"))
        if os.path.exists(safe_path):
            with open(safe_path, "r", encoding="utf-8") as f:
                return f.read()
        return f"Error: {safe_path} does not exist."

    @tool
    def write_file(file_path: str, content: str, replace: bool = False) -> str:
        """Writes or updates a file with the given content."""
        safe_path = os.path.join(base_path, file_path.lstrip("./"))

        # Ensure the parent directory exists before writing the file
        parent_dir = os.path.dirname(safe_path)
        if parent_dir:  # Only create parent dir if it's not empty
            os.makedirs(parent_dir, exist_ok=True)

        # Write the file content
        mode = "w" if replace or not os.path.exists(safe_path) else "a"
        with open(safe_path, mode, encoding="utf-8") as f:
            f.write(content)

        return f"Successfully {'created' if mode == 'w' else 'updated'} {safe_path}"

    return [list_project_structure, read_file, write_file]


fallback_pages = [
    {
        "name": "index",
        "description": "Landing/home page that serves as the main entry point and introduces the application to visitors",
        "content": "Hero section with compelling headline and app description, navigation menu with links to all main pages, call-to-action buttons for primary actions, feature highlights or benefits section, footer with contact info and links",
    },
    {
        "name": "login",
        "description": "User authentication page for existing users to access their accounts",
        "content": "Login form with email/username and password fields, remember me checkbox, forgot password link, link to register page for new users, form validation with error messages, loading states for form submission",
    },
    {
        "name": "register",
        "description": "User registration page for new users to create accounts",
        "content": "Registration form with required fields (name, email, password, confirm password), validation with real-time feedback, terms and conditions acceptance, link to login page for existing users, success confirmation",
    },
]


def identify_website_pages(description: str, mvp: str = "") -> List[Dict[str, str]]:
    """Identify all pages needed for the website with detailed descriptions."""
    page_identification_prompt = f"""
    Based on the following project description, identify the pages that this website should contain.
    
    Project Description: {description.strip()}
    MVP Features: {mvp.strip()}
    
    Analyze the project requirements and think about the user journey. For each page, provide:
    1. The page name (without .html extension, use lowercase with hyphens for multi-word names)
    2. A clear description of what this page is for and its purpose in the user journey
    3. Detailed list of specific elements, sections, and functionality that should be included
    
    Return ONLY a JSON array of objects with this structure:
    [
        {{
            "name": "index", 
            "description": "Landing/home page that serves as the main entry point and introduces the application to visitors",
            "content": "Hero section with compelling headline and app description, navigation menu with links to all main pages, call-to-action buttons for primary actions (login/register/get-started), feature highlights or benefits section, testimonials or social proof if applicable, footer with contact info and links",
        }},
        {{
            "name": "login", 
            "description": "User authentication page for existing users to access their accounts",
            "content": "Login form with email/username and password fields, remember me checkbox, forgot password link, link to register page for new users, form validation with error messages, loading states for form submission",
        }}
    ]
    
    Be comprehensive but try to summarize the user journey in max 5 to 6 pages. Include only essential pages for the MVP functionality.
    Consider pages like: landing/home (index.html is the mandatory entry point not base.html or home.html), authentication (login/register), main application pages, user profile/settings if needed.
    """
    llm = get_llm()

    response = llm.predict(page_identification_prompt)

    try:
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
                print(f"✅ Identified {len(pages_data)} pages for the website:")
                for page in pages_data:
                    print(f"   📄 {page['name']}.html - {page['description']}")
                return pages_data

            # Fallback if structure is wrong
            print(
                "⚠️ Page identification returned invalid structure, using fallback pages"
            )
            return fallback_pages
        else:
            # Fallback to basic pages if JSON parsing fails
            print(
                "⚠️ Could not parse page identification response, using fallback pages"
            )
            return fallback_pages
    except Exception as e:
        # Fallback to basic pages
        print(f"⚠️ Error in page identification: {e}, using fallback pages")
        return fallback_pages


def get_relevant_images(description: str) -> Dict[str, List[str]]:
    """
    Extracts 3 relevant keywords from a description using a Gemini model,
    fetches related images from the local FastAPI image service,
    and returns them grouped by tag.
    """

    # Ask LLM to extract 3 keywords
    prompt = (
        "Extract exactly 3 short, distinct keywords that best represent visual "
        "themes for the following website description. "
        "Return them as a JSON list of strings without any extra text.\n\n"
        f"Description:\n{description}"
    )
    llm = get_llm()

    response = llm.predict(prompt)
    keywords_text = response.strip()

    # Parse output safely
    try:
        start = keywords_text.find("[")
        end = keywords_text.rfind("]") + 1
        if start != -1 and end != 0:
            keywords_text = keywords_text[start:end]

        tags = json.loads(keywords_text)
        if not isinstance(tags, list):
            raise ValueError

    except Exception:
        # Fallback: split by comma if model didn’t return JSON
        tags = [word.strip() for word in keywords_text.split(",") if word.strip()]

    if len(tags) == 0:
        tags = ["abstract"]

    # Call local image service
    try:
        res = requests.post(
            "http://localhost:8001/get_images", json={"tags": tags}, timeout=20
        )
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        raise RuntimeError(f"Image service request failed: {e}")

    return data


def find_matching_image(media_path: str, html_filename: str) -> str | None:
    """Check if there's an image with the same base name as the HTML file."""
    base_name = os.path.splitext(html_filename)[0]
    if not os.path.exists(media_path):
        return None

    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        possible_path = os.path.join(media_path, base_name + ext)
        if os.path.exists(possible_path):
            return possible_path
    return None


def write_html_file(base_path: str, filename: str, html_content: str):
    """Writes HTML file to disk, ensuring valid HTML structure."""
    if "<html" not in html_content.lower():
        print(f"   ⚠️ Warning: {filename} does not contain valid HTML structure.")
    file_path = os.path.join(base_path, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"   ✅ Created {filename} ({len(html_content)} chars)")


def generate_frontend_prompts(
    description: str, pages: List[dict], mvp: str = "", design_guidelines: str = ""
) -> List[str]:
    """Structure frontend requests into step-by-step page generation prompts."""
    try:
        image_data = get_relevant_images(description)
    except Exception as e:
        print(f"[Warning] Could not fetch images: {e}")
        image_data = {}

    # Flatten image URLs
    all_image_urls = []
    for tag, urls in image_data.items():
        all_image_urls.extend(urls)

    visual_assets_context = (
        "AVAILABLE IMAGE ASSETS:\n" + "\n".join(all_image_urls)
        if all_image_urls
        else "No image assets available; use generic placeholders."
    )

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

        # Add special instructions based on page type
        page_specific_instructions = ""
        if (
            "login" in page_name.lower()
            or "register" in page_name.lower()
            or "form" in page_content.lower()
        ):
            page_specific_instructions = """
        FORM-SPECIFIC REQUIREMENTS:
        - Include proper form validation with JavaScript
        - Add loading states and success/error messages
        - Use appropriate input types and validation attributes
        """
        elif "index" in page_name.lower() or "home" in page_name.lower():
            page_specific_instructions = """
        LANDING PAGE REQUIREMENTS:
        - Engaging hero section that captures attention
        - Clear call-to-action buttons
        """
        visual_and_icon_guidelines = f"""
        VISUAL ENHANCEMENT REQUIREMENTS:
        - Use plenty of relevant images and icons for better aesthetics and communication.
        - Use images from the list below when designing sections:
        {visual_assets_context}
        - Optimize layout to visually balance text and imagery.
        - Give images width and height to avoid unexpected spillage
        - Use Font Awesome (Free) icons via CDN:
          <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css">
        - Integrate icons for buttons, navigation, features, and section headings where appropriate.
        """

        prompt = f"""
        Create a complete {page_name}.html file for the following project:

        PROJECT CONTEXT:
        Description: {description.strip()}
        MVP Features: {mvp.strip()}
        Design Guidelines: {design_guidelines.strip()}

        PAGE SPECIFIC DETAILS:
        Page Name: {page_name}.html
        Page Purpose: {page_description}
        Required Content/Elements: {page_content}

        WEBSITE STRUCTURE:
        {other_pages_context}

        TECHNICAL REQUIREMENTS:
        - Use tailwind CDN for for modern and professional styling, and internal CSS if required for complex styling
        - Include internal <script> tags for functionalities and interactivity.
        - Use meaningful id and class attributes where needed
        - Implement responsive design with mobile-first approach using CSS Grid and Flexbox
        - Include proper navigation menu that links to other pages in the website
        - Follow the design guideline for colors and typography

        {page_specific_instructions}
        {visual_and_icon_guidelines}

        CRITICAL IMPLEMENTATION NOTES:
        - MANDATORY: Include ALL the required content/elements specified above for this specific page
        - The HTML should be complete and self-contained
        - **IMPORTANT**: Generate clean HTML without any html escape characters (like &quot;) or literal newlines.

        Generate the complete HTML file content and return it as clean, properly formatted HTML.
        """

        prompts.append(prompt)

    return prompts


# def clean_html_content(raw_content: str) -> str:
#     """Clean and process HTML content to remove escape characters and ensure proper formatting."""
#     # Replace literal \n with actual newlines
#     processed = raw_content.replace("\\n", "\n")
#     # Replace literal \t with actual tabs
#     processed = processed.replace("\\t", "\t")
#     # Replace literal \r with actual carriage returns
#     processed = processed.replace("\\r", "\r")
#     # Remove any extra quotes that might wrap the content
#     processed = processed.strip("\"'")
#     # Remove any leading/trailing whitespace
#     processed = processed.strip()

#     return processed


async def generate_frontend(prompts: List[str], chat_id: str, app_type="vanilla"):
    """Generate frontend pages step by step with context of previously generated files."""
    await TerminalLogger.log(
        "info", "development", f"Starting development for project-{chat_id}"
    )
    await asyncio.sleep(2)

    # Create project directory
    base_path = os.path.abspath(
        os.path.join(".", f"code-environment/project-{chat_id}")
    )
    media_path = os.path.abspath(os.path.join("media", str(chat_id)))
    os.makedirs(base_path, exist_ok=True)
    print(f"📁 Created project directory: {base_path}")

    system_prompt = (
        REACT_SYSTEM_PROMPT if app_type == "react" else FRONTEND_SYSTEM_PROMPT
    )

    total_pages = len(prompts)

    for i, user_request in enumerate(prompts, 1):
        print(f"\n🔄 Generating page {i}/{total_pages}...")

        filename = extract_filename(user_request)
        if not filename:
            print("   ❌ Could not extract filename from prompt.")
            continue

        print(f"   📄 Generating: {filename}")
        image_path = find_matching_image(media_path, filename)

        # Create the full prompt with system instructions
        full_prompt = f"{system_prompt}\n\nUser Request:\n{user_request}"

        try:
            llm = get_llm()
            if image_path:
                print(
                    f"   🖼️ Found image match for {filename}: {os.path.basename(image_path)}"
                )
                html_content = generate_ui_from_image(full_prompt, image_path)
            else:
                response = llm.invoke(full_prompt)
                html_content = getattr(response, "content", None) or getattr(
                    response, "text", str(response)
                )

                # Look for HTML content in the response
                if "<!DOCTYPE html>" in html_content or "<html" in html_content:
                    # Extract the HTML content
                    start_idx = html_content.find("<!DOCTYPE html>")
                    if start_idx == -1:
                        start_idx = html_content.find("<html")

                    if start_idx != -1:
                        end_idx = html_content.rfind("</html>") + 7
                        if end_idx > 6:  # Found closing tag
                            actual_html = html_content[start_idx:end_idx]
                        else:
                            # Take everything from start
                            actual_html = html_content[start_idx:]

                        # Clean the HTML content
                        processed_html = actual_html

                        # Write the file
                        file_path = os.path.join(base_path, filename)
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(processed_html)

                        print(
                            f"   ✅ Successfully created {filename} ({len(processed_html)} characters)"
                        )
                    else:
                        print(f"   ❌ No HTML content found in response for {filename}")
                        print(f"   Response preview: {html_content[:200]}...")
                else:
                    print(f"   ❌ No HTML structure found in response for {filename}")
                    print(f"   Response preview: {html_content[:200]}...")

        except Exception as e:
            print(f"   ❌ Error generating content: {e}")
            continue

    print(f"\n🎉 Generated all pages successfully!")
    await TerminalLogger.log(
        "success",
        "development",
        f"Development completed! Generated all pages.",
    )


def structure_react_requests(
    description: str, mvp: str = "", design_guidelines: str = ""
) -> List[str]:
    """Structure React frontend requests into step-by-step component generation prompts."""
    # First identify main components/pages needed
    components_identification_prompt = f"""
    Based on the following React project description, identify the main components and pages needed.
    
    Project Description: {description.strip()}
    MVP Features: {mvp.strip()}
    Design Guidelines: {design_guidelines.strip()}
    
    Think about the component structure for a React application. For each component, provide:
    1. The component name (without .jsx extension)
    2. A clear description of what this component does
    3. Key props, state, and functionality it should have
    
    Return ONLY a JSON array of objects with this structure:
    [
        {{
            "name": "App",
            "description": "Main application component with routing",
            "functionality": "Sets up React Router, manages global state, renders main layout with navigation"
        }},
        {{
            "name": "Header",
            "description": "Navigation header component",
            "functionality": "Logo, navigation menu, user authentication status, responsive mobile menu"
        }}
    ]
    
    Be comprehensive but realistic. Focus on essential components for the MVP.
    """
    llm = get_llm()

    response = llm.predict(components_identification_prompt)

    try:
        import json

        start = response.find("[")
        end = response.rfind("]") + 1
        if start != -1 and end != 0:
            components_json = response[start:end]
            components_data = json.loads(components_json)
            # Validate structure and extract component names for grouping
            if isinstance(components_data, list) and all(
                isinstance(comp, dict) and "name" in comp for comp in components_data
            ):
                components = [comp["name"] for comp in components_data]
                components_details = components_data
            else:
                components = ["App", "Header", "HomePage", "LoginPage", "Dashboard"]
                components_details = [
                    {
                        "name": comp,
                        "description": f"{comp} component",
                        "functionality": "Basic functionality",
                    }
                    for comp in components
                ]
        else:
            components = ["App", "Header", "HomePage", "LoginPage", "Dashboard"]
            components_details = [
                {
                    "name": comp,
                    "description": f"{comp} component",
                    "functionality": "Basic functionality",
                }
                for comp in components
            ]
    except Exception:
        components = ["App", "Header", "HomePage", "LoginPage", "Dashboard"]
        components_details = [
            {
                "name": comp,
                "description": f"{comp} component",
                "functionality": "Basic functionality",
            }
            for comp in components
        ]

    prompts = []

    # Group components into logical generation steps
    component_groups = []

    # First group: Core structure (App, routing, main layout)
    core_components = [
        c
        for c in components
        if c.lower() in ["app", "header", "footer", "navbar", "layout"]
    ]
    if core_components:
        component_groups.append(core_components)

    # Second group: Main pages
    page_components = [
        c
        for c in components
        if "page" in c.lower()
        or c.lower() in ["home", "login", "register", "dashboard"]
    ]
    page_components = [c for c in page_components if c not in core_components]
    if page_components:
        # Split pages into smaller groups if too many
        for i in range(0, len(page_components), 3):
            component_groups.append(page_components[i : i + 3])

    # Third group: Utility components
    utility_components = [
        c for c in components if c not in core_components and c not in page_components
    ]
    if utility_components:
        for i in range(0, len(utility_components), 2):
            component_groups.append(utility_components[i : i + 2])

    for i, component_group in enumerate(component_groups):
        other_components = [c for c in components if c not in component_group]
        other_components_context = (
            f"Other components in this project: {', '.join(other_components)}.jsx"
        )

        if i > 0:
            previous_groups = [c for group in component_groups[:i] for c in group]
            previous_context = f"Previously generated components: {', '.join(previous_groups)}.jsx - ensure consistency and proper imports."
        else:
            previous_context = "This is the first set of components being generated."

        # Get detailed information for components in this group
        group_details = []
        for comp_name in component_group:
            comp_detail = next(
                (c for c in components_details if c["name"] == comp_name), None
            )
            if comp_detail:
                group_details.append(
                    f"- {comp_name}: {comp_detail['description']} | Functionality: {comp_detail['functionality']}"
                )
            else:
                group_details.append(
                    f"- {comp_name}: Component functionality to be determined"
                )

        component_details_text = "\n".join(group_details)

        prompt = f"""
        Generate the following React components for this project:
        
        Project Description: {description.strip()}
        MVP Features: {mvp.strip()}
        Design Guidelines: {design_guidelines.strip()}
        
        COMPONENT SPECIFIC DETAILS:
        {component_details_text}
        
        Components to generate in this step: {', '.join(component_group)}
        {other_components_context}
        {previous_context}
        
        Requirements:
        - Use functional components with React hooks
        - Use inline CSS styling only (no external CSS files)
        - Include proper prop validation with PropTypes
        - Ensure components are modular and reusable
        - Use React Router for navigation if needed
        - Include proper state management with useState
        - Add proper event handlers and form validation
        - Ensure responsive design
        - Use semantic HTML elements
        - Available libraries: react-router-dom, axios, react-icons, @heroicons/react, prop-types, lodash, date-fns, react-markdown
        - IMPORTANT: Implement the specific functionality described above for each component
        - **MANDATORY**: Use the write_file tool to save each component as ComponentName.jsx
        - **DO NOT** display the code in your response - only use the write_file tool
        
        Generate complete, functional React components and save them using write_file tool.
        """

        prompts.append(prompt)

    return prompts


async def generate_react_frontend(prompts: List[str], project_id: str):
    """Generate React frontend components step by step with context of previously generated files."""
    await TerminalLogger.log("info", "development", "React development started!")
    await asyncio.sleep(3)

    # Create project directory structure
    base_path = os.path.abspath(
        os.path.join(".", f"code-environment/project-{project_id}")
    )
    src_path = os.path.join(base_path, "src")
    components_path = os.path.join(src_path, "components")
    os.makedirs(src_path, exist_ok=True)
    os.makedirs(components_path, exist_ok=True)

    generated_components = []

    for i, user_request in enumerate(prompts):
        time.sleep(2)

        # Add context of previously generated components
        context_info = ""
        if generated_components:
            context_info = f"\n\nPreviously generated components for reference:\n"
            for comp_info in generated_components:
                context_info += f"\n--- {comp_info['filename']} ---\n"
                # Include first 800 chars to avoid token limits
                content_preview = (
                    comp_info["content"][:800] + "..."
                    if len(comp_info["content"]) > 800
                    else comp_info["content"]
                )
                context_info += content_preview
                context_info += "\n"

        # Create the full prompt with system instructions
        full_prompt = (
            f"{REACT_SYSTEM_PROMPT}\n\nUser Request:\n{user_request}{context_info}"
        )

        # Use direct LLM call
        try:
            llm = get_llm()
            response = llm.invoke(full_prompt)

            # Extract component names from the request
            import re

            jsx_matches = re.findall(r"(\w+)\.jsx", user_request)

            # Get response content
            jsx_content = (
                response.content if hasattr(response, "content") else str(response)
            )

            # Try to extract and save each component
            for jsx_file in jsx_matches:
                # Look for the component code in the response
                if f"{jsx_file}" in jsx_content and (
                    "import" in jsx_content
                    or "function" in jsx_content
                    or "const" in jsx_content
                ):
                    # Try to extract the component code
                    # Look for patterns like "// ComponentName.jsx" or similar
                    component_start = jsx_content.find(f"{jsx_file}")
                    if component_start != -1:
                        # Find the actual JSX code - look for import statements or function declarations
                        code_start = jsx_content.find(
                            "import",
                            component_start - 200 if component_start > 200 else 0,
                        )
                        if code_start == -1:
                            code_start = jsx_content.find(
                                "function",
                                component_start - 100 if component_start > 100 else 0,
                            )
                        if code_start == -1:
                            code_start = jsx_content.find(
                                "const",
                                component_start - 100 if component_start > 100 else 0,
                            )

                        if code_start != -1:
                            # Find the end of the component (look for export default or end of file)
                            code_end = jsx_content.find("export default", code_start)
                            if code_end != -1:
                                code_end = jsx_content.find(";", code_end) + 1
                                if code_end == 0:  # No semicolon found
                                    code_end = (
                                        jsx_content.find(
                                            "\n",
                                            jsx_content.find(
                                                "export default", code_start
                                            ),
                                        )
                                        + 1
                                    )
                            else:
                                # Take a reasonable chunk
                                code_end = code_start + 2000

                            component_code = jsx_content[code_start:code_end].strip()

                            # Determine file path (App.jsx goes to src/, others to components/)
                            if jsx_file.lower() == "app":
                                file_path = os.path.join(src_path, f"{jsx_file}.jsx")
                            else:
                                file_path = os.path.join(
                                    components_path, f"{jsx_file}.jsx"
                                )

                            # Process the component code to fix newlines
                            # Replace literal \n with actual newlines
                            processed_code = component_code.replace("\\n", "\n")
                            # Also handle \t for tabs
                            processed_code = processed_code.replace("\\t", "\t")
                            # Remove any extra quotes that might wrap the content
                            processed_code = processed_code.strip("\"'")

                            # Write the file
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(processed_code)

                            print(f"✅ Successfully created {jsx_file}.jsx")

                            # Store for context
                            generated_components.append(
                                {
                                    "filename": f"{jsx_file}.jsx",
                                    "content": processed_code,
                                }
                            )
                        else:
                            print(f"❌ Could not find component code for {jsx_file}")
                    else:
                        print(f"❌ Component {jsx_file} not found in response")
                else:
                    print(f"❌ No JSX content found for {jsx_file}")

        except Exception as e:
            print(f"❌ Error generating React components: {e}")
            continue

    await TerminalLogger.log("success", "development", "React development finished!")
