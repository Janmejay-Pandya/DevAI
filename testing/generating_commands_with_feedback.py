import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel
from typing import List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


class Step(BaseModel):
    step: int
    command: str
    description: str


class InstructionOutput(BaseModel):
    steps: List[Step]


instruction_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a senior engineer at a professional software company. 
                Convert the given idea into a step-by-step instruction guide with terminal commands to run on windows to setup a project based on user needs.
                if its a frontend project use vite react.
                Make sure the commands are complete, error-free, and well-structured.
                These commands will be actually be implemented by an autonomous agent.
                so make sure each and every minute details is included and you are not making any mistake:
                
                {previous_feedback}

                {{
                    "steps": [{{
                        "step": "1",
                        "command": "mkdir frontend",
                        "description": "Initializing directory"
                    }},...]
                }}
                Do not include the actual coding implementation.
                reply strictly in JSON format without any extra text.
                """,
        ),
        ("user", "{input}"),
    ]
)

instruction_parser = JsonOutputParser(pydantic_object=InstructionOutput)
instruction_chain = instruction_prompt | llm | instruction_parser


review_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert engineer who reviews step-by-step guides for correctness.
                  If everything is correct, respond with {{"feedback": "approved"}}.
                  Otherwise, point out any mistakes in JSON format: 
                  {{"feedback": "Your mistakes description here"}}
                  Reply with only JSON and nothing else""",
        ),
        ("user", "Review the following steps: {steps}"),
    ]
)


def review_steps(state):
    """LLM reviews steps and either approves or provides feedback."""
    review_chain = review_prompt | llm
    review_result = review_chain.invoke(
        {"steps": json.dumps([step.__dict__ for step in state.instructions.steps])}
    )

    if "approved" in review_result.content.lower():
        return {"approved": True, "feedback": None}
    else:
        feedback_json = review_result.content
        return {"approved": False, "feedback": feedback_json}


class WorkflowState(BaseModel):
    instructions: InstructionOutput = None
    feedback: Optional[str] = None
    approved: bool = False
    user_input: str


workflow = StateGraph(WorkflowState)


# 1. Generate steps
def generate_steps(state):
    """Generates steps using LLM based on user input and feedback (if any)."""
    previous_feedback = state.feedback if state.feedback else "No prior feedback."

    instructions = instruction_chain.invoke(
        {
            "input": state.user_input,
            "previous_feedback": f"Previous feedback: {previous_feedback}",
        }
    )
    return {"instructions": instructions}


workflow.add_node("generate_steps", generate_steps)

# 2. Review steps
workflow.add_node("review_steps", review_steps)

# 3. Connect the nodes
workflow.add_edge("generate_steps", "review_steps")


# 4. Handle Approval Loop
def check_approval(state):
    """If approved, end the process; otherwise, regenerate steps."""

    if state.approved:
        print("✅ Steps Approved! Here is the final instruction set:")
        print(json.dumps(state.instructions.dict(), indent=2))
        return "end"
    else:
        print("❌ Feedback received. Regenerating steps...")
        print(f"Feedback: {state.feedback}")
        return "generate_steps"


workflow.add_conditional_edges("review_steps", check_approval)

workflow.set_entry_point("generate_steps")
workflow.add_node("end", lambda x: x)
checkpointer = MemorySaver()
graph = workflow.compile()


user_input = input("Hey, how can I help you today?\n")

graph.invoke({"user_input": user_input})
