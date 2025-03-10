import os
from langchain_google_genai import ChatGoogleGenerativeAI
import pytest
from sqlalchemy import text, inspect
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)


@pytest.fixture(scope="session")
def setup_database():
    # Create test database
    db_path = "sqlite:///tests/sample.db"
    db = SQLDatabase.from_uri(db_path)

    with db._engine.connect() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )

        conn.execute(
            text(
                """
                INSERT INTO users (username, password, email)
                VALUES 
                    ('john_doe', 'password123', 'john.doe@example.com'),
                    ('jane_smith', 'securePass456', 'jane.smith@example.com'),
                    ('bob_jones', 'mypassword789', 'bob.jones@example.com')
                """
            )
        )

        conn.commit()

    return db


@pytest.fixture
def setup_agent(setup_database):
    db = setup_database

    # Force the database to refresh its metadata
    inspector = inspect(db._engine)
    table_names = inspector.get_table_names()
    print(f"Inspector found tables: {table_names}")

    # Recreate the SQLDatabase object to ensure fresh metadata
    db_uri = str(db._engine.url)
    fresh_db = SQLDatabase.from_uri(
        db_uri,
        include_tables=["users"],  # Explicitly include the users table
        sample_rows_in_table_info=3,  # Include sample rows in table info
    )

    # Verify the database is correctly set up
    print(f"Table info: {fresh_db.get_table_info()}")

    # Set up the agent with the LLM
    llm = ChatGoogleGenerativeAI(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        model="gemini-1.5-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    # Create the agent executor
    agent_executor = create_sql_agent(
        llm, db=fresh_db, agent_type="openai-tools", verbose=True
    )

    return agent_executor, fresh_db


def test_database_setup(setup_database):
    """Test that the database is set up correctly"""
    db = setup_database

    # Check if users table exists with correct schema
    result = db.run("PRAGMA table_info(users)")

    # Ensure the result is parsed correctly
    if isinstance(result, str):
        result = eval(result)

    column_names = [col[1] for col in result]

    assert len(column_names) == 5
    assert "user_id" in column_names
    assert "username" in column_names
    assert "password" in column_names
    assert "email" in column_names
    assert "created_at" in column_names


def test_data_insertion(setup_database):
    """Test that data was inserted correctly"""
    db = setup_database

    # Check the number of users
    result = db.run("SELECT COUNT(*) FROM users")

    # Ensure parsing works correctly
    if isinstance(result, str):
        result = eval(result)

    assert int(result[0][0]) == 3

    # Check specific user data
    result = db.run("SELECT username, email FROM users WHERE username = 'john_doe'")
    if isinstance(result, str):
        result = eval(result)

    assert result[0][0] == "john_doe"
    assert result[0][1] == "john.doe@example.com"


def test_query_limit(setup_database):
    """Test the SELECT query with LIMIT"""
    db = setup_database

    result = db.run("SELECT * FROM users LIMIT 10;")
    if isinstance(result, str):
        result = eval(result)

    assert len(result) == 3  # Only 3 users exist


def test_agent_using_query(setup_agent):
    """Test the actual LLM agent response for retrieving emails"""
    agent_executor, db = setup_agent

    db_uri = db._engine.url
    db = SQLDatabase.from_uri(str(db_uri))

    tables = db.run("SELECT name FROM sqlite_master WHERE type='table';")
    print(f"Available tables: {tables}")

    # Debug: Verify users exist in the database
    users = db.run("SELECT * FROM users;")
    print(f"Users in database: {users}")

    # Run the LLM agent with the query
    query = "get emails of all users starting with letter j"
    result = agent_executor.invoke(query)

    # Verify the response contains the expected emails
    assert "john.doe@example.com" in str(result)
    assert "jane.smith@example.com" in str(result)
    assert "bob.jones@example.com" not in str(result)  # This should not be included

    # Additional checks to verify the agent used appropriate SQL
    # These are indirect tests since we don't have direct access to the SQL the agent generated
    j_users = db.run("SELECT email FROM users WHERE username LIKE 'j%'")

    # Parse the result properly
    if isinstance(j_users, str):
        j_users = eval(j_users)

    expected_emails = ["john.doe@example.com", "jane.smith@example.com"]
    actual_emails = [row[0] for row in j_users]

    # Verify all expected emails are found in database query
    for email in expected_emails:
        assert email in actual_emails
