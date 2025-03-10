import os
import json
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import tool
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv, find_dotenv
from typing import List
from constants import system_prompt

BASE_PATH: str = "./codebase/backend"


@tool
def list_project_structure() -> str:
    """To understand the project structure. It returns a formatted tree-like structure of the project."""
    ignore_dirs: List[str] = ["venv", "node_modules", "__pycache__"]
    result = os.popen(f"tree {BASE_PATH} /f /a").read()
    with open("project_structure.txt", "w") as file:
        file.write(result)
    return result


list_project_structure.invoke(input={})


@tool
def read_file(file_path: str) -> str:
    """Reads the contents of a file if it exists."""
    safe_path = os.path.join(BASE_PATH, file_path.lstrip("./"))
    if os.path.exists(safe_path):
        with open(safe_path, "r", encoding="utf-8") as f:
            return f.read()
    return f"Error: {safe_path} does not exist."


read_file.invoke(input={"file_path": "./README.md"})


@tool
def write_file(file_path: str, content: str, replace: bool = False) -> str:
    """Writes or updates a file with the given content."""
    safe_path = os.path.join(BASE_PATH, file_path.lstrip("./"))

    # Ensure the parent directory exists before writing the file
    os.makedirs(os.path.dirname(safe_path), exist_ok=True)

    # Check if file exists, and create it if not
    if not os.path.exists(safe_path):
        open(safe_path, "w").close()  # Creates an empty file

    # Write content to the file
    with open(safe_path, "w" if replace else "a", encoding="utf-8") as f:
        f.write(content)

    return f"Updated {safe_path}"


load_dotenv(find_dotenv(), override=True)

llm = ChatGoogleGenerativeAI(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

tools = [list_project_structure, read_file, write_file]

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# agent_executor.invoke({"input": "use list_project_structure to see the project structure and then tell me whats in the project"})
agent_executor.invoke(
    {
        "input": "create a mvc register api using user model with fields email, name, and password."
    }
)
# agent_executor.invoke(
#     {"input": "use the tools and create and add the login functionality using jwt."}
# )
