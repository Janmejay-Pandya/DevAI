import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv(), override=True)

# Initialize multiple LLMs for debate
llm_mvp_generator = ChatGoogleGenerativeAI(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-2.0-flash",
    temperature=0.7,
)
llm_design_brainstorm = ChatGoogleGenerativeAI(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-2.0-flash",
    temperature=0.6,
)
llm_techstack_decider = ChatGoogleGenerativeAI(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-2.0-flash",
    temperature=0.7,
)


# Generate Initial MVP Feature List
def generate_mvp_features(product_description, changes):
    prompt = f"""
    Given the product description: "{product_description}",
    generate a very minimal MVP feature list. 
    Focus strictly on essential features needed for a functional product.
    Avoid advanced features like payment integrations, analytics, or third-party APIs.

    """
    if changes:
        prompt += (
            f"\nConsider the previous MVP/features and user suggestions: {changes}"
        )

    response = llm_mvp_generator.predict(prompt)
    return response


# Brainstorm Design Guidelines
def brainstorm_design_guidelines(product_description, changes=None):
    prompt = f"""
    Given the product description: "{product_description}", suggest clear and focused design guidelines and themes.
    Focus only on design aspects like color palette and typography.

    - Choose colors thoughtfully: if the design is dark-themed, suggest lighter, high-contrast colors for primary elements and text, and vice versa.
    - Prioritize popular, visually appealing, and harmonious colors that suit the product's tone.
    - Recommend typography that complements the theme and enhances readability.
    - Be direct and specific: provide only one recommended color palette and one typography choice with a brief explanation for each.
    - Avoid unnecessary details, multiple options, or unrelated suggestions.
    """

    if changes:
        prompt += f"\nIncorporate the following user suggestions or previous recommendations: {changes}"

    response = llm_design_brainstorm.predict(prompt)
    return response


def decide_tech_stack(product_description, final_mvp, design_guidelines):
    prompt = f"""
    Given the product description: "{product_description}", the finalized MVP feature list: {final_mvp}, and the design guidelines: {design_guidelines},
    suggest the most suitable tech stack.
    Consider frontend and backend technologies, database choices, and scalability factors.
    For frontend choices are either React with JS or HTML, CSS & JS.
    For Backend We currently support Express.js
    For database we can go with sqlite for development and later switch to a more robust database.
    Don't give options; just provide a single tech stack recommendation.
    """
    response = llm_techstack_decider.predict(prompt)
    return response
