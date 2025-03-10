import os
from langchain_core.tools import tool


@tool
def read_file(file_path: str) -> str:
    """Reads the contents of a file if it exists."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return f"Error: {file_path} does not exist."


@tool
def write_file(file_path: str, content: str, replace: bool = False) -> str:
    """Writes or updates a file with the given content."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if replace:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content)
    return f"Updated {file_path}"
