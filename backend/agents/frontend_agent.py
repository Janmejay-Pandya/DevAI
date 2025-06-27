import os
import json
import asyncio
from typing import List
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import tool
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv, find_dotenv
from .prompts import FRONTEND_SYSTEM_PROMPT, REACT_SYSTEM_PROMPT, CODE_PLANNER_PROMPT
from utils.terminal_utils import TerminalLogger
from utils.text_utils import extract_prompt_list

load_dotenv(find_dotenv(), override=True)

def get_tools(project_id: str):
    BASE_PATH = os.path.abspath(os.path.join(".", f"code-environment/project{project_id}"))

    @tool
    def list_project_structure() -> str:
        """To understand the project structure. It returns a formatted tree-like structure of the project."""
        ignore_dirs: List[str] =["venv", "node_modules", "__pycache__"]
        result = os.popen(f"tree -f -I 'node_modules' {BASE_PATH}").read()
        with open("project_structure.txt", "w") as file:
            file.write(result)
        return result

    @tool
    def read_file(file_path: str) -> str:
        """Reads the contents of a file if it exists."""
        safe_path = os.path.join(BASE_PATH, file_path.lstrip("./"))
        if os.path.exists(safe_path):
            with open(safe_path, "r", encoding="utf-8") as f:
                return f.read()
        TerminalLogger.log("success", "development", "Development Finished!")
        return f"Error: {safe_path} does not exist."

    @tool
    def write_file(file_path: str, content: str, replace: bool = False) -> str:
        """Writes or updates a file with the given content."""
        safe_path = os.path.join(BASE_PATH, file_path.lstrip("./"))
        
        # Ensure the parent directory exists before writing the file
        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
        if not os.path.exists(safe_path):
            open(safe_path, "w").close()
        with open(safe_path, "w" if replace else "a", encoding="utf-8") as f:
            f.write(content)
        return f"Updated {safe_path}"

    return [list_project_structure, read_file, write_file]
    
llm = ChatGoogleGenerativeAI(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

def structure_frontend_requests(self, description: str, mvp: str="", design_guidelines: str=""):
    planner_prompt = CODE_PLANNER_PROMPT.format(
        description=description.strip(),
        mvp=mvp.strip(),
        design_guidelines=design_guidelines.strip(),
    )

    response = llm.predict(planner_prompt)
    
    try:
        return extract_prompt_list(response)
    except Exception as e:
        raise ValueError("Failed to parse structured prompt list.") from e


async def generate_frontend(user_request: str, project_id: str, app_type="vanilla"):
    await TerminalLogger.log("info", "development", "Development started!")
    await asyncio.sleep(3)

    tools = get_tools(project_id)
    system_prompt = react_prompt if app_type == "react" else vanilla_prompt

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt), 
        ("human", "{input}"), 
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    agent_executor.invoke({"input": user_request})

    await TerminalLogger.log("success", "development", "Development Finished!")
