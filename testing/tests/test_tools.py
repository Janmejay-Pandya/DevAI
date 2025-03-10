import os
import tempfile
import pytest
from main import read_file, write_file


@pytest.fixture
def setup_test_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file_path = os.path.join(temp_dir, "test.txt")
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write("This is test content")

        special_chars_file = os.path.join(temp_dir, "special.txt")
        with open(special_chars_file, "w", encoding="utf-8") as f:
            f.write("Special characters: áéíóú\n新年快乐")

        empty_file_path = os.path.join(temp_dir, "empty.txt")
        with open(empty_file_path, "w", encoding="utf-8") as f:
            pass

        yield {
            "temp_dir": temp_dir,
            "test_file": test_file_path,
            "special_file": special_chars_file,
            "empty_file": empty_file_path,
            "nonexistent_file": os.path.join(temp_dir, "nonexistent.txt"),
        }


def test_existing_file(setup_test_files):
    """Test reading an existing file returns the correct content."""
    result = read_file(setup_test_files["test_file"])
    assert result == "This is test content"


def test_nonexistent_file(setup_test_files):
    """Test that the function returns an error message when file doesn't exist."""
    nonexistent_path = setup_test_files["nonexistent_file"]
    result = read_file(nonexistent_path)
    assert result == f"Error: {nonexistent_path} does not exist."


def test_unicode_content(setup_test_files):
    """Test reading a file with unicode/special characters."""
    result = read_file(setup_test_files["special_file"])
    assert result == "Special characters: áéíóú\n新年快乐"


def test_empty_file(setup_test_files):
    """Test reading an empty file."""
    result = read_file(setup_test_files["empty_file"])
    assert result == ""


def test_write_new_file():
    """Test writing content to a new file."""
    file_path = "./tests/test_files/sample_text_file.txt"
    result = write_file.invoke(
        input={"file_path": file_path, "content": "Hello, world!"}
    )

    assert result == f"Updated {file_path}"
    assert os.path.exists(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert content == "Hello, world!"


def test_append_to_existing_file():
    """Test appending content to an existing file."""
    file_path = "./tests/test_files/sample_text_file.txt"

    # Append to the file
    result = write_file.invoke(
        input={"file_path": file_path, "content": "\nAdditional content"}
    )

    assert result == f"Updated {file_path}"

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert content == "Hello, world!\nAdditional content"


def test_replace_existing_file():
    """Test replacing content in an existing file."""
    file_path = "./tests/test_files/sample_text_file.txt"

    result = write_file.invoke(
        input={"file_path": file_path, "content": "", "replace": True}
    )

    assert result == f"Updated {file_path}"

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert content == ""
