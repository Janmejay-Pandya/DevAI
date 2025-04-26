import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv, find_dotenv
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.prompts.chat import MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory

load_dotenv(find_dotenv(), override=True)

# Initialize multiple LLMs for debate
llm_mvp_generator = ChatGoogleGenerativeAI(google_api_key=os.getenv("GOOGLE_API_KEY"),model="gemini-1.5-flash", temperature=0.7)
llm_minimalist = ChatGoogleGenerativeAI(google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash", temperature=0.8)
llm_scalability_advocate = ChatGoogleGenerativeAI(google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash", temperature=0.8)
llm_ux_focus = ChatGoogleGenerativeAI(google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash", temperature=0.8)
llm_final_decision = ChatGoogleGenerativeAI(google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash", temperature=0.6)
llm_design_brainstorm = ChatGoogleGenerativeAI(google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash", temperature=0.6)
llm_techstack_decider = ChatGoogleGenerativeAI(google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-1.5-flash", temperature=0.7)

# Define system roles
roles = {
    "Minimalist": "Focus on only the core essential features needed for MVP.",
    "Scalability Advocate": "Think about how features can be expanded in the future and balance feasibility.",
    "UX Focus": "Prioritize user experience, ease of use, and modern design choices."
}

# Generate Initial MVP Feature List
def generate_mvp_features(product_description):
    prompt = f"""
    Given the product description: "{product_description}", generate an initial MVP feature list.
    Focus only on essential features needed for a minimal but functional product.
    """
    response = llm_mvp_generator.predict(prompt)
    print(response)
    return response

# Debate on MVP features
def debate_mvp_features(feature_list):
    critiques = {}
    for role, instruction in roles.items():
        prompt = f"""
        Given the MVP feature list:

        {feature_list}

        Provide your critique as a {role}. {instruction}
        List any features that should be removed, added, or modified.
        """
        critiques[role] = globals()[f"llm_{role.lower().replace(' ', '_')}"].predict(prompt)

    print("********** Critiques from Different Perspectives **********")
    print(critiques)
    return critiques

# Finalize MVP after debate
def finalize_mvp(feature_list, critiques):
    prompt = f"""
    Given the initial MVP feature list:
    {feature_list}
    And the critiques from different perspectives:
    {critiques}
    Refine the MVP feature list by keeping only the most important suggestions.
    Output the final MVP features in a structured JSON format, as a list of string (functionalities).
    """
    final_mvp = llm_final_decision.predict(prompt)
    return final_mvp


# Brainstorm Design Guidelines
def brainstorm_design_guidelines(product_description):
    prompt = f"""
    Given the product description: "{product_description}", suggest design guidelines and themes.
    Include aspects like color palette, typography, and branding style.
    Do not include any unnecessary details or features. Just focus on design.
    """
    response = llm_design_brainstorm.predict(prompt)
    return response


def decide_tech_stack(product_description, final_mvp, design_guidelines):
    prompt = f"""
    Given the product description: "{product_description}", the finalized MVP feature list: {final_mvp}, and the design guidelines: {design_guidelines},
    suggest the most suitable tech stack.
    Consider frontend and backend technologies, database choices, deployment options, and scalability factors.
    Don't give options; just provide a single tech stack recommendation.
    """
    response = llm_techstack_decider.predict(prompt)
    return response