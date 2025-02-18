import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel
from typing import List

# Initialize the LLM
llm = ChatGroq(model="llama3-70b-8192", temperature=0.0, max_retries=2, verbose=True)


# --- Step 1: Define Input Data Model ---
class Step(BaseModel):
    step: int
    command: str
    description: str


class InstructionOutput(BaseModel):
    steps: List[Step]


# --- Step 2: Define LLM for Instruction Generation ---
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

# --- Step 3: Define LLM for Feedback & Approval ---
review_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert engineer who reviews step-by-step guides for correctness.
                  If everything is correct, respond with "approved".
                  Otherwise, point out any mistakes in JSON format: 
                  {{"feedback": "Your mistake description here"}} """,
        ),
        ("user", "Review the following steps: {steps}"),
    ]
)


def review_steps(state):
    """LLM reviews steps and either approves or provides feedback."""
    print(state)
    review_chain = review_prompt | llm
    review_result = review_chain.invoke(
        {"steps": json.dumps([step.__dict__ for step in state.instructions.steps])}
    )

    if "approved" in review_result.lower():
        return {"approved": True, "feedback": None}
    else:
        return {"approved": False, "feedback": review_result}


# --- Step 4: Define State for LangGraph ---
class WorkflowState(BaseModel):
    instructions: InstructionOutput = None
    feedback: str = None
    approved: bool = False
    user_input: str


# --- Step 5: Define the Workflow ---
workflow = StateGraph(WorkflowState)


# 1. Generate steps
def generate_steps(state):
    """Generates steps using LLM based on user input."""
    instructions = instruction_chain.invoke({"input": state.user_input})
    return {"instructions": instructions}


workflow.add_node("generate_steps", generate_steps)

# 2. Review steps
workflow.add_node("review_steps", review_steps)

# 3. Connect the nodes
workflow.add_edge("generate_steps", "review_steps")


# 4. Handle Approval Loop
def check_approval(state):
    """If approved, end the process; otherwise, regenerate steps."""
    if state["approved"]:
        print("✅ Steps Approved! Here is the final instruction set:")
        print(json.dumps(state["instructions"].dict(), indent=2))
        return "end"
    else:
        print("❌ Feedback received. Regenerating steps...")
        print(f"Feedback: {state['feedback']}")
        return "generate_steps"


workflow.add_conditional_edges("review_steps", check_approval)

# 5. Finalizing Graph
workflow.set_entry_point("generate_steps")
workflow.add_node("end", lambda x: x)
checkpointer = MemorySaver()
graph = workflow.compile()

# --- Step 6: Run the Workflow ---
user_input = input("Hey, how can I help you today?\n")

graph.invoke({"user_input": user_input})
