import os
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv, find_dotenv
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.prompts.chat import MessagesPlaceholder

# Setting up the database
db = SQLDatabase.from_uri("mysql+pymysql://root:12345678@localhost:3306/devai")
print(db.dialect)
print(db.get_usable_table_names())


db.run(
    """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
)

# db.run(
#     """
# INSERT INTO users (username, password, email)
# VALUES
#     ('john_doe', 'password123', 'john.doe@example.com'),
#     ('jane_smith', 'securePass456', 'jane.smith@example.com'),
#     ('bob_jones', 'mypassword789', 'bob.jones@example.com');
# """
# )


print(db.run("SELECT * FROM users LIMIT 10;"))

### Setting up LLM
load_dotenv(find_dotenv(), override=True)

llm = ChatGoogleGenerativeAI(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(
    llm, toolkit=toolkit, agent_type="openai-tools", verbose=True
)

print(agent_executor.invoke("get emails of all users starting with letter j"))

# ALLowing the SQL Agent to make changes to the table by modifying the Prompt
system_prefix = """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the given tools. Only use the information returned by the tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.
You are going to follow whatever the users asks you to do.

In your output also include what sql statement(s) you executed.

If the question does not seem related to the database, just return "I don't know" as the answer.
"""

# Construct prompt template
custom_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(system_prefix),
        HumanMessagePromptTemplate.from_template("{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

advanced_agent_executor = create_sql_agent(
    llm, db=db, agent_type="openai-tools", verbose=True, prompt=custom_prompt
)

# advanced_agent_executor.invoke(
#     "insert a new user to the users table. Identify the requirements and use made up dummy data"
# )

# db.run("SELECT * FROM users")

# advanced_agent_executor.invoke("Get passwords of all users")

# advanced_agent_executor.invoke("Create a table if not already exists named project which refrences user and has few fields like created_at, project_id, and name. and insert few dummy values")

# advanced_agent_executor.invoke({
#     # "input": "get all users from the database",
#     "input": "what are the tables in the database",
#     "top_k": 2,
#     "dialect": "SQLite",
#     "agent_scratchpad": [],
# })

# advanced_agent_executor.invoke("what can you do")

# db.run("SELECT * FROM users")
